#!/usr/bin/env python3
"""Check published reconstruction evidence using only the Python standard library.

This checks archived identities and stored predicates. It does not decode pressure
captures, rebuild the producer, repeat the DSP experiment, or assess sound quality.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]
OLD = "/workspace/virtual-instrument-keyra/out/full-body-basis/v1"
NOTES = ["A0", "C1", "A1", "C2", "D#2", "A2", "C3", "D#3", "C4",
         "D#4", "A4", "C5", "D#5", "A5", "C6", "C7", "C8"]
CASE_IDS = {f"{note}v{layer}" for note in NOTES for layer in (4, 12)}
WITNESSES = {f"{note}v{layer}" for note in ("A0", "C3", "C6") for layer in (4, 12)}
FRAMES = 182400
CASE_BYTES = FRAMES * 14 * 8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_data(data):
    def invalid(value):
        raise ValueError(f"Non-finite JSON constant: {value}")
    return json.loads(data, parse_constant=invalid)


def finite_tree(value):
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_tree(v) for v in value.values())
    if isinstance(value, list):
        return all(finite_tree(v) for v in value)
    return True


class Archive:
    def __init__(self, index):
        self.index = index
        self.by_path = {}
        self.by_sha = {}
        self.external = {}
        self.checked = 0
        for row in index.get("artifacts", []) + index.get("reused_artifacts", []):
            relative = Path(row["package_path"])
            require(not relative.is_absolute() and ".." not in relative.parts,
                    f"Unsafe published path: {relative}")
            path = (ROOT / relative).resolve()
            require(path.is_relative_to(ROOT), f"Path escapes repository: {path}")
            require(path.is_file(), f"Missing published artifact: {relative}")
            stored = path.read_bytes()
            require(digest(stored) == row["stored_sha256"], f"Stored hash: {relative}")
            encoding = row["encoding"]
            require(encoding in ("identity", "gzip"), f"Unknown encoding: {encoding}")
            data = gzip.decompress(stored) if encoding == "gzip" else stored
            require(digest(data) == row["sha256"], f"Decoded hash: {relative}")
            require(len(data) == row["bytes"], f"Decoded length: {relative}")
            # Raw pressure outputs and executable binaries belong in external metadata.
            require(not str(relative).endswith("/basis.f64le"), "Raw basis shipped in package")
            item = (row, data)
            self.by_sha.setdefault(row["sha256"], []).append(item)
            for old_path in row.get("archived_paths", []) + [str(relative), str(path)]:
                self.by_path.setdefault(old_path, []).append(item)
            self.checked += 1
        for row in index.get("external_artifacts", []):
            old_path = row.get("oldpath", row.get("path", row.get("archived_path")))
            require(isinstance(old_path, str), "External artifact lacks old path")
            require(row["bytes"] >= 0 and len(row["sha256"]) == 64,
                    f"Malformed external identity: {old_path}")
            self.external.setdefault(old_path, []).append(row)

    def resolve(self, path, sha):
        for row, data in self.by_path.get(path, []):
            if row["sha256"] == sha:
                return data
        raise ValueError(f"Unresolved published identity: {path} ({sha})")

    def by_hash(self, sha):
        require(sha in self.by_sha, f"Unresolved published digest: {sha}")
        return self.by_sha[sha][0][1]

    def identity(self, path, sha, size=None):
        for row, _ in self.by_path.get(path, []):
            if row["sha256"] == sha and (size is None or row["bytes"] == size):
                return
        for row in self.external.get(path, []):
            if row["sha256"] == sha and (size is None or row["bytes"] == size):
                return
        raise ValueError(f"Unresolved archived identity: {path} ({sha})")

    def role(self, name):
        require(name in self.index["roles"], f"Missing role: {name}")
        row = self.index["roles"][name]
        return json_data(self.resolve(row["path"], row["sha256"]))


def check_gram(row, name):
    require(finite_tree(row), f"Non-finite Gram evidence: {name}")
    error = abs(row["direct_energy"] - row["gram_energy"])
    require(error == row["error"], f"Stored Gram error differs: {name}")
    passed = (error <= row["bound"] and row["min_eigenvalue"] >= -row["psd_bound"])
    require(passed and row["pass"] is True, f"Gram gate failed: {name}")


def check_stats(stats, record, name):
    require(finite_tree(stats), f"Non-finite stored stats: {name}")
    expected = {
        "frames": stats["frames"] == FRAMES,
        "direct_bitexact": stats["direct_max_error"] == 0 and stats["direct_nonidentical_samples"] == 0,
        "force_proof": stats["force_proof_mismatches"] == 0,
        "partition": stats["partition_error_over_bound"] <= 1,
        "weighted": stats["positive_weight_error_over_bound"] <= 1,
        "hp": stats["hp24_partition_max_error"] <= stats["hp24_partition_bound"],
        "basis": (stats["basis_min"] >= 0 and stats["basis_max"] <= 1
                  and stats["basis_partition_max_error"] == 0
                  and len(stats["basis_support_modes"]) == 6
                  and min(stats["basis_support_modes"]) > 0),
        "finite": stats["nonfinite"] == 0,
        "bytes": record["bytes"] == CASE_BYTES,
    }
    require(len(stats["final_qp"]) == 475 and all(len(row) == 2 for row in stats["final_qp"]),
            f"Board state dimensions: {name}")
    require(len(stats["final_hp_previous"]) == 7
            and all(len(row) == 4 for row in stats["final_hp_previous"]),
            f"HP state dimensions: {name}")
    for gate, passed in expected.items():
        require(passed and record["gates"][gate] is True, f"Stored gate {gate}: {name}")
    require(record["gates"]["input_after"] is True, f"Input identity gate: {name}")
    require(record["gates"]["source_after"] is True, f"Source identity gate: {name}")
    require(all(v is True for v in record["gates"].values()) and record["pass"] is True,
            f"Case gate summary: {name}")


def verify(index):
    archive = Archive(index)
    protocol = archive.role("protocol")
    freeze = archive.role("freeze")
    result = archive.role("result")
    manifest = archive.role("manifest")
    bindings = archive.role("input_bindings")
    post = archive.role("post_review")
    source_audit = archive.role("source_audit")
    summary = archive.role("summary_validation")
    roles = index["roles"]
    protocol_sha = roles["protocol"]["sha256"]
    require(freeze["protocol_sha256"] == protocol_sha == result["frozen_protocol_sha256"],
            "Protocol/freeze/result binding")
    require(protocol["rate"] == 48000 and protocol["frames_per_case"] == FRAMES
            and protocol["modes"] == 475, "Frozen model dimensions")
    require(protocol["basis"]["centers_hz"] == [55, 140, 350, 900, 2400, 6500],
            "Frozen basis centers")
    require(protocol["basis"]["test_alpha"] == [.5, .75, 1, 1.25, 1.5, 2],
            "Frozen diagnostic weights")
    require(protocol["output"]["raw_only"] is True, "Raw-only representation")
    require(protocol["output"]["total_bytes_34"] == 34 * CASE_BYTES, "Frozen byte budget")
    require(protocol["pressure_or_trace_access_before_freeze"] is False, "Pre-access declaration")
    require(protocol["input_bindings_sha256"] == roles["input_bindings"]["sha256"],
            "Input bindings digest")
    require(protocol["sources"] == freeze["sources"], "Frozen source identities")
    for path, sha in protocol["sources"].items():
        archive.resolve(path, sha)
    require(result["producer_source_sha256"] == protocol["sources"][OLD + "/replay.cpp"],
            "Producer source binding")
    coefficients = protocol["coefficients"]
    require(coefficients == freeze["coefficients"], "Coefficient freeze binding")
    archive.identity(coefficients["path"], coefficients["sha256"], 475 * 11 * 8)
    require(bindings["cases"] == protocol["cases"], "Frozen case inventory")
    require({c["id"] for c in protocol["cases"]} == CASE_IDS and len(protocol["cases"]) == 34,
            "Expected 34 TRAIN cases")
    require(set(protocol["stages"]["witnesses"]) == WITNESSES, "Six witness inventory")
    for path, sha in bindings["historical_binding_sources"].items():
        archive.identity(path, sha)
    case_inputs = {c["id"]: c for c in protocol["cases"]}
    fresh = {c["id"] for c in protocol["cases"] if c["trace_binding"].startswith("fresh")}
    require(fresh == {"C3v4", "C3v12", "C4v4", "C4v12"}, "Fresh/historical trace provenance")
    require(result["pass"] is True and result["failed_case"] is None and result["count"] == 34,
            "Result is a complete reconstruction pass")
    require({c["id"] for c in result["cases"]} == CASE_IDS and len(result["cases"]) == 34,
            "Result case inventory")
    total = 0
    grams = 0
    for record in result["cases"]:
        ident = record["id"]
        case = case_inputs[ident]
        stem = OLD + "/renders/" + ident
        stats = json_data(archive.resolve(stem + "/stats.json", record["stats_sha256"]))
        require(json_data(archive.resolve(stem + "/receipt.json",
                    manifest["renders/" + ident + "/receipt.json"]["sha256"])) == record,
                f"Receipt/result equality: {ident}")
        check_stats(stats, record, ident)
        require(record["trace_sha256"] == case["expected_trace_sha256"], f"Trace digest: {ident}")
        archive.identity(case["trace"], case["expected_trace_sha256"], FRAMES * 15 * 8)
        archive.identity(case["force_proof"], case["expected_proof_sha256"], FRAMES * 3 * 8)
        archive.identity(stem + "/basis.f64le", record["output_sha256"], CASE_BYTES)
        total += record["bytes"]
        if ident in WITNESSES:
            require(record["stage"] == "witnesses", f"Witness stage: {ident}")
            require(record["gates"]["chunks"] is True and record["gates"]["gram"] is True,
                    f"Witness chunk/Gram gates: {ident}")
            require(record["alternate_output_sha256"] == record["output_sha256"],
                    f"Chunk raw output identity: {ident}")
            alternate = json_data(archive.resolve(stem + "/alternate-stats.json",
                                                  record["alternate_stats_sha256"]))
            require(alternate == stats, f"Chunk final state identity: {ident}")
            require(len(record["coherent_gram"]) == 2, f"Stereo Gram count: {ident}")
            for channel, gram in enumerate(record["coherent_gram"]):
                check_gram(gram, f"{ident}/{channel}")
                grams += 1
        else:
            require(record["stage"] == "remaining", f"Remaining stage: {ident}")
    require(total == result["total_output_bytes"] == 694579200 and total < 2**30,
            "Retained representation budget")
    require(grams == 12, "Twelve actual coherent Gram checks")
    check_gram(json_data(archive.by_hash(result["synthetic_gram_sha256"])), "synthetic")
    # Verify every archived manifest identity without opening external captures.
    for path, row in manifest.items():
        archive.identity(OLD + "/" + path, row["sha256"], row["bytes"])
    archive.identity(OLD + "/replay", result["producer_binary_sha256"])
    require(post["case_count"] == 34 and post["direct_pressure_samples_bitidentical"] == 34 * FRAMES * 2,
            "Independent pressure sample count")
    require(post["force_frames_authenticated_against_historical_before_after_proofs"] == 34 * FRAMES,
            "Independent force frame count")
    require(post["coherent_actual_gram_checks"] == 12 and set(post["chunk_witnesses"]) == WITNESSES,
            "Independent witness counts")
    for key in ("zero_direct_pressure_errors", "zero_direct_bitmismatches",
                "zero_forceproof_mismatches", "zero_nonfinite", "synthetic_gram"):
        require(post[key] is True, f"Independent review predicate: {key}")
    require(post["raw_binary_output_bytes"] == total, "Independent output byte count")
    for path, sha in post["reviewed_sha256"].items():
        archive.identity(OLD + "/" + path, sha)
    require(source_audit["source_proof"]["475_modes"] is True, "Source audit mode count")
    for path, sha in source_audit["inputs"].items():
        archive.identity("/workspace/virtual-instrument-keyra/" + path, sha)
    for version in ("pre-access-v1", "pre-access-v2"):
        directory = OLD + "/" + version + "/"
        rejection_sha = manifest[version + "/rejection.json"]["sha256"]
        rejection = json_data(archive.resolve(directory + "rejection.json", rejection_sha))
        require(rejection["traces_opened"] is False, f"Archived failure trace access: {version}")
        output_flag = "numerical_outputs_created" if version.endswith("v1") else "case_outputs_created"
        require(rejection[output_flag] is False, f"Archived failure output scope: {version}")
        old_freeze = json_data(archive.resolve(directory + "freeze.json",
                                  manifest[version + "/freeze.json"]["sha256"]))
        archive.resolve(directory + "protocol.json", old_freeze["protocol_sha256"])
        for path, sha in old_freeze["sources"].items():
            # Source freeze paths predate archival relocation; match the versioned content.
            archive.resolve(directory + Path(path).name, sha)
    require(summary["study"] == "body_radiation_basis"
            and summary["passed_cases"] == 34 and summary["total_cases"] == 34,
            "Published summary scope")
    for key in ("default_changed", "fit_performed", "reference_pcm_accessed", "production_ready_claim"):
        require(summary[key] is False, f"No-adoption/no-fit summary: {key}")
    return {"pass": True, "published_artifacts_checked": archive.checked,
            "stored_cases_checked": 34, "chunk_witnesses": 6, "coherent_gram_checks": 12,
            "retained_external_basis_bytes": total,
            "scope": "Hashes and stored evidence only; no PCM decode, producer build, fit or sonic approval."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=PACKAGE / "index.json",
                        help="Published package index (default: this directory's index.json)")
    args = parser.parse_args()
    try:
        report = verify(json_data(args.index.read_bytes()))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
