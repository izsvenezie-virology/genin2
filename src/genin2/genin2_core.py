import importlib_resources, joblib, itertools, sys, csv, logging, time
from Bio.Align import PairwiseAligner
from typing import List, Tuple, Optional


__version__ = '2.0.0'
__author__ = 'Alessandro Sartori'
__contact__ = 'asartori@izsvenezie.it'

MIN_VPROB_THR = 0.4 # Minimum probability for keeping a version prediction (as low confidence)
VPROB_THR = 0.6 # Minimum probability for accepting a version prediction (as good confidence)
MAX_COMPATIBLE_GENS = 3 # Maximum number of compatible genotypes to accept. If the prediction returns more, they will be discarded as unreliable

alignment_refs: dict[str, str] = {}
genotype2versions: dict[str, dict[str, str]] = {}
models: dict[str, any]
output_segments_order = ['PB2', 'PB1', 'PA', 'NP', 'NA', 'MP', 'NS']
logger = logging.getLogger(__name__)


def critical_error(msg: str, ex: Optional[Exception] = None) -> None:
    if ex is not None:
        logger.critical('%s (%s, %s)', msg, type(ex).__name__, str(ex))
    else:
        logger.critical(msg)
    logger.critical("The above error was critical and the program will now exit")
    logger.critical("If this problem persists and you need assistance, open an issue at https://github.com/izsvenezie-virology/genin2/issues")
    sys.exit(-1)


