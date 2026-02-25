#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Load all available sequences into a binary archive and save it as `seg2ver2seq.joblib`.

Sequence format:
  - Sequences are looked for in ../sequences
  - Files must be named GENOTYPE.fa, optionally GENOTYPE.SUBGENOTYPE.fa (e.g., AB.fa, DI.2.1.fa, ...)
  - Fasta deflines must be formatted as >[...]_SEGMENT
  - An optional extra/ subdirectory can contain additional sequences with unknown genotypes.
      - If the filename starts with `mixed_`, FASTA deflines must end with the cluster ID formatted as `_vXX`.
      - Otherwise, the cluster ID '?' will be assumed and the sequence trated as outgroup.

Genotype list:
  - Information about *all* genotypes composition is extracted from `all_compositions.tsv`
  - Genotypes to be considered relevant are read from `compositions.tsv`

Archive format:
  - Sequence: tuple[seq_id: str, seq_nt: str, genotype_name: str]
  - Ver2Seq: dict[cluster_id: str, list[Sequence]]
  - Seg2Ver2Seq: dict[segment_name: str, Ver2Seq]
  
'''


import os, joblib, itertools, datetime
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects


seg_names = ['NA', 'NP', 'MP', 'NS', 'PA', 'PB1', 'PB2']


def plot_heatmaps(seg2ver2seq, gens_of_interest):
    fig, axs = plt.subplots(4, 2, figsize=(14, 6))
    for seg, ax in zip(seg_names, axs.flatten()):
        ver2seq = seg2ver2seq[seg]
        versions = list(ver2seq.keys())
        n_seqs = [len(ver2seq[v]) for v in versions]
        ax.matshow([n_seqs], cmap='OrRd_r', aspect='auto', vmin=0, vmax=50)
        ax.xaxis.set_ticks_position('bottom')
        for i, n in enumerate(n_seqs):
            txt = ax.text(i, 0, n, ha="center", va="center", color='k')
            txt.set_path_effects([PathEffects.withStroke(linewidth=4, foreground='w')])
        ax.set_title(seg)
        ax.set_xticks(range(len(versions)))
        ax.set_xticklabels(versions)
        ax.set_yticks([])

    # Display colorbar
    fig.delaxes(axs[-1][-1])
    cbar = plt.colorbar(axs[-1][-1].imshow([[0, 50]], cmap='OrRd_r', aspect='auto'), location='top', fraction=0.4, extend='max')
    cbar.ax.xaxis.set_ticks_position('bottom')
    cbar.set_label('Number of sequences')
    cbar.set_ticks([0, 50])
    cbar.set_ticklabels(['0', '>50'])

    plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05, hspace=1, wspace=0.1)
    today = datetime.date.today().strftime("%Y%m%d")
    plt.savefig(f"img/versions_heatmap_{today}.png", dpi=300)


    # Plot genotype heatmaps by segment
    fig, axs = plt.subplots(8, 1, figsize=(14, 6))
    for seg, ax in zip(seg_names, axs.flatten()):
        ver2seq = seg2ver2seq[seg]
        gens = list(gens_of_interest.keys())
        n_seqs = [sum(1 for _, _, gen in itertools.chain(*ver2seq.values()) if gen == g) for g in gens]
        ax.matshow([n_seqs], cmap='OrRd_r', aspect='auto', vmin=0, vmax=50)
        ax.xaxis.set_ticks_position('bottom')
        for i, n in enumerate(n_seqs):
            txt = ax.text(i, 0, n, ha="center", va="center", color='k')
            txt.set_path_effects([PathEffects.withStroke(linewidth=4, foreground='w')])
        ax.set_title(seg)
        if seg == seg_names[-1]:
            ax.set_xticks(range(len(gens)))
            ax.set_xticklabels(gens)
        else:
            ax.set_xticks([])
        ax.set_yticks([])

    # Display colorbar
    fig.delaxes(axs[-1])
    cbar = plt.colorbar(axs[-1].imshow([[0, 50]], cmap='OrRd_r', aspect='auto'), location='bottom', fraction=0.5, shrink=0.5, extend='max')
    cbar.ax.xaxis.set_ticks_position('top')
    cbar.set_label('Number of sequences')
    cbar.set_ticks([0, 50])
    cbar.set_ticklabels(['0', '>50'])

    plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05, hspace=0.8, wspace=0.1)
    today = datetime.date.today().strftime("%Y%m%d")
    plt.savefig(f"img/genotypes_heatmap_{today}.png", dpi=300)


# Load the genotype compositions we want in the dataset
compositions_of_interest = [l.strip().split('\t') for l in open('../genin2/src/genin2/compositions.tsv')]
cols = compositions_of_interest.pop(0)
gens_of_interest = {l[0].rsplit('-', 1)[1]: {seg: l[i+1] for i, seg in enumerate(cols[1:]) if seg != 'HA'} for l in compositions_of_interest}
vers_of_interest = {s: set(g[s] for g in gens_of_interest.values()) for s in seg_names}

# Load all genotypes compositions
all_compositions = [l.strip().split('\t') for l in open('all_compositions.tsv')]
cols = all_compositions.pop(0)
all_compositions = {l[0]: {seg: l[i+1] for i, seg in enumerate(cols[1:]) if seg != 'HA'} for l in all_compositions}

# Load all sequences
seg2ver2seq = {s: {} for s in seg_names}

def add_seqs(fname, gen_name, seg2ver=None, n_max=1e5):
    lines = open(fname).readlines()
    n = min(len(lines), n_max)

    for i in range(0, int(n), 2):
        try:
            seq_id = lines[i].strip()
            seq_nt = lines[i+1].strip()
            if seg2ver is None:
                # Get version from seq_id
                seg_name, ver = seq_id.rsplit('_', 2)[1:]
                ver = ver[1:]  # Remove leading 'v'
            else:
                seg_name = seq_id.rsplit('_', 1)[1]
                ver = seg2ver[seg_name] if seg_name in seg2ver else '?'
        except:
            print(f"Error processing sequence in {fname} at line {i+1}")
            continue

        if seg_name == 'HA':
            continue

        if ver not in vers_of_interest[seg_name]:
            ver = '?'

        if ver not in seg2ver2seq[seg_name]:
            seg2ver2seq[seg_name][ver] = []
        seg2ver2seq[seg_name][ver].append((seq_id, seq_nt, gen_name if base_gen_name in gens_of_interest else None))


for gen_file in os.listdir('sequences'):
    if gen_file == 'extra':
        for extra_file in os.listdir('sequences/extra'):
            if extra_file.startswith('mixed_'):
                add_seqs(f'sequences/extra/{extra_file}', extra_file, n_max=1000, seg2ver=None)
            else:
                add_seqs(f'sequences/extra/{extra_file}', extra_file, n_max=1000, seg2ver={})
    else:
        gen_name = gen_file.rsplit('.', 1)[0] # Remove extension
        base_gen_name = gen_name.split('.')[0]
        
        if base_gen_name not in all_compositions:
            print(f"Genotype '{base_gen_name}' (from {gen_name}) has unknown composition, skipping.")
        else:
            comp = all_compositions[base_gen_name]
            add_seqs(f"sequences/{gen_file}", gen_name, comp)

# Save the sequences
joblib.dump(seg2ver2seq, 'seg2ver2seq.joblib')

plot_heatmaps(seg2ver2seq, gens_of_interest)
