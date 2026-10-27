#!/usr/bin/env python3
"""Check generated full-core build commands without compiling or running piano DSP."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import tempfile

PROJECT = Path(__file__).resolve().parents[1]


def definition(tokens, name):
    value = None
    for token in tokens:
        if token in ("-U" + name, "/U" + name):
            value = None
        elif token.startswith(("-D" + name + "=", "/D" + name + "=")):
            value = token.split("=", 1)[1]
    return value


def validate(instrument, compiler, workspace):
    cases = [
        ("native", "OriginalControl", "0", [], None, None),
        ("free-opt-out", "OriginalControl", "1", ["-DKEYRA_RACK_FULL_FREE_UNISON_SIMD=OFF"], "0", None),
        ("pressure-opt-out", "OriginalControl", "1", ["-DKEYRA_RACK_FULL_PRESSURE_SIMD=OFF"], None, "0"),
        ("unsupported-flag", "OriginalControl", "1", ["-DKEYRA_RACK_HAS_OPENMP_SIMD=FALSE"], "0", "0"),
        ("confidence", "FrozenConfidenceGrand", "1", [], "0", "0"),
        ("confidence-pressure-opt-in", "FrozenConfidenceGrand", "0", ["-DKEYRA_RACK_FULL_PRESSURE_SIMD=ON"], "0", None),
    ]
    results = []
    for name, profile, inherited, extra, expected, pressure_expected in cases:
        build = workspace / name
        command = ["cmake", "-S", str(PROJECT), "-B", str(build),
                   "-DCMAKE_CXX_COMPILER=" + compiler,
                   "-DKEYRA_INSTRUMENT_DIR=" + str(instrument),
                   "-DKEYRA_BUILD_EXPERIMENTAL_FULL_MODEL=ON", "-DBUILD_TESTING=ON",
                   "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
                   "-DKEYRA_RACK_FULL_MODEL_PROFILE=" + profile,
                   "-DCMAKE_CXX_FLAGS=-DKEYRA_FULL_FREE_UNISON_SIMD=" + inherited +
                   " -DKEYRA_FULL_PRESSURE_SIMD=" + inherited,
                   *extra]
        call = subprocess.run(command, capture_output=True, text=True)
        if call.returncode:
            raise ValueError(name + " configure failed: " + call.stdout + call.stderr)
        # Reconfigure without the explicit OFF argument: the cache must retain it.
        if name == "pressure-opt-out":
            repeated = subprocess.run([item for item in command if item != "-DKEYRA_RACK_FULL_PRESSURE_SIMD=OFF"],
                                      capture_output=True, text=True)
            if repeated.returncode:
                raise ValueError(name + " cached reconfigure failed: " + repeated.stdout + repeated.stderr)
        cache = (build / "CMakeCache.txt").read_text()
        supported = "1" if "KEYRA_RACK_HAS_OPENMP_SIMD:INTERNAL=1" in cache else "0"
        if expected is None:
            expected = supported
        if pressure_expected is None:
            pressure_expected = supported
        commands = json.loads((build / "compile_commands.json").read_text())
        cores = {}
        for row in commands:
            if Path(row["file"]).name != "FullInstrument.cpp":
                continue
            tokens = row.get("arguments") or shlex.split(row["command"])
            rendered = row.get("command") or " ".join(tokens)
            target = "scalar" if "keyra_rack_full_scalar_core.dir" in rendered else "native"
            selected = definition(tokens, "KEYRA_FULL_FREE_UNISON_SIMD")
            if selected != ("0" if target == "scalar" else expected):
                raise ValueError(name + ": incorrect " + target + " free/unison selection")
            pressure = definition(tokens, "KEYRA_FULL_PRESSURE_SIMD")
            if pressure != ("0" if target == "scalar" else pressure_expected):
                raise ValueError(name + ": incorrect " + target + " pressure selection")
            if ("-fopenmp-simd" in tokens) != (target == "native" and "1" in (expected, pressure_expected)):
                raise ValueError(name + ": missing or unexpected OpenMP SIMD flag")
            for macro, value in (("KEYRA_FULL_FAST_CONTACT", "1"),
                                 ("KEYRA_FULL_MECHANISM_CACHE", "1"),
                                 ("KEYRA_FULL_MODEL_PROFILE", "0" if profile == "OriginalControl" else "1")):
                if definition(tokens, macro) != value:
                    raise ValueError(name + ": unrelated full-core selection changed: " + macro)
            cores[target] = {"free_unison": selected, "pressure": pressure}
        if set(cores) != {"native", "scalar"}:
            raise ValueError(name + ": both full-core compile commands are required")
        results.append({"case": name, "simd_selection": cores,
                        "cached_pressure_OFF_preserved": True if name == "pressure-opt-out" else None})
    return {"build_policy": "passed", "cases": results,
            "piano_DSP_compiled_or_executed": False, "SDK_validated": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instrument-dir", required=True, type=Path)
    parser.add_argument("--compiler", required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="keyra-reason-build-policy-") as folder:
        print(json.dumps(validate(args.instrument_dir.resolve(), args.compiler, Path(folder)), indent=2))


if __name__ == "__main__":
    main()
