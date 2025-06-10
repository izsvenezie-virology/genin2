from click import File
import importlib_resources, joblib, sys, csv, logging, time
from typing import List, Tuple, Optional
import genin2.update_checker as update_checker
from genin2.di_discriminator import DIDiscriminator
from genin2.utils import alignment_refs, read_fasta, pairwise_alignment, encode_sequence


__version__ = '2.1.3'
__author__ = 'Alessandro Sartori'
__contact__ = 'asartori@izsvenezie.it'

MIN_SEQ_COV = 0.7 # Minimum fraction of valid input NTs wrt the total length of the ref seq
MAX_COMPATIBLE_GENS = 3 # Maximum number of compatible genotypes to accept. If the prediction returns more, all will be discarded as unreliable

genotype2versions: dict[str, dict[str, str]] = {}
models: dict[str, any]
output_segments_order = ['PB2', 'PB1', 'PA', 'NP', 'NA', 'MP', 'NS']
di_discr: DIDiscriminator = None


def critical_error(msg: str, ex: Optional[Exception] = None) -> None:
    '''
    Log a critical error message and exit the program, optionally printing information about an exception

    Args:
        msg (str): The error message
        ex (Optional[Exception]): The exception to log. Defaults to None.
    '''
    if ex is not None:
        logging.critical('%s (%s, %s)', msg, type(ex).__name__, str(ex))
    else:
        logging.critical(msg)
    logging.critical("The above error was critical and the program will now exit")
    logging.critical("If you need assistance, you can open an issue at https://github.com/izsvenezie-virology/genin2/issues")
    sys.exit(-1)


def init_data() -> None:
    '''
    Load the compositions table and the prediction models. If an error occurs, a critical error is raised.
    '''
    global genotype2versions, models, di_discr

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
        logging.debug(f'Model build date: {models["build_date"]}')
    except Exception as e:
        critical_error("Couldn't load prediction models", e)

    try:
        di_discr = DIDiscriminator()
        logging.debug(f'DI discriminator models build date: {di_discr.model_build_date}')
    except Exception as e:
        critical_error("Couldn't load DI discriminator models", e)


def predict_sample(sample: dict[str, str]) -> Tuple[str, dict[str, Tuple[str, str]]]:
    ver_predictions: dict[str, Tuple[str, str]] = {}
    ver_predictions['MP'] = ('20', None)
    low_confidence = False

    for seg_name, seq in sample.items():
        if seg_name == 'MP':
            continue
        
        seq_cov = (len(seq) - seq.upper().count('N')) / len(alignment_refs[seg_name])
        if (seq_cov < MIN_SEQ_COV):
            ver_predictions[seg_name] = ('?', f'low quality ({int(seq_cov*100)}% valid)')
            low_confidence = True
            continue
        
        v, n = predict_seg_version(seg_name, seq)
        ver_predictions[seg_name] = (v, n)
        if n is not None:
            low_confidence = True
    
    for seg_name in alignment_refs.keys():
        if seg_name not in ver_predictions:
            ver_predictions[seg_name] = ('?', 'missing')
            low_confidence = True

    genotype = (None, None)
    compatible = get_compatible_genotypes({s: (v if x is None else '?') for s, (v, x) in ver_predictions.items()})
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
        logging.error(f"Failed to align and encode {seg_name} sequence. {type(e).__name__}, {str(e)}")
        return ('?', 'model error')

    model = models[seg_name]
    prediction = model.predict([encoded_seq])[0]
    return (prediction, None if prediction != '?' else 'unassigned')