def init_data() -> None:
    global alignment_refs, genotype2versions, models

    try:
        # >A/chicken/Italy/21VIR1151-2/2021_seg_ver=20
        alignment_refs['NA'] = 'ATGAATCCAAATCAGAAAATAGCGACCATTGGCTCCATCTCATTGGGACTAGTTGTATTCAATGTTCTACTGCATGCCTTGAGCATCATATTAATGGTGTTAGCCCTGGGGAAAAGTGAAAACAATGGAATCTGCAAGGGAACTATAGTAAGGGAATATAATGAAACAGTTAGGATAGAGAAAGTGACCCAGTGGTACAACACTAGTGTAGTCGAATATGTACCGCATTGGAACGAGGGCGCTTATATAAACAACACCGAACCAATATGTGATGTCAAGGGCTTTGCACCTTTTTCCAAGGACAACGGAATAAGAATTGGCTCCAGAGGACATATTTTTGTCATAAGGGAGCCTTTCGTCTCTTGTTCACCTGTAGAGTGCAGAACTTTCTTCCTCACTCAGGGAGCTCTACTCAATGACAAACACTCAAATGGAACAGTGAAGGATAGGAGCCCATTCAGAACTCTCATGAGTGTCGAAGTGGGTCAATCACCCAATGTGTATCAAGCAAGGTTTGAAGCTGTAGCATGGTCAGCAACAGCCTGTCATGATGGTAAGAAATGGATGACGATTGGTGTGACAGGGCCAGATTCGAAAGCAATAGCAGTAGTCCATTACGGAGGAGTGCCTACTGATATTGTTAACTCCTGGGCAGGAGACATATTACGGACTCAGGAGTCATCTTGTACTTGCATTCAAGGTAATTGTTATTGGGTAATGACTGACGGTCCATCCAATAGACAGGCGCAGTATAGAATATACAAAGCAAATCAAGGCAAAATAATTGACCAAGCAGATGTCAGCTTTAGTGGAGGGCATATTGAGGAATGCTCTTGTTATCCAAATGATGGTAAAGTGGAATGCGTGTGTAGAGACAACTGGATGGGAACTAACAGGCCTGTGCTAATTATCTCGCCTGACCTCTCTTACAGGGTTGGGTATTTATGTGCGGGATTGCCCAGTGACACTCCAAGAGGGGAAGATGCCCAATTTGTCGGTTCGTGCACTAGTCCCATGGGAAATCAGGGGTATGGCGTAAAAGGTTTCGGGTTCCGACAGGGATCTGATGTGTGGATGGGGCGGACAATTAGTCGAACCTCCAGGTCAGGGTTTGAAATAATAAGGATAAAGAATGGTTGGACGCAGACAAGCAAAGAACGGATTAGAAGGCAGGTGGTTGTTGATAATTTGAATTGGTCGGGATACAGTGGGTCTTTCACTTTACCAGTAGAATTGTCTGGGAGGGAATGTTTAGTCCCCTGTTTTTGGGTCGAAATGATCAGAGGCAGGCCAGAAGAAAGAACAATCTGGACCTCTAGTAGCTCCATTGTAATGTGTGGAGTTGATCATGAAATTGCCGATTGGTCATGGCACGATGGAGCTATTCTTCCCTTTGACATCGATGGGATGTAA'
        # >A/avian/Italy/21VIR10913-3/2021_seg_ver=1
        alignment_refs['NP'] = 'ATGGCGTCTCAAGGCACCAAACGATCCTATGAACAGATGGAGACTGGTGGAGAGCGCCAGAATGCCACTGAGATCAGAGCATCTGTTGGACGAATGGTTGGTGGAATTGGGAGGTTCTACATACAGATGTGCACTGAGCTCAAACTCAGCGACCATGAAGGAAGGCTGATCCAGAACAGCATAACAATAGAGAGAATGGTTCTCTCTGCATTTGATGAAAGGAGGAACAAATATCTGGAAGAACACCCCAGTGCGGGGAAGGACCCGAAGAAAACTGGAGGTCCAATTTATCGAAGGAGAGATGGGAAATGGGTGAGAGAACTGATCCTGTATGACAAAGAGGAGATCAGGAGAATCTGGCGTCAAGCGAACAATGGAGAAGACGCAACTGCTGGTCTCACTCACCTGATGATCTGGCATTCTAATTTAAATGATGCCACATACCAGAGGACGAGAGCTCTCGTGCGTACTGGGATGGACCCCAGGATGTGCTCTCTTATGCAAGGATCAACTCTCCCAAGGAGGTCTGGAGCTGCTGGTGCAGCAGTAAAGGGAGTCGGGACGATGGTGATGGAACTAATTCGGATGATAAAGCGAGGAATTAATGATCGGAACTTCTGGAGAGGCGAGAACGGACGAAGGACAAGGATTGCATATGAGAGAATGTGCAACATCCTCAAAGGGAAATTCCAAACAGCAGCGCAAAGAGCAATGATGGACCAGGTGCGTGAAAGCAGGAATCCTGGCAATGCTGAAATTGAAGATCTCATCTTTCTGGCACGGTCTGCACTCATCCTGAGAGGATCAGTGGCTCATAAGTCCTGCTTGCCTGCTTGTGTGTACGGACTCGCTGTAGCCAGTGGATACGACTTTGAGAGAGAAGGGTACTCTCTAGTTGGGATAGATCCTTTCCGTCTGCTTCAAAACAGTCAGGTCTTCAGCCTCATTAGACCAAATGAGAATCCAGCACACAAGAGTCAATTGGTATGGATGGCATGTCATTCCGCAGCATTCGAGGATCTGAGAGTCTCAAGTTTCATCAGAGGAACAAGAGTAGTTCCAAGAGGACAACTATCCACAAGAGGGGTTCAAATTGCTTCAAATGAGAACATGGAAACAATGGACTCCAGCACTCTTGAACTGAGAAGCAGATATTGGGCTATAAGAACCAGGAGTGGAGGGAACACCAACCAACAGAGAGCATCTGCAGGACAGATCAGTGTACAGCCCACTTTTTCGGTACAGAGAAATCTTCCCTTTGAAAGAGCGACCATTATGGCGGCGTTCACAGGGAATACTGAGGGCAGAACATCCGACATGAGGACTGAAATCATAAGAATGATGGAAAGTGCCAGACCAGAAGATGTGTCTTTCCAGGGGCGGGGAGTCTTCGAGCTTTCGGACGAAAAGGCAACGAACCCGATCGTGCCTTCCTTTGACATGAGTAATGAAGGATCTTATTTCTTCGGAGACAATGCAGAGGAGTATGACAATTAA'
        # >A/avian/Italy/21VIR10913-3/2021_seg_ver=1 
        alignment_refs['NS'] = 'ATGGATTCCAACACTGTGTCAAGCTTTCAGGTAGACTGCTTTCTTTGGCATGTCCGCAAACGATTTGCAGACCAAGAACTGGGTGATGCCCCATTCCTTGACCGGCTTCGCCGAGATCAGAAATCCCTGAGAGGAAGAGGCAGCACTCTTGGTCTGGACATCGAAACAGCCACCCGTGTGGGAAAGCAGATAGTGGAGCGGATTCTGGAAGAAGAATCTGATGAGGCACTTAAAATGACTATTGCCCCCGTGCCAGCTTCACGCTACCTAACTGACATGACTCTTGAGGAGATGTCAAGGGACTGGTTCATGCTCATGCCCAAACAGAAAGTGGCAGGTTCCCTTTGCATCAGAATGGACCAGGCAATAATGGATAAAAACATCATATTGAAAGCAAACTTCAGTGTGATTTTTGACCGGCTGAAAACCCTAATACTAATTAGAGCTTTCACAGAAGAAGGAGCAATTGTGGGAGAAATCTCACCATTACCTTCTCTTCCAGGACATACTAATGAGGATGTCAAAAATGCAATTGGGGTCCTCATCGGAGGACTTGAATGGAATGATAACACAGTTCGAGTCTCTGAAACTCTACAGAGATTCGCTTGGAGAAGCAGTAATGAGGATGGGAGACCTCCACTCCCTCCAAAGCAGAAACGGAAAATGGCGAAGACAATTGAGTCAGAAGTTTGAAGAAATAAGATGGCTGATTGAAGAAGTGCGGCACAGATTGAAGATTACAGAGAACAGTTTCGAACAGATAACTTTCATGCAAGCCTTACAACTATTGCTTGAAGTGGAGCAAGAGATAAGAACTTTCTCGTTTCAGCTTATTTAA'
        # >A/avian/Italy/21VIR10913-3/2021_seg_ver=1
        alignment_refs['PA'] = 'ATGGAAGACTTTGTGCGACAATGCTTCAATCCAATGATTGTCGAGCTTGCGGAAAAAGCAATGAAAGAATATGGGGAAGATCCGAAAATCGAGACAAACAAATTTGCCGCAATATGCACACACTTAGAAGTCTGTTTCATGTATTCGGATTTCCATTTTATTGATGAACGAGGCGAATCAATGATTGTAGAATCTGGCGATCCAAATGCATTATTGAAACACCGATTTGAGATAATCGAAGGGAGAGACCGAGCAATGGCCTGGACAGTGGTGAATAGTATCTGCAACACCACAGGAGTCGAAAAGCCCAAATTCCTCCCTGATTTGTATGACTACAAAGAGAACCGATTCATTGAAATTGGAGTAACGCGAAGGGAAGTTCACATATACTATTTAGAAAAAGCCAACAAGATAAAATCGGAGAAAACACACATTCACATATTCTCATTCACTGGAGAGGAAATGGCCACCAAGGCGGAATACACCCTTGATGAAGAGAGCAGAGCAAGAATAAAAACCAGACTGTTCACTATAAGACAAGAAATGGCCAGTAGAGGTCTATGGGATTCCTTTCGTCAGTCCGAGAGAGGCGAAGAGACAACTGAAGAAAGATTTGAAATCACAGGAACCATGCGCAGGCTTGCCGACCAAAGTCTCCCACCGAACTTCTCCAGCCTTGAAAACTTTAGAGCCTATGTGGATGGATTCGAACCGAACGGCTGCATTGAGGGCAAGCTTTCTCAAATGTCAAAAGAAGTGAACGCCAGAATTGAGCCATTCCTGAAGACAACACCACGCCCTCTCAGATTACCTGATGGGCCTCCTTGTTCTCAGCGGTCGAAGTTCTTGCTGATGGATGCCCTTAAGTTGAGCATCGAAGACCCTAGCCATGAGGGGGAGGGCATACCGCTGTATGATGCAATCAAATGCATGAAGACATTTTTTGGCTGGAAAGAGCCCAACCTCGTAAAGCCGCATGAGAAAGGCATAAACCCTAATTACCTCCTGGCTTGGAAGCAGGTGCTGGCAGAACTTCAAGATATTGAGAATGAGGAAAAATTTCCAAAAACAAAGAACATGAAGAAAACAAGCCAATTGAAGTGGGCACTTGGTGAGAACATGGCACCAGAAAAAGTGGACTTTGAGGACTGCAAAGATGTTAGCGATCTAAGACAGTACGACAGTGACGAACCAGAGCCTAGATCACTAGCAAGCTGGATTCAGAGTGAATTCAACAAGGCATGCGAATTGACAGATTCGAGTTGGATTGAACTTGATGAGATAGGGGAAGACGTTGCTCCAATCGAACACATTGCGAGTATGAGGAGGAACTATTTCACAGCGGAGGTATCCCATTGCAGGGCCACTGAATACATAATGAAGGGAGTATACATAAACACAGCCCTATTGAATGCATCCTGTGCAGCCATGGATGACTTCCAACTGATTCCAATGATAAGCAAGTGCAGAACCAAAGAAGGAAGACGGAGGACAAATCTGTATGGATTCATTATAAAAGGAAGATCCCATTTGAGGAATGACACCGATGTGGTAAACTTTGTGAGCATGGAATTCTCTCTAACTGACCCGAGGCTAGAGCCACACAAATGGGAAAAGTACTGTGTTCTTGAGATAGGAGACATGCTCCTACGGACTGCAATAGGCCAAGTGTCGAGGCCCATGTTCCTGTATGTGAGAACCAATGGGACTTCCAAGATCAAAATGAAATGGGGCATGGAGATGAGACGATGCCTTCTTCAGTCCCTTCAACAAATTGAGAGCATGATTGAGGCCGAATCTTCTGTCAAAGAGAAGGACATGACCAAGGAATTCTTTGAAAACAAATCAGAAACATGGCCAATTGGAGAATCACCCAAAGGGGTTGAGGAAGGCTCTATTGGGAAAGTATGCAGAACATTGCTAGCAAAGTCTGTGTTCAACAGCCTATATGCATCTCCACAACTCGAGGGATTTTCAGCTGAATCAAGAAAATTGCTTCTCATTGTTCAGGCACTTAGGGACAACCTGGAACCTGGAACCTTCGATCTTGGGGGGCTATATGAAGCAATTGAGGAGTGCCTGATTAACGATCCCTGGGTTTTGCTTAATGCGTCTTGGTTCAACTCCTTCCTCACACATGCACTGAAATAG'
        # >A/avian/Italy/21VIR10913-3/2021_seg_ver=1
        alignment_refs['PB1'] = 'ATGGATGTCAATCCGACTTTACTTTTCTTAAAAGTGCCAGCGCAAGATGCCATAAGTACCACATTCCCTTACACTGGAGATCCTCCATACAGCCATGGAACAGGGACAGGATACACAATGGACACAGTCAACAGAACACATCAATACTCAGAGAAGGGAAAATGGACAACAAACACAGAAACCGGAGCACCTCAACTCAACCCAATTGATGGGCCACTACCTGAGGACAACGAACCGAGCGGATATGCACAAACAGATTGCGTGTTGGAAGCAATGGCTTTCCTTGAAGAGTCCCACCCAGGGATCTTTGAAAACTCTTGTCTTGAAACGATGGAAGTCGTTCAGCAAACAAGAGTGGACAAACTAACTCAAGGTCGCCAGACATATGACTGGACACTGAATAGAAACCAACCAGCTGCAACTGCCCTGGCCAACACTATAGAGGTCTTCAGATCAAACGGTCTAACAGCCAATGAATCGGGGAGACTAATAGATTTCCTCAAGGATGTGATGGACTCAATGGATAAAGAAGAAATGGAAATAACAACACATTTCCAGAGAAAGAGAAGAGTAAGGGACAACATGACCAAGAAAATGGTCACACAAAGAACAATAGGAAAGAAGAAACAAAGGCTAAACAAGAGGAGCTACTTAATAAGAGCACTGACACTGAATACAATGACAAAAGATGCAGAAAGAGGCAAATTGAAGAGACGGGCGATTGCAACACCAGGGATGCAGATTAGAGGATTTGTGTACTTTGTCGAAACACTGGCAAGGAGCATCTGTGAAAAACTTGAGCAATCTGGACTCCCCGTTGGAGGGAATGAGAAGAAGGCTAAATTGGCAAATGTCGTGAGAAAAATGATGACTAACTCACAAGATACAGAGCTCTCCTTCACAATTACTGGAGACAACACCAAATGGAATGAGAATCAAAATCCTCGGATGTTTCTGGCAATGATAACATACATTACAAGAAACCAACCTGAATGGTTTAGAAATGTCTTAAGTATTGCCCCTATAATGTTCTCGAACAAAATGGCGAGATTGGGAAAAGGGTACATGTTTGAAAGTAAGAGCATGAAGTTACGGACACAAATACCTGCAGAATTGCTTGCAAACATTGACTTAAAATACTTCAATGAATCAACAAGAAAGAAAATCGAAAAGATAAGGCCTCTACTAATAGATGGCACTGCCTCATTGAGTCCTGGAATGATGATGGGCATGTTCAATATGCTGAGTACAGTATTAGGAGTTTCAATCCTAAATCTTGGGCAAAAGAATTACACCAAAACCACATACTGGTGGGATGGACTCCAATCCTCTGATGATTTCGCCCTCATAGTAAATGCACCGAATCATGAGGGAATACAAGCAGGAGTGGATAGGTTCTATAGGACCTGCAAACTGGTCGGGATCAATATGAGCAAAAAGAAGTCTTACATAAACCGGACTGGAACATTTGAGTTCACAAGCTTTTTCTATCGCTATGGATTTGTGGCTAACTTCAGTATGGAGCTGCCCAGCTTTGGGGTTTCTGGGATCAATGAATCAGCTGACATGAGCATTGGCGTCACAGTGATAAAGAACAACATGATAAACAATGACCTTGGACCAGCAACAGCTCAAATGGCCCTTCAACTATTCATCAAAGATTACAGGTACACGTACCGATGCCACAGAGGTGACACACAAATTCAAACGAGGAGATCATTCGAGCTGAAGAAGCTGTGGGAACAGACCCGTTCAAAGGCAGGACTGTTGGTGTCAGATGGAGGACCAAATCTATACAACATCCGGAATCTCCATATCCCAGAGGTCTGCCTGAAGTGGGAGCTGATGGACGAAGATTACCAGGGCAGGTTGTGTAATCCTCTGAACCCATTTGTCAGCCATAAAGAAATTGAGTCCGTAAACAATGCTGTGGTGATGCCAGCTCACGGTCCAGCCAAAAGCATGGAATATGATGCCGTTGCGACTACACACTCATGGACTCCTAAAAGGAATCGTTCCATTCTCAATACCAGTCAAAGGGGAATTCTTGAGGATGAACAGATGTACCAGAAATGCTGCAGTCTATTCGAGAAATTCTTCCCCAGTAGTTCATACAGGAGACCAGTTGGAATTTCCAGCATGGTGGAGGCCATGGTGTCTAGGGCCCGAATCGATGCACGCATTGATTTCGAATCTGGAAGGATCAAGAAGGAAGAGTTTGCTGAGATCATGAAGATCTGTTCCACCATTGAAGAGCTCAGACGGCAAAAATAG'
        # >A/avian/Italy/21VIR10913-3/2021_seg_ver=1
        alignment_refs['PB2'] = 'ATGGAGAGAATAAAAGAGCTAAGAGATTTGATGTCGCAGTCTCGCACTCGCGAGATACTGACAAAAACCACCGTGGACCATATGGCCATAATCAAGAAATATACATCAGGAAGACAGGAGAAGAACCCTGCACTTAGGATGAAGTGGATGATGGCAATGAAATATCCGATTACAGCAGACAAAAGGATAATGGAGATGATCCCTGAAAGAAACGAGCAAGGTCAGACTCTTTGGAGCAAAACAAATGATGCTGGATCGGATAGAGTAATGGTGTCACCTCTGGCTGTGACGTGGTGGAATAGAAATGGACCAACAACAAGTACAGTCCATTACCCAAAGGTCTATAAAACTTACTTTGAAAAGGTTGAAAGGTTAAAGCATGGAACCTTCGGCCCTGTCCATTTCCGGAATCAGGTTAAGATACGCCGCAGAGTTGACATAAACCCGGGCCATGCAGACCTCAGTGCTAAAGAAGCACAAGACGTCATCATGGAGGTCGTTTTCCCAAATGAAGTCGGAGCCAGAATATTGACATCAGAGTCACAGTTAACAATTACAAAAGAAAAGAAGGAGGAACTCCAGGACTGTAAGATTGCCCCTCTAATGGTGGCATACATGTTGGAGAGAGAACTGGTTCGAAAAACCAGATTCCTGCCAGTAGCTGGCGGAACAAGTAGCGTATATATCGAAGTGTTGCACCTGACTCAAGGAACCTGCTGGGAACAAATGTATACGCCAGGAGGAGAAGTGAGAAATGATGACATTGACCAAAGTTTAATTATTGCTGCCAGAAATATCGTTAGGAGAGCAACAGTATCAGCAGACCCATTGGCTTCACTACTGGAGATGTGCCATAGTACACAGATTGGCGGGATAAGAATGGTAGACATTCTTAGACAGAACCCAACAGAAGAGCAAGCCGTGGATATATGCAAAGCAGCAATGGGTTTAAGAATCAGTTCATCCTTCAGTTTTGGAGGTTTCACTTTCAAAAGGACAAGCGGATCATCTGTCAAAAGAGAAGAGGAAGTGCTCACCGGCAACCTCCAAACATTGAAAATAAGAGTACATGAAGGGTATGAGGAATTCACAATGGTTGGGCGGAGAGCAACAGCCATTCTAAGGAAAGCAACCAGAAGGCTGATCCAATTGATAGTAAGTGGAAAAGACGAGCAGTCAATCGCCGAAGCGATCATAGTGGCAATGGTGTTCTCTCAAGAGGATTGCATGATAAAGGCTGTACGAGGTGATTTAAATTTTGTCAATAGAGCGAATCAGCGGCTCAATCCTATGCATCAGCTCCTGAGGCATTTCCAAAAGGATGCAAAGGTACTATTCCAAAACTGGGGAATTGAACCCATTGACAATGTCATGGGAATGATAGGAATATTGCCTGATATGACTCCCAGCACAGAGATGTCACTAAGAGGAGTGAGGGTCAGTAAAATGGGAGTGGATGAATATTCCAGTACTGAGAGGGTGGTCGTGAGTATTGATCGCTTCTTGAGGGTACGAGACCAGAGAGGAAATGTACTCTTGTCTCCCGAAGAGGTCAGTGAAACACAGGGAACAGAGAAGCTAACGATAACATATTCATCATCCATGATGTGGGAAATTAATGGCCCTGAGTCAGTGCTAGTTAACACATATCAATGGGTCATCAGAAACTGGGAAACTGTGAAGATTCAGTGGTCCCAAGACCCTACAATGCTATACAACAAGATGGAGTTTGAGCCTTTTCAGTCCTTGGTGCCCAAGGCAGCCAGAGGCCAGTACAGTGGATTTGTAAGGACCTTATTCCAGCAGATGCGTGATGTGCTGGGAACCTTTGACACTGTCCAGATAATAAAGCTACTTCCATTTGCAGCAGCACCACCGGAACAGAGTAGGATGCAGTTCTCTTCTCTAACTGTAAACGTAAGGGGTTCAGGAATGAGAATACTTGTGAGAGGAAACTCCCCTGTGTTCAACTATAATAAGGCAACCAAGAGGCTCATAGTCCTTGGAAAGGATGCTGGTGCATTGACAGGAGACCCAGGTGAGGGGACAGCAGGAGTGGAGTCTGCGGTATTGAGAGGGTTCCTAATTCTGGGCAAAGAGGACAAAAGATATGGACCAGCGCTGAGCATCAATGAATTGAGCAATCTTGCGAAAGGGGAGAAGGCTAATGTGTTGATAGGGCAAGGAGACGTGGTGTTGGTGATGAAACGGAAACGGGACTCTAGCATACTTACTGACAGCCAGACAGCGACCAAAAGAATTCGGATGGCCATCAATTA'
    except Exception as e:
        critical_error("Couldn't load alignment references", e)

    try:
        comp_file = csv.reader(
            open(importlib_resources.files('genin2').joinpath('compositions.tsv'), 'r'),
            delimiter='\t'
        )
        cols = next(comp_file)

        for line in comp_file:
            genotype2versions[line[0]] = {seg: ver for seg, ver in zip(cols[1:], line[1:])}
    except Exception as e:
        critical_error("Couldn't load genotype compositions", e)

    try:
        models = joblib.load(
            importlib_resources.files('genin2').joinpath('models.xz')
        )
    except Exception as e:
        critical_error("Couldn't load prediction models", e)


