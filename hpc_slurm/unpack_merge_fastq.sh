#!/bin/bash
#BSUB -J unpack_merge          # Job name
#BSUB -q hpc                   # Queue name
#BSUB -n 8                     # Number of CPU cores
#BSUB -R "span[hosts=1]"       # Use a single host
#BSUB -R "rusage[mem=4GB]"     # Memory per core
#BSUB -M 4GB                   # Total memory limit per core
#BSUB -W 24:00                 # Runtime limit (24 hours)
#BSUB -o unpack_merge_%J.out   # Standard output file
#BSUB -e unpack_merge_%J.err   # Standard error file

# --- Environment setup ---
export PATH="/work3/trhova/miniconda3/bin:$PATH"
source /work3/trhova/miniconda3/etc/profile.d/conda.sh
conda activate pytools

# --- Run the unpack and merge script ---
python /work3/trhova/hpc_python/unpack_merge_fastq.py
