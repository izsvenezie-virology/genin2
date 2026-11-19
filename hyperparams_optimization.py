#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import joblib, datetime
from sklearn import svm
from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics import f1_score, balanced_accuracy_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from utils import *
import numpy as np


MIN_SEQ_COV = 0.8
RAND_STATE = 42
K_CALIB = 3
K_GRID = 3
J = 6

param_grid = {
    'fs__threshold': [p*(1-p) for p in [0.6, 0.7, 0.8, 0.9]],
    'clf__estimator__C': [1e-5, 1e-4, 1e-3, 0.01, 0.1, 1],
}
f_params = open('tables/hyperparams.tsv', 'w')
f_params.write("seg\tC\tthr\nf1_macro\n")


def train_segment(seg_name: str, xy_train):
    print(f"[{seg_name}] Encoding sequences...")

    ref = alignment_refs[seg_name]
    x_raw, y_raw = zip(*xy_train)
    xy_all = encode_and_filter(x_raw, y_raw, ref)
    print(f"     Aligned and encoded {len(xy_all)} sequences for training dataset")

    # Hold out outliers
    x_train, y_train = zip(*[(x, y) for _, x, y in xy_all if y != '?'])

    pipe = Pipeline([
        ('fs', VarianceThreshold()),
        ('clf', CalibratedClassifierCV(
                svm.LinearSVC(max_iter=int(1e6), tol=1e-6),
                cv=K_CALIB
            )
        )
    ])

    print(f"[{seg_name}] Optimizing hyperparameters...", flush=True)
    cv = StratifiedKFold(n_splits=K_GRID, shuffle=True, random_state=RAND_STATE)
    grid_search = GridSearchCV(estimator=pipe, param_grid=param_grid, cv=cv, refit=True, scoring='f1_macro', n_jobs=J)
    grid_search.fit(x_train, y_train)
    
    print(f"[{seg_name}] Best estimator: Macro-F1 = {grid_search.best_score_:.2f}")
    f_params.write(f"{seg_name}\t{grid_search.best_params_['fs__threshold']:.2f}\t{grid_search.best_params_['clf__estimator__C']}\t{grid_search.best_score_:.2f}\n")
    
    seq_names, x_all, y_all = zip(*xy_all)
    clf_calibrated, best_p = calibrate_clf(grid_search.best_estimator_, seq_names, x_all, y_all)

    print(f"'{seg_name}': {{"
        f"'th': {grid_search.best_params_['fs__threshold']:.2f}, 'c':{grid_search.best_params_['clf__estimator__C']}, 'p': {best_p}"
    "}\n")
    return clf_calibrated, best_p


def encode_and_filter(X, Y, ref) -> list[tuple[str, list, str]]:
    res = []

    for (name, x), y in zip(X, Y):
        x = pairwise_alignment(ref, x)
        seq_cov = (len(x) - x.upper().count('N') - x.count('-')) / len(ref)
        
        if seq_cov >= MIN_SEQ_COV:
            res.append((name, encode_nt(x), str(y)))
        # else:
        #     print(f"  Low coverage sequence: {name} ({int(seq_cov*100)}%), discarding")

    return res


def calibrate_clf(clf, meta, X, Y):
    def tune_prob(clf, x, y):
        best_p = 0
        max_scores = []

        for p in np.arange(1.0, 0.2, -0.05):
            scores = score_p(clf, x, y, p)
            
            if len(max_scores) == 0:
                max_scores = scores
                continue

            if all(_new >= _old for _new, _old in zip(scores, max_scores)):
                max_scores, best_p = scores, p

        score_p(clf, x, y, best_p, log=True)
        return max_scores, best_p

    def score_p(clf, x, yt, prob_thresh, log=False):
        probs = clf.predict_proba(x)
        max_probs = probs.max(axis=1)
        labels  = clf.classes_[probs.argmax(axis=1)]
        yp = [v if p > prob_thresh else '?' for v, p in zip(labels, max_probs)]

        if log:
            for n, t, p in zip(meta, Y, yp):
                if t != p:
                    print(f"{n}: t/{t} != p/{p}")
        
        return [
            # min(recall_score(yt, yp, average=None)),
            # min(f1_score(yt, yp, average=None)),
            # balanced_accuracy_score(yt, yp),
            f1_score(yt, yp, average='macro'),
        ]
    
    print(f"     Tuning probability threshold...")
    scores, best_p = tune_prob(clf, X, Y)
    print(f"     Best p: {best_p:.3f} with scores f1 = {scores}")

    return clf, best_p


def main():
    segs: list[str] = list(alignment_refs.keys())
    xy = joblib.load('xy.joblib')
    
    models = {}
    for seg_name in segs:
        clf, pt = train_segment(seg_name, xy[seg_name])
        models[seg_name] = (clf, pt)

    models['build_date'] = str(datetime.datetime.now())
    joblib.dump(models, 'models/models.xz')
    f_params.close()
    

if __name__ == "__main__":
    main()