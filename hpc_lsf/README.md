# LSF Job Script Catalog

This folder contains LSF (`#BSUB`) job scripts. It used to be named like Slurm in earlier drafts, but these are **not Slurm scripts**. Submit them with `bsub`, not `sbatch`.

Important: these scripts are templates from real projects. They still contain project-specific paths, sample counts, database paths, and Conda activation commands. Do not submit them unchanged.

## Edit Before Running

For every script, check:

| Item | Why it matters |
| --- | --- |
| `#BSUB -J "name[1-N]"` | Array range must match sample count. |
| `#BSUB -q` | Queue must be valid for your account. |
| `#BSUB -n` | Cores should match tool threads. |
| `#BSUB -R "rusage[mem=...]"` and `#BSUB -M` | Memory must fit the tool and DTU LSF rules. |
| `#BSUB -W` | Wall time must be long enough but not excessive. |
| `#BSUB -o` / `#BSUB -e` | Log directories must exist before `bsub`. |
| Conda path/env | Must exist for your account. |
| `PROJECT_DIR`, `RAW_DIR`, `INPUT_DIR`, `OUT_DIR`, `OUTPUT_DIR` | Must point to your project. |
| `DB_PATH`, `DB_BASE`, `METAPHLAN_DB` | Must point to installed databases. |
| sample source | Manifest or input glob must match your files. |

Search for project-specific paths:

```bash
grep -n "/work3/" hpc_lsf/*.sh
```

## Script Inventory

| Script | Purpose | Type | Main assumptions |
| --- | --- | --- | --- |
| `unpack_merge_fastq.sh` | Run the Python unpack/merge helper as an LSF job. | Single job | Calls `hpc_python/unpack_merge_fastq.py`; edit Conda and script path. |
| `kneaddata_metagenomics_80.sh` | Run KneadData across a sample array. | Array job | Expects `samples.txt`, paired `SAMPLE_R1.fastq.gz`/`SAMPLE_R2.fastq.gz`, host DB path. |
| `kneaddata_metagenomics_80_retry.sh` | Retry selected KneadData samples. | Array job | Uses an inline sample list; edit before use. |
| `kneaddata_SA2409_array.sh` | Run KneadData for a specific historical project layout. | Array job | Project-specific folder structure and sample naming. |
| `humann38_metagenomics80_array.sh` | Run HUMAnN on merged KneadData FASTQs. | Array job | Expects `*_kneaddata_merged.fastq` inputs and MetaPhlAn DB path. |
| `humann38_metagenomics80_with_virus_flag_array.sh` | HUMAnN variant with viral flag/options. | Array job | Same as above, with variant output path/options. |
| `humann38_SA2409_array.sh` | HUMAnN for a specific historical project layout. | Array job | Expects `*_merged.fastq` inputs. |
| `samples.txt` | Example sample manifest. | Text file | One sample ID per line; no comments for current `sed` usage. |

## Array Jobs

Array jobs use:

```bash
#BSUB -J "knead[1-80]"
```

LSF sets `LSB_JOBINDEX` to one number per task. Scripts use that number to pick a sample:

```bash
SAMPLE_NAME=$(sed -n "${LSB_JOBINDEX}p" "$SAMPLES_FILE")
```

If your sample list has 12 lines, the array range should be `[1-12]`.

## Logs

Prefer log filenames with `%I` and `%J` for arrays:

```bash
#BSUB -o /work3/<dtu-user>/<project>/logs/job_%I_%J.out
#BSUB -e /work3/<dtu-user>/<project>/logs/job_%I_%J.err
```

Create the log directory before submission:

```bash
mkdir -p /work3/<dtu-user>/<project>/logs
bsub < hpc_lsf/script.sh
```

## Safe Test Pattern

Before a full run:

1. create a one-sample manifest
2. adjust array range to `[1-1]`
3. submit
4. inspect logs
5. confirm outputs
6. scale to all samples

## Related Docs

- [HPC mental model](../docs/01_hpc_mental_model.md)
- [LSF jobs and `bsub`](../docs/04_lsf_jobs_and_bsub.md)
- [Using this repo for metagenomics](../docs/06_using_this_repo_for_metagenomics.md)
