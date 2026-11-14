#!/usr/bin/env python3
"""Check consistency of mode documentation and acceptance examples, not runtime policy."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES = ["auto", "approve", "plan", "unattended"]
DECISIONS = {"allow", "ask", "reflect", "block", "stop_approval_required"}


def validate(data, contract):
    errors = []
    if data.get("schema_version") != 1 or data.get("modes") != MODES:
        errors.append("Expected schema 1 and canonical auto/approve/plan/unattended modes")
    if "| Action | auto | approve | plan | unattended |" not in contract:
        errors.append("Mode matrix columns differ from the acceptance fixture")
    ids = set()
    coverage = set()
    for case in data.get("cases", []):
        identity = case.get("id")
        if not identity or identity in ids:
            errors.append(f"Missing/duplicate case ID: {identity}")
        ids.add(identity)
        mode = case.get("mode")
        expected = case.get("expected")
        facts = case.get("facts", {})
        if mode not in MODES or expected not in DECISIONS:
            errors.append(f"Unknown mode/decision in {identity}")
        coverage.add((case.get("category"), mode))
        if mode == "unattended" and expected in {"ask", "reflect"}:
            errors.append(f"Unattended must not wait for approval/reflection: {identity}")
        if facts.get("absolute_deny") and expected != "block":
            errors.append(f"Hard deny must block in every mode: {identity}")
        if mode == "plan" and (facts.get("mutating") or facts.get("unknown_mcp_effects")) and expected != "block":
            errors.append(f"Plan must block mutations/unknown effects: {identity}")
        if facts.get("scope_granted") is False and expected in {"allow", "reflect"}:
            errors.append(f"Reflection cannot supply missing scope: {identity}")
        if facts.get("required_containment_available") is False and expected != "block":
            errors.append(f"Missing containment must fail closed: {identity}")
        if facts.get("checkpoint_required") and not facts.get("checkpoint_ready") and expected != "block":
            errors.append(f"A required missing checkpoint must block: {identity}")
    for category in ("authorized-read", "absolute-deny", "containment-unavailable", "covered-edit",
                     "local-mutating-command", "destructive-uncertainty-within-scope",
                     "missing-execution-scope", "unknown-mcp-effects",
                     "tainted-outbound-without-exact-grant", "missing-required-checkpoint"):
        for mode in MODES:
            if (category, mode) not in coverage:
                errors.append(f"Missing acceptance case: {category}/{mode}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    data = json.loads((ROOT / "docs/contracts/fixtures/permission-decisions.json").read_text())
    contract = (ROOT / "docs/contracts/tools-and-policy.md").read_text()
    errors = validate(data, contract)
    if errors:
        raise SystemExit("\n".join(errors))
    if args.self_test:
        for identity, invalid in (("covered-edit-plan", "allow"),
                                  ("unknown-mcp-effects-unattended", "ask"),
                                  ("missing-execution-scope-auto", "allow")):
            broken = copy.deepcopy(data)
            next(c for c in broken["cases"] if c["id"] == identity)["expected"] = invalid
            assert validate(broken, contract), identity
        print("Self-test passed: Plan mutation, unattended approval wait, and missing-scope permission errors detected.")
    print(f"Permission contract checks passed: four modes, {len(data['cases'])} acceptance examples. Runtime execution pending.")


if __name__ == "__main__":
    main()
