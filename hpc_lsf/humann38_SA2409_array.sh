#!/bin/bash
#BSUB -J "humann38_SA2409[1-48]"
#BSUB -q hpc
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=9GB]"
#BSUB -M 9GB
#BSUB -W 48:00
#BSUB -o /work3/trhova/humann_project/SA_24_09_Humann_Run/logs/humann38_SA2409_%I_%J.out
#BSUB -e /work3/trhova/humann_project/SA_24_09_Humann_Run/logs/humann38_SA2409_%I_%J.err

# -------------------------------
# Environment setup
# -------------------------------
export PATH="/work3/trhova/miniconda3/bin:$PATH"
source /work3/trhova/miniconda3/etc/profile.d/conda.sh
conda activate /work3/trhova/humann_project/humann38

# -------------------------------
# Variables and paths
# -------------------------------
INPUT_DIR="/work3/trhova/humann_project/SA_24_09"
OUTPUT_DIR="/work3/trhova/humann_project/SA_24_09_Humann_Run/output"
DB_BASE="/work3/trhova/humann_project/humann38_transfer_bundle"
METAPHLAN_DB="$DB_BASE/metaphlan41_databases"

mkdir -p "$OUTPUT_DIR"
mkdir -p "/work3/trhova/humann_project/SA_24_09_Humann_Run/logs"

# -------------------------------
# Select sample for this array index
# -------------------------------
SAMPLE=$(ls "$INPUT_DIR"/*_merged.fastq | sed -n "${LSB_JOBINDEX}p")
SAMPLE_NAME=$(basename "$SAMPLE" .fastq)

echo "Processing sample: $SAMPLE_NAME"

# -------------------------------
# Run HUMAnN
# -------------------------------
humann \
  --input "$SAMPLE" \
  --output "$OUTPUT_DIR/$SAMPLE_NAME" \
  --threads 8 \
  --metaphlan-options "--bowtie2db $METAPHLAN_DB --index mpa_vOct22_CHOCOPhlAnSGB_202403"

echo "HUMAnN completed for $SAMPLE_NAME"
