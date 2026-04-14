"""Tests for rattle_api.builder — ConfigBuilder idempotent apply."""

from rattle_api.builder import BuildReport, ConfigBuilder

# ---------------------------------------------------------------------------
# FakeRattleClient — records every HTTP call for assertion.
# ---------------------------------------------------------------------------


class FakeRattleClient:
    """In-memory stand-in for RattleClient.

    Records every call to ``list_all``, ``get``, ``post``, ``patch``, ``put``,
    and ``delete`` in ``self.calls`` and returns canned responses from
    ``self.store`` so tests can simulate the live Rattle catalogue.
    """

    def __init__(self, *, initial_state=None):
        self.calls: list[tuple[str, str, dict | None]] = []
        self.store: dict[str, list[dict]] = initial_state or {}
        self._next_id = 1000

    # ---- helpers used by tests --------------------------------------------

    def set_list(self, path: str, items: list[dict]) -> None:
        self.store[path] = items

    def get_writes(self, method: str | None = None) -> list[tuple[str, str, dict | None]]:
        if method is None:
            return [c for c in self.calls if c[0] in ("POST", "PATCH", "PUT", "DELETE")]
        return [c for c in self.calls if c[0] == method]

    # ---- RattleClient surface ---------------------------------------------

    def list_all(self, path, **params):
        self.calls.append(("LIST", path, params))
        return list(self.store.get(path, []))

    def get(self, path, **params):
        self.calls.append(("GET", path, params))
        return self.store.get(path, None)

    def post(self, path, json=None):
        self.calls.append(("POST", path, json))
        new_id = self._next_id
        self._next_id += 1
        record = {"id": new_id, **(json or {})}
        # Accumulate created records by collection name.
        collection = path.split("/")[0]
        self.store.setdefault(collection, []).append(record)
        return record

    def patch(self, path, json=None):
        self.calls.append(("PATCH", path, json))
        return {"ok": True, **(json or {})}

    def put(self, path, json=None):
        self.calls.append(("PUT", path, json))
        return {"ok": True, **(json or {})}

    def delete(self, path):
        self.calls.append(("DELETE", path, None))
        return None


# ---------------------------------------------------------------------------
# BuildReport
# ---------------------------------------------------------------------------


class TestBuildReport:
    def test_empty_counts(self):
        r = BuildReport()
        assert r.counts() == {"created": 0, "updated": 0, "unchanged": 0, "failed": 0}

    def test_to_dict_shape(self):
        r = BuildReport()
        r.created.append({"op": "ensure_product", "name": "p"})
        data = r.to_dict()
        assert "counts" in data
        assert "created" in data
        assert data["counts"]["created"] == 1

    def test_merge(self):
        a = BuildReport()
        a.created.append({"op": "ensure_product", "name": "p1"})
        b = BuildReport()
        b.updated.append({"op": "ensure_product", "name": "p2"})
        a.merge(b)
        assert len(a.created) == 1
        assert len(a.updated) == 1


# ---------------------------------------------------------------------------
# fetch_live_state
# ---------------------------------------------------------------------------


class TestFetchLiveState:
    def test_primes_name_index_from_api(self):
        client = FakeRattleClient()
        client.set_list("products", [{"id": 1, "name": "ProductA"}])
        client.set_list(
            "groups",
            [
                {
                    "id": 10,
                    "name": "Wheels",
                    "is_multi": False,
                    "options": [{"id": 100, "name": "17 inch"}],
                }
            ],
        )
        builder = ConfigBuilder(client, verbose=False)
        state = builder.fetch_live_state()

        assert builder.name_index[("product", "producta")] == 1
        assert builder.name_index[("group", "wheels")] == 10
        assert builder.name_index[("option", "17 inch")] == 100
        assert state["products"] == [{"id": 1, "name": "ProductA"}]


# ---------------------------------------------------------------------------
# ensure_product
# ---------------------------------------------------------------------------


