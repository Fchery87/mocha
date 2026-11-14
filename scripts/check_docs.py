#!/usr/bin/env python3
"""Check local Markdown references and requirement coverage without changing files."""
import argparse
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {f"FR-{n:03d}" for n in range(1, 25)} | {
    f"NFR-{n:03d}" for n in range(1, 10)
}
CONTRACTS = ("runtime", "tools-and-policy", "providers-and-mcp", "storage-and-context")


def anchors(text):
    found = set()
    counts = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        found.add(f"{slug}-{count}" if count else slug)
    found.update(re.findall(r'<a\s+(?:name|id)=["\']([^"\']+)', text))
    return found


def check(root):
    errors = []
    files = [p for p in root.rglob("*.md") if ".git" not in p.parts
             and "research" not in p.parts]
    for path in sorted(files):
        text = path.read_text()
        # Strip fenced examples so example links do not become repository contracts.
        prose = re.sub(r"^```.*?^```[^\n]*$", "", text, flags=re.M | re.S)
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", prose):
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            dest = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not dest.exists():
                errors.append(f"{path.relative_to(root)}: missing link {target}")
            elif parsed.fragment and dest.suffix == ".md":
                if unquote(parsed.fragment) not in anchors(dest.read_text()):
                    errors.append(f"{path.relative_to(root)}: missing anchor {target}")
    prd = root / "docs/02-prd.md"
    coverage = root / "docs/verification.md"
    if not prd.exists() or not coverage.exists():
        errors.append("PRD or verification plan missing")
    else:
        headings = re.findall(r"^### ((?:FR|NFR)-\d{3}):", prd.read_text(), re.M)
        rows = re.findall(r"^\| ((?:FR|NFR)-\d{3}) \|", coverage.read_text(), re.M)
        for kind, items in (("PRD headings", headings), ("verification rows", rows)):
            if set(items) != REQUIRED or len(items) != len(REQUIRED):
                errors.append(f"{kind}: expected each of 33 requirements once; "
                              f"missing={sorted(REQUIRED-set(items))}, count={len(items)}")
    current = [prd, root / "docs/04-architecture.md"]
    current += [root / f"docs/contracts/{name}.md" for name in CONTRACTS]
    for path in current:
        if not path.exists():
            errors.append(f"required specification missing: {path.relative_to(root)}")
        elif re.search(r"\bOPEN-\d+\b|\bStatus\s*\|\s*ACCEPTED\b|\|\s*ACTIVE\b", path.read_text()):
            errors.append(f"stale decision/activation marker: {path.relative_to(root)}")
    return errors, len(files)


def self_test():
    # Reproduce two actual risks in this docs refresh: broken asset references and
    # requirements without a verifier. Never mutate the real working tree.
    with tempfile.TemporaryDirectory(prefix="mocha-doc-check-") as folder:
        root = Path(folder)
        (root / "docs/contracts").mkdir(parents=True)
        (root / "README.md").write_text("[logo](assets/mocha-logo-dark.svg)\n")
        (root / "docs/02-prd.md").write_text("\n".join(f"### {r}: example" for r in sorted(REQUIRED)))
        (root / "docs/verification.md").write_text("\n".join(
            f"| {r} | 001 | proof |" for r in sorted(REQUIRED) if r != "FR-004"))
        (root / "docs/04-architecture.md").write_text("# Architecture\n")
        for name in CONTRACTS:
            (root / f"docs/contracts/{name}.md").write_text(f"# {name}\n")
        errors, _ = check(root)
        assert any("missing link" in e for e in errors), errors
        assert any("verification rows" in e for e in errors), errors
        (root / "README.md").write_text("[PRD](docs/02-prd.md#fr-001-example)\n")
        (root / "docs/verification.md").write_text("\n".join(
            f"| {r} | 001 | proof |" for r in sorted(REQUIRED)))
        errors, _ = check(root)
        assert not errors, errors
        (root / "README.md").write_text("[PRD](docs/02-prd.md#absent)\n")
        errors, _ = check(root)
        assert any("missing anchor" in e for e in errors), errors
    print("Self-test passed: broken local link, absent anchor, and missing requirement coverage detected.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    errors, count = check(ROOT)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Documentation checks passed: {count} current Markdown files, 33 requirement mappings, four contracts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
