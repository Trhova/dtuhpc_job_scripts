# DTU HPC Metagenomics Workflow Guide

This repository is a beginner-friendly guide and script collection for running metagenomics work on DTU HPC. It is not only a place to store job scripts: it is meant to explain the daily workflow from laptop to DTU HPC, from editing code to submitting LSF jobs, and from raw sequencing files to KneadData/HUMAnN outputs.

The included scripts are useful templates, but they are still project-specific in places. Before running anything, read [Using This Repo for Metagenomics](docs/06_using_this_repo_for_metagenomics.md) and replace every project path, sample count, database path, and Conda environment with your own values.

## Who This Repo Is For

This repo is for DTU students, employees, and collaborators with DTU HPC access who need a practical starting point for:

- connecting to DTU HPC from a laptop
- setting up SSH keys and VS Code Remote-SSH
- understanding login nodes, transfer nodes, interactive nodes, and LSF jobs
- adapting metagenomics scripts for KneadData, MetaPhlAn, and HUMAnN
- keeping data, logs, code, and results in sensible places

If your department or group has a special cluster, queue, storage area, or access route, use that local guidance together with this repo. When in doubt, check the official DTU HPC documentation.

## What You Will Learn

After reading the guide, you should understand:

1. what DTU HPC is and why it uses a scheduler
2. how to connect from your laptop with SSH
3. how SSH keys, public keys, private keys, and `~/.ssh/config` fit together
4. how to use VS Code Remote-SSH without overloading login nodes
5. where to put code, raw data, databases, logs, and results
6. when to use `linuxsh` for light interactive work
7. when and how to submit real jobs with `bsub`
8. how to monitor, inspect, cancel, and debug jobs
9. how to move data with the transfer node
10. how the included metagenomics scripts fit into a raw-data-to-results workflow

## Start Here

```text
Laptop
  |
  | 1. Read the mental model
  v
docs/01_hpc_mental_model.md
  |
  | 2. Set up SSH and VS Code
  v
docs/02_ssh_and_vscode_remote.md
  |
  | 3. Do a first safe HPC session
  v
docs/03_first_hpc_session.md
  |
  | 4. Learn LSF job scripts
  v
docs/04_lsf_jobs_and_bsub.md
  |
  | 5. Learn data transfer
  v
docs/05_transferring_data.md
  |
  | 6. Adapt this repo's metagenomics scripts
  v
docs/06_using_this_repo_for_metagenomics.md
```

For the shortest path, read these in order:

1. [HPC Mental Model](docs/01_hpc_mental_model.md)
2. [SSH and VS Code Remote-SSH](docs/02_ssh_and_vscode_remote.md)
3. [First HPC Session](docs/03_first_hpc_session.md)
4. [LSF Jobs and `bsub`](docs/04_lsf_jobs_and_bsub.md)
5. [Transferring Data](docs/05_transferring_data.md)
6. [Using This Repo for Metagenomics](docs/06_using_this_repo_for_metagenomics.md)

## Repository Layout

| Path | What it is for |
| --- | --- |
| `README.md` | This overview and entry point. |
| `docs/01_hpc_mental_model.md` | Plain-language explanation of DTU HPC concepts. |
| `docs/02_ssh_and_vscode_remote.md` | SSH keys, SSH config, VS Code Remote-SSH, and troubleshooting. |
| `docs/03_first_hpc_session.md` | Step-by-step tutorial from SSH login to a tiny `bsub` job. |
| `docs/04_lsf_jobs_and_bsub.md` | Detailed explanation of `#BSUB` scripts, arrays, resources, logs, and debugging. |
| `docs/05_transferring_data.md` | `scp`, `rsync`, transfer node usage, data placement, and Git safety. |
| `docs/06_using_this_repo_for_metagenomics.md` | How the included KneadData/HUMAnN/Python scripts fit together. |
| `hpc_lsf/` | LSF (`#BSUB`) job script templates. See [hpc_lsf/README.md](hpc_lsf/README.md). |
| `hpc_python/` | Python helper scripts. See [hpc_python/README.md](hpc_python/README.md). |
| `envs/` | Tracked Conda environment exports, if present. See [envs/README.md](envs/README.md). |
| `thesis_templates/` | Optional thesis templates. Not required for HPC workflows. |

## Beginner Mental Model of DTU HPC

An HPC cluster is a shared collection of servers. You do not run heavy analyses directly where you log in. The usual pattern is:

1. Your laptop connects to a login node with SSH.
2. You edit files, check paths, and submit work from the login node.
3. LSF, the scheduler, decides when and where your job runs.
4. The job runs later on a compute node.
5. Logs and outputs are written to shared storage.
6. Large input and output transfers go through a transfer node.

Think of the login node as a front desk, not a laboratory bench. It is for coordination. Real analysis belongs in LSF jobs.

DTU/DCC documentation states that DTU HPC uses LSF, provides a general central cluster for DTU staff and students, gives each user a 30 GB backed-up home directory, and offers scratch storage such as `/work3` on request. Scratch is for active computation and is not a backup. Check official DTU HPC documentation for current hardware, hostnames, quotas, and request procedures.

## Quickstart: Laptop to First Job

This quickstart assumes you already have DTU HPC access. If you do not, start with DTU HPC documentation or your department's onboarding.