class TestEnsureProduct:
    def test_creates_when_missing(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        report = builder.apply([{"op": "ensure_product", "name": "Drill X100", "base_price": 500}])
        assert len(report.created) == 1
        assert client.get_writes("POST")[0][1] == "products"
        assert builder.name_index[("product", "drill x100")] is not None

    def test_idempotent_second_apply_is_unchanged(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [{"op": "ensure_product", "name": "Drill X100", "base_price": 500}]
        builder.apply(ops)
        client.calls.clear()

        builder2 = ConfigBuilder(client, verbose=False)
        builder2.fetch_live_state()
        client.calls.clear()
        report = builder2.apply(ops)
        assert len(report.unchanged) == 1
        assert client.get_writes("POST") == []

    def test_patches_on_drift(self):
        client = FakeRattleClient(
            initial_state={"products": [{"id": 1, "name": "Drill X100", "base_price": 500}]}
        )
        builder = ConfigBuilder(client, verbose=False)
        builder.fetch_live_state()
        client.calls.clear()

        report = builder.apply([{"op": "ensure_product", "name": "Drill X100", "base_price": 550}])
        assert len(report.updated) == 1
        assert client.get_writes("PATCH")[0][1] == "products/1"


# ---------------------------------------------------------------------------
# Name resolution across ops in a single batch
# ---------------------------------------------------------------------------


class TestNameResolution:
    def test_option_resolves_group_created_in_same_batch(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [
            {"op": "ensure_group", "name": "Wheels", "is_multi": False},
            {
                "op": "ensure_option",
                "name": "17 inch",
                "group": "Wheels",
                "price": 0,
                "recommended": True,
            },
            {
                "op": "ensure_option",
                "name": "19 inch",
                "group": "Wheels",
                "price": 500,
            },
        ]
        report = builder.apply(ops)
        assert len(report.created) == 3
        assert not report.failed

        post_payloads = [c[2] for c in client.get_writes("POST") if c[1] == "options"]
        # Both options should have been posted with the group id that was
        # assigned when `ensure_group` ran.
        group_id = builder.name_index[("group", "wheels")]
        for payload in post_payloads:
            assert payload["group_id"] == group_id

    def test_missing_group_reference_fails_gracefully(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [
            {
                "op": "ensure_option",
                "name": "Orphan",
                "group": "NonExistentGroup",
                "price": 10,
            }
        ]
        report = builder.apply(ops)
        assert len(report.failed) == 1
        assert "NonExistentGroup" in report.failed[0]["error"]

    def test_bom_resolves_option_by_name(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [
            {"op": "ensure_group", "name": "Wheels", "is_multi": False},
            {
                "op": "ensure_option",
                "name": "17 inch",
                "group": "Wheels",
                "recommended": True,
            },
            {"op": "ensure_part", "part_number": "P-000", "part_name": "Chassis"},
            {
                "op": "ensure_part",
                "part_number": "P-017",
                "part_name": "17-inch wheel",
            },
            {
                "op": "ensure_bom_item",
                "parent_part": "P-000",
                "child_part": "P-017",
                "quantity": 4,
                "usage_subclauses": [{"option": "17 inch", "factor": 1.0}],
            },
        ]
        report = builder.apply(ops)
        assert not report.failed
        bom_calls = [c for c in client.calls if c[0] == "POST" and "bom" in c[1]]
        assert len(bom_calls) == 1
        payload = bom_calls[0][2]
        # usage_subclauses must have the option resolved to an id.
        assert (
            payload["usage_subclauses"][0]["option_id"] == builder.name_index[("option", "17 inch")]
        )


# ---------------------------------------------------------------------------
# link_group_to_area
# ---------------------------------------------------------------------------


class TestLinkGroupToArea:
    def test_links_group_to_area(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [
            {"op": "ensure_product", "name": "ProdA", "base_price": 1},
            {"op": "ensure_area", "name": "Mechanics", "parent_product": "ProdA"},
            {"op": "ensure_group", "name": "Wheels", "is_multi": False},
            {"op": "link_group_to_area", "group": "Wheels", "area": "Mechanics"},
        ]
        builder.apply(ops)
        link_calls = [c for c in client.calls if c[0] == "POST" and c[1].endswith("/areas")]
        # area attachment to product + group-to-area link = 2
        assert len(link_calls) >= 1


# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------


class TestConstraints:
    def test_constraint_pair(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [
            {"op": "ensure_group", "name": "G1", "is_multi": False},
            {"op": "ensure_option", "name": "A", "group": "G1"},
            {"op": "ensure_option", "name": "B", "group": "G1"},
            {
                "op": "ensure_constraint_pair",
                "option_1": "A",
                "option_2": "B",
                "description": "incompatible",
            },
        ]
        report = builder.apply(ops)
        assert not report.failed
        constraint_calls = [c for c in client.calls if c[0] == "POST" and c[1] == "constraints"]
        assert len(constraint_calls) == 1
        payload = constraint_calls[0][2]
        assert "option_id1" in payload
        assert "option_id2" in payload

    def test_constraint_rule(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [
            {
                "op": "ensure_constraint_rule",
                "description": "If A is selected, forbid B",
                "rule_json": [{"if": {"option_selected": "A"}, "then": {"forbid_options": ["B"]}}],
            }
        ]
        report = builder.apply(ops)
        assert not report.failed
        assert any(c[1] == "constraints/rules" for c in client.calls)


# ---------------------------------------------------------------------------
# dry_run
# ---------------------------------------------------------------------------


class TestDryRun:
    def test_dry_run_makes_no_http_writes(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, dry_run=True, verbose=False)
        ops = [
            {"op": "ensure_product", "name": "ProdA"},
            {"op": "ensure_group", "name": "G", "is_multi": False},
            {"op": "ensure_option", "name": "A", "group": "G"},
        ]
        builder.apply(ops)
        assert client.get_writes("POST") == []
        assert client.get_writes("PATCH") == []
        assert client.get_writes("PUT") == []
        assert len(builder.report.created) == 3

    def test_dry_run_apply_convenience(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [{"op": "ensure_product", "name": "ProdA"}]
        builder.dry_run_apply(ops)
        assert client.get_writes("POST") == []
        assert builder.dry_run is False  # restored


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_unknown_op_type_is_recorded_as_failed(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        report = builder.apply([{"op": "do_the_impossible", "name": "x"}])
        assert len(report.failed) == 1
        assert "unknown op type" in report.failed[0]["error"]

    def test_non_dict_op_is_recorded_as_failed(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        report = builder.apply(["not a dict"])  # type: ignore[list-item]
        assert len(report.failed) == 1

    def test_failed_op_does_not_abort_batch(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [
            {"op": "do_the_impossible"},
            {"op": "ensure_product", "name": "StillHere"},
        ]
        report = builder.apply(ops)
        assert len(report.failed) == 1
        assert len(report.created) == 1


# ---------------------------------------------------------------------------
# Full scenario — realistic wheels example
# ---------------------------------------------------------------------------


class TestRealisticWheelScenario:
    """The #1 rule example — 17/19 inch wheels as explicit options with BOM."""

    def test_end_to_end_wheels_scenario(self):
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [
            {"op": "ensure_product", "name": "Drill X100", "base_price": 10000},
            {
                "op": "ensure_area",
                "name": "Mechanics",
                "parent_product": "Drill X100",
            },
            {"op": "ensure_group", "name": "Wheels", "is_multi": False},
            {"op": "link_group_to_area", "group": "Wheels", "area": "Mechanics"},
            {
                "op": "ensure_option",
                "name": "17 inch",
                "group": "Wheels",
                "price": 0,
                "recommended": True,
            },
            {
                "op": "ensure_option",
                "name": "19 inch",
                "group": "Wheels",
                "price": 500,
            },
            {"op": "ensure_part", "part_number": "P-000", "part_name": "Chassis"},
            {
                "op": "ensure_part",
                "part_number": "P-017",
                "part_name": "17-inch wheel assy",
            },
            {
                "op": "ensure_part",
                "part_number": "P-019",
                "part_name": "19-inch wheel assy",
            },
            {
                "op": "ensure_bom_item",
                "parent_part": "P-000",
                "child_part": "P-017",
                "quantity": 4,
                "usage_subclauses": [{"option": "17 inch", "factor": 1.0}],
            },
            {
                "op": "ensure_bom_item",
                "parent_part": "P-000",
                "child_part": "P-019",
                "quantity": 4,
                "usage_subclauses": [{"option": "19 inch", "factor": 1.0}],
            },
        ]
        report = builder.apply(ops)
        # Everything should apply without errors.
        assert not report.failed, report.failed
        # Product, area, group, 2 options, 3 parts, 2 BOM lines = 9 creates
        # plus links and area attachment.
        assert len(report.created) >= 9

    def test_rerun_after_fetch_is_idempotent(self):
        """Second run against the same 'catalogue' should be a no-op."""
        client = FakeRattleClient()
        builder = ConfigBuilder(client, verbose=False)
        ops = [
            {"op": "ensure_product", "name": "Drill X100", "base_price": 10000},
            {"op": "ensure_group", "name": "Wheels", "is_multi": False},
            {
                "op": "ensure_option",
                "name": "17 inch",
                "group": "Wheels",
                "price": 0,
                "recommended": True,
            },
        ]
        builder.apply(ops)

        # Simulate a re-run by priming a fresh builder from the accumulated
        # FakeRattleClient state.
        # For groups, the FakeRattleClient does not synthesize an options
        # array, so prepare a pre-populated store.
        group_id = builder.name_index[("group", "wheels")]
        client.store["groups"] = [
            {
                "id": group_id,
                "name": "Wheels",
                "is_multi": False,
                "options": [{"id": 9001, "name": "17 inch", "price": 0, "recommended": True}],
            }
        ]
        client.calls.clear()

        builder2 = ConfigBuilder(client, verbose=False)
        builder2.fetch_live_state()
        client.calls.clear()
        report = builder2.apply(ops)
        assert not report.failed
        assert len(report.unchanged) == 3
        assert len(report.created) == 0
        assert client.get_writes("POST") == []
