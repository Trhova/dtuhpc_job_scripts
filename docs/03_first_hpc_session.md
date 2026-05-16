# 03 - First HPC Session

This tutorial walks through a safe first DTU HPC session. It submits a tiny LSF job before touching the metagenomics scripts.

Use placeholders:

- `<dtu-user>`: your DTU username
- `<project>`: your project folder name
- `<repo-url>`: URL for this repository

## 1. Connect to DTU Network or VPN

If you are off campus, connect to the DTU VPN or remote-access method required for your account. Check official DTU documentation for current setup.

## 2. SSH Into a Login Node

From your laptop:

```bash
ssh dtu-hpc-login
```

Or without an SSH config alias:

```bash
ssh <dtu-user>@login1.hpc.dtu.dk
```

## 3. Check Where You Are

Run:

```bash
hostname
whoami
pwd
date
```

Interpretation:

- `hostname` should be a DTU HPC host, not your laptop.
- `whoami` should show your DTU username.
- `pwd` shows your current remote directory.

## 4. Check Storage and Quota

Home quota:

```bash
getquota_zhome.sh
cd ~ && du -h --max-depth=1 .
```

Scratch/project storage:

```bash
ls /work3
getquota_work3.sh
```

If you do not have scratch space, follow the official DTU HPC request process.

## 5. Create a Project Folder

Use your approved scratch/project path. Example:

```bash
mkdir -p /work3/<dtu-user>/<project>
cd /work3/<dtu-user>/<project>
pwd
```

Keep raw data, databases, Conda environments, logs, and outputs under project/scratch storage, not in your 30 GB home directory.

## 6. Clone This Repo

```bash
cd /work3/<dtu-user>/<project>
git clone <repo-url> dtuhpc_job_scripts
cd dtuhpc_job_scripts
```

Inspect:

```bash
ls
ls hpc_lsf
ls hpc_python
```

## 7. Open the Repo in VS Code

From your laptop, connect with VS Code Remote-SSH to `dtu-hpc-login`.

Open this folder in the remote VS Code window:

```text
/work3/<dtu-user>/<project>/dtuhpc_job_scripts
```

In the integrated terminal:

```bash
hostname
pwd
git status
```

## 8. Inspect Scripts Without Running Them

Read the scripts first:

```bash
sed -n '1,120p' hpc_lsf/kneaddata_metagenomics_80.sh
sed -n '1,120p' hpc_lsf/humann38_metagenomics80_array.sh
```

Look for:

- `#BSUB -J` array size
- `#BSUB -o` and `#BSUB -e` log paths
- `PROJECT_DIR`
- `RAW_DIR` or `INPUT_DIR`
- `OUTPUT_DIR` or `OUT_DIR`
- database paths
- Conda activation paths

Do not submit these scripts until you have replaced project-specific values.

## 9. Start `linuxsh` for a Light Test

Use `linuxsh` for small interactive checks:

```bash
linuxsh
hostname
pwd
python --version
exit
```

Use `linuxsh` for tiny tests only. Use `bsub` for real work.

## 10. Submit a Tiny LSF Test Job

Create a safe test script:

```bash
mkdir -p logs
nano hello_lsf.sh
```

Paste:

```bash
#!/bin/sh
#BSUB -q hpc
#BSUB -J hello_lsf
#BSUB -n 1
#BSUB -R "rusage[mem=1GB]"
#BSUB -M 1GB
#BSUB -W 00:05
#BSUB -oo logs/hello_%J.out
#BSUB -eo logs/hello_%J.err

echo "Running on:"
hostname
echo "Started:"
date
echo "Working directory:"
pwd
echo "Hello from LSF"
```

Submit:

```bash
bsub < hello_lsf.sh
```

## 11. Monitor the Job

```bash
bjobs
bstat
```

If you have a job ID:

```bash
bjobs -l <job-id>
bpeek <job-id>
```

Possible states:

- `PEND`: waiting
- `RUN`: running
- `DONE`: finished successfully
- `EXIT`: failed or killed

## 12. Inspect Log Files

```bash
ls -lh logs
cat logs/hello_*.out
cat logs/hello_*.err
```

Expected output includes:

- a compute-node hostname
- dates
- `Hello from LSF`

If `logs/hello_*.err` is empty, that is normal for a successful tiny job.

## 13. Clean Up the Test

```bash
rm hello_lsf.sh
rm logs/hello_*.out logs/hello_*.err
```

Do not clean up real logs until you are sure you no longer need them.

## 14. Next Step

After this works:

1. Read [LSF Jobs and `bsub`](04_lsf_jobs_and_bsub.md).
2. Read [Using This Repo for Metagenomics](06_using_this_repo_for_metagenomics.md).
3. Personalize scripts before running real data.
