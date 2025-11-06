#!/usr/bin/env python3
import gzip
from pathlib import Path

input_dir = Path("/work3/trhova/metagenomics_input/cleaned_fastq")
output_dir = Path("/work3/trhova/metagenomics_input/merged_fastq")
output_dir.mkdir(exist_ok=True)

# Collect all R1 files
r1_files = sorted(input_dir.glob("*_R1.fastq.gz"))

for r1 in r1_files:
    sample = r1.name.replace("_R1.fastq.gz", "")
    r2 = input_dir / f"{sample}_R2.fastq.gz"
    if not r2.exists():
        print(f"⚠️ Skipping {sample}: missing R2 file")
        continue

    merged = output_dir / f"{sample}_merged.fastq.gz"
    print(f"Merging {r1.name} + {r2.name} -> {merged.name}")

    with gzip.open(merged, "wb") as out_f:
        for f in [r1, r2]:
            with gzip.open(f, "rb") as in_f:
                while True:
                    chunk = in_f.read(1024 * 1024)
                    if not chunk:
                        break
                    out_f.write(chunk)

print("\n✅ Done merging all paired FASTQs for HUMAnN input.")