def predict_sample(sample: dict[str, str]) -> Tuple[str, dict[str, str]]:
    ver_predictions: dict[str, str] = {}
    low_confidence = False

    for seg_name, seq in sample.items():
        pred_v, pred_p = predict_seg_version(seg_name, seq)

        if pred_v == '?' or pred_p < MIN_VPROB_THR:
            ver_predictions[seg_name] = ('?', 'unassigned')
            low_confidence = True
        elif pred_p > VPROB_THR:
            ver_predictions[seg_name] = (pred_v, None)
        else:
            ver_predictions[seg_name] = (pred_v + '*', 'low confidence')
            low_confidence = True
    
    for seg_name in alignment_refs.keys():
        if seg_name not in ver_predictions:
            ver_predictions[seg_name] = ('?', 'missing')
            low_confidence = True

    genotype = (None, None)
    compatible = get_compatible_genotypes({s: v for s, (v, _) in ver_predictions.items()})
    if len(compatible) == 1 and not low_confidence:
        genotype = (compatible[0], None)
    elif len(compatible) == 0:
        genotype = ('[unassigned]', 'unknown composition')
    elif len(compatible) > MAX_COMPATIBLE_GENS:
        genotype = ('[unassigned]', 'insufficient data')
    else:
        genotype = ('[unassigned]', f'compatible with {", ".join(compatible)}')

    return genotype, ver_predictions


