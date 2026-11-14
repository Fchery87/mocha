#!/usr/bin/env python3
"""Prove fixed task graders fail broken/stub inputs and pass references. No model calls."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
corpus = json.loads((ROOT / "docs/fixtures/coding-acceptance.json").read_text())
with tempfile.TemporaryDirectory(prefix="mocha-corpus-") as folder:
    root = Path(folder)
    for task in corpus["tasks"]:
        assert hashlib.sha256(task["initial_source"].encode()).hexdigest() == task["initial_sha256"]
        assert hashlib.sha256(task["grader_source"].encode()).hexdigest() == task["grader_sha256"]
        for field, expected in (("initial_source", False), ("reference_source", True)):
            source = root / "candidate.rs"
            binary = root / "grader"
            source.write_text(task[field] + task["grader_source"])
            compiled = subprocess.run(["rustc", "--edition", task["edition"], "--test", str(source), "-o", str(binary)], capture_output=True, text=True, timeout=30)
            if compiled.returncode:
                raise SystemExit(compiled.stderr)
            ran = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
            assert (ran.returncode == 0) == expected, (task["id"], field, ran.stdout, ran.stderr)
        print(task["id"] + ": initial fails and reference passes the independent grader")
print("Corpus fixtures verified. No Mocha implementation or real-model coding outcome tested.")
