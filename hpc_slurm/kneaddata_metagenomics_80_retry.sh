#!/bin/bash
#BSUB -J "knead_retry[1-35]"
#BSUB -q hpc
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=2GB]"
#BSUB -M 2GB
#BSUB -W 24:00
#BSUB -o /work3/trhova/kneaddata_project/metagenomics_80/logs/knead_retry_%I_%J.out
#BSUB -e /work3/trhova/kneaddata_project/metagenomics_80/logs/knead_retry_%I_%J.err

# --- Conda environment ---
export PATH="/work3/trhova/miniconda3/bin:$PATH"
source /work3/trhova/miniconda3/etc/profile.d/conda.sh
conda activate kneaddata-0.12.3

# --- Project paths ---
PROJECT_DIR="/work3/trhova/kneaddata_project/metagenomics_80"
RAW_DIR="/work3/trhova/metagenomics_input/cleaned_fastq"
OUT_DIR="$PROJECT_DIR/kneaddata_output"
DB_PATH="/work3/trhova/Reference_genomes_and_databases/reference_mouse/bowtie2_mm39"
SAMPLES_FILE="${KNEADDATA_SAMPLES_FILE:-$PROJECT_DIR/samples_retry.txt}"

mkdir -p "$OUT_DIR"
mkdir -p "$PROJECT_DIR/logs"

if [ ! -s "$SAMPLES_FILE" ]; then
  echo "Samples file not found or empty: $SAMPLES_FILE" >&2
  exit 1
fi

# --- Determine sample for this array job ---
SAMPLE_NAME=$(sed -n "${LSB_JOBINDEX}p" "$SAMPLES_FILE")
mkdir -p "$OUT_DIR/$SAMPLE_NAME"

echo "Processing sample: $SAMPLE_NAME (retry)"

# --- Input FASTQs ---
R1="$RAW_DIR/${SAMPLE_NAME}_R1.fastq.gz"
R2="$RAW_DIR/${SAMPLE_NAME}_R2.fastq.gz"

# --- Run Kneaddata ---
kneaddata \
  -i1 "$R1" \
  -i2 "$R2" \
  -o "$OUT_DIR/$SAMPLE_NAME" \
  -db "$DB_PATH" \
  --bypass-trf \
  --threads 8