def predict_seg_version(seg_name: str, seq: str) -> Tuple[str, float]:
    try:
        encoded_seq = pairwise_alignment(alignment_refs[seg_name], seq)
        encoded_seq = encode_sequence(encoded_seq)
    except Exception as e:
        logger.error(f"Failed to align and encode {seg_name} sequence. {type(e).__name__}, {str(e)}")
        return ('?', 0.0)

    model = models[seg_name]
    v_probs = model.predict_proba([encoded_seq])[0]

    max_p, max_v = 0, '?'
    for c, p in zip(model.classes_, v_probs):
        if p > max_p:
            max_p, max_v = p, c
    
    return (max_v, max_p)


def pairwise_alignment(ref_seq, q_seq):
    aligner = PairwiseAligner()
    aligner.match_score = 1
    aligner.mismatch_score = -1
    aligner.open_gap_score = -4
    aligner.extend_gap_score = -1
    ref_al, q_al = aligner.align(ref_seq, q_seq)[0]
    cut_al = cut_alignment(ref_al, q_al)
    return cut_al


def cut_alignment(ref, qry):
    gap_idxs = [i for i, nt in enumerate(ref) if nt == '-']
    return ''.join(nt for i, nt in enumerate(qry) if i not in gap_idxs)


def encode_sequence(seq: str) -> List[bool]:
    T, F = True, False
    encoding_dict = {
        'A': [T, F, F, F], 'C': [F, T, F, F], 'G': [F, F, T, F], 'T': [F, F, F, T], 'U': [F, F, F, T], 'W': [T, F, F, T],
        'S': [F, T, T, F], 'M': [T, T, F, F], 'K': [F, F, T, T], 'R': [T, F, T, F], 'Y': [F, T, F, T], 'B': [F, T, T, T],
        'D': [T, F, T, T], 'H': [T, T, F, T], 'V': [T, T, T, F], 'N': [T, T, T, T], 'Z': [F, F, F, F], '-': [F, F, F, F]
    }
    return list(itertools.chain(*[encoding_dict[base] for base in seq]))


