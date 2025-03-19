---
layout: default
title: Usage
nav_order: 3
permalink: /usage
---

# Usage

Launching **Genin2** is as easy as:

```sh
genin2 -o output.tsv input.fa
```

To see the complete list of supported parameters and their effects use the `-h` or `--help` option:

```sh
genin2 --help
```

## Input guidelines

**Genin2** expects the input to be a nucleotidic, IUPAC-encoded, FASTA file. Please ensure that each sequence name starts with the `>` character and ends with an undersore (`_`) followed by the name of the segment, e.g.:
```
>any_text|any_string/seq_name_PB1
                             ^^^^
```
For additional deatils on the accepted input format, please see the [FAQs](./faqs) section.

## Output Format and Interpretation

The results of the analysis are saved to disk as Tab-Separated Values (TSV). This format allows for quick and easy handling as they can be opened as tables with MS Excel, but also for simple and efficient processing by other scripts if you are setting up **Genin2** to work inside of a larger pipeline.

The results table consists of 10 columns:
- **Column 1**: Sample Name

  The sample name, as read from the input FASTA

- **Column 2**: Genotype

  The assigned genotype. Note that a value is only written here when it is certain; in all other cases the genotype is set as `[unassigned]` and the *Notes* column will provide additional information (see below).

- **Columns 3 to 9**: PB2, PB1, PA, NP, NA MP, NS

  The version that each segment is classified as.
  - If the confidence of the prediction is below a safety threshold, an asterisk (`*`) is appended to the number.
  - If the confidence is also below an acceptance threshold, it is discarded. In this and all other cases where a version is not available, a `?` is displayed, with additional information in the *Notes* column.
  - Note: HA is ignored, as all samples are assumend to bellong to the 2.3.4.4b H5 clade.
  - Note: MP is always assumed to be version "20", as it is the only version present in Genin2's genotypes list.

- **Column 10**: Notes

  Details on failed or discarded predictions and assigments. This column contains information about these events:
  - Genotypes might be `[unassigned]` because of an unknown composition (*"unknown composition"*), or because accepted versions are too few and the composition matches more than a single genotype (*"insufficient data"*). In the latter case however, if the set of matches is small they are listed as "*compatible with*".
  - Segment versions might be `?` if the segment was not present in the input file (*"missing*"), the sequence had insufficient coverage (*"low quality"*, see [FAQs](./faqs) for details), if the prediction reported insufficient confidence (*"low confidence*"), or the classification failed in general (*"unassigned"*).
