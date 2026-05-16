# Conda Environment Notes

This folder may contain exported Conda environment files used by the project.

Important: exported Conda YAML files can contain a local `prefix:` path. Do not copy another user's prefix into your setup. If a YAML contains `prefix: /some/local/path`, remove that line before creating an environment on your account.

## Create an Environment

Example shape:

```bash
conda env create -f envs/<environment-file>.yml
```

Then activate:

```bash
conda activate <env-name>
```

If you install Conda under project storage, batch scripts may need:

```bash
source /work3/<dtu-user>/<project>/miniconda3/etc/profile.d/conda.sh
conda activate <env-name>
```

## Verify Tools

For KneadData:

```bash
which kneaddata
kneaddata --version
```

For HUMAnN and MetaPhlAn:

```bash
which humann
humann --version
which metaphlan
metaphlan --version
```

For Python helpers:

```bash
which python
python --version
python -c "import matplotlib; print(matplotlib.__version__)"
```

## Keep Environments Off Home When Large

Conda environments can be large. If your home quota is limited, install environments under approved project/scratch storage and document the path in your project notes. Check official DTU HPC guidance for current storage policy.