def get_compatible_genotypes(versions: dict[str, str]) -> List[str]:
    '''
    Get all compatible genotypes based on the provided versions

    Args:
        versions (dict[str, str]): A dict mapping each segment to the most likely version. '?' is trated as an unknown version.

    Returns:
        List[str]: The list of genotypes that are compatible with the given versions. Might be an empty list.
    '''

    gset = genotype2versions
    for s, v in versions.items():
        if v != '?':
            gset = {gen: comp for gen, comp in gset.items() if comp[s] == v}
    
    return list(gset.keys())


def read_fasta(file):
    sample_name = None
    seq = []
    
    for line in file:
        if not (line := line.strip()):
            continue

        if line.startswith('>'):
            if sample_name is not None:
                yield sample_name, ''.join(seq).upper()
            sample_name = line[1:]
            seq.clear()
        else:
            seq.append(line)
    
    if sample_name is not None:
        yield sample_name, ''.join(seq).upper()


def read_samples(file):
    curr_sample_name = None
    sample = {}

    for name, seq in read_fasta(file):    
        name, seg_name = name.rsplit('_', 1)
        
        if name != curr_sample_name:
            if curr_sample_name is not None:
                yield curr_sample_name, sample
            sample.clear()
            curr_sample_name = name

        if seg_name not in alignment_refs.keys():
            if seg_name != 'HA' and seg_name != 'MP':
                logger.warn(f"Segment {seg_name} is not recognized")
            continue
        
        sample[seg_name] = seq
    
    if curr_sample_name is not None:
        yield curr_sample_name, sample


