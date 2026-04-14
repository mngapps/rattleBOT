"""
ConfigBuilder — idempotent applier for ``ensure_*`` operations against the
Rattle REST API.

The prompt template library in :mod:`rattle_api.prompt_templates` drives the
AI to emit structured ``ensure_*`` operation lists. This module takes those
lists and executes them **directly** via :class:`rattle_api.client.RattleClient`
as idempotent get-or-create calls — no intermediate JSON files, no hand-apply
step. The user validates the result by opening the Rattle frontend.

Each ``ensure_*`` method:

1. looks up the target entity by natural key (name),
2. creates it if missing,
3. patches it if a drift is detected,
4. records the resolved id in an in-memory name→id map so downstream
   operations in the same batch can reference by name.

A :class:`BuildReport` summarises every operation as ``created``, ``updated``,
``unchanged``, or ``failed``.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any

from .client import RattleClient

# ---------------------------------------------------------------------------
# BuildReport
# ---------------------------------------------------------------------------


@dataclass
class BuildReport:
    """Structured summary of a :meth:`ConfigBuilder.apply` run."""

    created: list[dict] = field(default_factory=list)
    updated: list[dict] = field(default_factory=list)
    unchanged: list[dict] = field(default_factory=list)
    failed: list[dict] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        return {
            "created": len(self.created),
            "updated": len(self.updated),
            "unchanged": len(self.unchanged),
            "failed": len(self.failed),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": self.counts(),
            "created": self.created,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "failed": self.failed,
        }

    def merge(self, other: BuildReport) -> None:
        self.created.extend(other.created)
        self.updated.extend(other.updated)
        self.unchanged.extend(other.unchanged)
        self.failed.extend(other.failed)


# ---------------------------------------------------------------------------
# ConfigBuilder
# ---------------------------------------------------------------------------


class ConfigBuilder:
    """Apply ``ensure_*`` operations idempotently to the Rattle REST API."""

    SUPPORTED_OPS: tuple[str, ...] = (
        "ensure_product",
        "ensure_area",
        "ensure_group",
        "link_group_to_area",
        "ensure_option",
        "ensure_area_config",
        "ensure_part",
        "ensure_bom_item",
        "ensure_constraint_pair",
        "ensure_constraint_rule",
        "patch_option_recommended",
        "ensure_document_template",
        "ensure_structure_block",
        "ensure_attachment",
    )

    def __init__(self, client: RattleClient, *, dry_run: bool = False, verbose: bool = True):
        self.client = client
        self.dry_run = dry_run
        self.verbose = verbose
        # (entity_type, natural_key_lower) -> id
        self.name_index: dict[tuple[str, str], Any] = {}
        # cached full records keyed the same way — lets us detect drift
        self.record_index: dict[tuple[str, str], dict] = {}
        self.report = BuildReport()

    # -- helpers -------------------------------------------------------------

    def _log(self, action: str, entity: str, name: str, detail: str = "") -> None:
        if not self.verbose:
            return
        marker = {"CREATE": "+", "UPDATE": "~", "UNCHANGED": "=", "FAIL": "!"}.get(action, "?")
        msg = f"  {marker} {action:<9} {entity:<18} {name!r}"
        if detail:
            msg += f"  {detail}"
        print(msg, file=sys.stderr)

    @staticmethod
    def _nk(name: str) -> str:
        return (name or "").strip().lower()

    def _resolve(self, entity_type: str, name: str) -> Any:
        """Return the id of a previously-indexed entity by name, or raise."""
        key = (entity_type, self._nk(name))
        if key not in self.name_index:
            raise LookupError(
                f"No {entity_type} with name {name!r} known to the builder — "
                f"emit the ensure_* op for it before referencing it"
            )
        return self.name_index[key]

    def _index(self, entity_type: str, name: str, record: dict) -> None:
        key = (entity_type, self._nk(name))
        self.name_index[key] = record.get("id")
        self.record_index[key] = record

    @staticmethod
    def _safe_list(result: Any) -> list[dict]:
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            data = result.get("data")
            if isinstance(data, list):
                return data
        return []

    # -- live-state prime ----------------------------------------------------

    def fetch_live_state(self) -> dict:
        """Prime the name index from the tenant's current catalogue.

        Fetches products, areas, groups (with options), and parts via
        :meth:`RattleClient.list_all` and records each entity's id and
        natural key so subsequent ``ensure_*`` calls can find existing
        records without creating duplicates.

        Returns a dict summary suitable for passing to the prompt templates
        as ``live_state``.
        """
        state: dict[str, list[dict]] = {
            "products": [],
            "areas": [],
            "groups": [],
            "parts": [],
        }

        try:
            products = self._safe_list(self.client.list_all("products"))
            state["products"] = products
            for p in products:
                self._index("product", p.get("name", ""), p)
        except Exception as exc:  # pragma: no cover - best-effort prime
            print(f"  warn: could not prime products: {exc}", file=sys.stderr)

        try:
            areas = self._safe_list(self.client.list_all("areas"))
            state["areas"] = areas
            for a in areas:
                self._index("area", a.get("name", ""), a)
        except Exception as exc:  # pragma: no cover
            print(f"  warn: could not prime areas: {exc}", file=sys.stderr)

        try:
            groups = self._safe_list(self.client.list_all("groups"))
            state["groups"] = groups
            for g in groups:
                self._index("group", g.get("name", ""), g)
                for opt in g.get("options") or []:
                    self._index("option", opt.get("name", ""), opt)
        except Exception as exc:  # pragma: no cover
            print(f"  warn: could not prime groups: {exc}", file=sys.stderr)

        try:
            parts = self._safe_list(self.client.list_all("parts"))
            state["parts"] = parts
            for part in parts:
                nk = part.get("part_number") or part.get("part_name") or ""
                self._index("part", nk, part)
        except Exception as exc:  # pragma: no cover
            print(f"  warn: could not prime parts: {exc}", file=sys.stderr)

        return state

    # -- top-level dispatch --------------------------------------------------

    def apply(self, operations: list[dict]) -> BuildReport:
        """Apply *operations* to the Rattle API in order."""
        for raw in operations:
            if not isinstance(raw, dict):
                self.report.failed.append({"op": raw, "error": "operation must be a dict"})
                self._log("FAIL", "?", str(raw)[:40], "not a dict")
                continue
            op_type = raw.get("op")
            if op_type not in self.SUPPORTED_OPS:
                self.report.failed.append({"op": raw, "error": f"unknown op type {op_type!r}"})
                self._log("FAIL", op_type or "?", raw.get("name", "?"), "unknown op")
                continue
            handler = getattr(self, op_type, None)
            if handler is None:
                self.report.failed.append({"op": raw, "error": f"no handler for {op_type!r}"})
                continue
            op_kwargs = {k: v for k, v in raw.items() if k != "op"}
            try:
                handler(**op_kwargs)
            except Exception as exc:
                self.report.failed.append({"op": raw, "error": str(exc)})
                self._log("FAIL", op_type, op_kwargs.get("name", "?"), str(exc))
        return self.report

    def dry_run_apply(self, operations: list[dict]) -> BuildReport:
        """Convenience — run :meth:`apply` with ``dry_run=True`` semantics."""
        prior = self.dry_run
        self.dry_run = True
        try:
            return self.apply(operations)
        finally:
            self.dry_run = prior

    # -- ensure_* handlers ---------------------------------------------------

    def _classify(
        self,
        *,
        entity: str,
        op: str,
        name: str,
        existing: dict | None,
        drifted: bool,
        created_record: dict | None,
    ) -> None:
        entry = {"op": op, "entity": entity, "name": name}
        if existing is None:
            self.report.created.append(entry)
            self._log("CREATE", entity, name)
        elif drifted:
            self.report.updated.append(entry)
            self._log("UPDATE", entity, name)
        else:
            self.report.unchanged.append(entry)
            self._log("UNCHANGED", entity, name)
        if created_record is not None:
            self._index(entity, name, created_record)

    # ---- products ----------------------------------------------------------

    def ensure_product(
        self,
        *,
        name: str,
        base_price: float | int | None = None,
        currency: str | None = None,
        description: str | None = None,
        **extras: Any,
    ) -> Any:
        key = ("product", self._nk(name))
        existing = self.record_index.get(key)
        payload: dict[str, Any] = {"name": name}
        if base_price is not None:
            payload["base_price"] = base_price
        if currency is not None:
            payload["currency"] = currency
        if description is not None:
            payload["description"] = description

        drifted = False
        if existing:
            for k, v in payload.items():
                if k == "name":
                    continue
                if existing.get(k) != v:
                    drifted = True
                    break
            if drifted and not self.dry_run:
                updated = self.client.patch(f"products/{existing['id']}", json=payload)
                if isinstance(updated, dict):
                    self._index("product", name, updated)
            self._classify(
                entity="product",
                op="ensure_product",
                name=name,
                existing=existing,
                drifted=drifted,
                created_record=None,
            )
            return existing.get("id")

        if self.dry_run:
            self._classify(
                entity="product",
                op="ensure_product",
                name=name,
                existing=None,
                drifted=False,
                created_record={"id": None, **payload},
            )
            return None

        created = self.client.post("products", json=payload) or {}
        record = {**payload, **(created if isinstance(created, dict) else {})}
        self._classify(
            entity="product",
            op="ensure_product",
            name=name,
            existing=None,
            drifted=False,
            created_record=record,
        )
        return record.get("id")

    # ---- areas -------------------------------------------------------------

    def ensure_area(
        self,
        *,
        name: str,
        parent_product: str | None = None,
        description: str | None = None,
        **extras: Any,
    ) -> Any:
        key = ("area", self._nk(name))
        existing = self.record_index.get(key)
        payload: dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description

        product_id: Any = None
        if parent_product:
            try:
                product_id = self._resolve("product", parent_product)
            except LookupError:
                product_id = None

        drifted = False
        if existing:
            if description is not None and existing.get("description") != description:
                drifted = True
                if not self.dry_run:
                    updated = self.client.patch(f"areas/{existing['id']}", json=payload)
                    if isinstance(updated, dict):
                        self._index("area", name, updated)
            self._classify(
                entity="area",
                op="ensure_area",
                name=name,
                existing=existing,
                drifted=drifted,
                created_record=None,
            )
            return existing.get("id")

        if self.dry_run:
            self._classify(
                entity="area",
                op="ensure_area",
                name=name,
                existing=None,
                drifted=False,
                created_record={"id": None, **payload},
            )
            return None

        created = self.client.post("areas", json=payload) or {}
        record = {**payload, **(created if isinstance(created, dict) else {})}
        # Assign the area to the product if we know its id.
        if product_id is not None and record.get("id") is not None:
            try:
                self.client.post(
                    f"products/{product_id}/areas",
                    json={"area_id": record["id"]},
                )
            except Exception as exc:  # pragma: no cover - best effort
                print(
                    f"  warn: failed to attach area {name!r} to product {parent_product!r}: {exc}",
                    file=sys.stderr,
                )
        self._classify(
            entity="area",
            op="ensure_area",
            name=name,
            existing=None,
            drifted=False,
            created_record=record,
        )
        return record.get("id")

    # ---- groups ------------------------------------------------------------

    def ensure_group(
        self,
        *,
        name: str,
        is_multi: bool = False,
        description: str | None = None,
        reuse_existing: bool = False,
        existing_group_id: Any = None,
        **extras: Any,
    ) -> Any:
        key = ("group", self._nk(name))
        existing = self.record_index.get(key)

        # Reuse hint from the AI: if the id exists in the live state, treat
        # it as pre-existing even if the name differs slightly.
        if reuse_existing and existing_group_id is not None and not existing:
            # find by id in the record_index
            for (etype, _), rec in list(self.record_index.items()):
                if etype == "group" and rec.get("id") == existing_group_id:
                    existing = rec
                    break

        payload: dict[str, Any] = {"name": name, "is_multi": bool(is_multi)}
        if description is not None:
            payload["description"] = description

        drifted = False
        if existing:
            if existing.get("is_multi", False) != bool(is_multi):
                drifted = True
            if description is not None and existing.get("description") != description:
                drifted = True
            if drifted and not self.dry_run:
                updated = self.client.patch(f"groups/{existing['id']}", json=payload)
                if isinstance(updated, dict):
                    self._index("group", name, updated)
            self._classify(
                entity="group",
                op="ensure_group",
                name=name,
                existing=existing,
                drifted=drifted,
                created_record=None,
            )
            return existing.get("id")

        if self.dry_run:
            self._classify(
                entity="group",
                op="ensure_group",
                name=name,
                existing=None,
                drifted=False,
                created_record={"id": None, **payload},
            )
            return None

        created = self.client.post("groups", json=payload) or {}
        record = {**payload, **(created if isinstance(created, dict) else {})}
        self._classify(
            entity="group",
            op="ensure_group",
            name=name,
            existing=None,
            drifted=False,
            created_record=record,
        )
        return record.get("id")

    def link_group_to_area(self, *, group: str, area: str, **extras: Any) -> None:
        try:
            group_id = self._resolve("group", group)
            area_id = self._resolve("area", area)
        except LookupError as exc:
            self.report.failed.append(
                {
                    "op": {"op": "link_group_to_area", "group": group, "area": area},
                    "error": str(exc),
                }
            )
            self._log("FAIL", "link", f"{group!r}->{area!r}", str(exc))
            return

        entry = {"op": "link_group_to_area", "group": group, "area": area}
        if self.dry_run:
            self.report.created.append(entry)
            self._log("CREATE", "group->area", f"{group!r}->{area!r}")
            return
        try:
            self.client.post(
                f"groups/{group_id}/areas",
                json={"area_id": area_id},
            )
            self.report.created.append(entry)
            self._log("CREATE", "group->area", f"{group!r}->{area!r}")
        except Exception as exc:  # pragma: no cover
            self.report.failed.append({"op": entry, "error": str(exc)})
            self._log("FAIL", "link", f"{group!r}->{area!r}", str(exc))

    # ---- options -----------------------------------------------------------

    def ensure_option(
        self,
        *,
        name: str,
        group: str,
        price: float | int = 0,
        recommended: bool = False,
        description: str | None = None,
        **extras: Any,
    ) -> Any:
        try:
            group_id = self._resolve("group", group)
        except LookupError as exc:
            self.report.failed.append(
                {"op": {"op": "ensure_option", "name": name, "group": group}, "error": str(exc)}
            )
            self._log("FAIL", "option", name, str(exc))
            return None

        key = ("option", self._nk(name))
        existing = self.record_index.get(key)

        payload: dict[str, Any] = {
            "name": name,
            "group_id": group_id,
            "price": price,
            "recommended": bool(recommended),
        }
        if description is not None:
            payload["description"] = description

        drifted = False
        if existing:
            if existing.get("price") != price:
                drifted = True
            if bool(existing.get("recommended", False)) != bool(recommended):
                drifted = True
            if description is not None and existing.get("description") != description:
                drifted = True
            if drifted and not self.dry_run:
                updated = self.client.patch(f"options/{existing['id']}", json=payload)
                if isinstance(updated, dict):
                    self._index("option", name, updated)
            self._classify(
                entity="option",
                op="ensure_option",
                name=name,
                existing=existing,
                drifted=drifted,
                created_record=None,
            )
            return existing.get("id")

        if self.dry_run:
            self._classify(
                entity="option",
                op="ensure_option",
                name=name,
                existing=None,
                drifted=False,
                created_record={"id": None, **payload},
            )
            return None

        created = self.client.post("options", json=payload) or {}
        record = {**payload, **(created if isinstance(created, dict) else {})}
        self._classify(
            entity="option",
            op="ensure_option",
            name=name,
            existing=None,
            drifted=False,
            created_record=record,
        )
        return record.get("id")

    def ensure_area_config(
        self,
        *,
        option: str,
        area: str,
        price: float | int | None = None,
        description: str | None = None,
        recommended: bool | None = None,
        **extras: Any,
    ) -> None:
        try:
            option_id = self._resolve("option", option)
            area_id = self._resolve("area", area)
        except LookupError as exc:
            self.report.failed.append(
                {
                    "op": {"op": "ensure_area_config", "option": option, "area": area},
                    "error": str(exc),
                }
            )
            self._log("FAIL", "area-config", f"{option!r}@{area!r}", str(exc))
            return

        payload: dict[str, Any] = {}
        if price is not None:
            payload["price"] = price
        if description is not None:
            payload["description"] = description
        if recommended is not None:
            payload["recommended"] = bool(recommended)

        entry = {"op": "ensure_area_config", "option": option, "area": area}
        if self.dry_run:
            self.report.updated.append(entry)
            self._log("UPDATE", "area-config", f"{option!r}@{area!r}")
            return
        try:
            self.client.put(
                f"options/{option_id}/area-config",
                json={"area_id": area_id, **payload},
            )
            self.report.updated.append(entry)
            self._log("UPDATE", "area-config", f"{option!r}@{area!r}")
        except Exception as exc:  # pragma: no cover
            self.report.failed.append({"op": entry, "error": str(exc)})
            self._log("FAIL", "area-config", f"{option!r}@{area!r}", str(exc))

    # ---- parts & BOM -------------------------------------------------------

    def ensure_part(
        self,
        *,
        part_number: str | None = None,
        part_name: str,
        part_cost: float | int | None = None,
        part_type: str | None = None,
        **extras: Any,
    ) -> Any:
        natural = part_number or part_name
        key = ("part", self._nk(natural))
        existing = self.record_index.get(key)

        payload: dict[str, Any] = {"part_name": part_name}
        if part_number is not None:
            payload["part_number"] = part_number
        if part_cost is not None:
            payload["part_cost"] = part_cost
        if part_type is not None:
            payload["part_type"] = part_type

        drifted = False
        if existing:
            for k, v in payload.items():
                if existing.get(k) != v:
                    drifted = True
                    break
            if drifted and not self.dry_run:
                updated = self.client.patch(f"parts/{existing['id']}", json=payload)
                if isinstance(updated, dict):
                    self._index("part", natural, updated)
            self._classify(
                entity="part",
                op="ensure_part",
                name=str(natural),
                existing=existing,
                drifted=drifted,
                created_record=None,
            )
            return existing.get("id")

        if self.dry_run:
            self._classify(
                entity="part",
                op="ensure_part",
                name=str(natural),
                existing=None,
                drifted=False,
                created_record={"id": None, **payload},
            )
            return None

        created = self.client.post("parts", json=payload) or {}
        record = {**payload, **(created if isinstance(created, dict) else {})}
        self._classify(
            entity="part",
            op="ensure_part",
            name=str(natural),
            existing=None,
            drifted=False,
            created_record=record,
        )
        return record.get("id")

    def ensure_bom_item(
        self,
        *,
        parent_part: str,
        child_part: str,
        quantity: float | int = 1,
        uom: str | None = None,
        usage_subclauses: list[dict] | None = None,
        **extras: Any,
    ) -> None:
        try:
            parent_id = self._resolve("part", parent_part)
            child_id = self._resolve("part", child_part)
        except LookupError as exc:
            self.report.failed.append(
                {
                    "op": {
                        "op": "ensure_bom_item",
                        "parent_part": parent_part,
                        "child_part": child_part,
                    },
                    "error": str(exc),
                }
            )
            self._log("FAIL", "bom", f"{parent_part!r}->{child_part!r}", str(exc))
            return

        # Resolve option names inside usage_subclauses to ids.
        resolved_clauses: list[dict] = []
        for clause in usage_subclauses or []:
            opt_name = clause.get("option") or clause.get("option_name")
            factor = clause.get("factor", 1.0)
            if opt_name is None and "option_id" in clause:
                resolved_clauses.append({"option_id": clause["option_id"], "factor": factor})
                continue
            try:
                opt_id = self._resolve("option", opt_name or "")
            except LookupError as exc:
                self.report.failed.append(
                    {
                        "op": {
                            "op": "ensure_bom_item",
                            "parent_part": parent_part,
                            "child_part": child_part,
                            "option": opt_name,
                        },
                        "error": str(exc),
                    }
                )
                self._log("FAIL", "bom", f"{parent_part!r}->{child_part!r}", str(exc))
                return
            resolved_clauses.append({"option_id": opt_id, "factor": factor})

        payload: dict[str, Any] = {
            "child_part_id": child_id,
            "quantity": quantity,
            "usage_subclauses": resolved_clauses,
        }
        if uom is not None:
            payload["uom"] = uom

        entry = {
            "op": "ensure_bom_item",
            "parent_part": parent_part,
            "child_part": child_part,
        }
        if self.dry_run:
            self.report.created.append(entry)
            self._log("CREATE", "bom", f"{parent_part!r}->{child_part!r}")
            return
        try:
            self.client.post(f"parts/{parent_id}/bom", json=payload)
            self.report.created.append(entry)
            self._log("CREATE", "bom", f"{parent_part!r}->{child_part!r}")
        except Exception as exc:  # pragma: no cover
            self.report.failed.append({"op": entry, "error": str(exc)})
            self._log("FAIL", "bom", f"{parent_part!r}->{child_part!r}", str(exc))

    # ---- constraints -------------------------------------------------------

    def ensure_constraint_pair(
        self,
        *,
        option_1: str,
        option_2: str,
        product: str | None = None,
        description: str | None = None,
        **extras: Any,
    ) -> None:
        try:
            opt1_id = self._resolve("option", option_1)
            opt2_id = self._resolve("option", option_2)
        except LookupError as exc:
            self.report.failed.append(
                {
                    "op": {
                        "op": "ensure_constraint_pair",
                        "option_1": option_1,
                        "option_2": option_2,
                    },
                    "error": str(exc),
                }
            )
            self._log("FAIL", "constraint", f"{option_1!r}x{option_2!r}", str(exc))
            return

        product_id = None
        if product:
            try:
                product_id = self._resolve("product", product)
            except LookupError:
                product_id = None

        payload: dict[str, Any] = {"option_id1": opt1_id, "option_id2": opt2_id}
        if product_id is not None:
            payload["product_id"] = product_id
        if description is not None:
            payload["description"] = description

        entry = {"op": "ensure_constraint_pair", "option_1": option_1, "option_2": option_2}
        if self.dry_run:
            self.report.created.append(entry)
            self._log("CREATE", "constraint", f"{option_1!r}x{option_2!r}")
            return
        try:
            self.client.post("constraints", json=payload)
            self.report.created.append(entry)
            self._log("CREATE", "constraint", f"{option_1!r}x{option_2!r}")
        except Exception as exc:  # pragma: no cover
            self.report.failed.append({"op": entry, "error": str(exc)})
            self._log("FAIL", "constraint", f"{option_1!r}x{option_2!r}", str(exc))

    def ensure_constraint_rule(
        self,
        *,
        description: str,
        rule_json: list | None = None,
        product: str | None = None,
        **extras: Any,
    ) -> None:
        product_id = None
        if product:
            try:
                product_id = self._resolve("product", product)
            except LookupError:
                product_id = None

        payload: dict[str, Any] = {
            "description": description,
            "rule_json": rule_json or [],
        }
        if product_id is not None:
            payload["product_id"] = product_id

        entry = {"op": "ensure_constraint_rule", "description": description}
        if self.dry_run:
            self.report.created.append(entry)
            self._log("CREATE", "constraint-rule", description[:40])
            return
        try:
            self.client.post("constraints/rules", json=payload)
            self.report.created.append(entry)
            self._log("CREATE", "constraint-rule", description[:40])
        except Exception as exc:  # pragma: no cover
            self.report.failed.append({"op": entry, "error": str(exc)})
            self._log("FAIL", "constraint-rule", description[:40], str(exc))

    # ---- guided-selling patch ---------------------------------------------

    def patch_option_recommended(
        self,
        *,
        option: str,
        recommended: bool,
        preset: str | None = None,
        **extras: Any,
    ) -> None:
        try:
            option_id = self._resolve("option", option)
        except LookupError as exc:
            self.report.failed.append(
                {
                    "op": {
                        "op": "patch_option_recommended",
                        "option": option,
                        "recommended": recommended,
                    },
                    "error": str(exc),
                }
            )
            self._log("FAIL", "rec-patch", option, str(exc))
            return

        entry = {
            "op": "patch_option_recommended",
            "option": option,
            "recommended": recommended,
            "preset": preset,
        }
        if self.dry_run:
            self.report.updated.append(entry)
            self._log("UPDATE", "recommended", option)
            return
        try:
            self.client.patch(f"options/{option_id}", json={"recommended": bool(recommended)})
            self.report.updated.append(entry)
            self._log("UPDATE", "recommended", option)
        except Exception as exc:  # pragma: no cover
            self.report.failed.append({"op": entry, "error": str(exc)})
            self._log("FAIL", "recommended", option, str(exc))

    # ---- documents system --------------------------------------------------

    def ensure_document_template(
        self,
        *,
        name: str,
        doc_type: str = "offer",
        product: str | None = None,
        **extras: Any,
    ) -> Any:
        key = ("document_template", self._nk(name))
        existing = self.record_index.get(key)
        payload: dict[str, Any] = {"name": name, "doc_type": doc_type}
        if product:
            try:
                payload["product_id"] = self._resolve("product", product)
            except LookupError:
                pass

        if existing:
            self._classify(
                entity="document_template",
                op="ensure_document_template",
                name=name,
                existing=existing,
                drifted=False,
                created_record=None,
            )
            return existing.get("id")

        if self.dry_run:
            self._classify(
                entity="document_template",
                op="ensure_document_template",
                name=name,
                existing=None,
                drifted=False,
                created_record={"id": None, **payload},
            )
            return None

        created = self.client.post("documents/templates", json=payload) or {}
        record = {**payload, **(created if isinstance(created, dict) else {})}
        self._classify(
            entity="document_template",
            op="ensure_document_template",
            name=name,
            existing=None,
            drifted=False,
            created_record=record,
        )
        return record.get("id")

    def ensure_structure_block(
        self,
        *,
        template: str,
        slug: str,
        title: str,
        node_type: str = "chapter",
        parent_slug: str | None = None,
        order_index: int | None = None,
        **extras: Any,
    ) -> Any:
        try:
            template_id = self._resolve("document_template", template)
        except LookupError as exc:
            self.report.failed.append(
                {"op": {"op": "ensure_structure_block", "slug": slug}, "error": str(exc)}
            )
            self._log("FAIL", "struct-block", slug, str(exc))
            return None

        key = ("structure_block", f"{template_id}:{self._nk(slug)}")
        existing = self.record_index.get(key)
        payload: dict[str, Any] = {
            "slug": slug,
            "title": title,
            "node_type": node_type,
        }
        if order_index is not None:
            payload["order_index"] = order_index
        if parent_slug:
            payload["parent_slug"] = parent_slug

        if existing:
            self.report.unchanged.append({"op": "ensure_structure_block", "slug": slug})
            self._log("UNCHANGED", "struct-block", slug)
            return existing.get("id")

        if self.dry_run:
            record = {"id": None, **payload}
            self.name_index[key] = None
            self.record_index[key] = record
            self.report.created.append({"op": "ensure_structure_block", "slug": slug})
            self._log("CREATE", "struct-block", slug)
            return None

        created = (
            self.client.post(f"documents/templates/{template_id}/structure/blocks", json=payload)
            or {}
        )
        record = {**payload, **(created if isinstance(created, dict) else {})}
        self.name_index[key] = record.get("id")
        self.record_index[key] = record
        self.report.created.append({"op": "ensure_structure_block", "slug": slug})
        self._log("CREATE", "struct-block", slug)
        return record.get("id")

    def ensure_attachment(
        self,
        *,
        template: str,
        structure_slug: str,
        content_block_id: Any = None,
        dynamic_key: str | None = None,
        is_required: bool = False,
        order_index: int | None = None,
        **extras: Any,
    ) -> None:
        try:
            template_id = self._resolve("document_template", template)
        except LookupError as exc:
            self.report.failed.append(
                {
                    "op": {
                        "op": "ensure_attachment",
                        "structure_slug": structure_slug,
                    },
                    "error": str(exc),
                }
            )
            self._log("FAIL", "attachment", structure_slug, str(exc))
            return

        key = ("structure_block", f"{template_id}:{self._nk(structure_slug)}")
        struct = self.record_index.get(key)
        if struct is None:
            err = f"structure_slug {structure_slug!r} not known in template {template!r}"
            self.report.failed.append(
                {"op": {"op": "ensure_attachment", "structure_slug": structure_slug}, "error": err}
            )
            self._log("FAIL", "attachment", structure_slug, err)
            return

        payload: dict[str, Any] = {}
        if content_block_id is not None:
            payload["content_block_id"] = content_block_id
        if dynamic_key is not None:
            payload["dynamic_key"] = dynamic_key
        if is_required:
            payload["is_required"] = True
        if order_index is not None:
            payload["order_index"] = order_index

        entry = {"op": "ensure_attachment", "structure_slug": structure_slug}
        if self.dry_run:
            self.report.created.append(entry)
            self._log("CREATE", "attachment", structure_slug)
            return
        try:
            struct_id = struct.get("id")
            self.client.post(
                f"documents/templates/{template_id}/structure/blocks/{struct_id}/attachments",
                json=payload,
            )
            self.report.created.append(entry)
            self._log("CREATE", "attachment", structure_slug)
        except Exception as exc:  # pragma: no cover
            self.report.failed.append({"op": entry, "error": str(exc)})
            self._log("FAIL", "attachment", structure_slug, str(exc))
