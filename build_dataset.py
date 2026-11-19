#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, joblib, datetime, re, random
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from Bio import SeqIO


MIN_CLASS_CARDINALITY = 6
MAX_CLASS_CARDINALITY = 50
SEGMENTS = ['NA', 'NP', 'MP', 'NS', 'PA', 'PB1', 'PB2']
REJECTION_CLASS_PREFIX = 'reject/'
RAND_STATE = 8

rejection_classes = {
    'NA': ['hu_sw_na_p'],
    'MP': ['mp_clust_01', 'mp_clust_02', 'mp_clust_03', 'mp_clust_04', 'mp_clust_05']
}

random.seed(RAND_STATE)


def add_seqs(dataset, fname, seg2ver: str|dict ='error'):
    for record in SeqIO.parse(fname, 'fasta'):
        seg, ver = 'error', '?'

        if isinstance(seg2ver, str):
            if seg2ver == 'infer':  # Get version from seq_id
                seg, ver = record.id.rsplit('_', 2)[1:]
                ver = ver[1:]  # Remove leading 'v'
            else:  # It's a rejection class
                seg = record.id.rsplit('_', 1)[1]
                if seg == 'HA':
                    continue
                if seg in rejection_classes and seg2ver in rejection_classes[seg]:
                    ver = REJECTION_CLASS_PREFIX + seg2ver
                else:
                    ver = '?'
        else:
            seg = record.id.rsplit('_', 1)[1]
            if seg == 'HA':
                continue

            ver = seg2ver[seg]

        if ver not in dataset[seg]:
            dataset[seg][ver] = []
        dataset[seg][ver].append((record.id, record.seq))
        

def plot_heatmaps(dataset):
    fig, axs = plt.subplots(4, 2, figsize=(14, 6))
    for seg, ax in zip(SEGMENTS, axs.flatten()):
        xy = dataset[seg]
        ys = [y for _, y in xy]
        versions = list(set(ys))
        n_seqs = [ys.count(v) for v in versions]
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


def shuffle_and_clip(seg2ver2seq):
    res = {}

    for seg, ver2seq in seg2ver2seq.items():
        res[seg] = {}
        for ver, seq in ver2seq.items():
            random.shuffle(seq)
            res[seg][ver] = seq[:MAX_CLASS_CARDINALITY]

    return res


def filter_low_represented(seg2ver2seq):
    res = {}
    discared_versions = {}

    for seg, ver2seq in seg2ver2seq.items():
        res[seg] = {}
        discarded_seqs = []
        discared_versions[seg] = set()

        for ver, seqs in ver2seq.items():
            if len(seqs) >= MIN_CLASS_CARDINALITY:
                res[seg][ver] = seqs
            else:
                print(f"  [{seg}] Discarded class {ver}")
                discarded_seqs.extend(seqs)
                discared_versions[seg].add(ver)

        if '?' not in res[seg]:
            res[seg]['?'] = []
        res[seg]['?'].extend(discarded_seqs)

    return (res, discared_versions)


'''
Print genotypes that can't be predicted because of discarded versions
'''
def print_dead_genotypes(compositions: dict[str, dict[str, str]], discarded: dict[str, set[str]]):
    for gen_name, comp in compositions.items():
        for seg, v in comp.items():
            if seg != 'Include' and v in discarded[seg]:
                print(f"   Dead genotype: {gen_name} for version {seg}/{v} (important: {comp['Include']})")
                break


def main():
    seg2ver2seq = {s: {} for s in SEGMENTS}

    # Load genotypes compositions
    compositions = [l.strip().split('\t') for l in open('all_compositions.tsv')]
    header = compositions.pop(0)
    compositions = {l[0]: {seg: l[i+1] for i, seg in enumerate(header[1:]) if seg != 'HA'} for l in compositions}
    
    for gen_file in os.listdir('sequences'):
        if gen_file == 'extra':
            for extra_file in os.listdir('sequences/extra'):
                if extra_file.startswith('mixed_'):
                    add_seqs(seg2ver2seq, f'sequences/extra/{extra_file}', seg2ver='infer')
                else:
                    add_seqs(seg2ver2seq, f'sequences/extra/{extra_file}', seg2ver=str(extra_file).replace('.fa', ''))
        elif gen_file.endswith('.fa'):
            gen_name = re.search(r'EA-[0-9]{4}-.+\.fa', gen_file)
            if gen_name is None:
                print(f"Cannot parse genotype filename: {gen_file}")
                continue

            base_gen_name = gen_name.group(0).split('.')[0]
            
            if base_gen_name not in compositions:
                print(f"Genotype '{base_gen_name}' (from {gen_name}) has unknown composition, skipping.")
            else:
                comp = compositions[base_gen_name]
                add_seqs(seg2ver2seq, f"sequences/{gen_file}", comp)
        else:
            print(f"What should I do with this? {gen_file}")

    print("Shuffling and clipping...")
    seg2ver2seq = shuffle_and_clip(seg2ver2seq)

    print("Filtering out low-cardinality classes...")
    (seg2ver2seq, discarded_versions) = filter_low_represented(seg2ver2seq)

    print_dead_genotypes(compositions, discarded_versions)

    dataset_xy = {}
    seq_dump = open('tables/dataset_ref.txt', 'w')
    for seg, ver2seq in seg2ver2seq.items():
        dataset_xy[seg] = [(s, v) for v, seq in ver2seq.items() for s in seq]
        seq_dump.write(f"{seg}\n")
        seq_dump.write('\n'.join(name for (name, _), _ in dataset_xy[seg]) + '\n\n')
        
    
    print("Saving all...")
    joblib.dump(dataset_xy, 'xy.joblib')

    print("Plotting heatmaps...")
    plot_heatmaps(dataset_xy)


if __name__ == '__main__':
    main()
