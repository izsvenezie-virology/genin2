---
layout: default
title: FAQs
nav_order: 4
permalink: /faqs
---

# FAQs

- General
  - [Which genotypes are recognized by Genin2?](#q-which-genotypes-are-recognized-by-genin2)
- About input data
  - [Do I need to use a particular format for the FASTA headers?](#q-do-i-need-to-use-a-particular-format-for-the-fasta-headers)
  - [Can the input file contain more than a single sample?](#q-can-the-input-file-contain-more-than-a-single-sample)
  - [Are my sequences required to have all segments?](#q-are-my-sequences-required-to-have-all-segments)
  - [Do sequences need to be complete?](#q-do-sequences-need-to-be-complete)


## *Q: Which genotypes are recognized by Genin2?*
### Answer:

Genin2's prediction models are regularely updated to include relevant new genotypes. You can inspect the table on which predictions are based upon by opening the file [src/genin2/compositions.tsv](https://github.com/izsvenezie-virology/genin2/blob/master/src/genin2/compositions.tsv). Generally speaking, we aim to support all epidemiologically relevant European genotypes, i.e., those observed in at least 3 occurences in at least 2 different coutnries.

## *Q: What does "low quality" mean when a sequence is flagged as discarded?*
### Answer:

Internally, **Genin2** contains some genome references used to normalize the encoding process of the models. If an input sequence does not cover a significant enough portion of the relative reference, it is considered too little informative for a reliable prediction and is discarded. The valid portion of a sequence consists in the ratio between the length of the input sequence minus the number of `N`s, divided by the length of the internal reference.

By default, this minimum ratio is set to 0.7. If you wish to raise or relax this limit, you can manually set it on the commandline with the `--min-seq-cov` option.

## *Q: Do I need to use a particular format for the FASTA headers?*
### Answer:

Yes. The header should follow this format:
- Start with the `>` character
- Contain a sample identifier, such as `A/species/nation/XYZ`. This part can contain any text you wish, and it will be used to group segments together. Ensure it is the same for all segments belonging to the same sample, and that there are no duplicates across different samples.
- End with the undercsore character (`_`) and one of the following segment names: `PB2`, `PB1`, `PA`, `HA`, `NP`, `NA`, `MP`, `NS`. The correct association between sequence and segment is essential for the correct choice of the prediction parameters.
A valid header might look like this: `>A/chicken/Italy/ID_XXYYZZ/1997_PA`


## *Q: Can the input file contain more than a single sample?*
### Answer:
  
Yes, you can use how many samples you wish.

## *Q: Are my sequences required to have all segments?*
### Answer:

No, any number of available segments is accepted by the program. Clearly, missing genes might prevent the unique assignment of a genotype, but you will nonetheless gain knowledge on the versions of the processed segments. Moreover, HA and MP are ignored regardless: the former is assumed from the clade, while the latter, as of now, is only present in the dataset with the version "20".

## *Q: Do sequences need to be complete?*
### Answer:

No, not necessarily. Partial sequences are accepted, but the prediction will be based solely on the available data. Sometimes a chunk of sequence is enough for a confident discrimination, and some other times is not.
