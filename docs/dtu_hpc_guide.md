# DTU HPC Access Guide

This page collects the practical steps needed to connect to DTU HPC, work from VS Code, move data, and submit LSF jobs. It intentionally uses placeholders. Do not commit private SSH keys, passwords, tokens, raw sequencing data, or project-specific credentials.

## 1. Connect to DTU HPC

### Accounts

DTU students and employees can normally use their DTU credentials for HPC access. Visitors need a DTU guest account with the UNIX Databar service enabled by a DTU sponsor.

Use your DTU username exactly as issued. Usernames and passwords are case-sensitive.

### Network access

From the DTU network or DTU VPN:

```bash
ssh <dtu-user>@login1.hpc.dtu.dk
```

Other documented DTU/DCC login nodes include:

```text
login1.hpc.dtu.dk
login2.hpc.dtu.dk
login1.gbar.dtu.dk
login2.gbar.dtu.dk
```

P1 users should follow their project onboarding material. The P1 guide lists `login9.hpc.dtu.dk` for P1 DTU HPC access.

### From outside DTU

The DTU/DCC access guide notes that remote access outside DTU can require SSH-key authentication. The P1 guide additionally documents a VPN flow using Cisco Secure Client/AnyConnect and `vpn.dtu.dk`.

Typical pattern:

1. Install DTU-supported VPN software if required for your affiliation.
2. Connect to the DTU VPN.
3. SSH to the login node assigned to your account or project.
4. Use SSH keys for persistent access where allowed.

Generate a new key with a passphrase:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/<key-name>
```

Copy only the public key:

```bash
ssh-copy-id -i ~/.ssh/<key-name>.pub <dtu-user>@<login-node>
```

Then connect:

```bash
ssh -i ~/.ssh/<key-name> <dtu-user>@<login-node>
```

Never copy the private key into this repository. The private key is the file without `.pub`.

## 2. Recommended SSH Config

Put host aliases in `~/.ssh/config` on your own machine:

```sshconfig
Host dtu-hpc
    HostName login1.hpc.dtu.dk
    User <dtu-user>
    IdentityFile ~/.ssh/<key-name>
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 5

Host dtu-hpc-p1
    HostName login9.hpc.dtu.dk
    User <dtu-user>
    IdentityFile ~/.ssh/<key-name>
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 5
```

Use only the alias that matches your access. Test it:

```bash
ssh dtu-hpc
```

## 3. SSH Port Tunnels

Port forwarding is useful when a process on HPC exposes a local web service, for example Jupyter, RStudio Server, TensorBoard, MLflow, or a development server. The tunnel maps a local port on your laptop to a port reachable from the SSH session.

Basic local tunnel:

```bash
ssh -L <local-port>:localhost:<remote-port> dtu-hpc
```

Example for a Jupyter server running on the remote side at port `8888`:

```bash
ssh -L 8888:localhost:8888 dtu-hpc
```

Then open this on your laptop:

```text
http://localhost:8888
```

For long-running or resource-heavy services, start the service from an interactive node or a batch allocation rather than directly on the login node.

## 4. VS Code Remote SSH and Port Forwarding

DTU/DCC has stated that the VS Code Remote extension is not officially supported on the DCC clusters. Many users still use it for editing and lightweight workflows, but keep the login node clean: do not run heavy analyses, indexing, language servers, or notebooks on the login node.

### Install locally

On your laptop:

1. Install Visual Studio Code.
2. Install the `Remote - SSH` extension.
3. Add a host alias in `~/.ssh/config`, as shown above.
4. In VS Code, run `Remote-SSH: Connect to Host...` and choose `dtu-hpc`.

### Open a project folder

After connecting, open a folder on HPC:

```text
/work3/<dtu-user>/<project>
```

Use VS Code for editing, Git, small terminal commands, and submitting jobs. Move compute work into LSF scripts.

### Forward a port in VS Code

If a remote process prints a URL such as `http://localhost:8888/?token=...`, forward the port through VS Code:

1. Connect to `dtu-hpc` with Remote SSH.
2. Open the VS Code `Ports` view.
3. Click `Forward a Port`.
4. Enter the remote port, for example `8888`.
5. Open the forwarded local URL in your browser.

Equivalent SSH config entry:

```sshconfig
Host dtu-hpc-jupyter
    HostName login1.hpc.dtu.dk
    User <dtu-user>
    IdentityFile ~/.ssh/<key-name>
    IdentitiesOnly yes
    LocalForward 8888 localhost:8888
```

Connect with:

```bash
ssh dtu-hpc-jupyter
```

### Safer Jupyter pattern

Use an interactive shell first:

```bash
ssh dtu-hpc
linuxsh
cd /work3/<dtu-user>/<project>
conda activate <env-name>
jupyter lab --no-browser --ip=127.0.0.1 --port=8888
```

Then forward port `8888` from your local machine or from the VS Code Ports view. If the interactive node prints a different hostname, use the exact forwarding route recommended by DTU support for your allocation.

## 5. Working on the Cluster

### Login nodes

Use login nodes for:

