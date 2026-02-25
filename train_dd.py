#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Train the DD model (DI Discriminator)
'''

import joblib, datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from utils import *
import matplotlib.pyplot as plt


clfs = {
    'NA': RandomForestClassifier(n_jobs=4, n_estimators=100, criterion='gini', max_features=0.1, random_state=8),
    'NP': RandomForestClassifier(n_jobs=4, n_estimators=100, criterion='gini', max_features=0.1, random_state=8),
    'NS': RandomForestClassifier(n_jobs=4, n_estimators=100, criterion='gini', max_features=0.1, random_state=8),
    'MP': RandomForestClassifier(n_jobs=4, n_estimators=100, criterion='gini', max_features=0.1, random_state=8),
    'PA': RandomForestClassifier(n_jobs=4, n_estimators=100, criterion='gini', max_features=0.1, random_state=8),
    'PB1': RandomForestClassifier(n_jobs=4, n_estimators=100, criterion='gini', max_features=0.1, random_state=8),
    'PB2': RandomForestClassifier(n_jobs=4, n_estimators=100, criterion='gini', max_features=0.1, random_state=8),
}
MAX_SEQS = 100
subgens = ['DI', 'DI.1', 'DI.2', 'DI.2.1']

sub2seg2seq = {sg: {seg: [] for seg in alignment_refs.keys()} for sg in subgens}
for sg in subgens:
    lines = [l.strip() for l in open('sequences/' + sg + '.fa', 'r').readlines()]

    for i in range(0, len(lines), 2):
        s_name, seq = lines[i], lines[i+1]
        seg_name = s_name.strip().rsplit('_', 1)[1]
        if seg_name != 'HA':
            sub2seg2seq[sg][seg_name].append((s_name, seq.strip().upper()))


def train_segment(seg_name):
    ref = alignment_refs[seg_name]
    clf = clfs[seg_name]
    X, Y = [], []
    
    for sg in subgens:
        xs = [encode_nt(pairwise_alignment(ref, s_nt)) for s_id, s_nt in sub2seg2seq[sg][seg_name][:MAX_SEQS]]
        X.extend(xs)
        Y.extend([sg]*len(xs))

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, random_state=8)

    print(f"[{seg_name}] Fitting model")
    clf.fit(X_train, Y_train)
    print(f"[{seg_name}] Scoring... ", end='', flush=True)
    score = clf.score(X_test, Y_test)
    print(f"{score:.3f}")

    print('-._.-`'*10)

    y_pred = clf.predict(X_test)
    cf_labels = sorted(set(list(Y_test) + list(Y_train)))
    return clf, cf_labels, confusion_matrix(Y_test, y_pred, labels=cf_labels)

models = {}
fig, axs = plt.subplots(2, 4, figsize=(10, 8))

for ax, seg_name in zip(axs.flatten(), alignment_refs.keys()):
    print(seg_name)
    clf, ys, cfm = train_segment(seg_name)
    models[seg_name] = clf

    ax.imshow(cfm, aspect=1, cmap='hot', norm='symlog', vmin=0, vmax=max(sum(r) for r in cfm))
    ax.set_xticks(range(len(ys)), labels=ys)
    ax.set_yticks(range(len(ys)), labels=ys)
    for i in range(len(ys)):
        for j in range(len(ys)):
            if cfm[i, j] != 0:
                text = ax.text(j, i, cfm[i, j], ha="center", va="center", color="green", size=16)
    ax.set_title(seg_name)

print("Saving to disk...")
models['build_date'] = str(datetime.datetime.now())
joblib.dump(models, 'models/dd.xz', protocol=4)

fig.tight_layout()
today = datetime.date.today().strftime("%Y%m%d")
fig.savefig(f"img/training_confusion_matrix_dd_{today}.png")