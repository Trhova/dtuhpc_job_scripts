# 01 - DTU HPC Mental Model

This page explains the concepts behind DTU HPC before you run commands. If you are new to HPC, read this first.

## What an HPC Cluster Is

An HPC cluster is a shared computing system made of many servers. Instead of running large analyses on your laptop, you upload or stage files on shared storage and ask the cluster to run the work.

The key difference from a normal server is that many people share it. A scheduler decides when jobs run and which compute nodes they use.

For metagenomics, HPC is useful because workflows can involve:

- large FASTQ files
- many samples
- large host and microbial reference databases
- tools that use multiple CPU cores
- long runtimes
- many output and log files

## The Main Pieces

```text
Your laptop
  |
  | SSH / VS Code Remote-SSH
  v
Login node  ---- bsub job request ---->  LSF scheduler
  |                                      |
  | small commands                       | starts job when resources are available
  v                                      v
Shared storage <-------------------- Compute node
  ^
  |
Transfer node for large scp/rsync transfers
```

## Login Nodes

A login node is the front door to the cluster. You connect to it with SSH.

Use login nodes for:

- editing files
- using Git
- checking paths with `ls`, `pwd`, and `du`
- submitting jobs with `bsub`
- monitoring jobs with `bjobs` or `bstat`
- reading small log files

Do not use login nodes for:

- KneadData on real samples
- HUMAnN on real samples
- large Python processing
- unpacking large sequencing deliveries
- Jupyter notebooks on real data
- CPU-heavy, memory-heavy, or I/O-heavy work

Why this matters: login nodes are shared by many users and are sized for coordination. Heavy commands can slow down SSH, editors, and job submission for everyone, and administrators may kill disruptive processes.

## Compute Nodes

Compute nodes are where real work runs. You normally do not SSH to a compute node directly. You submit a job script to LSF, and LSF starts the job on a compute node when resources are available.

Use compute jobs for:

- KneadData
- MetaPhlAn
- HUMAnN
- large FASTQ merging
- large summaries
- repeated work across many samples

## Transfer Nodes

Transfer nodes are for moving data. DTU/DCC documents `transfer.gbar.dtu.dk` for large data transfer; use the transfer host documented for your account.

Use transfer nodes for:

- `rsync` of raw FASTQ folders
- downloading result folders
- moving many files without loading login nodes

Do not use transfer nodes for compute workloads.

## Interactive Nodes and `linuxsh`

`linuxsh` starts an interactive application-node shell from a login session.

Use `linuxsh` when you need a prompt for a small test:

- activate a Conda environment
- run `tool --help`
- test one tiny input file
- check whether a database path works
- debug a command before converting it to an LSF script

Use `bsub` instead when work should:

- survive disconnects
- run longer than a short test
- use real FASTQ files
- use many CPU cores
- use substantial memory
- repeat across samples

## Jobs and Schedulers

A job is a request: "run this script with these resources." DTU HPC uses LSF, so the command to submit a job is:

```bash
bsub < job_script.sh
```

`bsub` does not run the script in your current terminal. It sends the script to LSF. LSF checks queue policy and requested resources, then starts the job on a compute node when resources are available.

Common job states:

| State | Meaning |
| --- | --- |
| `PEND` | The job is waiting for resources or policy conditions. |
| `RUN` | The job is running on a compute node. |
| `DONE` | The job ended successfully. |
| `EXIT` | The job failed, was killed, or exited with an error. |

## LSF and `bsub`

LSF job scripts use `#BSUB` lines at the top. These lines tell LSF what resources you want.

Example:

```bash
#!/bin/sh
#BSUB -q hpc
#BSUB -J example
#BSUB -n 4
#BSUB -R "rusage[mem=4GB]"
#BSUB -M 5GB
#BSUB -W 02:00
#BSUB -oo logs/example_%J.out
#BSUB -eo logs/example_%J.err

hostname
date
```

## Queues, Cores, Memory, and Wall Time

| Term | Plain-language meaning |
| --- | --- |
| Queue | The resource pool or policy class. Many examples use `hpc`; check official docs for available queues. |
| Core/slot | A CPU execution slot. If a tool uses `--threads 8`, the job often requests `#BSUB -n 8`. |
| Memory request | The RAM you ask LSF to reserve for scheduling. |
| Memory limit | The RAM limit that may kill a job if exceeded. Confirm DTU's current interpretation in official docs. |
| Wall time | Maximum runtime. If the job runs longer, LSF may stop it. |

Requesting too little memory can kill jobs. Requesting far too much memory or wall time can make jobs wait longer.

## Storage Areas

| Storage | Use for | Avoid |
| --- | --- | --- |
| Home `~` | SSH config, source code, small notes, small important files. DTU/DCC documents a 30 GB backed-up home quota. | Raw FASTQs, big databases, large Conda envs, large outputs. |
| Scratch/project storage such as `/work3/<dtu-user>/<project>` | Raw data, databases, Conda envs, logs, temporary files, outputs. | Treating it as a backup. Scratch is usually not backed up. |
| Local laptop | Local copies of final summaries, reports, and code clones. | Only copy what you are allowed to store locally. |

Check quotas before large work:

```bash
getquota_zhome.sh
getquota_work3.sh
du -sh /work3/<dtu-user>/<project>
```

If you need scratch space, follow the official DTU HPC request process. DTU/DCC documentation currently says to write to HPC support and explain why you need scratch space.

## Job Logs

Logs are not optional decoration. They are how you understand what happened.

Every production job should have:

- stdout log: normal messages and tool progress
- stderr log: warnings and errors
- job ID in the filename, usually `%J`
- array index in the filename for arrays, usually `%I`

Example:

```bash
#BSUB -oo logs/kneaddata_%I_%J.out
#BSUB -eo logs/kneaddata_%I_%J.err
```

For metagenomics jobs, useful log lines include:

```bash
echo "Sample: $SAMPLE_NAME"
echo "Input R1: $R1"
echo "Input R2: $R2"
echo "Output: $OUT_DIR/$SAMPLE_NAME"
date
```

## Rule of Thumb

Before pressing Enter on a login node, ask:

- Will this read or write large FASTQ files?
- Will it use more than one or two cores?
- Will it run for more than a few minutes?
- Will it use many GB of memory?
- Is it a full analysis rather than a tiny test?

If yes, do not run it on the login node. Use `linuxsh` for a tiny interactive test or `bsub` for real work.
