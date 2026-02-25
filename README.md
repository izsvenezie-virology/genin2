# Genin2 training procedure overview

Dependencies:
- Python >= 3.9
- Biopython
- scikit-learn
- matplotlib


## 0. Assemble your dataset

Details on how to organize and format your sequences are reported in the docstrings of `build_dataset.py`-


## 1. Build the dataset

Assemble a binary dump of all training data with:

```bash
$ ./build_dataset.py
```

This will create `seg2ver2seq.joblib`. For more info check the docstrings in the source file.

Now check `img/genotypes_heatmap.png` and `img/versions_heatmap.png` for data statistics.


## 2. Train the SVMs

```bash
$ ./train_svms.py seg2ver2seq.joblib
```

This will create `models/models.xz` and `temp/training_seqs.tsv`. The latter contains the list of sequences used for training that should be uxcluded from validation.

Now check `img/cf_matrix_{date}.png` for a Confusion Matrix of training performance.


## 3. Train the DD (DI Discriminator) for sub-genotypes

```bash
$ ./train_dd.py
```

This will create `models/dd.xz`.

Now check `img/training_confusion_matrix_dd_{date}.png` for a Confusion Matrix of training performance.


## 4. Validate the SVMs

```bash
$ ./validate_svms.py seg2ver2seq.joblib
```

Validation raw data is now available in `temp/`.


## 5. Validate the DD

```bash
$ ./validate_dd.py
```

Validation raw data is now available in `temp/` and `img/`.


## 6. (optional) Perform an overall validation of all sequences on the assembled software

```bash
$ ./validate_genin2.py
```

## 7. Plot validation metrics

```bash
$ ./plot_svm_measures.py
$ ./plot_svm_measures_2.py
```
