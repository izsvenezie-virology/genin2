#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, joblib, datetime
from sklearn import svm
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from utils import *
import numpy as np


MIN_SEQ_COV = 0.7

if len(sys.argv) != 2:
    print("Usage: {sys.argv[0]} dataset.joblib")
    sys.exit(-1)


clfs = {
    'NA': svm.SVC(kernel='poly', degree=10, cache_size=1000, random_state=69420),
    'NP': svm.SVC(kernel='poly', degree=10, cache_size=1000, random_state=69420),
    'NS': svm.SVC(kernel='poly', degree=10, cache_size=1000, random_state=69420),
    'MP': svm.SVC(kernel='poly', degree=10, cache_size=1000, random_state=69420),
    'PA': svm.SVC(kernel='poly', degree=10, cache_size=1000, random_state=69420),
    'PB1': svm.SVC(kernel='poly', degree=10, cache_size=1000, random_state=69420),
    'PB2': svm.SVC(kernel='poly', degree=10, cache_size=1000, random_state=69420),
}

segs: list[str] = list(alignment_refs.keys())
fig, axs = plt.subplots(2, 4, figsize=(12, 8))
seg2ver2seq: dict[str, dict[str, str]] = joblib.load(sys.argv[1])
models: dict[str, svm.SVC | str] = {}
scores: dict[str, float] = {}

f_train_seqs = open(f'temp/training_seqs.tsv', 'w')
f_train_seqs.write('segment\tseq_id\n')



def split_ma_furbo(in_ver2seq: dict[str, str], n_max=50, train_size=0.8) \
    -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[str], list[str]]:
    
    # Divide each version sequences by genotype
    ver2gen2seq: dict[str, dict[str, list[tuple[str, str]]]] = {}
    for ver, seqs in in_ver2seq.items():
        if ver not in ver2gen2seq:
            ver2gen2seq[ver] = {}

        for (seq_id, seq_nt, gen) in seqs:
            gen = gen.split('.')[0] if gen is not None else '?' # Use base genotype only, discard subgen info
            seq_cov = (len(seq_nt) - seq_nt.upper().count('N')) / len(alignment_refs[seg_name])
            if seq_cov < MIN_SEQ_COV:
                print(f"  {seq_id} has low coverage ({int(seq_cov*100)}%), discarding")
                continue
            if gen not in ver2gen2seq[ver]:
                ver2gen2seq[ver][gen] = []
            ver2gen2seq[ver][gen].append((seq_id, seq_nt))
    
    # Get n_max sequeces for each version, alternating between genotypes for better variance
    out_ver2seq: dict[str, list[tuple[str, str]]] = {}
    for ver, gen2seq in ver2gen2seq.items():
        out_ver2seq[ver] = []
        bins = list(gen2seq.values())
        bin_idx = 0

        while len(out_ver2seq[ver]) < n_max:
            bin = bins[bin_idx]
            out_ver2seq[ver].append(bin.pop())
            
            if len(bin) == 0:
                bins.pop(bin_idx)
            if len(bins) == 0:
                break
            else:
                bin_idx = (bin_idx + 1) % len(bins)
    
    # Split the sequences into training and testing sets
    X_test, X_train, Y_test, Y_train = [], [], [], []
    for ver, seqs in out_ver2seq.items():
        tot_seqs = len(seqs)
        n_train = int(tot_seqs * train_size)
        # print(f"  {ver}: {n_train}/{tot_seqs}")
        X_train.extend(seqs[:n_train])
        X_test.extend(seqs[n_train:])
        Y_train.extend([ver] * n_train)
        Y_test.extend([ver] * (tot_seqs - n_train))
    
    return X_train, X_test, Y_train, Y_test


def train_segment(seg_name: str):
    ver2seq: dict[str, str] = seg2ver2seq[seg_name]
    ref: str = alignment_refs[seg_name]
    clf: svm.SVC = clfs[seg_name]

    print(f"[{seg_name}] Splitting (ma in modo furbo)")
    X_train, X_test, Y_train, Y_test = split_ma_furbo(ver2seq, n_max=50, train_size=0.8)
    f_train_seqs.write('\n'.join([f'{seg_name}\t{seq_id}' for seq_id, _ in X_train]) + '\n')
    print(f"[{seg_name}] Encoding sequences")
    X_train = np.array([encode_nt(pairwise_alignment(ref, seq)) for _, seq in X_train], dtype=bool)
    X_test = np.array([encode_nt(pairwise_alignment(ref, seq)) for _, seq in X_test], dtype=bool)
    
    print(f"[{seg_name}] Fitting model")
    clf.fit(X_train, Y_train)

    print(f"[{seg_name}] Scoring... ", end='', flush=True)
    Y_predicted = clf.predict(X_test)
    score = float(clf.score(X_test, Y_test))
    print(f"{score:.3f}")
    print('-._.-^'*12)

    cf_labels = sorted(set(list(Y_test) + list(Y_train)))
    return clf, score, cf_labels, confusion_matrix(Y_test, Y_predicted, labels=cf_labels)


for ax, seg_name in zip(axs.flatten(), segs):
    clf, score, ys, cfm = train_segment(seg_name)
    models[seg_name] = clf
    scores[seg_name] = score
    ax.imshow(cfm, aspect=1, cmap='hot', norm='symlog', vmin=0, vmax=max(sum(r) for r in cfm))
    ax.set_xticks(range(len(ys)), labels=ys)
    ax.set_yticks(range(len(ys)), labels=ys)
    for i in range(len(ys)):
        for j in range(len(ys)):
            if cfm[i, j] != 0:
                text = ax.text(j, i, cfm[i, j], ha="center", va="center", color="green")
    ax.set_title(seg_name)

print("Saving to disk...")
models['build_date'] = str(datetime.datetime.now())
joblib.dump(models, 'models/models.xz', protocol=4)

axs[-1][-1].axis('off')
fig.tight_layout()
today = datetime.date.today().strftime("%Y%m%d")
fig.savefig(f"img/cf_matrix_{today}.png")