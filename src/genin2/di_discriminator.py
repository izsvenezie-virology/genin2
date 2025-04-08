import importlib_resources, joblib
from collections import namedtuple
from genin2.utils import alignment_refs, pairwise_alignment, encode_sequence


n_segs = len(alignment_refs.keys())
SubgenotypePrediction = namedtuple('SubgenotypePrediction', ['subgenotype', 'confidence', 'segments'])


class DIDiscriminator:
    def __init__(self):
        self.dd_models = joblib.load(importlib_resources.files('genin2').joinpath('dd.xz'))
        self.model_build_date = self.dd_models['build_date']
    
    def predict_sample(self, sample):
        segments_pred = {sn: self._predict_segment(sn, nt) for sn, nt in sample.items()}
        subg_scores = {subg: list(segments_pred.values()).count(subg) / n_segs for subg in set(segments_pred.values())}
        subgenotype = max(subg_scores.items(), key=lambda x: x[1])
        return SubgenotypePrediction(subgenotype[0], subgenotype[1], segments_pred)

    def _predict_segment(self, seg_name, seg_seq):
        aligned = pairwise_alignment(alignment_refs[seg_name], seg_seq)
        return self.dd_models[seg_name].predict([encode_sequence(aligned)])[0]