1. Connect to the DTU network or VPN if required.
2. Test password login:

   ```bash
   ssh <dtu-user>@login1.hpc.dtu.dk
   ```

3. Generate an SSH key locally and add an SSH config alias using [SSH and VS Code Remote-SSH](docs/02_ssh_and_vscode_remote.md).
4. Connect from VS Code using `Remote-SSH: Connect to Host...`.
5. Open or create a project folder on scratch/project storage:

   ```text
   /work3/<dtu-user>/<project>
   ```

6. Clone this repo on HPC:

   ```bash
   cd /work3/<dtu-user>/<project>
   git clone <repo-url> dtuhpc_job_scripts
   cd dtuhpc_job_scripts
   ```

7. Submit a tiny test job, not a metagenomics production job yet:

   ```bash
   mkdir -p logs
   cat > hello_lsf.sh <<'EOF'
   #!/bin/sh
   #BSUB -q hpc
   #BSUB -J hello_lsf
   #BSUB -W 00:05
   #BSUB -n 1
   #BSUB -R "rusage[mem=1GB]"
   #BSUB -M 1GB
   #BSUB -oo logs/hello_%J.out
   #BSUB -eo logs/hello_%J.err

   hostname
   date
   echo "Hello from an LSF job"
   EOF

   bsub < hello_lsf.sh
   bjobs
   ```

8. Inspect the logs when the job finishes:

   ```bash
   ls logs
   cat logs/hello_*.out
   ```

For a slower step-by-step version, follow [First HPC Session](docs/03_first_hpc_session.md).

## How This Repo's Scripts Fit Into the Workflow

The metagenomics path is:

| Stage | Purpose | Main files |
| --- | --- | --- |
| Raw data staging | Put raw FASTQs or sequencing archives on scratch/project storage. | `docs/05_transferring_data.md` |
| Unpack/merge FASTQs | Convert delivered archives/lanes into paired FASTQs. | `hpc_lsf/unpack_merge_fastq.sh`, `hpc_python/unpack_merge_fastq.py` |
| KneadData | Remove host/contaminant reads and produce cleaned sample outputs. | `hpc_lsf/kneaddata_*.sh` |
| HUMAnN input prep | Merge KneadData paired reads into files expected by HUMAnN scripts. | `hpc_python/merge_pairs_for_humann.py` |
| HUMAnN | Profile pathways/gene families with HUMAnN/MetaPhlAn. | `hpc_lsf/humann38_*.sh` |
| Postprocess | Normalize, regroup, and merge tables. | `hpc_python/humann_postprocess.py`, `hpc_python/humann_merge_tables.py` |
| Summaries | Summarize read counts and QC outputs. | `hpc_python/kneaddata_read_summary.py`, `hpc_python/read_quality_hist.py` |

The current scripts are templates extracted from a real project. They contain assumptions about paths, sample names, database locations, Conda environments, and array sizes. Do not submit them unchanged.

## Safety Warnings

- **Login nodes:** Do not run KneadData, HUMAnN, large Python processing, Jupyter notebooks, or large file indexing directly on login nodes.
- **Data size:** Raw FASTQs, databases, `.tar.gz` deliveries, BAM/SAM files, and result folders can be huge. Keep them out of Git.
- **Quotas:** Home storage is limited. A full home directory can break VS Code server installs, shell startup, Conda caches, and small writes. Check quota before large work.
- **Scratch:** Scratch/project storage is for active work and is usually not backed up. Copy important final results to an approved backed-up location.
- **Secrets:** Never commit SSH private keys, passwords, tokens, or credentials. Only public keys (`*.pub`) are intended to be copied to a server.
- **Historical paths:** If you see a personal path in a script, replace it with `/work3/<dtu-user>/<project>/...` or your approved project path before use.

## Detailed Docs

- [01 - HPC Mental Model](docs/01_hpc_mental_model.md)
- [02 - SSH and VS Code Remote-SSH](docs/02_ssh_and_vscode_remote.md)
- [03 - First HPC Session](docs/03_first_hpc_session.md)
- [04 - LSF Jobs and `bsub`](docs/04_lsf_jobs_and_bsub.md)
- [05 - Transferring Data](docs/05_transferring_data.md)
- [06 - Using This Repo for Metagenomics](docs/06_using_this_repo_for_metagenomics.md)
- [LSF script catalog](hpc_lsf/README.md)
- [Python helper catalog](hpc_python/README.md)
- [Conda environment notes](envs/README.md)

## Official DTU References

Check official DTU HPC documentation for current details:

- DTU/DCC access guide: <https://www.hpc.dtu.dk/?page_id=2501>
- DTU/DCC LSF jobs: <https://www.hpc.dtu.dk/?page_id=1416>
- DTU/DCC job monitoring: <https://www.hpc.dtu.dk/?page_id=1519>
- DTU/DCC storage: <https://www.hpc.dtu.dk/?page_id=59>
- DTU/DCC disk space and quota FAQ: <https://www.hpc.dtu.dk/?page_id=927>
- DTU/DCC LSF 10 overview: <https://www.hpc.dtu.dk/?page_id=2513>
- DTU/DCC Central DTU HPC Cluster: <https://www.hpc.dtu.dk/?page_id=2520>
