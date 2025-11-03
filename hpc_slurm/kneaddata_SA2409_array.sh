#!/bin/bash
#BSUB -J "knead[1-48]"
#BSUB -q hpc
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=2GB]"
#BSUB -M 2GB
#BSUB -W 24:00
#BSUB -o logs/knead_%I_%J.out
#BSUB -e logs/knead_%I_%J.err

export PATH="/work3/trhova/miniconda3/bin:$PATH"
source /work3/trhova/miniconda3/etc/profile.d/conda.sh
conda activate kneaddata-0.12.3

PROJECT_DIR="/work3/trhova/kneaddata_project/SA_24_09"
RAW_DIR="$PROJECT_DIR/X204SC24111322-Z01-F002_02/01.RawData"
OUT_DIR="$PROJECT_DIR/kneaddata_output"
DB_PATH="/work3/trhova/kneaddata_project/Reference_genomes_and_databases/reference_mouse/bowtie2_mm39"

SAMPLE_NAME=$(sed -n "${LSB_JOBINDEX}p" $PROJECT_DIR/samples.txt)
SAMPLE_PATH="$RAW_DIR/$SAMPLE_NAME"
mkdir -p "$OUT_DIR/$SAMPLE_NAME"

echo "Processing sample: $SAMPLE_NAME"
kneaddata \
  -i1 "$SAMPLE_PATH/${SAMPLE_NAME}_1.fq.gz" \
  -i2 "$SAMPLE_PATH/${SAMPLE_NAME}_2.fq.gz" \
  -o "$OUT_DIR/$SAMPLE_NAME" \
  -db "$DB_PATH" \
  --bypass-trf \
  --threads 8
