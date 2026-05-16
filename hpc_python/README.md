# Python Helper Catalog

This folder contains Python helpers used around the metagenomics LSF jobs.

Important: several helpers still contain project-specific default paths. Inspect each script before running it, especially any path under `/work3/...`.

## General Pattern

Run helpers from the repository root on HPC:

```bash
cd /work3/<dtu-user>/<project>/dtuhpc_job_scripts
conda activate <env-name>
python hpc_python/<script>.py --help
```

If a script does not support `--help` or still has paths at the top of the file, open it and edit/copy it carefully before use.

## Helper Inventory

| Script | Purpose | Beginner notes |
| --- | --- | --- |
| `unpack_merge_fastq.py` | Extract sequencing archives and merge lanes into paired FASTQs. | Contains `TAR_DIR`, `EXTRACT_DIR`, and `OUTPUT_DIR` constants that must be changed before use. Run as an LSF job for large data. |
| `kneaddata_read_summary.py` | Parse KneadData logs and write summary CSV/plot. | Has CLI arguments for `--kneaddata-root` and `--output-dir`; safer than editing source. |
| `merge_pairs_for_humann.py` | Merge paired FASTQs into HUMAnN input files. | Contains hard-coded input/output paths; inspect and edit before use. |
| `read_quality_hist.py` | Plot quality score histogram from a FASTQ. | Contains a hard-coded FASTQ path; inspect and edit before use. |
| `humann_postprocess.py` | Normalize/regroup HUMAnN outputs. | Contains project-specific output root and HUMAnN binary path. |
| `humann_merge_tables.py` | Collect and merge HUMAnN/MetaPhlAn tables across samples. | Contains project-specific paths and recreates staging directories. Read before running. |

## Example: KneadData Summary

```bash
python hpc_python/kneaddata_read_summary.py \
  --kneaddata-root /work3/<dtu-user>/<project>/kneaddata_project/kneaddata_output \
  --output-dir /work3/<dtu-user>/<project>/kneaddata_project
```

Expected outputs:

```text
kneaddata_read_summary.csv
kneaddata_host_contamination.png
```

## Before Running Helpers

Check:

```bash
grep -n "/work3/" hpc_python/*.py
python hpc_python/kneaddata_read_summary.py --help
```

Ask:

- Does this script read or write large data?
- Should it run in `linuxsh` or as an LSF job instead of on a login node?
- Are all input paths correct?
- Will it overwrite or delete anything?
- Is the intended Conda environment active?

## Good Future Improvements

The helpers would be easier for new users if all scripts accepted CLI arguments instead of requiring source edits. Until that refactor happens, treat source defaults as examples from one project, not universal defaults.
