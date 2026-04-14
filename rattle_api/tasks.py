"""
AI-driven task runner for Rattle product and interchange data.

Provides ready-made tasks that any CLI coding agent or automated pipeline
can invoke to:
  - Analyse / enrich product data
  - Transform interchange data between formats
  - Generate product descriptions, pricing suggestions, etc.
  - Analyse pricelists for configurator anti-patterns
  - Suggest BOM-aware configuration structures
  - Push AI-produced results back to the Rattle API

All tasks are model-agnostic — the active AI provider is selected at
runtime via the ``AI_PROVIDER`` env var or explicit argument.
"""

import json
import os
import sys

from .client import RattleClient
from .provider import get_provider

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ai(provider=None):
    """Resolve AI provider (lazy so callers can override)."""
    return provider or get_provider()


# ---------------------------------------------------------------------------
# Task: describe_products
# ---------------------------------------------------------------------------


def describe_products(tenant, *, provider=None, limit=5, language="de"):
    """Use AI to generate marketing descriptions for products.

    Fetches up to *limit* products from the Rattle API, sends each to the
    configured AI provider, and PATCHes the generated description back.

    Returns:
        list[dict] – ``[{"id": …, "description": …}, …]``
    """
    ai = _ai(provider)
    client = RattleClient(tenant)
    products = client.list_all("products", per_page=min(limit, 100))[:limit]

    system = (
        f"You are a product copywriter.  Write a short, professional "
        f"product description in {'German' if language == 'de' else language}.  "
        f"Return ONLY the description text, no headings or markdown."
    )

    results = []
    for prod in products:
        prod_id = prod.get("id")
        name = prod.get("name", "Unknown product")
        details = json.dumps(prod, ensure_ascii=False, default=str)[:2000]

        prompt = (
            f"Product name: {name}\n\n"
            f"Raw data:\n{details}\n\n"
            f"Write a 2-3 sentence product description."
        )

        try:
            description = ai.complete(prompt, system=system)
            # Push back to Rattle
            client.patch(f"products/{prod_id}", json={"description": description})
            results.append({"id": prod_id, "name": name, "description": description})
            print(f"  OK  {prod_id}: {name}")
        except Exception as exc:
            print(f"  FAIL {prod_id}: {exc}", file=sys.stderr)
            results.append({"id": prod_id, "name": name, "error": str(exc)})

    return results


# ---------------------------------------------------------------------------
# Task: classify_products
# ---------------------------------------------------------------------------


def classify_products(tenant, *, provider=None, limit=10):
    """Use AI to suggest category tags for products.

    Returns:
        list[dict] – ``[{"id": …, "tags": [str, …]}, …]``
    """
    ai = _ai(provider)
    client = RattleClient(tenant)
    products = client.list_all("products", per_page=min(limit, 100))[:limit]

    system = (
        "You are a product classifier for a product catalogue. "
        "Given the product JSON, return a JSON array of 1-5 category tag "
        "strings (in English). Return ONLY the JSON array, nothing else."
    )

    results = []
    for prod in products:
        prod_id = prod.get("id")
        prompt = json.dumps(prod, ensure_ascii=False, default=str)[:3000]

        try:
            tags = ai.complete_json(prompt, system=system)
            results.append({"id": prod_id, "tags": tags})
            print(f"  OK  {prod_id}: {tags}")
        except Exception as exc:
            print(f"  FAIL {prod_id}: {exc}", file=sys.stderr)
            results.append({"id": prod_id, "error": str(exc)})

    return results


# ---------------------------------------------------------------------------
# Task: transform_interchange
# ---------------------------------------------------------------------------


