---
title: Installation
layout: default
nav_order: 2
permalink: /install
---


# Install Genin2

Genin2 can be installed using two different methods, based on your preference and workflow. You can choose either, regardless of your operating system:

- [Method 1: PIP](#method-1-pip)
- [Method 2: Conda](#method-2-condabioconda)

## Method 1: PIP

Before proceeding, please ensure you have already installed [Python](https://www.python.org/downloads/) and [Pip](https://pypi.org/project/pip/) (the latter is usually already included with the Python installation). Then, open a terminal and run:

```sh
pip install genin2
```

To update the program and include any new genotype that might have been added, run:

```sh
pip install --upgrade genin2
```

## Method 2: Conda/Bioconda

Genin2 is also available on the [Bioconda](https://bioconda.github.io/recipes/genin2/README.html) channel
Ensure you have [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) (or [Mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)) installed and run:

```sh
conda install -c bioconda genin2
```
