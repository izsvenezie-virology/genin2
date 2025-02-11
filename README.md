# Genin2

## Table of contents:

- [Features](#features)
- [Installation](#installation)
    - [Method 1: PIP](#method-1-pip)
    - [Method 2: Conda](#method-2-conda)
- [Usage](#usage)
- [FAQs](#faqs)
- [How to cite Genin2](#cite-genin2)
- [License](#license)
- [Fundings](#fundings)

## Features

- 🐧 **Cross-platform**: Genin2 can be run on any platform that supports the Python interpreter. Including, but not limited to: Windows, Linux, MacOS.
- 🪶 **Extremely lightweight**: the prediction models weight less than 1 MB
- 🌸 **Easy on the resources**: genin2 can be run on any laptop; 1 CPU and 200 MB of RAM is all it takes
- ⚡ **Lightning-fast**: on a single 2.30 GHz core, Genin2 can process more than 1'200 sequences per minute

## Installation

**Genin2** is compatible with Windows, Linux, and macOS. It can be installed in two ways:
- Using Python's package manager (PIP)
- Using the Conda package management system

### Method 1: PIP

Before proceeding, please ensure you have already installed [Python](https://www.python.org/downloads/) and [Pip](https://pypi.org/project/pip/) (the latter is usually already included with the Python installation). Then, open a terminal and run:

```sh
pip install genin2
```

### Method 2: Conda

**Genin2** is available on Conda from the [bioconda](https://bioconda.github.io/genin2) channel. Ensure you have installed [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) and run:

```sh
conda install -c bioconda genin2
```

## Usage

Launching **Genin2** is as easy as:

```sh
genin2 input.fa
```

### Input guidelines

**Genin2** expects the input to be a nucleotidic, IUPAC-encoded, FASTA file. Please ensure that each sequence name starts with the `>` character and ends with an undersore (`_`) followed by the name of the segment, e.g.:
```
>any_text|any_string/seq_name_PB1
                             ^^^^
```
For additional deatils on the accepted input format, please see the [FAQs](#faqs) section.

### Output Format and Interpretation

...

## FAQs

- About input data
  - [Do I need to use a particular format for the FASTA headers?](#q-do-i-need-to-use-a-particular-format-for-the-fasta-headers)
  - [Can the input file contain more than a single sample?](#q-can-the-input-file-contain-more-than-a-single-sample)
  - [Are my sequences required to have all segments?](#q-are-my-sequences-required-to-have-all-segments)
  - [Do sequences need to be complete?](#q-do-sequences-need-to-be-complete)


### *Q: Do I need to use a particular format for the FASTA headers?*
#### Answer:

Yes. The header should follow this format:
- Start with the ` character
- Contain a sample identifier, such as `A/species/nation/XYZ`. This part can contain any text you wish, and it will be used to group segments together. Ensure it is the same for all segments belonging to the same sample, and that there are no duplicates across different samples.
- End with the unsercsore character (`_`) and one of the following segment names: `PB2`, `PB1`, `PA`, `HA`, `NP`, `NA`, `MP`, `NS`. The correct association between sequence and segment is essential for the correct choice of the prediction parameters.
A valid header might look like this: `>A/chicken/Italy/ID_XXYYZZ/1997_PA`


### *Q: Can the input file contain more than a single sample?*
#### Answer:
  
Yes, you can use how many samples you wish. However, please take care to group the segments by sample. For instace, a valid file might look like this:

```
>sample_1_PB2
agat...
>sample_1_NP
accg...                VALID file!
>sample_2_PB2     <--- Here, data for sample_1 ends,
ggaa...                and sample_2 starts
>sample_2_NP
tcag...
```

```
>sample_1_PB2
agat...
>sample_2_NP
tcag...                INVALID file!
>sample_1_NP      <--- Here, sample_1 is referenced again,
accg...                but its chunk had already ended
>sample_2_PB2
ggaa...
```

### *Q: Are my sequences required to have all segments?*
#### Answer:

No, any number of available segments is accepted by the program. Clearly, missing genes might prevent the unique assignment of a genotype, but you will nonetheless gain knowledge on the versions of the processed segments.

### *Q: Do sequences need to be complete?*
#### Answer:

No, not necessarily. Partial sequences are accepted, but the prediction will be based solely on the available data. Sometimes a chunk of sequence is enough for a confident discrimination, and some other times is not.

## Cite Genin2

## License

**Genin2** is licensed under the GNU Affero v3 license (see [LICENSE](LICENSE)).


## Fundings

This work was supported by KAPPA-FLU HORIZON-CL6-2022-FARM2FORK-02-03 (grant agreement No 101084171) and by the NextGeneration EU-MUR PNRR Extended Partnership initiative on Emerging Infectious Diseases (Project no. PE00000007, INF-ACT).

>Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Health and Digital Executive Agency (HEDEA). 
>Neither the European Union nor the granting authority can be held responsible for them