def transform_interchange(
    tenant, source_format, target_format, data_file, *, provider=None, push=False
):
    """Use AI to transform interchange data between formats.

    Reads *data_file* (JSON), asks the AI to convert from *source_format*
    to *target_format*, and optionally pushes results to the Rattle API.

    Supported format hints: "rattle", "datanorm", "eclass", "bmecat",
    "custom" (the AI adapts based on the hint).

    Args:
        tenant:        Rattle tenant name.
        source_format: Input data format identifier.
        target_format: Desired output format identifier.
        data_file:     Path to a JSON file with the source records.
        provider:      Optional explicit AIProvider instance.
        push:          If True, POST each transformed record to Rattle.

    Returns:
        list[dict] – transformed records.
    """
    ai = _ai(provider)

    with open(data_file, encoding="utf-8") as fh:
        source_data = json.load(fh)

    if not isinstance(source_data, list):
        source_data = [source_data]

    system = (
        f"You are a data transformation engine.  Convert each record from "
        f"'{source_format}' format to '{target_format}' format.  Return a "
        f"JSON array of the converted records.  Preserve all data; adapt "
        f"field names and structures to match the target schema."
    )

    prompt = json.dumps(source_data, ensure_ascii=False, default=str)[:8000]

    transformed = ai.complete_json(prompt, system=system, max_tokens=4096)
    if not isinstance(transformed, list):
        transformed = [transformed]

    print(f"  Transformed {len(transformed)} record(s) ({source_format} → {target_format})")

    if push:
        client = RattleClient(tenant)
        for record in transformed:
            try:
                client.post("products", json=record)
                print(f"  PUSH OK: {record.get('name', record.get('id', '?'))}")
            except Exception as exc:
                print(f"  PUSH FAIL: {exc}", file=sys.stderr)

    return transformed


# ---------------------------------------------------------------------------
# Task: analyse_data
# ---------------------------------------------------------------------------


def analyse_data(tenant, *, provider=None, question=None):
    """Ask an AI an open-ended question about the tenant's product data.

    Fetches a sample of products and lets the AI answer *question*
    (or a default analytical prompt).

    Returns:
        str – the AI's analysis.
    """
    ai = _ai(provider)
    client = RattleClient(tenant)
    sample = client.list_all("products", per_page=20)[:20]

    system = (
        "You are a data analyst.  You receive a JSON sample of "
        "products from a catalogue.  Answer the user's question "
        "with clear, actionable insights."
    )
    if not question:
        question = (
            "Analyse this product sample.  Identify any data quality "
            "issues, missing fields, and suggest improvements."
        )

    prompt = (
        f"Product sample ({len(sample)} items):\n"
        f"{json.dumps(sample, ensure_ascii=False, default=str)[:6000]}\n\n"
        f"Question: {question}"
    )

    analysis = ai.complete(prompt, system=system, max_tokens=2048)
    print(analysis)
    return analysis


# ---------------------------------------------------------------------------
# Task: analyse_pricelist
# ---------------------------------------------------------------------------


def _resolve_source_file(tenant, source_file):
    """Resolve source file path — absolute or relative to source/<tenant>/."""
    if os.path.isabs(source_file):
        return source_file
    from .source import SOURCE_DIR

    return os.path.join(SOURCE_DIR, tenant.lower(), source_file)


def analyse_pricelist(tenant, source_file, *, provider=None, language="de"):
    """Analyse a pricelist / technical document for configurator anti-patterns.

    Two-phase analysis:
      1. Heuristic scan (free, no AI) via :func:`knowledge.detect_anti_patterns`
      2. AI analysis with embedded consulting knowledge + tenant profile

    Args:
        tenant:      Rattle tenant name.
        source_file: Filename relative to ``source/<tenant>/``, or absolute path.
        provider:    Optional explicit AIProvider instance.
        language:    Output language (default ``"de"``).

    Returns:
        dict with ``source_file``, ``file_type``, ``anti_patterns_heuristic``,
        ``ai_analysis``.
    """
    from .knowledge import detect_anti_patterns, system_prompt_analyse_pricelist
    from .memory import TenantMemory
    from .source import read_source

    ai = _ai(provider)
    filepath = _resolve_source_file(tenant, source_file)
    source = read_source(filepath)

    # Phase 1: heuristic scan (Excel only — structured data)
    heuristic_results = []
    if source["type"] == "excel":
        heuristic_results = detect_anti_patterns(source["data"])

    # Phase 2: AI analysis (tenant profile is read-only, never written)
    tenant_profile = TenantMemory(tenant).inject_into_prompt()
    system = system_prompt_analyse_pricelist(
        language=language,
        tenant_profile=tenant_profile or None,
    )
    if source["type"] == "excel":
        content = json.dumps(source["data"], ensure_ascii=False, default=str)[:8000]
    else:
        content = str(source["data"])[:8000]

    prompt = f"Source file: {source['filename']} ({source['type']})\n\nContent:\n{content}"

    ai_analysis = {}
    try:
        ai_analysis = ai.complete_json(prompt, system=system, max_tokens=4096)
        print(f"  OK  analyse_pricelist: {source['filename']}")
    except Exception as exc:
        print(f"  FAIL analyse_pricelist: {exc}", file=sys.stderr)
        ai_analysis = {"error": str(exc)}

    return {
        "source_file": source_file,
        "file_type": source["type"],
        "anti_patterns_heuristic": heuristic_results,
        "ai_analysis": ai_analysis,
    }


