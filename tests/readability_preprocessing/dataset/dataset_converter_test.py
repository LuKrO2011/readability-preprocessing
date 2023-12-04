import os

from src.readability_preprocessing.dataset.dataset_converter import (
    BWCodeLoader,
    BWCsvLoader,
    CsvFolderToDataset,
    DornCodeLoader,
    DornCsvLoader,
    KrodCodeLoader,
    ScalabrioCodeLoader,
    ScalabrioCsvLoader,
    TwoFoldersToDataset,
)
from tests.readability_preprocessing.utils.utils import DirTest


class TestDataConversion(DirTest):
    test_data_dir = "res/raw_data"

    def test_ScalabrioDataConversion(self):
        # Test loading and saving Scalabrio dataset
        data_dir = os.path.join(self.test_data_dir, "scalabrio")
        csv = os.path.join(data_dir, "scores.csv")
        snippets_dir = os.path.join(data_dir, "Snippets")

        # Load the data
        data_loader = CsvFolderToDataset(
            csv_loader=ScalabrioCsvLoader(), code_loader=ScalabrioCodeLoader()
        )
        dataset = data_loader.convert_to_dataset(csv, snippets_dir)

        # Store the dataset
        dataset.save_to_disk(self.output_dir)

        # Check if the dataset was saved successfully
        assert os.path.exists(self.output_dir)

    def test_BWDataConversion(self):
        # Test loading and saving BW dataset
        data_dir = os.path.join(self.test_data_dir, "bw")
        csv = os.path.join(data_dir, "scores.csv")
        snippets_dir = os.path.join(data_dir, "Snippets")

        # Load the data
        data_loader = CsvFolderToDataset(
            csv_loader=BWCsvLoader(), code_loader=BWCodeLoader()
        )
        dataset = data_loader.convert_to_dataset(csv, snippets_dir)

        # Store the dataset
        dataset.save_to_disk(self.output_dir)

        # Check if the dataset was saved successfully
        assert os.path.exists(self.output_dir)

    def test_DornDataConversion(self):
        # Test loading and saving Dorn dataset
        data_dir = os.path.join(self.test_data_dir, "dorn")
        csv = os.path.join(data_dir, "scores.csv")
        snippets_dir = os.path.join(data_dir, "Snippets")

        # Load the data
        data_loader = CsvFolderToDataset(
            csv_loader=DornCsvLoader(), code_loader=DornCodeLoader()
        )
        dataset = data_loader.convert_to_dataset(csv, snippets_dir)

        # Store the dataset
        dataset.save_to_disk(self.output_dir)

        # Check if the dataset was saved successfully
        assert os.path.exists(self.output_dir)

    def test_KrodDataConversion(self):
        # Test loading and saving Krodinger dataset
        data_dir = os.path.join(self.test_data_dir, "krod")
        original = os.path.join(data_dir, "original")
        rdh = os.path.join(data_dir, "rdh")

        # Load the data
        data_loader = TwoFoldersToDataset(
            original_loader=KrodCodeLoader(),
            rdh_loader=KrodCodeLoader(name_appendix="_rdh"),
        )
        dataset = data_loader.convert_to_dataset(original, rdh)

        # Store the dataset
        dataset.save_to_disk(self.output_dir)

        # Check if the dataset was saved successfully
        assert os.path.exists(self.output_dir)
