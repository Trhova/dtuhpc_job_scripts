#!/usr/bin/env python3
"""
Post-process HUMAnN per-sample outputs:
  * generate CPM and relative-abundance tables
  * regroup CPM gene families to EC numbers

Run this after HUMAnN finishes for all samples. Execute from an interactive
session with the HUMAnN conda environment activated so the humann_* utilities
are on PATH.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from typing import Dict

OUTPUT_ROOT = Path("/work3/trhova/humann_project/metagenomics_80/humann_run/output")
HUMANN_ENV_BIN = Path("/work3/trhova/humann_project/humann38/bin")


def run_command(cmd: list[str]) -> None:
    """Run a shell command and echo it first."""
    print(" ".join(cmd))
    env = os.environ.copy()
    env["PATH"] = f"{HUMANN_ENV_BIN}:{env['PATH']}"
    subprocess.run(cmd, check=True, env=env)


def normalize_table(table_path: Path, units: str, output_path: Path) -> None:
    """Call humann_renorm_table unless the output already exists."""
    if output_path.exists():
        return
    run_command(
        [
            "humann_renorm_table",
            "--input",
            str(table_path),
            "--units",
            units,
            "--output",
            str(output_path),
        ]
    )


def detect_uniref_scope(genefamilies_file: Path) -> str:
    """Return humann_regroup_table group spec based on UniRef IDs."""
    with genefamilies_file.open() as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            feature = line.split("\t", 1)[0]
            if feature.startswith("UniRef50_"):
                return "uniref50_level4ec"
            return "uniref90_level4ec"
    raise RuntimeError(f"Could not detect UniRef scope in {genefamilies_file}")


def regroup_to_ec(genefamilies_cpm: Path, group_spec: str, output_path: Path) -> None:
    if output_path.exists():
        return
    run_command(
        [
            "humann_regroup_table",
            "--input",
            str(genefamilies_cpm),
            "--groups",
            str(group_spec),
            "--output",
            str(output_path),
        ]
    )


def process_sample(sample_dir: Path) -> None:
    sample = sample_dir.name
    tables: Dict[str, Path] = {
        "genefamilies": sample_dir / f"{sample}_genefamilies.tsv",
        "pathabundance": sample_dir / f"{sample}_pathabundance.tsv",
        "pathcoverage": sample_dir / f"{sample}_pathcoverage.tsv",
    }

    if not all(path.exists() for path in tables.values()):
        print(f"Skipping {sample}: missing HUMAnN outputs.")
        return

    # Generate CPM and RelAb tables for each output.
    for name, path in tables.items():
        normalize_table(path, "cpm", path.with_name(f"{sample}_{name}_cpm.tsv"))
        normalize_table(path, "relab", path.with_name(f"{sample}_{name}_relab.tsv"))

    # Regroup CPM-normalized gene families to EC numbers.
    genefamilies_cpm = sample_dir / f"{sample}_genefamilies_cpm.tsv"
    if not genefamilies_cpm.exists():
        print(f"Skipping EC regroup for {sample}: CPM table missing.")
        return

    ec_output = sample_dir / f"{sample}_genefamilies_cpm_level4ec.tsv"
    if ec_output.exists():
        print(f"Skipping EC regroup for {sample}: output already exists.")
        return

    groups = detect_uniref_scope(tables["genefamilies"])
    regroup_to_ec(genefamilies_cpm, groups, ec_output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        default=OUTPUT_ROOT,
        type=Path,
        help="Root directory containing per-sample HUMAnN output folders.",
    )
    args, _ = parser.parse_known_args()

    for sample_dir in sorted(args.output_root.iterdir()):
        if sample_dir.is_dir():
            process_sample(sample_dir)

    print("HUMAnN post-processing complete.")


if __name__ == "__main__":
    main()