# ---------------------------------------------------------------------------
# Task: suggest_configuration
# ---------------------------------------------------------------------------


def suggest_configuration(
    tenant, source_file, *, provider=None, language="de", product_filter=None
):
    """Generate explicit BOM-aware configuration recommendations.

    Fetches existing groups/options from Rattle to prefer reuse over
    duplication.  Suggests forbidden combinations and area overrides.

    Args:
        tenant:         Rattle tenant name.
        source_file:    Filename relative to ``source/<tenant>/``, or absolute.
        provider:       Optional explicit AIProvider instance.
        language:       Output language (default ``"de"``).
        product_filter: Optional product name to focus on.

    Returns:
        dict with ``source_file``, ``existing_groups_checked``, ``products``
        (each with ``groups``, ``usage_subclauses``, ``forbidden_combinations``).
    """
    from .knowledge import system_prompt_suggest_configuration
    from .memory import TenantMemory
    from .source import read_source

    ai = _ai(provider)
    client = RattleClient(tenant)
    filepath = _resolve_source_file(tenant, source_file)
    source = read_source(filepath)

    # Fetch existing groups/options for reuse
    existing_groups = []
    try:
        existing_groups = client.list_all("groups")
    except Exception:
        print("  WARN: could not fetch existing groups", file=sys.stderr)

    # Tenant profile is read-only — explicit writes only via `memory` commands.
    tenant_profile = TenantMemory(tenant).inject_into_prompt()
    system = system_prompt_suggest_configuration(
        language=language,
        existing_groups=existing_groups if existing_groups else None,
        tenant_profile=tenant_profile or None,
    )

    if source["type"] == "excel":
        content = json.dumps(source["data"], ensure_ascii=False, default=str)[:8000]
    else:
        content = str(source["data"])[:8000]

    prompt = f"Source file: {source['filename']} ({source['type']})\n\n"
    if product_filter:
        prompt += f"Focus on product: {product_filter}\n\n"
    prompt += f"Content:\n{content}"

    try:
        result = ai.complete_json(prompt, system=system, max_tokens=8192)
        print(f"  OK  suggest_configuration: {source['filename']}")
    except Exception as exc:
        print(f"  FAIL suggest_configuration: {exc}", file=sys.stderr)
        result = {"error": str(exc), "products": []}

    # Ensure top-level structure
    if isinstance(result, dict) and "products" not in result:
        result = {"products": result if isinstance(result, list) else [result]}

    return {
        "source_file": source_file,
        "existing_groups_checked": len(existing_groups),
        **result,
    }


# ---------------------------------------------------------------------------
# Registry (for CLI dispatch)
# ---------------------------------------------------------------------------

TASKS = {
    "describe-products": describe_products,
    "classify-products": classify_products,
    "transform-interchange": transform_interchange,
    "analyse-data": analyse_data,
    "analyse-pricelist": analyse_pricelist,
    "suggest-configuration": suggest_configuration,
}


# ---------------------------------------------------------------------------
# Prompt-template stage runner + full pipeline runner
# ---------------------------------------------------------------------------


def _read_source_content(source_file, *, tenant):
    """Resolve and read a source file; return (source_dict, content_str)."""
    from .source import read_source

    filepath = _resolve_source_file(tenant, source_file)
    source = read_source(filepath)
    if source["type"] == "excel":
        content = json.dumps(source["data"], ensure_ascii=False, default=str)[:12000]
    else:
        content = str(source["data"])[:12000]
    return source, content


def _parse_operations(raw):
    """Extract an ``operations`` list from the AI's JSON response."""
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        ops = raw.get("operations")
        if isinstance(ops, list):
            return ops
    return []


