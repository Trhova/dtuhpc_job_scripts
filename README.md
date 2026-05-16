# DTU HPC Guide and Job Scripts

This repository is a practical guide for working on the DTU HPC/DCC LSF cluster, plus reusable job scripts and Python helpers for metagenomics workflows. It is meant to be safe to share: examples use placeholders such as `<dtu-user>`, `<project>`, and `<path-to-private-key>`.

## Start Here

| Need | Where to go |
| --- | --- |
| Connect from home or campus | [DTU HPC access guide](docs/dtu_hpc_guide.md#1-connect-to-dtu-hpc) |
| Set up VS Code SSH access and port forwarding | [VS Code and SSH tunnels](docs/dtu_hpc_guide.md#4-vs-code-remote-ssh-and-port-forwarding) |
| Submit and monitor LSF jobs | [Batch jobs with LSF](docs/dtu_hpc_guide.md#6-submit-and-monitor-lsf-jobs) |
| Adapt the included metagenomics scripts | [Repository scripts](#repository-scripts) |
| Check storage, modules, and etiquette | [Working on the cluster](docs/dtu_hpc_guide.md#5-working-on-the-cluster) |

## Quick Connection Pattern

1. Connect to the DTU network. From outside DTU, use DTU VPN/Cisco Secure Client if your account requires it.
2. SSH to a login node:

   ```bash
   ssh <dtu-user>@login1.hpc.dtu.dk
   ```

   P1 users may have a project-specific login node such as `login9.hpc.dtu.dk`; use the host given by your DTU/P1 onboarding material.

3. Keep login-node work light: edit files, use Git, stage data, and submit jobs.
4. Run compute-heavy work through LSF batch jobs or `linuxsh`, not directly on the login node.

## Repository Scripts

| Path | Description |
| --- | --- |
| `hpc_slurm/` | LSF (`#BSUB`) submission scripts for KneadData, HUMAnN, and FASTQ preparation. Despite the folder name, these are LSF scripts, not Slurm scripts. |
| `hpc_python/` | Python utilities for unpacking FASTQ archives, merging lanes, plotting QC summaries, and reporting KneadData/HUMAnN results. |
| `thesis_templates/` | General DTU thesis submission templates in Markdown and Word formats. |
| `docs/` | Outward-facing DTU HPC notes, including SSH, VPN, VS Code, storage, modules, and LSF examples. |

Everything else in a working HPC project area (`envs/`, `humann_project/`, `kneaddata_project/`, sequencing data, logs, etc.) should stay out of Git.

## Adapting the Scripts

1. Clone the repository onto DTU HPC, for example under `/work3/<dtu-user>/<project>/`.
2. Replace project-specific paths in `hpc_slurm/` with your own `/work1/<dtu-user>` or `/work3/<dtu-user>` paths.
3. Make sure the referenced Conda environments exist. Several scripts expect environments such as `kneaddata-0.12.3` and `pytools`.
4. Run a small single-sample test before submitting large arrays.

Example submit:

```bash
bsub < hpc_slurm/kneaddata_metagenomics_80.sh
```

Each submission script contains:

- `#BSUB` directives for queue, job name, cores, memory, wall time, logs, and arrays.
- Conda activation and environment setup.
- Input/output paths that should be reviewed before running.
- Tool-specific commands for KneadData, HUMAnN, or FASTQ preparation.

## Python Utilities

Activate the relevant environment before running a helper:

```bash
conda activate pytools
python hpc_python/unpack_merge_fastq.py
```

Available helpers:

- `unpack_merge_fastq.py` extracts tarred sequencing drops, merges lanes into paired FASTQ files, and prints a verification summary.
- `kneaddata_read_summary.py` collates KneadData reports across samples into a concise table.
- `merge_pairs_for_humann.py` prepares merged FASTQ pairs for HUMAnN runs.
- `read_quality_hist.py` generates quality score histograms from FASTQ files.
- `humann_postprocess.py` renormalizes per-sample HUMAnN tables and regroups CPM gene families to level-4 EC categories.
- `humann_merge_tables.py` gathers normalized outputs and MetaPhlAn profiles, then builds cohort-wide matrices under `humann_run/merged_tables/`.

## Useful Commands

```bash
# Enter an interactive application node for light testing
linuxsh

# Submit a job
bsub < path/to/job.sh

# Compact job status
bstat
bstat -C
bstat -M

# Native LSF job list
bjobs

# Remove a queued or running job
bkill <job-id>

# Check scratch quota on work3
getquota_work3.sh
```

## Sources

This guide links back to DTU/DCC documentation and the P1 DTU HPC guide where relevant. Start with:

- DTU/DCC access guide: <https://www.hpc.dtu.dk/?page_id=2501>
- DTU/DCC LSF batch jobs: <https://www.hpc.dtu.dk/?page_id=1416>
- DTU/DCC job monitoring: <https://www.hpc.dtu.dk/?page_id=1519>
- DTU/DCC storage: <https://www.hpc.dtu.dk/?page_id=59>
- DTU/DCC modules: <https://www.hpc.dtu.dk/?page_id=282>
- DTU network and VPN: <https://www.inside.dtu.dk/en/it-information-technology/it-access-and-network/netvaerk-og-vpn>
- P1 DTU HPC guide: <https://hpc.aicentre.dk/clusters/dtu-hpc/>
