# 02 - SSH and VS Code Remote-SSH

This page explains how to connect from your laptop to DTU HPC and use VS Code safely.

Use placeholders:

- `<dtu-user>`: your DTU username, for example `sXXXXXX` or your DTU initials
- `<login-host>`: the login host documented for your account, for example `login1.hpc.dtu.dk`
- `<transfer-host>`: the transfer host documented for your account, for example `transfer.gbar.dtu.dk`
- `<project>`: your project name
- `<path-to-private-key>`: local path to your SSH private key

Check official DTU HPC documentation for current hostnames, VPN requirements, and access rules.

## What SSH Is

SSH is an encrypted way to log in from your laptop to another machine. In this workflow:

```text
local laptop terminal or VS Code
  |
  | SSH
  v
DTU HPC login node
```

After SSH connects, commands run on the remote HPC login node, not on your laptop.

VS Code Remote-SSH uses the same SSH connection. The editor window is local, but the files and terminal are remote.

## Passwords, Keys, and Prompts

| Thing | Meaning |
| --- | --- |
| DTU password | Authenticates your DTU account when password login is used. |
| SSH private key | Secret file on your laptop. Never share or commit it. |
| SSH public key | Matching `.pub` file. This can be installed on HPC. |
| Key passphrase | Password that unlocks your private key locally. It is not your DTU password. |
| Host key | Server identity. If it changes unexpectedly, stop and verify DTU guidance. |

You may see different prompts:

- DTU password prompt: asks for your DTU account password.
- Key passphrase prompt: unlocks the private key on your laptop.
- Host authenticity prompt: appears the first time you connect to a host.

## Check Whether You Can Log In

From your laptop:

```bash
ssh <dtu-user>@<login-host>
```

Example shape:

```bash
ssh <dtu-user>@login1.hpc.dtu.dk
```

If you are outside the DTU network, connect to the DTU VPN or remote-access route required for your account before trying SSH.

Once logged in:

```bash
hostname
pwd
whoami
exit
```

## Generate an SSH Key Locally

Run this on your laptop, not on HPC.

First inspect existing keys so you do not overwrite something important:

```bash
ls -la ~/.ssh
```

Generate a new key:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -f ~/.ssh/dtu_hpc_ed25519 -C "<dtu-user>@dtu-hpc"
```

When prompted:

1. Confirm the filename if it is correct.
2. Enter a passphrase.
3. Re-enter the passphrase.

This creates:

```text
~/.ssh/dtu_hpc_ed25519      # private key: keep secret
~/.ssh/dtu_hpc_ed25519.pub  # public key: install on HPC
```

Windows users can run equivalent commands in PowerShell, Git Bash, or WSL if OpenSSH is installed. The key usually lives under `C:\Users\<you>\.ssh\`.

## Install the Public Key on HPC

Use the method documented for your DTU account. If `ssh-copy-id` is available:

```bash
ssh-copy-id -i ~/.ssh/dtu_hpc_ed25519.pub <dtu-user>@<login-host>
```

If that fails, use a manual method. On your laptop, print the public key:

```bash
cat ~/.ssh/dtu_hpc_ed25519.pub
```

Copy the single output line. It should begin with `ssh-ed25519`.

On HPC:

```bash
ssh <dtu-user>@<login-host>
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
```

Paste the public key as one line, save, then run:

```bash
chmod 600 ~/.ssh/authorized_keys
exit
```

Never paste the private key. The private key is the file without `.pub`.

Test key login:

```bash
ssh -i ~/.ssh/dtu_hpc_ed25519 <dtu-user>@<login-host>
```

## Recommended `~/.ssh/config`

Create or edit `~/.ssh/config` on your laptop:

```sshconfig
Host dtu-hpc-login
    HostName <login-host>
    User <dtu-user>
    IdentityFile ~/.ssh/dtu_hpc_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 5

Host dtu-hpc-transfer
    HostName <transfer-host>
    User <dtu-user>
    IdentityFile ~/.ssh/dtu_hpc_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 5