- Editing files.
- Git operations.
- Small file checks.
- Submitting jobs.
- Monitoring jobs.

Do not run heavy CPU, memory, GPU, or large I/O work on login nodes.

### Interactive node

DTU/DCC documents `linuxsh` as a way to move from a login node to an interactive application node:

```bash
linuxsh
```

This is useful for small tests, environment setup, and commands that should not run on the login node. It is still a shared environment, so use batch jobs for real workloads.

### Storage

Common DTU/DCC storage locations:

| Location | Use |
| --- | --- |
| `~` | Home directory. Backed up, but quota-limited. Good for code, configs, and small results. |
| `/work1/<dtu-user>` | Scratch/project work area where available. Not backed up. |
| `/work3/<dtu-user>` | Scratch/project work area where available. Not backed up. |
| `/dtu/p1/` | Additional P1 storage documented by the P1 guide. Use only if you have access. |

Check home usage:

```bash
cd ~ && du -h --max-depth=1 .
```

Check `/work3` quota if available:

```bash
getquota_work3.sh
```

Scratch filesystems are for active HPC work and are not backups. Keep irreplaceable data somewhere backed up.

### Modules

DTU/DCC uses environment modules for software:

```bash
module list
module avail
module load <module-name>
module unload <module-name>
module show <module-name>
```

Batch jobs start from a clean environment, so load required modules inside the job script before running your program.

## 6. Submit and Monitor LSF Jobs

DTU/DCC uses IBM Spectrum LSF on the documented LSF 10 cluster. A minimal job script:

```bash
#!/bin/sh
#BSUB -q hpc
#BSUB -J example_job
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -M 5GB
#BSUB -W 02:00
#BSUB -oo logs/example_%J.out
#BSUB -eo logs/example_%J.err

cd /work3/<dtu-user>/<project>
module load <module-name>
source /work3/<dtu-user>/miniconda3/etc/profile.d/conda.sh
conda activate <env-name>

python script.py --input input.txt --output output.txt
```

Submit:

```bash
bsub < example_job.sh
```

Monitor:

```bash
bstat
bstat -C
bstat -M
bjobs
showstart <job-id>
bpeek <job-id>
bhist -l <job-id>
```

Cancel:

```bash
bkill <job-id>
```

Useful LSF directives:

| Directive | Meaning |
| --- | --- |
| `#BSUB -q hpc` | Queue. |
| `#BSUB -J name` | Job name. |
| `#BSUB -n 4` | Number of cores/slots. |
| `#BSUB -R "span[hosts=1]"` | Keep all cores on one host. |
| `#BSUB -R "rusage[mem=4GB]"` | Request memory per core/slot. |
| `#BSUB -M 5GB` | Memory limit. |
| `#BSUB -W 24:00` | Wall-time limit. |
| `#BSUB -oo file_%J.out` | Standard output, overwrite mode. |
| `#BSUB -eo file_%J.err` | Standard error, overwrite mode. |

## 7. Data Transfer

For small transfers:

```bash
scp local_file.txt dtu-hpc:/work3/<dtu-user>/<project>/
scp dtu-hpc:/work3/<dtu-user>/<project>/result.txt .
```

For resumable directory sync:

```bash
rsync -avP local_folder/ dtu-hpc:/work3/<dtu-user>/<project>/local_folder/
rsync -avP dtu-hpc:/work3/<dtu-user>/<project>/results/ ./results/
```

If your group uses a DTU transfer host, replace `dtu-hpc` with the documented transfer host and keep the same placeholder pattern.

## 8. Troubleshooting

| Symptom | Check |
| --- | --- |
| SSH times out from home | Connect to DTU VPN or verify that your account is allowed remote SSH. |
| Permission denied | Confirm username case, key path, key passphrase, and whether the public key is installed. |
| VS Code server fails | DTU/DCC does not officially support VS Code Remote. Try a terminal-only SSH workflow or contact support if the failure blocks work. |
| Job exits immediately | Inspect `logs/*.err`, confirm paths exist, and load modules/Conda inside the job script. |
| Job is pending | Use `showstart <job-id>`, check memory/core requests, and inspect queue load. |
| Home quota is full | Move active data to scratch and keep only code/configs/small outputs in `~`. |

## Sources

- DTU/DCC access guide: <https://www.hpc.dtu.dk/?page_id=2501>
- DTU/DCC cluster access FAQ: <https://www.hpc.dtu.dk/?page_id=862>
- DTU/DCC LSF batch jobs: <https://www.hpc.dtu.dk/?page_id=1416>
- DTU/DCC job monitoring: <https://www.hpc.dtu.dk/?page_id=1519>
- DTU/DCC storage: <https://www.hpc.dtu.dk/?page_id=59>
- DTU/DCC modules: <https://www.hpc.dtu.dk/?page_id=282>
- DTU network and VPN: <https://www.inside.dtu.dk/en/it-information-technology/it-access-and-network/netvaerk-og-vpn>
- P1 DTU HPC guide: <https://hpc.aicentre.dk/clusters/dtu-hpc/>
