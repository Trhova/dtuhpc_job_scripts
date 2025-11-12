#!/bin/bash
#BSUB -J "humann38_metagenomics80_virus[1-80]"
#BSUB -q hpc
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=9GB]"
#BSUB -M 9GB
#BSUB -W 48:00
#BSUB -o /work3/trhova/humann_project/metagenomics_80/humann_run/logs/humann38_met80_virus_%I_%J.out
#BSUB -e /work3/trhova/humann_project/metagenomics_80/humann_run/logs/humann38_met80_virus_%I_%J.err

# -------------------------------
# Environment setup
# -------------------------------
export PATH="/work3/trhova/miniconda3/bin:$PATH"
source /work3/trhova/miniconda3/etc/profile.d/conda.sh
conda activate /work3/trhova/humann_project/humann38

# -------------------------------
# Variables and paths
# -------------------------------
INPUT_DIR="/work3/trhova/humann_project/metagenomics_80/humann_input"
OUTPUT_DIR="/work3/trhova/humann_project/metagenomics_80/humann_run/output_virus"
LOG_DIR="/work3/trhova/humann_project/metagenomics_80/humann_run/logs"
DB_BASE="/work3/trhova/humann_project/humann38_transfer_bundle"
METAPHLAN_DB="$DB_BASE/metaphlan41_databases"
VSC_DB="$METAPHLAN_DB/mpa_vOct22_CHOCOPhlAnSGB_202403_VSG"
METAPHLAN_OPTS="--bowtie2db $METAPHLAN_DB --index mpa_vOct22_CHOCOPhlAnSGB_202403 --profile_vsc --vsc-db $VSC_DB"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"

# -------------------------------
# Select sample for this array index
# -------------------------------
SAMPLE=$(ls "$INPUT_DIR"/*_kneaddata_merged.fastq | sed -n "${LSB_JOBINDEX}p")
if [ -z "$SAMPLE" ]; then
  echo "No sample found for index $LSB_JOBINDEX" >&2
  exit 1
fi
SAMPLE_NAME=$(basename "$SAMPLE" .fastq)

echo "Processing sample (virus flag): $SAMPLE_NAME"

# -------------------------------
# Run HUMAnN with viral profiling
# -------------------------------
humann \
  --input "$SAMPLE" \
  --output "$OUTPUT_DIR/$SAMPLE_NAME" \
  --threads 8 \
  --metaphlan-options "$METAPHLAN_OPTS"

echo "HUMAnN (virus flag) completed for $SAMPLE_NAME"
