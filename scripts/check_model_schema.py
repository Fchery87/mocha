#!/usr/bin/env python3
"""Validate the model schema and compatibility fixture. Requires jsonschema."""
import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1] / "docs/contracts"
schema = json.loads((ROOT / "models.schema.json").read_text())
fixture = json.loads((ROOT / "fixtures/models.legacy.sanitized.json").read_text())
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)
validator.validate(fixture)
providers = fixture["providers"]
assert len(providers) == 4
assert sum(len(p["models"]) for p in providers.values()) == 61
assert any("api" in m and m["api"] != p["api"]
           for p in providers.values() for m in p["models"])
assert any("contextWindow" not in m or "maxTokens" not in m
           for p in providers.values() for m in p["models"])


def rejects(change):
    candidate = copy.deepcopy(fixture)
    change(candidate["providers"][next(iter(providers))])
    assert list(validator.iter_errors(candidate)), "Invalid configuration was accepted"


rejects(lambda p: p.update(api="unsupported-api"))
rejects(lambda p: p.update(apiKey="synthetic-forbidden-value"))
rejects(lambda p: p.update(baseUrl="https://user:synthetic@example.invalid/v1"))
rejects(lambda p: p["models"][0].update(contextWindow=-1))
rejects(lambda p: p["models"][0].update(compat={"supportsStore": "false"}))
print("Schema passed: Draft 2020-12, four providers/61 entries, API overrides, "
      "loadable missing limits, and five invalid-configuration cases rejected.")