def get_compatible_genotypes(versions: dict[str, str]) -> List[str]:
    '''
    Get all compatible genotypes based on the provided versions. If no genotypes are compatible, an empty list is returned.

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


def preload_samples(file: File) -> dict[str, dict[str, str]]:
    '''
    Load all samples contained in a FASTA file into a dictionary. The keys are the sample names and the values are dictionaries
    mapping each segment to the corresponding sequence.

    Args:
        file (File): A file handle of a FASTA file

    Returns:
        dict[str, dict[str, str]]: A dictionary mapping each sample name to a dictionary of segments and sequences
    '''
    samples = {}

    for name, seq in read_fasta(file):
        try:
            name, seg_name = name.rsplit('_', 1)
        except:
            logging.error("Discarding sequence, invalid FASTA header: %s", name)
            continue
        
        if seg_name not in alignment_refs.keys():
            if seg_name != 'HA' and seg_name != 'MP':
                logging.warning("Segment '%s' in sample '%s' is not recognized", seg_name, name)
            continue
        
        if name not in samples:
            samples[name] = {}

        if seg_name in samples[name]:
            logging.warning("Segment %s for sample %s was defined multiple times (keeping the last)", seg_name, name)
        samples[name][seg_name] = seq
    
    return samples


def prediction_to_tsv(sample_name, genotype, subgenotype, genotype_notes, ver_predictions):
    tsv_row, notes_col = [], []
    if genotype_notes is not None:
        notes_col.append(f'Genotype: {genotype_notes}')
    
    tsv_row = [sample_name, genotype, subgenotype or '']
    for seg in output_segments_order:
        v, n = ver_predictions[seg]
        tsv_row.append(v if n is None else '?')
        if n is not None:
            notes_col.append(f'{seg}: {n}')
    
    tsv_row.append('; '.join(notes_col))
    return tsv_row


def run(in_file: File, out_file: File, **kwargs):
    logging.basicConfig(
        level={'dbg': logging.DEBUG, 'inf': logging.INFO, 'wrn': logging.WARN, 'err': logging.ERROR}[kwargs['loglevel']],
        format='[%(levelname)s] %(message)s',
        stream=sys.stderr
    )
    logging.info("Initializing")
    update_checker.start_check()
    init_data()

    if 'min_seq_cov' in kwargs:
        global MIN_SEQ_COV
        MIN_SEQ_COV = kwargs['min_seq_cov']

    try:
        out_file.write('Sample Name\tGenotype\tSub-genotype\t' + '\t'.join(output_segments_order) + '\tNotes\n')
    except Exception as e:
        critical_error(f"Couldn't write to output file '{out_file}'", e)

    logging.info("Preloading samples")
    start_time = time.time()
    samples = preload_samples(in_file)
    logging.info("Read %d samples in %.1f seconds", len(samples), time.time() - start_time)

    logging.info("Starting analysis...")
    start_time = time.time()
    tot_seqs = 0
    for sample_name, sample in samples.items():
        logging.info(f"Processing {len(sample)} segments for {sample_name}")
        tot_seqs += len(sample)

        subgenotype = None
        (genotype, genotype_notes), ver_predictions = predict_sample(sample)
        if genotype == 'EA-2024-DI':
            subgenotype = di_discr.predict_sample(sample).subgenotype
        
        tsv_row = prediction_to_tsv(sample_name, genotype, subgenotype, genotype_notes, ver_predictions)
        out_file.write('\t'.join(tsv_row) + '\n')

    tot_time_s = time.time() - start_time
    h, m, s = (tot_time_s // 3600, tot_time_s % 3600 // 60, tot_time_s % 3600 % 60)
    logging.info(f"Processed {len(samples)} samples ({tot_seqs} sequences) in {h:.0f}h {m:.0f}m {s:.1f}s")

    latest_version = update_checker.get_result()
    if latest_version is not None and str(latest_version) != str(__version__):
        sys.stderr.writelines(f'''
  ╭───────────┬─────────────────────────┬───────────╮
  │           │  NEW VERSION AVAILABLE  │           │
  │           ╰─────────────────────────╯           │
  │                                                 │
  │  A new version of Genin2 has been released. To  │
  │  update your current installation, run:         │
  │    ╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶    │
  │          pip install --upgrade genin2           │
  │    ╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶    │
  │                                                 │
  │  To learn what's new (features and genotypes),  │
  │  please refer to the "CHANGELOG.md" file at:    │
  │                                                 │
  │  https://github.com/izsvenezie-virology/genin2  │
  │                                                 │
  │  Additional details:                            │
  │    • Installed version => v{__version__:17s}    │
  │    • Latest release => v{latest_version:20s}    │
  │                                                 │
  ╰─────────────────────────────────────────────────╯

''')
