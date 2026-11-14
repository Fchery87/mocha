#!/usr/bin/env python3
"""Check the written slice graph and coverage, without claiming runtime readiness."""
import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {f"SLICE-{n:03d}" for n in range(1, 20)}
REQUIREMENTS = {f"FR-{n:03d}" for n in range(1, 25)} | {f"NFR-{n:03d}" for n in range(1, 10)}


def validate(manifest, specs):
    errors = []
    rows = manifest.get("slices", [])
    ids = [r.get("id") for r in rows]
    if manifest.get("schema_version") != 1 or set(ids) != EXPECTED or len(ids) != 19:
        errors.append("Expected schema 1 and exactly SLICE-001 through SLICE-019")
    covered = set()
    visiting, visited = set(), set()
    graph = {r["id"]: r.get("blocked_by", []) for r in rows}

    def visit(identity):
        if identity in visiting:
            errors.append(f"Dependency cycle at {identity}")
            return
        if identity in visited:
            return
        visiting.add(identity)
        for dep in graph.get(identity, []):
            if dep not in graph:
                errors.append(f"Unknown dependency {dep} for {identity}")
            else:
                visit(dep)
        visiting.remove(identity)
        visited.add(identity)

    for row in rows:
        identity = row["id"]
        visit(identity)
        number = int(identity.rsplit("-", 1)[1])
        expected_milestone = "M0" if number == 1 else "M1" if number <= 8 else "M2"
        if row.get("milestone") != expected_milestone:
            errors.append(f"Wrong milestone for {identity}")
        requirements = set(row.get("requirements", []))
        if not requirements or not requirements <= REQUIREMENTS:
            errors.append(f"Missing/unknown requirement IDs for {identity}")
        covered |= requirements
        text = specs.get(identity)
        if text is None:
            errors.append(f"Missing specification for {identity}")
            continue
        if f"# {identity}:" not in text:
            errors.append(f"Mismatched spec title for {identity}")
        if "## User-visible result" not in text or "## Acceptance and failure cases" not in text:
            errors.append(f"Required spec sections missing for {identity}")
        cases = re.findall(r"^\| (\d{3}-A\d{2})", text, re.M)
        if len(cases) < 5 or len(cases) != len(set(cases)):
            errors.append(f"Missing/duplicate acceptance cases for {identity}")
        if f"cargo xtask verify slice-{number:03d}" not in text:
            errors.append(f"Missing planned verifier for {identity}")
        if any(req not in text for req in requirements):
            errors.append(f"Manifest/spec requirement mismatch for {identity}")
        if re.search(r"\bTODO\b|\bTBD\b|\bOPEN-\d+\b", text):
            errors.append(f"Unresolved placeholder in {identity}")
    if covered != REQUIREMENTS:
        errors.append("Missing PRD coverage: " + ", ".join(sorted(REQUIREMENTS - covered)))
    if "SLICE-016" in graph.get("SLICE-017", []):
        errors.append("Transcript UI must not wait on the external SIWC account gate")
    if not {"SLICE-012", "SLICE-014", "SLICE-016", "SLICE-018"} <= set(graph.get("SLICE-019", [])):
        errors.append("Release lacks required containment/MCP/SIWC/UI dependency gates")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "docs/slices/manifest.json").read_text())
    specs = {row["id"]: (ROOT / "docs/slices" / row["spec"]).read_text()
             for row in manifest["slices"] if (ROOT / "docs/slices" / row["spec"]).exists()}
    errors = validate(manifest, specs)
    if errors:
        raise SystemExit("\n".join(errors))
    if args.self_test:
        broken_specs = dict(specs)
        broken_specs.pop("SLICE-002")
        assert any("Missing specification" in e for e in validate(manifest, broken_specs))
        broken = copy.deepcopy(manifest)
        broken["slices"][0]["blocked_by"] = ["SLICE-002"]
        assert any("cycle" in e for e in validate(broken, specs))
        broken = copy.deepcopy(manifest)
        for row in broken["slices"]:
            row["requirements"] = [r for r in row["requirements"] if r != "FR-024"]
        assert any("Missing PRD coverage" in e for e in validate(broken, specs))
        print("Self-test passed: missing spec, dependency cycle and absent requirement coverage detected.")
    cases = sum(len(re.findall(r"^\| (\d{3}-A\d{2})", s, re.M)) for s in specs.values())
    print(f"Slice checks passed: 19 specs, acyclic dependencies, 33 requirements, {cases} acceptance cases. Runtime pending.")


if __name__ == "__main__":
    main()