def _write_trace(trace_dir, stage_id, *, prompt, ai_raw, report):
    """Save a per-stage transcript under *trace_dir* if provided."""
    if not trace_dir:
        return
    import os as _os

    _os.makedirs(trace_dir, exist_ok=True)
    path = _os.path.join(trace_dir, f"{stage_id}.json")
    payload = {
        "stage": stage_id,
        "prompt_head": prompt[:2000],
        "ai_output": ai_raw,
        "report": report.to_dict() if report is not None else None,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)


def run_build_stage(
    tenant,
    template_id,
    source_file=None,
    *,
    provider=None,
    language="de",
    dry_run=False,
    extra_inputs=None,
    client=None,
    builder=None,
    prior_features=None,
    trace_dir=None,
):
    """Run a single prompt template against live Rattle state.

    Renders the template via :mod:`rattle_api.prompt_templates`, calls the
    AI, passes the returned ``ensure_*`` operations through
    :class:`rattle_api.builder.ConfigBuilder`, and returns the
    :class:`BuildReport`. The builder applies operations **directly** to
    the Rattle REST API as idempotent get-or-create calls; set
    ``dry_run=True`` to inspect the operations without applying them.

    Validation happens in the Rattle frontend — the caller should open the
    tenant URL printed by :func:`run_build_configurator` and verify the
    configurator behaves as expected.
    """
    from .builder import BuildReport, ConfigBuilder
    from .memory import TenantMemory
    from .prompt_templates import get_template

    ai = _ai(provider)
    tpl = get_template(template_id)

    client = client or RattleClient(tenant)
    builder = builder or ConfigBuilder(client, dry_run=dry_run)
    if not builder.record_index:
        live_state = builder.fetch_live_state()
    else:
        live_state = {
            "products": [rec for (t, _), rec in builder.record_index.items() if t == "product"],
            "areas": [rec for (t, _), rec in builder.record_index.items() if t == "area"],
            "groups": [rec for (t, _), rec in builder.record_index.items() if t == "group"],
            "parts": [rec for (t, _), rec in builder.record_index.items() if t == "part"],
        }

    tenant_profile = TenantMemory(tenant).inject_into_prompt()

    source_content = ""
    source_filename = ""
    if source_file is not None:
        source, source_content = _read_source_content(source_file, tenant=tenant)
        source_filename = source["filename"]

    # Heuristic pre-pass (Excel only) for stages that use it.
    heuristic_findings = []
    if source_file is not None:
        from .source import read_source

        filepath = _resolve_source_file(tenant, source_file)
        parsed = read_source(filepath)
        if parsed["type"] == "excel":
            from .knowledge import detect_anti_patterns

            heuristic_findings = detect_anti_patterns(parsed["data"])

    build_kwargs = {
        "source_content": source_content,
        "live_state": live_state,
        "tenant_profile": tenant_profile or None,
        "tenant": tenant,
        "language": language,
        "heuristic_findings": heuristic_findings,
        "features": (extra_inputs or {}).get("features") or prior_features,
    }
    for k, v in (extra_inputs or {}).items():
        build_kwargs.setdefault(k, v)

    system = tpl.render(**build_kwargs)

    if source_file is not None:
        prompt = f"Source file: {source_filename}\n\nContent:\n{source_content}"
    else:
        prompt = "Use the live Rattle state above to complete this stage."
    if prior_features:
        prompt += (
            "\n\nFeatures discovered in the previous stage:\n"
            + json.dumps(prior_features, ensure_ascii=False)[:6000]
        )

    try:
        ai_raw = ai.complete_json(prompt, system=system, max_tokens=4096)
    except Exception as exc:
        print(f"  FAIL {template_id}: {exc}", file=sys.stderr)
        report = BuildReport()
        report.failed.append({"op": {"stage": template_id}, "error": str(exc)})
        _write_trace(trace_dir, template_id, prompt=prompt, ai_raw=None, report=report)
        return {
            "template_id": template_id,
            "report": report.to_dict(),
            "ai_output": None,
        }

    operations = _parse_operations(ai_raw)
    if tpl.read_only:
        # Read-only stages (review-configuration) do not emit operations.
        report = BuildReport()
    else:
        report = builder.apply(operations)

    _write_trace(trace_dir, template_id, prompt=prompt, ai_raw=ai_raw, report=report)

    return {
        "template_id": template_id,
        "report": report.to_dict(),
        "ai_output": ai_raw,
    }


