#!/usr/bin/env python3
"""
unpack_merge_fastq.py

Purpose:
  Automate unpacking large TAR archives of sequencing data
  and merging multiple sequencing lanes into single FASTQ pairs
  (R1 and R2) per sample.
  Sample name is determined as the part before '_EKD' in filenames.

Author: trhova
Environment: DTU HPC (pytools)
"""

import os
import tarfile
import gzip
import shutil
from pathlib import Path
import subprocess

# ------------------------------
# User-defined paths (edit before running)
# ------------------------------
TAR_DIR = "/work3/trhova/metagenomics_input/Metagenomics_80"    # location of TAR files
EXTRACT_DIR = "/work3/trhova/metagenomics_input/tmp_extract"     # temporary extraction area
OUTPUT_DIR = "/work3/trhova/metagenomics_input/cleaned_fastq"    # merged output folder

# ------------------------------
# Helper functions
# ------------------------------

def extract_tar(tar_path, extract_to):
    """Extract a TAR or TAR.GZ archive into a given directory."""
    print(f"Extracting {tar_path} → {extract_to}")
    with tarfile.open(tar_path, "r:*") as tar:
        tar.extractall(path=extract_to)
    print("✅ Extraction complete.")


def find_fastq_files(base_dir):
    """Recursively find all FASTQ(.gz) files inside extracted folder."""
    fastq_files = []
    for ext in ("*.fastq.gz", "*.fq.gz", "*.fastq", "*.fq"):
        fastq_files.extend(Path(base_dir).rglob(ext))
    print(f"Found {len(fastq_files)} FASTQ files under {base_dir}")
    return fastq_files


def group_by_sample(fastq_files):
    """
    Group R1/R2 FASTQ files by sample prefix.
    The prefix is defined as everything before '_EKD' in the filename.
    Read direction is inferred from '_1' or '_2' at the end of the name.
    """
    sample_dict = {}

    for f in fastq_files:
        name = f.name

        # Remove extensions
        for ext in [".fastq.gz", ".fq.gz", ".fastq", ".fq"]:
            if name.endswith(ext):
                name = name.replace(ext, "")
                break

        # Determine read type
        if name.endswith("_1"):
            read_type = "R1"
            name = name[:-2]
        elif name.endswith("_2"):
            read_type = "R2"
            name = name[:-2]
        else:
            read_type = "unknown"

        # Determine sample prefix (before _EKD if present)
        if "_EKD" in name:
            prefix = name.split("_EKD")[0]
        else:
            prefix = name

        sample_dict.setdefault(prefix, {}).setdefault(read_type, []).append(f)

    print(f"Grouped into {len(sample_dict)} samples.")
    return sample_dict


def merge_lanes(sample_name, reads_dict, output_dir):
    """Merge multiple lane FASTQs for each sample and direction."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for read_type, file_list in reads_dict.items():
        merged_file = output_dir / f"{sample_name}_{read_type}.fastq.gz"
        print(f"Merging {len(file_list)} lanes → {merged_file}")

        # Concatenate compressed reads safely
        with open(merged_file, "wb") as wfh:
            for f in sorted(file_list):
                with open(f, "rb") as rfh:
                    shutil.copyfileobj(rfh, wfh)

    print(f"✅ {sample_name} merge complete.")


def main():
    """Main driver function."""
    TAR_DIR_PATH = Path(TAR_DIR)
    for tar_file in TAR_DIR_PATH.glob("*.tar*"):
        batch_name = tar_file.stem
        batch_extract_dir = Path(EXTRACT_DIR) / batch_name
        batch_extract_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Extract the TAR archive
        extract_tar(tar_file, batch_extract_dir)

        # Step 2: Find FASTQ files inside extraction
        fastq_files = find_fastq_files(batch_extract_dir)

        # Step 3: Group by sample and read type
        grouped = group_by_sample(fastq_files)

        # Step 4: Merge lanes and write outputs
        for sample, reads in grouped.items():
            merge_lanes(sample, reads, OUTPUT_DIR)

    print("🎉 All TAR batches processed successfully.")


if __name__ == "__main__":
    main()
    # ------------------------------
    # Step 5: Verification summary
    # ------------------------------
    print("\n--- Verification Summary ---")
    out_dir = Path(OUTPUT_DIR)
    merged_files = sorted(out_dir.glob("*.fastq.gz"))

    # Map sample → count of files
    from collections import defaultdict
    sample_counts = defaultdict(int)
    for f in merged_files:
        sample_id = f.name.split("_R")[0]
        sample_counts[sample_id] += 1

    total_samples = len(sample_counts)
    print(f"Total unique samples in output: {total_samples}")
    print(f"Total FASTQ files in output: {len(merged_files)}")

    # Check how many have exactly 2 files
    perfect = sum(1 for v in sample_counts.values() if v == 2)
    incomplete = total_samples - perfect

    print(f"Samples with both R1 and R2: {perfect}")
    print(f"Samples missing a pair: {incomplete}")

    # Optional visualization (requires matplotlib)
    try:
        import matplotlib.pyplot as plt
        plt.bar(["R1+R2 OK", "Missing"], [perfect, incomplete])
        plt.title("FASTQ Merge Summary")
        plt.ylabel("Sample count")
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("(matplotlib not installed — skipping plot)")
