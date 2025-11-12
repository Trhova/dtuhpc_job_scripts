#!/usr/bin/env python3
"""
Merge HUMAnN per-sample outputs into cohort-wide matrices.

Steps:
 1. Copy each sample's output tables into staging folders (one per table type)
    to keep the files organized.
 2. Run humann_join_tables on each staging folder to create a merged matrix.
 3. Merge MetaPhlAn bugs list profiles as well.

Run from an interactive session inside the HUMAnN conda environment so the
humann_* utilities are on PATH.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict

OUTPUT_ROOT = Path("/work3/trhova/humann_project/metagenomics_80/humann_run/output")
STAGING_ROOT = OUTPUT_ROOT.parent / "merged_inputs"
MERGED_ROOT = OUTPUT_ROOT.parent / "merged_tables"
HUMANN_ENV_BIN = Path("/work3/trhova/humann_project/humann38/bin")

TABLE_SPECS: Dict[str, Dict[str, str]] = {
    "genefamilies": {
        "pattern": "{sample}_genefamilies.tsv",
        "merged": "humann_genefamilies.tsv",
    },
    "genefamilies_cpm": {
        "pattern": "{sample}_genefamilies_cpm.tsv",
        "merged": "humann_genefamilies_cpm.tsv",
    },
    "genefamilies_relab": {
        "pattern": "{sample}_genefamilies_relab.tsv",
        "merged": "humann_genefamilies_relab.tsv",
    },
    "genefamilies_cpm_level4ec": {
        "pattern": "{sample}_genefamilies_cpm_level4ec.tsv",
        "merged": "humann_genefamilies_cpm_level4ec.tsv",
    },
    "pathabundance": {
        "pattern": "{sample}_pathabundance.tsv",
        "merged": "humann_pathabundance.tsv",
    },
    "pathabundance_cpm": {
        "pattern": "{sample}_pathabundance_cpm.tsv",
        "merged": "humann_pathabundance_cpm.tsv",
    },
    "pathabundance_relab": {
        "pattern": "{sample}_pathabundance_relab.tsv",
        "merged": "humann_pathabundance_relab.tsv",
    },
    "pathcoverage": {
        "pattern": "{sample}_pathcoverage.tsv",
        "merged": "humann_pathcoverage.tsv",
    },
    "pathcoverage_cpm": {
        "pattern": "{sample}_pathcoverage_cpm.tsv",
        "merged": "humann_pathcoverage_cpm.tsv",
    },
    "pathcoverage_relab": {
        "pattern": "{sample}_pathcoverage_relab.tsv",
        "merged": "humann_pathcoverage_relab.tsv",
    },
    "metaphlan_bugs": {
        "pattern": "{sample}_humann_temp/{sample}_metaphlan_bugs_list.tsv",
        "merged": "metaphlan_bugs_list.tsv",
    },
}


def run_command(cmd: list[str]) -> None:
    env = os.environ.copy()
    env["PATH"] = f"{HUMANN_ENV_BIN}:{env['PATH']}"
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, env=env)


def prepare_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_tables(output_root: Path, staging_root: Path) -> Dict[str, int]:
    counts = {name: 0 for name in TABLE_SPECS}
    for table_name, spec in TABLE_SPECS.items():
        prepare_directory(staging_root / table_name)

    for sample_dir in sorted(p for p in output_root.iterdir() if p.is_dir()):
        sample = sample_dir.name
        for table_name, spec in TABLE_SPECS.items():
            rel_path = Path(spec["pattern"].format(sample=sample))
            src = sample_dir / rel_path
            if not src.exists():
                continue
            dest = staging_root / table_name / src.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            counts[table_name] += 1
    return counts


def join_tables(staging_root: Path, merged_root: Path, counts: Dict[str, int]) -> None:
    merged_root.mkdir(parents=True, exist_ok=True)
    for table_name, spec in TABLE_SPECS.items():
        stage_dir = staging_root / table_name
        if table_name == "metaphlan_bugs":
            continue
        if counts.get(table_name, 0) == 0:
            print(f"Skipping {table_name}: no files copied.")
            continue
        output_path = merged_root / spec["merged"]
        run_command(
            [
                "humann_join_tables",
                "--input",
                str(stage_dir),
                "--output",
                str(output_path),
            ]
        )

    # Handle MetaPhlAn bugs lists separately.
    metaphlan_stage = staging_root / "metaphlan_bugs"
    if counts.get("metaphlan_bugs", 0):
        print("Joining MetaPhlAn bugs lists with merge_metaphlan_tables.py")
        merged_bugs = merged_root / "metaphlan_bugs_list.tsv"
        files = sorted(metaphlan_stage.glob("*.tsv"))
        env = os.environ.copy()
        env["PATH"] = f"{HUMANN_ENV_BIN}:{env['PATH']}"
        with merged_bugs.open("w") as handle:
            subprocess.run(
                ["merge_metaphlan_tables.py", *[str(f) for f in files]],
                check=True,
                env=env,
                stdout=handle,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        default=OUTPUT_ROOT,
        type=Path,
        help="Per-sample HUMAnN output directory.",
    )
    parser.add_argument(
        "--staging-root",
        default=STAGING_ROOT,
        type=Path,
        help="Where to copy per-sample tables before merging.",
    )
    parser.add_argument(
        "--merged-root",
        default=MERGED_ROOT,
        type=Path,
        help="Destination directory for merged cohort tables.",
    )
    args, _ = parser.parse_known_args()

    print(f"Staging per-sample tables under {args.staging_root}")
    counts = copy_tables(args.output_root, args.staging_root)
    for table_name, count in counts.items():
        print(f"  {table_name}: {count} files")

    print(f"Merging staged tables into {args.merged_root}")
    join_tables(args.staging_root, args.merged_root, counts)
    print("HUMAnN table merging complete.")


if __name__ == "__main__":
    main()
