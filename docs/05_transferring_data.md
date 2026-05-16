# 05 - Transferring Data

This page explains how to move data between your laptop and DTU HPC.

## Use the Transfer Node for Large Data

Large transfers should not go through login nodes. DTU/DCC documents `transfer.gbar.dtu.dk` for large transfers; use the transfer host documented for your account.

Recommended SSH config alias:

```sshconfig
Host dtu-hpc-transfer
    HostName <transfer-host>
    User <dtu-user>
    IdentityFile <path-to-private-key>
    IdentitiesOnly yes
```

Then use:

```bash
ssh dtu-hpc-transfer
```

for transfer checks, and `scp`/`rsync` from your laptop for data movement.

## Where Raw Data Should Live

Use scratch/project storage for large data:

```text
/work3/<dtu-user>/<project>/raw_data
/work3/<dtu-user>/<project>/input_fastq
/work3/<dtu-user>/<project>/databases
/work3/<dtu-user>/<project>/results
```

Do not put raw FASTQs, `.tar.gz` deliveries, BAM/SAM files, databases, or full output folders in Git.

Good repo contents:

- scripts
- documentation
- small sample lists
- tiny test fixtures, if any
- environment specifications

Bad repo contents:

- raw sequencing data
- private keys
- passwords
- large databases
- generated logs from production runs
- full result folders

## Check File Sizes Before Transfer

On your laptop:

```bash
du -sh local_fastq_folder
find local_fastq_folder -type f | wc -l
```

On HPC:

```bash
du -sh /work3/<dtu-user>/<project>
getquota_work3.sh
```

Check quota before transferring a large dataset.

## `scp` Basics

Copy one local file to HPC:

```bash
scp sample_R1.fastq.gz dtu-hpc-transfer:/work3/<dtu-user>/<project>/input_fastq/
```

Copy one remote file to your laptop:

```bash
scp dtu-hpc-transfer:/work3/<dtu-user>/<project>/results/summary.tsv .
```

Copy a folder recursively:

```bash
scp -r local_folder dtu-hpc-transfer:/work3/<dtu-user>/<project>/
```

`scp` is simple, but if a large transfer is interrupted, `rsync` is usually better.

## `rsync` Basics

Copy a local folder's contents to HPC:

```bash
rsync -avP local_fastq_folder/ dtu-hpc-transfer:/work3/<dtu-user>/<project>/input_fastq/
```

Copy results from HPC to laptop:

```bash
rsync -avP dtu-hpc-transfer:/work3/<dtu-user>/<project>/results/ ./results/
```

Preview before doing a large transfer:

```bash
rsync -avP --dry-run local_fastq_folder/ dtu-hpc-transfer:/work3/<dtu-user>/<project>/input_fastq/
```

Important trailing slash rule:

| Source | Meaning |
| --- | --- |
| `folder/` | Copy the contents of `folder`. |
| `folder` | Copy the folder itself. |

## Transferring Many Files

For many files, use `rsync`:

```bash
rsync -avP --partial local_fastq_folder/ dtu-hpc-transfer:/work3/<dtu-user>/<project>/input_fastq/
```

Common excludes:

```bash
rsync -avP \
  --exclude "*.tmp" \
  --exclude ".DS_Store" \
  --exclude "__pycache__/" \
  local_folder/ dtu-hpc-transfer:/work3/<dtu-user>/<project>/local_folder/
```

For important data, use checksums or project-provided manifests if available:

```bash
sha256sum *.fastq.gz > checksums.sha256
sha256sum -c checksums.sha256
```

## Do Not Move Huge Files Through VS Code

VS Code is for editing and small file inspection. Do not drag-and-drop large FASTQ folders through the VS Code file browser.

Use terminal transfer tools:

- `rsync` for folders and resumable transfers
- `scp` for a small number of files
- project-specific data transfer tools if your group uses them

## After Transfer

On HPC:

```bash
cd /work3/<dtu-user>/<project>
du -sh input_fastq
find input_fastq -type f | head
find input_fastq -type f | wc -l
```

Check that filenames match script expectations:

```bash
ls input_fastq/*_R1.fastq.gz | head
ls input_fastq/*_R2.fastq.gz | head
```

If your files use different naming, update the scripts or rename files deliberately.

## Git Safety

Before committing:

```bash
git status
```

If you see large data files listed, stop. Add or adjust `.gitignore`, move data outside the repo, and commit only reusable code/docs/configuration.

The repository already ignores common large data patterns, but do not rely on `.gitignore` alone. Keep project data outside the repo folder when possible.
