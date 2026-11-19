# Genin2 training procedure overview

Dependencies:

- Python >= 3.9
- Biopython
- scikit-learn
- matplotlib

## 1. Build the dataset

Assemble a binary dump of all training data with:

```bash
./build_dataset.py
```

This will create `xy.joblib`. For more info check the docstrings in the source file.

## 2. Train the SVMs

```bash
./hyperparams_optimization.py
```

This will create `models/models.xz`with one model per segment (VarianceThreshold feature selection, SVM with linear kernel, probability calibration regressor)

## 3. Train the DD (DI Discriminator) for sub-genotypes

```bash
./train_dd.py
```

This will create `models/dd.xz`.
