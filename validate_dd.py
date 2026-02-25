#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, datetime
import matplotlib.pyplot as plt


def get_seq2gen():
    seq2gen = {}
    for gen_name in ['DI', 'DI.1', 'DI.2', 'DI.2.1']:
        gen_file = f'sequences/{gen_name}.fa'
        lines = open(gen_file).readlines()
        for i in range(0, len(lines), 2):
            seq_id = lines[i].strip()[1:-4]
            seq2gen[seq_id] = gen_name
    return seq2gen


def run_genin2():
    cmd = "cat sequences/DI* | genin2 -o temp/validation_tmp_dd.tsv -"
    os.system(cmd)


if __name__ == '__main__':
    print("Getting DD mapping")
    seq2subgen = get_seq2gen()

    print("Running models on DI sequences")
    run_genin2()

    print("Reading genin2 results")
    genin2_res = [l.strip().split('\t') for l in open('temp/validation_tmp_dd.tsv')]
    cols = genin2_res.pop(0)
    genin2_out = {}
    for l in genin2_res:
        if 'missing' in l[-1]:
            continue
        if l[1] == '[unassigned]' or l[2].strip() == '':
            genin2_out[l[0]] = '[unassigned]'
        else:
            genin2_out[l[0]] = l[2]


    print("Calculating scores")
    f_err = open("temp/validation_errors_dd.tsv", 'w')
    f_err.write("seq_id\tsubgen_true\tsubgen_predicted\n")
    gen2score = {}
    cf_labels = ['DI', 'DI.1', 'DI.2', 'DI.2.1', '[unassigned]']
    cf_matrix = {g: {g2: 0 for g2 in cf_labels} for g in cf_labels}
    for seq_id, prediction in genin2_out.items():
        subgen_true = seq2subgen[seq_id]
        cf_matrix[subgen_true][prediction] += 1

        if subgen_true not in gen2score:
            gen2score[subgen_true] = {'TP': 0, 'FP': 0, 'FN': 0}
        if prediction not in gen2score:
            gen2score[prediction] = {'TP': 0, 'FP': 0, 'FN': 0}

        if prediction == subgen_true:
            gen2score[subgen_true]['TP'] += 1
        else:
            gen2score[subgen_true]['FN'] += 1
            gen2score[prediction]['FP'] += 1
            f_err.write(f"{seq_id}\t{subgen_true}\t{prediction}\n")
    f_err.close()
    
    print("Printing scores")
    f_out = open('temp/validation_scores_dd.tsv', 'w')
    f_out.write("subgenotype\tTP\tFP\tFN\tPrecision\tRecall\tF1 Score\n")
    for gen_name, score in gen2score.items():
        TP = score['TP']
        FP = score['FP']
        FN = score['FN']
        try:
            precision = TP / (TP + FP)
            recall = TP / (TP + FN)
            f1 = 2 * precision * recall / (precision + recall)
        except ZeroDivisionError:
            precision, recall, f1 = '-', '-', '-'
        f_out.write(f"{gen_name}\t{TP}\t{FP}\t{FN}\t{precision}\t{recall}\t{f1}\n")
    f_out.close()

    print("Generating confusion matrix")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.matshow([[cf_matrix[g2][g1] for g2 in cf_labels] for g1 in cf_labels], cmap='cool', vmin=0, vmax=10)
    ax.set_xticks(range(len(cf_labels)))
    ax.set_xticklabels(cf_labels, rotation=90)
    ax.set_yticks(range(len(cf_labels)))
    ax.set_yticklabels(cf_labels)
    for i in range(len(cf_labels)):
        for j in range(len(cf_labels)):
            ax.text(j, i, str(cf_matrix[cf_labels[j]][cf_labels[i]]), ha='center', va='center')
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    today = datetime.date.today().strftime("%Y%m%d")
    plt.savefig(f"img/validation_confusion_matrix_dd_{today}.png")
    plt.close()

    print("Done")
