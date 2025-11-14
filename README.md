# Genin2

Genin2 is a lightning-fast bioinformatics tool to predict genotypes for clade 2.3.4.4b H5Nx viruses collected in Europe since October 2020. Genotypes are assigned using the methods described in [this article](https://doi.org/10.1093/ve/veae027). Genin2 identifies only epidemiologically relevant European genotypes, i.e., detected in at least 3 viruses collected from at least 2 countries. You can inspect the up-to-date list of supported genotypes in [this file](src/genin2/compositions.tsv).

Genin2 can also distinguish the four subtypes of `EA-2024-DI`: `DI`, `DI.1`, `DI.2`, and `DI.2.1`.

## Table of contents:

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Input guidelines](#input-guidelines)
  - [Output format and interpretation](#output-format-and-interpretation)
- [FAQs](#faqs)
- [How to cite Genin2](#cite-genin2)
- [License](#license)
- [Fundings](#fundings)

## Features

- :penguin: **Cross-platform**: Genin2 can be run on any platform that supports the Python interpreter. Including, but not limited to: Windows, Linux, MacOS.
- :balloon: **Extremely lightweight**: the prediction models weight less than 1 MB
- :cherry_blossom: **Easy on the resources**: genin2 can be run on any laptop; 1 CPU and 200 MB of RAM is all it takes
- :zap: **Lightning-fast**: on a single 2.30 GHz core, Genin2 can process more than 1'200 sequences per minute

## Installation

**Genin2** is compatible with Windows, Linux, and macOS. Before proceeding, please ensure you have already installed [Python](https://www.python.org/downloads/) and [Pip](https://pypi.org/project/pip/) (the latter is usually already included with the Python installation). Then, open a terminal and run:

```sh
pip install genin2
```

To **update** the program and include any new genotype that might have been added, run:

```sh
pip install --upgrade genin2
```

## Usage

Launching **Genin2** is as easy as:

```sh
genin2 -o output.tsv input.fa
```

To see the complete list of supported parameters and their effects use the `-h` or `--help` option:

```sh
genin2 --help
```

### Input guidelines

**Genin2** expects the input to be a nucleotidic, IUPAC-encoded, FASTA file. Please ensure that each sequence name starts with the `>` character and ends with an undersore (`_`) followed by the name of the segment, e.g.:
```
>any_text|any_string/seq_name_PB1
                             ^^^^
```
For additional deatils on the accepted input format, please see the [FAQs](#faqs) section.

### Output Format and Interpretation

The results of the analysis are saved to disk as Tab-Separated Values (TSV). This format allows for quick and easy handling as they can be opened as tables with MS Excel, but also for simple and efficient processing by other scripts if you are setting up **Genin2** to work inside of a larger pipeline.

The results table consists of 11 columns:

- **Column 1**: Sample Name

  The sample name, as read from the input FASTA

- **Column 2**: Genotype

  The assigned genotype. Note that a value is only written here when it is certain; in all other cases the genotype is set as `[unassigned]` and the *Notes* column will provide additional information (see below).

- **Column 3**: Sub-genotype

  For genotypes where sub-clustering is important, as is `EA-2024-DI`, subgenotype names such as `DI`, `DI.1`, `DI.2`, and `DI.2.1` will be specified in this column.

- **Columns 4 to 10**: PB2, PB1, PA, NP, NA MP, NS

  The version that each segment is classified as.
  - If a version prediction is not available, a `?` is displayed, with additional information in the *Notes* column.
  - Note: HA is ignored, as all samples are assumend to bellong to the 2.3.4.4b H5 clade.

- **Column 11**: Notes

  Details on failed or discarded predictions and assigments. This column contains information about these events:
  - Genotypes might be `[unassigned]` because of an unknown composition (*"unknown composition"*), or because accepted versions are too few and the composition matches more than a single genotype (*"insufficient data"*). In the latter case however, if the set of matches is small they are listed as "*compatible with*".
  - Segment versions might be `?` if the segment was not present in the input file (*"missing*"), the sequence had insufficient coverage (*"low quality"*, see [FAQs](#faqs) for details), or the classification failed in general (*"unassigned"*).

## FAQs

- General
  - [Which genotypes are recognized by Genin2?](#q-which-genotypes-are-recognized-by-genin2)
- About input data
  - [Do I need to use a particular format for the FASTA headers?](#q-do-i-need-to-use-a-particular-format-for-the-fasta-headers)
  - [Can the input file contain more than a single sample?](#q-can-the-input-file-contain-more-than-a-single-sample)
  - [Are my sequences required to have all segments?](#q-are-my-sequences-required-to-have-all-segments)
  - [Do sequences need to be complete?](#q-do-sequences-need-to-be-complete)


### *Q: Which genotypes are recognized by Genin2?*
#### Answer:

Genin2's prediction models are regularely updated to include relevant new genotypes. You can inspect the table on which predictions are based upon by opening the file [src/genin2/compositions.tsv](https://github.com/izsvenezie-virology/genin2/blob/master/src/genin2/compositions.tsv). Generally speaking, we aim to support all epidemiologically relevant European genotypes, i.e., those observed in at least 3 occurences in at least 2 different countries. Additionally, as of version 2.1.0, subgenotypes of `EA-2024-DI` are also supported.

### *Q: What does "low quality" mean when a sequence is flagged as discarded?*
#### Answer:

Internally, **Genin2** contains some genome references used to normalize the encoding process of the models. If an input sequence does not cover a significant enough portion of the relative reference, it is considered too little informative for a reliable prediction and is discarded. The valid portion of a sequence consists in the ratio between the length of the input sequence minus the number of `N`s, divided by the length of the internal reference.

By default, this minimum ratio is set to 0.7. If you wish to raise or relax this limit, you can manually set it on the commandline with the `--min-seq-cov` option.

### *Q: Do I need to use a particular format for the FASTA headers?*
#### Answer:

Yes. The header should follow this format:
- Start with the `>` character
- Contain a sample identifier, such as `A/species/nation/XYZ`. This part can contain any text you wish, and it will be used to group segments together. Ensure it is the same for all segments belonging to the same sample, and that there are no duplicates across different samples.
- End with the undercsore character (`_`) and one of the following segment names: `PB2`, `PB1`, `PA`, `HA`, `NP`, `NA`, `MP`, `NS`. The correct association between sequence and segment is essential for the correct choice of the prediction parameters.
A valid header might look like this: `>A/chicken/Italy/ID_XXYYZZ/1997_PA`


### *Q: Can the input file contain more than a single sample?*
#### Answer:
  
Yes, you can use how many samples you wish.

### *Q: Are my sequences required to have all segments?*
#### Answer:

No, any number of available segments is accepted by the program. Clearly, missing genes might prevent the unique assignment of a genotype, but you will nonetheless gain knowledge on the versions of the processed segments. Moreover, HA is ignored regardless, as it is assumed from the clade.

### *Q: Do sequences need to be complete?*
#### Answer:

No, not necessarily. Partial sequences are accepted, but the prediction will be based solely on the available data. Sometimes a chunk of sequence is enough for a confident discrimination, and some other times is not.

## Cite Genin2

We are currently writing the paper.
Until the publication please cite the GitHub repository:

[https://github.com/izsvenezie-virology/genin2](https://github.com/izsvenezie-virology/genin2)

## License

**Genin2** is licensed under the GNU Affero v3 license (see [LICENSE](LICENSE)).


## Fundings

This work was supported by the NextGeneration EU-MUR PNRR Extended Partnership initiative on Emerging Infectious Diseases (Project no. PE00000007, INF-ACT) and by Kappa-Flu project - Funded by the European Union under Grant Agreement (101084171). Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or REA. Neither the European Union nor the granting authority can be held responsible for them.