def run_build_configurator(
    tenant,
    source_file,
    *,
    provider=None,
    language="de",
    single_shot=False,
    dry_run=False,
    trace_dir=None,
    skip_stages=None,
    client=None,
):
    """Run the full configurator-building pipeline.

    Each stage produces ``ensure_*`` operations that are applied
    **directly** to the Rattle REST API via
    :class:`rattle_api.builder.ConfigBuilder`. The ``review-configuration``
    stage is always run last as a read-only pass against the final live
    state. The pipeline prints the tenant frontend URL so the user can
    click through and validate the configurator visually.

    With ``single_shot=True`` the pipeline makes a single AI call via the
    ``full-configurator`` template and applies all operations in one
    topologically-ordered ``ConfigBuilder.apply`` pass, still running the
    read-only review at the end.
    """
    from .builder import ConfigBuilder
    from .config import get_frontend_url
    from .prompt_templates import PIPELINE_STAGE_ORDER

    ai = _ai(provider)
    client = client or RattleClient(tenant)
    builder = ConfigBuilder(client, dry_run=dry_run)
    # Prime the builder's name index from the live Rattle state; stages
    # then share this one builder instance, so each stage sees the up-to-date
    # name→id map as earlier stages create new entities.
    builder.fetch_live_state()

    skip = set(skip_stages or [])
    results: list[dict] = []

    if single_shot:
        result = run_build_stage(
            tenant,
            "full-configurator",
            source_file,
            provider=ai,
            language=language,
            dry_run=dry_run,
            client=client,
            builder=builder,
            trace_dir=trace_dir,
        )
        results.append(result)
    else:
        prior_features = None
        for stage_id in PIPELINE_STAGE_ORDER:
            if stage_id in skip:
                print(f"  SKIP {stage_id}", file=sys.stderr)
                continue
            print(f"  STAGE {stage_id}", file=sys.stderr)
            result = run_build_stage(
                tenant,
                stage_id,
                source_file,
                provider=ai,
                language=language,
                dry_run=dry_run,
                client=client,
                builder=builder,
                prior_features=prior_features,
                trace_dir=trace_dir,
            )
            results.append(result)
            if stage_id == "discover-features":
                ai_out = result.get("ai_output") or {}
                if isinstance(ai_out, dict):
                    prior_features = ai_out.get("features")

    # Final read-only review against the latest live state.
    if "review-configuration" not in skip and not single_shot:
        # In the 9-stage path review-configuration has already been run as
        # the last stage; the wrapper skips it here.
        review_already = any(r.get("template_id") == "review-configuration" for r in results)
        if not review_already:
            results.append(
                run_build_stage(
                    tenant,
                    "review-configuration",
                    source_file=None,
                    provider=ai,
                    language=language,
                    dry_run=dry_run,
                    client=client,
                    builder=builder,
                    trace_dir=trace_dir,
                )
            )
    elif single_shot and "review-configuration" not in skip:
        results.append(
            run_build_stage(
                tenant,
                "review-configuration",
                source_file=None,
                provider=ai,
                language=language,
                dry_run=dry_run,
                client=client,
                builder=builder,
                trace_dir=trace_dir,
            )
        )

    # Aggregate builder report.
    summary = {
        "counts": builder.report.counts(),
        "stages": [r.get("template_id") for r in results],
        "single_shot": single_shot,
        "dry_run": dry_run,
    }
    frontend_url = get_frontend_url(tenant)
    created_product_names = [
        entry.get("name") for entry in builder.report.created if entry.get("entity") == "product"
    ]
    summary["frontend_url"] = frontend_url
    summary["created_products"] = created_product_names

    print("", file=sys.stderr)
    print(f"  DONE counts={summary['counts']}", file=sys.stderr)
    print(f"  OPEN {frontend_url}", file=sys.stderr)
    if created_product_names:
        print(
            f"  NEW PRODUCTS  {', '.join(str(n) for n in created_product_names)}",
            file=sys.stderr,
        )

    return {
        "summary": summary,
        "stages": results,
    }
