#!/usr/bin/env python3

from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt

raw_data = open('temp/svm_measures.tsv', 'r').readlines()
header = raw_data[0].strip().split('\t')
data = [
    {
        h: f for h, f in zip(header, line.strip().split('\t'))
    } for line in raw_data[1:]
]

seg_order = ['NS', 'MP', 'NA', 'NP', 'PA', 'PB1', 'PB2']
scores = {
    s: [] for s in seg_order
}

for row in data:
    seg = row['segment']
    scores[seg].append(float(row['f1']))


fig, axs = plt.subplots(7, 3, figsize=(8, 14), width_ratios=[0.02, 0.3, 0.68])
axs[0][0].axis('off')
bins = [i / 10 for i in range(0, 11)]

for i, seg_name in enumerate(seg_order):
    ax_n = axs[i][0]
    ax_m = axs[i][1]
    ax_h = axs[i][2]

    if i == 0:
        ax_m.set_title("Confusion matrix")
        ax_h.set_title("Distribution of classes F1-Measures")

    ax_n.text(0, 0.5, seg_name, va='center')
    ax_n.set_ylim(0, 1)
    ax_n.axis('off')

    yt, yp = open(f'temp/{seg_name}.tsv').readlines()
    yt, yp = yt.strip().split('\t'), yp.strip().split('\t')
    labels = list(set(yt))
    cf = confusion_matrix(yt, yp, labels=labels, normalize='true')
    ax_m.imshow(
        cf, aspect='equal', cmap='binary'
    )
    ax_m.set_xticks([])
    ax_m.set_yticks([])

    x = scores[seg_name]
    ax_h.hist(
        x, bins=bins, color='gray'
    )
    ax_h.set_xlim(0, 1)
    ax_h.set_xticks(bins)
    ax_h.set_yticks([0, len(labels)])
    ax_h.spines.top.set_visible(False)
    ax_h.spines.right.set_visible(False)
    print(f"{seg_name}\t{sum(x)/len(x):.2f}")

plt.tight_layout()
plt.savefig('img/svms.png')
plt.show()