```

What each line means:

| Line | Meaning |
| --- | --- |
| `Host dtu-hpc-login` | Short alias you type locally. |
| `HostName <login-host>` | Real DTU HPC hostname. |
| `User <dtu-user>` | Username to send to SSH. |
| `IdentityFile ...` | Private key on your laptop. |
| `IdentitiesOnly yes` | Use this key instead of trying many keys. |
| `ServerAliveInterval` | Sends keepalive packets. Helpful on unstable networks. |
| `ServerAliveCountMax` | Controls how many missed keepalives before disconnect. |

Set permissions:

```bash
chmod 600 ~/.ssh/config
```

Test:

```bash
ssh dtu-hpc-login
```

If this fails, fix terminal SSH before opening VS Code.

## Connect With VS Code Remote-SSH

1. Install VS Code on your laptop.
2. Install the `Remote - SSH` extension.
3. Confirm this works in a normal terminal:

   ```bash
   ssh dtu-hpc-login
   ```

4. Open VS Code.
5. Open the Command Palette.
6. Run `Remote-SSH: Connect to Host...`.
7. Choose `dtu-hpc-login`.
8. If asked, select your SSH config file.
9. If asked for a passphrase, enter the key passphrase.
10. Wait for the remote server install.
11. Confirm the lower-left VS Code indicator says something like `SSH: dtu-hpc-login`.

If the server install fails, see troubleshooting below.

## Open the Correct Project Folder

In the remote VS Code window:

1. Choose `File > Open Folder`.
2. Enter or browse to your project path, for example:

   ```text
   /work3/<dtu-user>/<project>/dtuhpc_job_scripts
   ```

3. Open the folder.
4. In the integrated terminal, verify:

   ```bash
   hostname
   pwd
   git status
   ```

Do not open all of `/work3`, raw data folders, database folders, or huge result folders in VS Code. It can make file browsing and indexing very slow.

## Choose the Remote Python Interpreter

In the remote VS Code window:

1. Open the Command Palette.
2. Run `Python: Select Interpreter`.
3. Choose the interpreter inside the intended remote Conda environment.

Verify in the integrated terminal:

```bash
conda activate <env-name>
which python
python --version
```

If VS Code and the terminal disagree, trust the command you will use in the terminal or LSF script. Make the interpreter match that environment.

## Use the Integrated Terminal Safely

The integrated terminal runs on the remote login node unless you explicitly start `linuxsh` or submit a job.

Safe login-node commands:

```bash
pwd
hostname
git status
ls hpc_lsf
mkdir -p logs
bsub < hpc_lsf/kneaddata_metagenomics_80.sh
bjobs
bstat
```

Unsafe login-node commands for real data:

```bash
kneaddata --threads 8 ...
humann --threads 8 ...
metaphlan large_sample.fastq ...
python hpc_python/unpack_merge_fastq.py
jupyter lab
```

Before pressing Enter, ask:

- Will this read/write large FASTQ files?
- Will it use many cores or many GB of RAM?
- Will it run for more than a few minutes?
- Is it a real analysis instead of a tiny test?

If yes, use `linuxsh` for a tiny test or `bsub` for real work.

## Troubleshooting

### `Permission denied (publickey)`

Check what SSH will use:

```bash
ssh -G dtu-hpc-login | less
ssh -vvv dtu-hpc-login
```

Check files:

```bash
ls -l ~/.ssh/dtu_hpc_ed25519 ~/.ssh/dtu_hpc_ed25519.pub ~/.ssh/config
```

Likely causes:

- wrong `User`
- wrong `HostName`
- public key not installed on HPC
- wrong `IdentityFile`
- private key permissions too open
- trying from outside DTU without required VPN

Fix local permissions:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config ~/.ssh/dtu_hpc_ed25519
```

### Host Key Verification Failed

Do not blindly delete host keys. A host-key warning can be harmless after an official rotation, but it can also indicate a security problem.

Steps:

1. Stop.
2. Check official DTU HPC host-key guidance or support notes.
3. Only after confirming the change is expected, remove the stale entry from `~/.ssh/known_hosts`.

### VS Code Server Fails to Install

First verify terminal SSH:

```bash
ssh dtu-hpc-login
```

Then check home quota and server size:

```bash
df -h ~
du -sh ~/.vscode-server 2>/dev/null
getquota_zhome.sh
```

Other fixes:

- open a smaller folder
- disable heavy remote extensions
- check the VS Code `Remote - SSH` output panel
- remove only a failed server version if safe:

  ```bash
  rm -rf ~/.vscode-server/bin/<failed-version>
  ```

If the server binary itself fails, check official DTU HPC documentation for current VS Code compatibility notes.

### `conda: command not found`

Conda may not be initialized in non-interactive shells.

Try:

```bash
source /work3/<dtu-user>/<project>/miniconda3/etc/profile.d/conda.sh
conda activate <env-name>
```

Use the actual path to your Conda installation. In LSF scripts, source `conda.sh` before `conda activate`.

### Wrong Python Interpreter

Symptoms:

- imports fail in VS Code but work in terminal
- VS Code linting points to the wrong packages
- `python --version` differs between VS Code and terminal

Fix:

```bash
conda activate <env-name>
which python
```

Then select that interpreter in VS Code.

### Slow Remote File Browsing

Likely causes:

- you opened `/work3` instead of the repo folder
- raw data or result folders are inside the VS Code workspace
- extensions are indexing many files

Fixes:

- open only `/work3/<dtu-user>/<project>/dtuhpc_job_scripts`
- keep raw data and results outside the repo folder
- use terminal commands for large trees
- add large folders to VS Code excludes if needed

### VPN or Network Problems

Symptoms:

- connection times out
- hostname cannot be resolved
- works on campus but not at home

Checks:

```bash
ping <login-host>
ssh -vvv dtu-hpc-login
```

If remote access requires DTU VPN for your account, connect VPN first. Check official DTU documentation for the current VPN client and setup.
