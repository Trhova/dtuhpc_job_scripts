# 06 - Using This Repo for Metagenomics

This page explains how the included scripts fit into a metagenomics workflow.

Important: the scripts in this repo are templates from real work. They contain project-specific paths, sample counts, database paths, and Conda environment names. Read and edit before submitting.

## Expected Workflow Order

```text
Raw sequencing delivery
  |
  v
Unpack / merge FASTQ lanes
  |
  v
KneadData host filtering
  |
  v
Prepare HUMAnN input FASTQs
  |
  v
HUMAnN / MetaPhlAn profiling
  |
  v
Normalize, regroup, and merge tables
  |
  v
Transfer summaries/results back
```

## Folder Plan for a New Project

Choose one project root, for example:

```text
/work3/<dtu-user>/<project>
```

Suggested layout:

```text
/work3/<dtu-user>/<project>/
  dtuhpc_job_scripts/        # this repo
  raw_delivery/              # original .tar/.tar.gz or supplier folders
  input_fastq/               # cleaned/merged FASTQ inputs
  databases/                 # host, MetaPhlAn, HUMAnN databases
  kneaddata_project/
    samples.txt
    logs/
    kneaddata_output/
  humann_project/
    humann_input/
    humann_run/
      logs/
      output/
      merged_tables/
```

Use your group's required layout if different. Keep raw data and outputs outside Git.

## Personalization Checklist

Before running any script, search for project-specific values:

```bash
grep -R "/work3/" hpc_lsf hpc_python
grep -R "trhova" hpc_lsf hpc_python
```

Edit:

| Item | What to check |
| --- | --- |
| `#BSUB -J "name[1-N]"` | `N` must match number of samples or retry samples. |
| `#BSUB -o` / `#BSUB -e` | Log paths must point to your project and exist before `bsub`. |
| Conda path | `source .../conda.sh` must point to your Conda install. |
| Conda environment | `conda activate ...` must use an environment that exists. |
| `PROJECT_DIR` | Project-specific output root. |
| `RAW_DIR` / `INPUT_DIR` | Input FASTQ folder. |
| `OUT_DIR` / `OUTPUT_DIR` | Output folder. |
| `DB_PATH` / `DB_BASE` | Reference database paths. |
| `SAMPLES_FILE` | One sample ID per line for KneadData arrays. |
| file patterns | FASTQ naming expected by the script. |

Do not submit until every value is yours.

## Sample Lists

KneadData array scripts use sample names from a text file.

Example `samples.txt`:

```text
sample_A
sample_B
sample_C
```

Rules:

- one sample ID per line
- no FASTQ suffix
- no comments unless the script skips comments
- line 1 maps to array index 1
- line 2 maps to array index 2

If there are 3 samples:

```bash
#BSUB -J "knead[1-3]"
```

Check sample count:

```bash
wc -l /work3/<dtu-user>/<project>/kneaddata_project/samples.txt
```

## Input FASTQ Naming

Several scripts expect paired FASTQs like:

```text
sample_A_R1.fastq.gz
sample_A_R2.fastq.gz
sample_B_R1.fastq.gz
sample_B_R2.fastq.gz
```

The sample ID in `samples.txt` must match the filename prefix:

```text
sample_A
```

Then the script can build:

```bash
R1="$RAW_DIR/${SAMPLE_NAME}_R1.fastq.gz"
R2="$RAW_DIR/${SAMPLE_NAME}_R2.fastq.gz"
```

If your files are named differently, edit the script or create a clean input folder with the expected names.

## Stage 1: Unpack and Merge FASTQ Deliveries

Files:

- `hpc_lsf/unpack_merge_fastq.sh`
- `hpc_python/unpack_merge_fastq.py`

Purpose:

- unpack `.tar` or `.tar.gz` sequencing deliveries
- find FASTQ files
- group files by sample
- merge lanes into one R1/R2 pair per sample

Before running:

- edit `TAR_DIR`, `EXTRACT_DIR`, and `OUTPUT_DIR` in the Python script
- edit Conda paths in the LSF script
- make sure temporary extraction has enough space
- use an LSF job for large deliveries

Expected output:

```text
sample_A_R1.fastq.gz
sample_A_R2.fastq.gz
```

## Stage 2: Run KneadData

Files:

- `hpc_lsf/kneaddata_metagenomics_80.sh`
- `hpc_lsf/kneaddata_metagenomics_80_retry.sh`
- `hpc_lsf/kneaddata_SA2409_array.sh`

Purpose:

- remove host/contaminant reads
- write per-sample KneadData outputs and logs

Before running:

