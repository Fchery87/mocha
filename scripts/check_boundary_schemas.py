#!/usr/bin/env python3
"""Validate declared JSON schemas, local fixture shapes and CRC32C log bytes."""
import argparse
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1] / "docs"
CONTRACTS = ROOT / "contracts"


def crc32c(data):
    value = 0xffffffff
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0x82f63b78 if value & 1 else 0)
    return value ^ 0xffffffff


def check_log_line(line, validator):
    record = json.loads(line)
    validator.validate(record)
    prefix, marker, _ = line.rpartition(',"checksum":')
    if not marker or f"{crc32c(prefix.encode()):08x}" != record["checksum"]:
        raise ValueError("CRC32C mismatch or checksum not serialized last")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    schemas = {p.name: json.loads(p.read_text()) for p in CONTRACTS.glob("*.schema.json")}
    registry = Registry()
    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    validators = {name: Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
                  for name, schema in schemas.items()}
    files = {"protocol": "protocol", "session": "session", "tools": "tools",
             "user-config": "user-config", "project-config": "project-config",
             "mcp-config": "mcp-config", "mcp-auth": "mcp-auth", "mcp-auth.oauth": "mcp-auth"}
    count = 0
    for fixture, schema in files.items():
        value = json.loads((CONTRACTS / f"fixtures/{fixture}.valid.json").read_text())
        for item in value if isinstance(value, list) else [value]:
            validators[schema + ".schema.json"].validate(item)
            count += 1
    assert crc32c(b"123456789") == 0xe3069283
    line = (CONTRACTS / "fixtures/session.valid.jsonl").read_text().rstrip("\n")
    check_log_line(line, validators["session.schema.json"])
    metadata = json.loads((ROOT / "oauth-client.json").read_text())
    assert metadata["client_id"] == "https://fchery87.github.io/mocha/oauth-client.json"
    assert metadata["redirect_uris"] == ["http://127.0.0.1:8732/oauth/mcp/callback"]
    assert metadata["token_endpoint_auth_method"] == "none"
    assert metadata["token_endpoint_auth_methods_supported"] == ["none"]
    if args.self_test:
        bad_project = {"schemaVersion": 1, "default_mode": "unattended"}
        assert list(validators["project-config.schema.json"].iter_errors(bad_project))
        bad_protocol = copy.deepcopy(json.loads((CONTRACTS / "fixtures/protocol.valid.json").read_text())[0])
        bad_protocol["method"] = "execute_arbitrary_code"
        assert list(validators["protocol.schema.json"].iter_errors(bad_protocol))
        bad_auth = copy.deepcopy(json.loads((CONTRACTS / "fixtures/mcp-auth.valid.json").read_text()))
        bad_auth["token"] = "synthetic-forbidden-value"
        assert list(validators["mcp-auth.schema.json"].iter_errors(bad_auth))
        try:
            check_log_line(line.replace("session-fixture", "session-changed"), validators["session.schema.json"])
        except ValueError:
            pass
        else:
            raise AssertionError("Corrupted log checksum accepted")
        missing_acceptance_ids = {"protocol_version": 1, "type": "request_accepted", "request_id": "r1", "method": "submit_prompt", "payload": {}}
        assert list(validators["protocol.schema.json"].iter_errors(missing_acceptance_ids))
        missing_turn = {"schema_version": 1, "session_id": "s1", "sequence": 2,
                        "timestamp": "2026-11-14T12:00:00Z", "type": "turn_finished",
                        "payload": {"outcome": "Done", "summary": "finished", "unresolved_operations": []}, "checksum": "00000000"}
        assert list(validators["session.schema.json"].iter_errors(missing_turn))
        bad_taint = {"protocol_version": 1, "type": "taint_changed", "session_id": "s1",
                     "sequence": 1, "durable_sequence": 1,
                     "payload": {"tainted": False, "origin_kind": "file", "origin_ref": "f1"}}
        assert list(validators["protocol.schema.json"].iter_errors(bad_taint))
        print("Self-test passed: project escalation, unknown method, plaintext auth, corrupted log, missing correlation IDs and taint clearing rejected.")
    print(f"Boundary checks passed: {len(schemas)} schemas, {count} positive messages, CRC32C and OAuth metadata. Runtime pending.")


if __name__ == "__main__":
    main()
