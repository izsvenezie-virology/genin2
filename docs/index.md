---
layout: home
title: Home
nav_order: 1
---


<img src="genin2_logo.png" style="max-width:80%; width:400px; margin:20px auto 40px; display:block;" alt="genin2" title="genin2 logo" />

Genin2 is a lightining-fast bioinformatic tool to predict genotypes for clade 2.3.4.4b H5Nx viruses collected in Europe since October 2020. Genotypes are assigned using the methods described in [this article](https://doi.org/10.1093/ve/veae027). Genin2 identifies only epidemiologically relevant European genotypes, i.e., detected in at least 3 viruses collected from at least 2 countries. You can inspect the up-to-date list of supported genotypes in [this file](https://github.com/izsvenezie-virology/genin2/blob/master/src/genin2/compositions.tsv).

Note that, as of version 2.1.0, Genin2 is also cabable of distinguishing the `DI`, `DI.1`, and `DI.2` subgenotypes.


## Table of contents:

- [Features](#features)
- [Installation](./install)
- [Usage](./usage)
  - [Input guidelines](./usage#input-guidelines)
  - [Output format and interpretation](./usage#output-format-and-interpretation)
- [FAQs](#faqs)
- [How to cite Genin2](#cite-genin2)
- [License](#license)
- [Fundings](#fundings)


## Features

- :penguin: **Cross-platform**: Genin2 can be run on any platform that supports the Python interpreter. Including, but not limited to: Windows, Linux, MacOS.
- :balloon: **Extremely lightweight**: the prediction models weight less than 1 MB
- :cherry_blossom: **Easy on the resources**: genin2 can be run on any laptop; 1 CPU and 200 MB of RAM is all it takes
- :zap: **Lightning-fast**: on a single 2.30 GHz core, Genin2 can process more than 1'200 sequences per minute


## Cite Genin2

We are currently writing the paper.
Until the publication please cite the GitHub repository:

[https://github.com/izsvenezie-virology/genin2](https://github.com/izsvenezie-virology/genin2)


## License

**Genin2** is licensed under the GNU Affero v3 license (see [LICENSE](LICENSE)).


## Fundings
This research was supported by the EU funding within the NextGeneration EU-MUR PNRR Extended Partnership initiative on Emerging Infectious Diseases (Project no. PE00000007, INF-ACT).

This work was funded by the European Union under grant agreement (101084171) - (Kappa-Flu). Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or REA. Neither the European Union nor the granting authority can be held responsible for them.