- set array size to the number of samples
- create `samples.txt`
- check `RAW_DIR`
- check `DB_PATH`
- check Conda activation
- create log directories before `bsub`

Small test:

```bash
head -1 /work3/<dtu-user>/<project>/kneaddata_project/samples.txt > /work3/<dtu-user>/<project>/kneaddata_project/samples_test.txt
```

If the script supports `KNEADDATA_SAMPLES_FILE`, submit with:

```bash
KNEADDATA_SAMPLES_FILE=/work3/<dtu-user>/<project>/kneaddata_project/samples_test.txt bsub < hpc_lsf/kneaddata_metagenomics_80.sh
```

Also make sure the script array range is suitable for a one-sample test.

Expected output:

```text
kneaddata_output/<sample>/
  <sample>_kneaddata.log
  ...
```

## Stage 3: Summarize KneadData

File:

- `hpc_python/kneaddata_read_summary.py`

Purpose:

- parse KneadData logs
- produce a summary table/CSV
- optionally plot host contamination

Example:

```bash
python hpc_python/kneaddata_read_summary.py \
  --kneaddata-root /work3/<dtu-user>/<project>/kneaddata_project/kneaddata_output \
  --output-dir /work3/<dtu-user>/<project>/kneaddata_project
```

Expected output:

```text
kneaddata_read_summary.csv
kneaddata_host_contamination.png
```

## Stage 4: Prepare HUMAnN Input

File:

- `hpc_python/merge_pairs_for_humann.py`

Purpose:

- merge KneadData paired outputs into single FASTQ files for HUMAnN

Current caveat:

- this helper has project-specific path defaults and limited CLI ergonomics
- read the file before running
- edit input/output paths

HUMAnN scripts may expect files matching:

```text
*_kneaddata_merged.fastq
```

or, in another script:

```text
*_merged.fastq
```

Check the exact glob in the HUMAnN LSF script you plan to use.

## Stage 5: Run HUMAnN / MetaPhlAn

Files:

- `hpc_lsf/humann38_metagenomics80_array.sh`
- `hpc_lsf/humann38_metagenomics80_with_virus_flag_array.sh`
- `hpc_lsf/humann38_SA2409_array.sh`

Purpose:

- run HUMAnN on each sample
- use MetaPhlAn database options
- write per-sample outputs

Before running:

- set array size
- check `INPUT_DIR`
- check `OUTPUT_DIR`
- check `DB_BASE`
- check `METAPHLAN_DB`
- check Conda activation
- check input filename pattern

Expected output:

```text
humann_run/output/<sample>/
  <sample>_genefamilies.tsv
  <sample>_pathabundance.tsv
  <sample>_pathcoverage.tsv
```

Exact filenames may differ by HUMAnN version and command options.

## Stage 6: Postprocess HUMAnN

Files:

- `hpc_python/humann_postprocess.py`
- `hpc_python/humann_merge_tables.py`

Purpose:

- normalize per-sample HUMAnN outputs
- regroup gene families
- collect/merge tables across samples

Current caveat:

- these helpers contain project-specific default paths
- inspect before running
- some operations recreate staging directories

Expected output:

```text
humann_run/merged_tables/
```

## Reference Databases

Metagenomics workflows require reference databases. This repo does not install them automatically.

Common examples:

| Database | Used by | Purpose |
| --- | --- | --- |
| Bowtie2 host reference | KneadData | Remove host reads. |
| MetaPhlAn database | MetaPhlAn/HUMAnN | Taxonomic profiling. |
| HUMAnN nucleotide/protein databases | HUMAnN | Functional profiling. |

Check official tool documentation and DTU/project guidance for installation commands, versions, storage needs, and approved locations.

Verify paths before running:

```bash
ls /work3/<dtu-user>/<project>/databases
ls /work3/<dtu-user>/<project>/databases/reference_mouse/bowtie2_mm39
```

## What Success Looks Like

| Stage | Success signal |
| --- | --- |
| Transfer | expected file count and size on `/work3`. |
| Unpack/merge | one R1 and one R2 FASTQ per sample. |
| KneadData | per-sample output folder and `_kneaddata.log`. |
| KneadData summary | CSV with one row per sample. |
| HUMAnN input prep | one merged FASTQ per sample matching HUMAnN glob. |
| HUMAnN | per-sample gene family/pathway tables. |
| Postprocess | normalized/regrouped/merged tables. |

## When to Scale Up

Only submit a full array after:

1. one sample runs successfully
2. logs are understandable
3. output files appear where expected
4. resource use is reasonable
5. sample count matches array size
6. you have enough quota

Then scale by adjusting:

- `#BSUB -J "name[1-N]"`
- sample manifest
- resource requests
- log paths
