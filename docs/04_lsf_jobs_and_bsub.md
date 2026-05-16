# 04 - LSF Jobs and `bsub`

DTU HPC uses LSF for batch jobs. This page explains the structure of an LSF script and how to submit, monitor, cancel, and debug jobs.

## What `bsub` Does

This command:

```bash
bsub < job.sh
```

sends `job.sh` to LSF. It does not run the script directly in your terminal. LSF starts it later on a compute node when the requested queue, cores, memory, and wall time are available.

## Anatomy of a `#BSUB` Script

```bash
#!/bin/sh
#BSUB -q hpc
#BSUB -J example_job
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -M 5GB
#BSUB -W 02:00
#BSUB -oo logs/example_%J.out
#BSUB -eo logs/example_%J.err

set -e

cd /work3/<dtu-user>/<project>/DTU_HPC_2026

source /work3/<dtu-user>/<project>/miniconda3/etc/profile.d/conda.sh
conda activate <env-name>

hostname
date
python hpc_python/kneaddata_read_summary.py --help
```

Line by line:

| Line | Meaning |
| --- | --- |
| `#!/bin/sh` | Shell used to run the script. |
| `#BSUB -q hpc` | Queue/resource pool. Check official docs for queues available to you. |
| `#BSUB -J example_job` | Job name shown by `bjobs`. |
| `#BSUB -n 4` | Request 4 cores/slots. Usually match tool threads. |
| `#BSUB -R "span[hosts=1]"` | Keep requested cores on one host. |
| `#BSUB -R "rusage[mem=4GB]"` | Request memory for scheduling. Confirm current DTU interpretation in official docs. |
| `#BSUB -M 5GB` | Memory limit. If exceeded, the job may be killed. |
| `#BSUB -W 02:00` | Maximum wall time, here 2 hours. |
| `#BSUB -oo logs/example_%J.out` | stdout log. `%J` becomes job ID. |
| `#BSUB -eo logs/example_%J.err` | stderr log. |
| `cd ...` | Move to the working directory. |
| `conda activate ...` | Activate required tools. |

## Job Name

Use a short descriptive job name:

```bash
#BSUB -J kneaddata_test
```

For arrays:

```bash
#BSUB -J "knead[1-80]"
```

This creates tasks 1 through 80.

## Queue

Many examples use:

```bash
#BSUB -q hpc
```

Queues define policies and resource pools. Some queues may be group-specific or hardware-specific. Check official DTU HPC docs before using a queue you have not used before.

## Cores and Threads

If a tool uses 8 threads:

```bash
#BSUB -n 8
kneaddata --threads 8 ...
```

Keep these consistent. Requesting 8 cores but using 1 thread wastes resources. Using 8 threads while requesting 1 core can overload the slot you were given.

## Memory

Scripts often contain both:

```bash
#BSUB -R "rusage[mem=4GB]"
#BSUB -M 5GB
```

Treat `rusage[mem=...]` as the memory request used for scheduling and `-M` as a limit that can kill the job if exceeded. Exact per-core/per-process behavior can depend on local LSF configuration; check DTU HPC docs for the current rule.

## Wall Time

```bash
#BSUB -W 24:00
```

This is the maximum runtime. Too short means the job may be killed. Too long may make scheduling slower. Start with one sample, inspect runtime, then scale.

## Logs

Always write logs:

```bash
#BSUB -oo logs/job_%J.out
#BSUB -eo logs/job_%J.err
```

For arrays:

```bash
#BSUB -oo logs/job_%I_%J.out
#BSUB -eo logs/job_%I_%J.err
```

`%I` is the array index. `%J` is the job ID.

Important: LSF opens log paths before the script body runs. Create log directories before `bsub`:

```bash
mkdir -p logs
bsub < job.sh
```

## Job Arrays

An array runs the same script many times with different indexes.

Example:

```bash
#BSUB -J "knead[1-3]"
```

If `samples.txt` contains:

```text
sample_A
sample_B
sample_C
```

Then:

| Array index | `LSB_JOBINDEX` | Sample selected by `sed -n "${LSB_JOBINDEX}p"` |
| --- | --- | --- |
| 1 | `1` | `sample_A` |
| 2 | `2` | `sample_B` |
| 3 | `3` | `sample_C` |

The array range must match your sample list:

```bash
wc -l samples.txt
```

If there are 37 samples, use:

```bash
#BSUB -J "knead[1-37]"
```

Do not add comments to `samples.txt` unless the script explicitly skips comments.

## Environment Activation

Batch shells may not load your interactive shell setup. Source Conda explicitly:

```bash
source /work3/<dtu-user>/<project>/miniconda3/etc/profile.d/conda.sh
conda activate <env-name>
which python
```

Use tool checks near the start of scripts:

```bash
which kneaddata
which humann
which metaphlan
```

## Input and Output Paths

Use absolute paths for production jobs:

```bash
PROJECT_DIR="/work3/<dtu-user>/<project>/kneaddata_project"
RAW_DIR="/work3/<dtu-user>/<project>/input_fastq"
OUT_DIR="$PROJECT_DIR/kneaddata_output"
DB_PATH="/work3/<dtu-user>/<project>/databases/reference_mouse/bowtie2_mm39"
```

Before submitting:

```bash
ls "$RAW_DIR"
ls "$DB_PATH"
mkdir -p "$OUT_DIR" "$PROJECT_DIR/logs"
```

## Submit

```bash
bsub < hpc_lsf/kneaddata_metagenomics_80.sh
```

For a test manifest, if a script supports an environment override:

```bash
KNEADDATA_SAMPLES_FILE=/work3/<dtu-user>/<project>/samples_test.txt bsub < hpc_lsf/kneaddata_metagenomics_80.sh
```

Check each script before assuming it supports overrides.

## Monitor

```bash
bjobs
bjobs -l <job-id>
bstat
bstat -C
bstat -M
showstart <job-id>
bpeek <job-id>
bhist -l <job-id>
```

`bstat`, `showstart`, and related helpers may be DTU/DCC-specific. If a command is unavailable, check official docs for the current command.

## Cancel

```bash
bkill <job-id>
```

For an array task:

```bash
bkill "<job-id>[<index>]"
```

## Debug Failed Jobs

Start with:

```bash
bjobs -l <job-id>
bhist -l <job-id>
cat logs/<job>.err
cat logs/<job>.out
```

Common failures:

| Symptom | Likely cause | Check |
| --- | --- | --- |
| Log file missing | Log directory did not exist before `bsub`. | `ls -ld logs` |
| `command not found` | Environment not activated. | `which <tool>` inside the job. |
| Input file not found | Path or sample name mismatch. | Echo and `ls` input paths. |
| Empty sample name | Array index exceeds sample list. | `wc -l samples.txt`, check `#BSUB -J`. |
| Killed for memory | Memory request/limit too low. | `bstat -M`, `bhist -l`. |
| Job stays pending | Queue busy or resource request large. | `bjobs -l`, `showstart`. |

## Annotated Metagenomics Array Skeleton

```bash
#!/bin/bash
#BSUB -J "knead[1-<N>]"
#BSUB -q hpc
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=2GB]"
#BSUB -M 2GB
#BSUB -W 24:00
#BSUB -oo /work3/<dtu-user>/<project>/logs/knead_%I_%J.out
#BSUB -eo /work3/<dtu-user>/<project>/logs/knead_%I_%J.err

set -euo pipefail

source /work3/<dtu-user>/<project>/miniconda3/etc/profile.d/conda.sh
conda activate kneaddata-0.12.3

PROJECT_DIR="/work3/<dtu-user>/<project>/kneaddata_project"
RAW_DIR="/work3/<dtu-user>/<project>/cleaned_fastq"
OUT_DIR="$PROJECT_DIR/kneaddata_output"
DB_PATH="/work3/<dtu-user>/<project>/databases/reference_mouse/bowtie2_mm39"
SAMPLES_FILE="$PROJECT_DIR/samples.txt"

SAMPLE_NAME=$(sed -n "${LSB_JOBINDEX}p" "$SAMPLES_FILE")
R1="$RAW_DIR/${SAMPLE_NAME}_R1.fastq.gz"
R2="$RAW_DIR/${SAMPLE_NAME}_R2.fastq.gz"

echo "Sample: $SAMPLE_NAME"
echo "R1: $R1"
echo "R2: $R2"

kneaddata \
  -i1 "$R1" \
  -i2 "$R2" \
  -o "$OUT_DIR/$SAMPLE_NAME" \
  -db "$DB_PATH" \
  --threads 8
```

This is an annotated teaching skeleton, not a replacement for checking the actual scripts.
