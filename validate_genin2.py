#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, datetime
import matplotlib.pyplot as plt


ONLY_COMPLETE = True

comp_file = [l.strip().split('\t') for l in open('../genin2/src/genin2/compositions.tsv')]
cols = comp_file.pop(0)
gens_of_interest = set(l[0].rsplit('-', 1)[1] for l in comp_file)


def get_seq2gen():
    seq2gen = {}
    for gen_file in os.listdir('sequences'):
        if gen_file == 'extra':
            continue
        gen_name = gen_file.rsplit('.', 1)[0]
        if gen_name in ['DI.1', 'DI.2']:
            gen_name = 'DI'
        lines = open(f'sequences/{gen_file}').readlines()
        for i in range(0, len(lines), 2):
            seq_id = lines[i].strip()[1:].rsplit('_', 1)[0]
            seq2gen[seq_id] = gen_name
    return seq2gen


def run_genin2():
    cmd = "cat sequences/*.fa | genin2 -o temp/validation_tmp.tsv -"
    os.system(cmd)


if __name__ == '__main__':
    print("Getting sequence to genotype mapping")
    seq2gen = get_seq2gen()

    print("Running models on all sequences")
    run_genin2()

    print("Reading genin2 results")
    genin2_res = [l.strip().split('\t') for l in open('temp/validation_tmp.tsv')]
    cols = genin2_res.pop(0)
    genin2_out = {}
    for l in genin2_res:
        if l[0] not in seq2gen:
            continue
        if ONLY_COMPLETE and 'missing' in l[-1]:
            continue
        if 'low quality' in l[-1]:
            continue
        
        if l[1] != '[unassigned]':
            l[1] = l[1].rsplit('-', 1)[1]
        
        genin2_out[l[0]] = {c: v for c, v in zip(cols, l)}

    print("Calculating scores")
    f_err = open("temp/validation_errors.tsv", 'w')
    f_err.write("seq_id\tgen_true\tgen_predicted\n")
    gen2score = {}
    cf_labels = sorted(list(gens_of_interest)) + ['[unassigned]']
    cf_matrix = {g: {g2: 0 for g2 in cf_labels} for g in cf_labels}
    for seq_id, predictions in genin2_out.items():
        gen_name_true = seq2gen[seq_id]

        if gen_name_true not in gens_of_interest:
            gen_name_true = '[unassigned]'
        gen_name_predicted = predictions['Genotype']

        cf_matrix[gen_name_true][gen_name_predicted] += 1

        if gen_name_true not in gen2score:
            gen2score[gen_name_true] = {'TP': 0, 'FP': 0, 'FN': 0}
        if gen_name_predicted not in gen2score:
            gen2score[gen_name_predicted] = {'TP': 0, 'FP': 0, 'FN': 0}

        if gen_name_predicted == gen_name_true:
            gen2score[gen_name_true]['TP'] += 1
        else:
            gen2score[gen_name_true]['FN'] += 1
            gen2score[gen_name_predicted]['FP'] += 1
            f_err.write(f"{seq_id}\t{gen_name_true}\t{gen_name_predicted}\n")
    f_err.close()
    
    print("Printing scores")
    f_out = open('temp/validation_scores.tsv', 'w')
    f_out.write("genotype\tTP\tFP\tFN\tPrecision\tRecall\tF1 Score\n")
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
    fig, ax = plt.subplots(figsize=(14, 14))
    ax.matshow([[cf_matrix[g2][g1] for g2 in cf_labels] for g1 in cf_labels], cmap='coolwarm', vmin=0, vmax=10)
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
    plt.savefig(f"img/validation_confusion_matrix_{today}.png")
    plt.close()

    print("Done")
