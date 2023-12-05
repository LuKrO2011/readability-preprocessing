import os

from src.readability_preprocessing.dataset.dataset_combiner import _load_datasets, \
    _remove_ambiguous_samples, combine_datasets
from tests.readability_preprocessing.utils.utils import DirTest, ENCODED_DIR

BW_DIR = ENCODED_DIR / "bw"
DORN_DIR = ENCODED_DIR / "dorn"
SCALABRIO_DIR = ENCODED_DIR / "scalabrio"


class DatasetCombinerTest(DirTest):

    @staticmethod
    def test_load_datasets():
        datasets = _load_datasets([BW_DIR, DORN_DIR, SCALABRIO_DIR])
        assert len(datasets) == 3

    @staticmethod
    def test_remove_ambiguous_samples():
        dataset = _load_datasets([BW_DIR])[0]
        dataset = _remove_ambiguous_samples(dataset, 0.5)
        assert len(dataset) == 50
        assert min(dataset["score"]) == 1.834710743801653
        assert max(dataset["score"]) == 4.347107438016529

    def test_combine_datasets(self):
        combine_datasets([BW_DIR, DORN_DIR, SCALABRIO_DIR], self.output_dir)
        assert len(os.listdir(self.output_dir)) == 3