def run(in_file: str, out_file: str):
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    logging.info("Initializing")
    init_data()

    try:
        out_file.write('Sample Name\tGenotype\t' + '\t'.join(output_segments_order) + '\tNotes\n')
    except Exception as e:
        critical_error(f"Couldn't write to output file '{out_file}'", e)

    logging.info("Starting analysis...")
    start_time = time.time()
    tot_samples, tot_seqs = 0, 0
    for sample_name, sample in read_samples(in_file):
        logging.info(f"Processing {len(sample)} segments for {sample_name}")
        (genotype, genotype_notes), ver_predictions = predict_sample(sample)
        tot_samples += 1
        tot_seqs += len(sample)

        notes_col = []
        if genotype_notes is not None:
            notes_col.append(f'Genotype: {genotype_notes}')
        
        tsv_row = [sample_name, genotype]
        for seg in output_segments_order:
            if seg == 'MP':
                tsv_row.append('20')
            else:
                ver, ver_notes = ver_predictions[seg]
                tsv_row.append(ver or '?')
                if ver_notes is not None:
                    notes_col.append(f'{seg}: {ver_notes}')
        
        tsv_row.append('; '.join(notes_col))
        out_file.write('\t'.join(tsv_row) + '\n')
    
    tot_time_s = int(time.time() - start_time)
    h, m, s = (tot_time_s // 3600, tot_time_s % 3600 // 60, tot_time_s % 3600 % 60)
    logger.info(f"Processed {tot_samples} samples ({tot_seqs} sequences) in {h}h {m}m {s}s")
