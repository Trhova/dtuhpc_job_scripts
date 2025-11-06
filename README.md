# DTU HPC Job Scripts

Utility scripts and job submissions I use on the DTU HPC cluster for processing metagenomics sequencing data. The repository is split between batch scripts that run on the cluster and Python helpers that prepare or summarize the data.

## Repository Layout

| Path | Description |
| --- | --- |
| `hpc_slurm/` | LSF (`#BSUB`) submission scripts that wrap tools like KneadData and HUMAnN with the paths used in my project space. |
| `hpc_python/` | Companion Python utilities for unpacking FASTQ archives, merging lanes, plotting QC summaries, and reporting KneadData results. |

Everything else in the workspace (`envs/`, `humann_project/`, `kneaddata_project/`, etc.) contains run-specific data and lives outside of Git tracking.

## Getting Started

1. Clone the repository onto DTU HPC (e.g., `/work3/xxx`).
2. Update the hard-coded project paths inside the scripts so they match your own workspace layout.
3. Make sure the referenced Conda environments exist. The submission scripts expect environments such as `kneaddata-0.12.3` and `pytools` to be available under `/work3/xxx/miniconda3`.

## Submitting Jobs

The scripts in `hpc_slurm/` target the LSF scheduler on DTU HPC.

```bash
# Example: submit KneadData array job
bsub < hpc_slurm/kneaddata_metagenomics_80.sh
```

Each script includes:

- Job metadata (`#BSUB` directives) you can tune for core counts, memory, wall-clock limits, and queue.
- Environment bootstrapping that adds Conda to the `PATH`, sources `conda.sh`, and activates the right environment.
- Tool-specific sections that set input/output folders within `/work3/xxx` and then launch the workload.

Logs and outputs are written under the project directories referenced in the script (`/work3/xxx/kneaddata_project/...` by default).

## Python Utilities

Use the helpers in `hpc_python/` from an interactive login node or within the batch scripts.

- `unpack_merge_fastq.py` – Extracts tarred sequencing drops, merges lanes into paired FASTQ files, and prints a verification summary.
- `kneaddata_read_summary.py` – Collates KneadData reports across samples into a concise table.
- `merge_pairs_for_humann.py` – Prepares merged FASTQ pairs for HUMAnN runs.
- `read_quality_hist.py` – Generates quality score histograms from FASTQ files.

Activate `pytools` (or whichever environment has the required dependencies) before invoking them:

```bash
conda activate pytools
python hpc_python/unpack_merge_fastq.py
```

## Tips

- Before large submits, run a single-sample dry run by editing `#BSUB -J` and the sample list inside the script so you can verify output paths.
- Keep `samples.txt` in your project directories sorted and in sync with available FASTQ files; the array jobs rely on the line number to match `LSB_JOBINDEX`.
- When tool environments change (e.g., new KneadData version), update both the Conda environment name in the script and the downstream paths so the logs remain organized.

## HPC Tips & Tricks

### Logging In

Use SSH to reach the DTU HPC login node for light tasks (editing files, Git, staging jobs, data transfer):

```bash
ssh xxx@login1.hpc.dtu.dk
```

### Interactive Compute Session

Launch an interactive shell on a compute node so heavier work stays off the login node:

```bash
linuxsh
conda activate pytools
python /work3/xxx/hpc_python/unpack_merge_fastq.py
```

- Starts immediately without waiting in queue.
- Gives live feedback while you experiment or debug.
- Leave the session with `exit` once finished.

### Transfer Data To/From HPC

Use the DTU transfer node for large copy jobs. The example below mirrors a HUMAnN results folder to a mounted drive on your workstation:

```bash
scp -r xxx@transfer.gbar.dtu.dk:/work3/xxx/humann_project/SA_24_09_Humann_Run /mnt/g/SA_24_09_Metagenome_Alex
```

Swap in your own project path and local destination as needed.

### Check Storage Usage

Run the DTU helper script to see current and remaining quota on `/work3`:

```bash
getquota_work3.sh
```

### Monitor Jobs

Helpful LSF commands for tracking utilization and job states:

```bash
bstat -C    # Cluster-wide utilization
bstat -M    # Queue utilization (memory view)
bjobs       # Your active and pending jobs
```

Enjoy the cleaner front page!
