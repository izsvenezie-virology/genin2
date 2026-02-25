#!/usr/bin/env python3

import matplotlib.pyplot as plt

raw_data = open('temp/svm_measures.tsv', 'r').readlines()
header = raw_data[0].strip().split('\t')
data = [
    {
        h: f for h, f in zip(header, line.strip().split('\t'))
    } for line in raw_data[1:]
]

seg_order = ['NS', 'MP', 'NA', 'NP', 'PA', 'PB1', 'PB2']
measures = ['precision', 'recall', 'f1']
nums = {seg: 0 for seg in seg_order}
scores = {
    s: {
            'precision': [],
            'recall': [],
            'f1': []
    } for s in seg_order
}

for row in data:
    seg = row['segment']
    for m in measures:
        scores[seg][m].append(float(row[m]))
    nums[seg] += int(row['tp']) + int(row['fn'])


fig, axs = plt.subplots(3, 1, figsize=(12, 10))
bins = [i / 10 for i in range(0, 11)]
ticks = [(b, b + 0.09) for b in bins[:-1]]
ticks[-1] = (0.9, 1.0)

for ax, measure in zip(axs, measures):
    x = {s: scores[s][measure] for s in seg_order}
    labels = [f"{s} (n={nums[s]})" for s in seg_order]
    x = list(x[s] for s in seg_order)

    ax.hist(
        x, bins=bins, label=labels, density=True, stacked=False,
        align='mid', rwidth=0.5, color=['firebrick', 'gold', 'greenyellow', 'green', 'darkturquoise', 'slateblue', 'violet']
    )
    for patch in ax.patches:
        patch.set_height(patch.get_height() / (len(bins) - 1))
    
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 1)
    ax.set_xticks(
        [b + 0.05 for b in bins[:-1]],
        [f'{t1:.2f} - {t2:.2f}' for t1, t2 in ticks]
    )
    ax.set_title(f'Distribution of {measure} across segments')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper center', ncols=7, fontsize='small', frameon=False)

plt.tight_layout()
plt.show()