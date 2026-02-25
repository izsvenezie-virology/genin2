#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import joblib
from utils import *
import sys


MIN_SEQ_COV = 0.7


def validate_segment(seg_name, ver2seq, clf):
    print(f"Validating segment {seg_name}...")
    Yt, Yp = [], []

    for v, seqs in ver2seq.items():
        print(f"    - {v} ({len(seqs)})")
        x = [seg_alignment_wrapper(seg_name, s) for s in seqs]
        Yt.extend([v] * len(x))
        Yp.extend(
            clf.predict(x)
        )

    err = sum(1 for yt, yp in zip(Yt, Yp) if yt != yp)
    print(1 - err/len(Yt))
    print('-._.-^'*12)

    return Yt, Yp


def score_segment(seg_name, Yt, Yp):
    print(seg_name)
    scores = {
        v: {
            'TP': 0,
            'FP': 0,
            'FN': 0
        } for v in set(Yt)
    }

    for yt, yp in zip(Yt, Yp):
        if yt == yp:
            scores[yt]['TP'] += 1
        else:
            scores[yt]['FN'] += 1
            scores[yp]['FP'] += 1
    
    for v, s in scores.items():
        TP = s['TP']
        FP = s['FP']
        FN = s['FN']

        print(f"  - {v}")
        try:
            precision = TP / (TP + FP)
            recall = TP / (TP + FN)
            f1 = 2 * precision * recall / (precision + recall)
        except ZeroDivisionError:
            precision, recall, f1 = '-', '-', '-'
        
        print(f"    Precision: {precision:.2f}")
        print(f"    Recall: {recall:.2f}")
        print(f"    F1-Measure: {f1:.2f}")
        
        yield [v, TP, FP, FN, precision, recall, f1]
    
    print()


def main(f_in):
    seg_names: list[str] = list(alignment_refs.keys())
    models = joblib.load('models/models.xz')
    seg2ver2seq: dict[str, dict[str, str]] = joblib.load(f_in)
    degs = set(list('ACGTUWSMKRYBDHVNZ-'))
    f_out = open('temp/svm_measures.tsv', 'w')
    f_out.write('\t'.join(['segment', 'version', 'tp', 'fp', 'fn', 'precision', 'recall', 'f1']) + '\n')

    train_seqs = {s: set() for s in seg_names}
    for l in open(f'temp/training_seqs.tsv').readlines()[1:]:
        seg, seq_id = l.strip().split('\t')
        train_seqs[seg].add(seq_id)
    
    for seg_name, ver2seq in seg2ver2seq.items():
        x = {}
        f_tmp = open(f'temp/validation_seqs_{seg_name}.tsv', 'w')
        for v, seqs in ver2seq.items():
            x[v] = []
            for s in seqs:
                if s[0] in train_seqs:
                    continue
                if (len(s[1]) - s[1].count('N') - s[1].count('-')) / len(alignment_refs[seg_name]) < MIN_SEQ_COV:
                    continue # Low coverage
                if any(c not in degs for c in s[1].upper()):
                    continue # Invalid nts
                
                x[v].append(s[1])
                f_tmp.write(f"{s[0]}\n")

                if len(x[v]) >= 200:
                    break

        yt, yp = validate_segment(
            seg_name,
            x,
            models[seg_name]
        )

        scores = score_segment(seg_name, yt, yp)
        open(f"temp/{seg_name}.tsv", 'w').write(
            '\t'.join(yt) + '\n' + '\t'.join(yp)
        )
        for row in scores:
            f_out.write(seg_name + '\t' + '\t'.join(str(r) for r in row) + '\n')


if __name__ == '__main__':    
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} seg2ver2seq.joblib")
        sys.exit(-1)
    else:
        main(sys.argv[1])

