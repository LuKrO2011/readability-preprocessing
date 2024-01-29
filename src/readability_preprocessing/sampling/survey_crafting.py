import logging
import os
import shutil
from pathlib import Path

import numpy as np

from readability_preprocessing.extractors.diff_extractor import compare_java_files
from readability_preprocessing.utils.utils import list_non_hidden

default_sample_amount: dict[str, int] = {
    "stratum0": 5,
    "stratum1": 10,
    "stratum2": 5,
    "stratum3": 10,
}


class Snippet:
    """
    A snippet is a code snippet. It belongs to a RDH.
    """

    def __init__(self, name: str):
        """
        Initialize the snippet.
        :param name:
        """
        self.stratum = None
        self.rdh = None
        self.name = name

    def set_rdh(self, rdh):
        """
        Set the rdh the snippet belongs to.
        :param rdh: The rdh the snippet belongs to.
        :return: None
        """
        self.rdh = rdh

    def set_stratum(self, stratum):
        """
        Set the stratum the snippet belongs to.
        :param stratum: The stratum the snippet belongs to.
        :return: None
        """
        self.stratum = stratum

    def get_path(self, root: Path) -> Path:
        """
        Get the path of the snippet.
        :return: The path of the snippet.
        """
        return root / self.stratum.name / self.rdh.name / self.name


class RDH:
    """
    A RDH is one readability-decreasing-heuristic variant generated by a single config.
    A RDH belongs to a stratum.
    """

    def __init__(self, name: str, snippets: dict[str, Snippet]):
        """
        Initialize the RDH.
        :param name: The name of the RDH.
        :param snippets: The list of unused snippets.
        """
        self.name = name
        self.snippets = snippets
        for snippet in snippets.values():
            snippet.set_rdh(self)
        self.stratum = None

    def set_stratum(self, stratum):
        """
        Set the stratum the RDH belongs to.
        :param stratum: The stratum the RDH belongs to.
        :return: None
        """
        self.stratum = stratum


class Method:
    """
    A method combines an original snippet with a no modification snippet and a dict of
    rdh snippets. A method belongs to a stratum.
    """

    def __init__(self, original: Snippet, nomod: Snippet, rdhs: dict[str, Snippet]):
        """
        Initialize the method.
        :param original: The original snippet.
        :param nomod: The nomod snippet.
        :param rdhs: The rdh snippets.
        """
        self.stratum = None
        self.original = original
        self.nomod = nomod
        self.rdhs = rdhs

    def set_stratum(self, stratum):
        """
        Set the stratum the method belongs to.
        :param stratum: The stratum the method belongs to.
        :return: None
        """
        self.stratum = stratum
        self.original.set_stratum(stratum)
        self.nomod.set_stratum(stratum)
        for rdh in self.rdhs.values():
            rdh.set_stratum(stratum)

    def compare_to_nomod(self, root: Path) -> list[Snippet]:
        """
        Compare each rdh snippet to the nomod snippet and return the not-different
        snippets.
        :param root: The root directory.
        :return: The not-different snippets.
        """
        not_diff = []
        for rdh in self.rdhs.values():
            is_diff = compare_java_files(self.nomod.get_path(root), rdh.get_path(root))
            if not is_diff:
                not_diff.append(rdh)
        return not_diff


class Stratum:
    """
    A stratum is a group of RDHs that are similar according to the stratified sampling.
    """

    def __init__(self, name: str, methods: list[Method]):
        """
        Initialize the stratum.
        :param name: The name of the stratum.
        :param methods: The methods belonging to the stratum.
        """
        self.name = name
        self.methods = methods
        for method in self.methods:
            method.set_stratum(self)


class Survey:
    """
    A survey contains a list of snippets.
    """

    def __init__(self, snippets):
        """
        Initialize the survey.
        :param snippets: The list of snippets belonging to the survey.
        """
        self.snippets = snippets


class SurveyCrafter:
    """
    A class for crafting surveys from the given input directory and save them to the
    given output directory.
    """

    def __init__(self, input_dir: str,
                 output_dir: str,
                 snippets_per_sheet: int = 20,
                 num_sheets: int = 20,
                 sample_amount: dict[str, float] = None,
                 original_name: str = "methods",
                 nomod_name: str = "none"):
        """
        Initialize the survey crafter.
        :param input_dir: The input directory with the stratas, rdhs and snippets.
        :param output_dir: The output directory to save the surveys to.
        :param snippets_per_sheet: How many snippets per sheet.
        :param sample_amount: How many original snippets per stratum.
        :param num_sheets: How many sheets.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.snippets_per_sheet = snippets_per_sheet
        self.num_sheets = num_sheets
        self.sample_amount = (sample_amount or
                              default_sample_amount.copy())
        self.original_name = original_name
        self.nomod_name = nomod_name

    def craft_surveys(self) -> None:
        """
        Craft surveys from the given input directory and save them to the given
        output directory.
        :return: None
        """
        strata = self.craft_stratas()

        # Log information about the stratas
        logging.info(f"Strata: Number of stratas: {len(strata)}")
        for stratum in strata.values():
            logging.info(f"{stratum.name}: Number of methods: {len(stratum.methods)}")

        stratas_with_methods = self.sample_methods(strata)
        not_diff_snippets = []
        for statum in stratas_with_methods.values():
            for method in statum.methods:
                not_diff_snippets += method.compare_to_nomod(Path(self.input_dir))

        # Log information about the not different snippets
        logging.info(
            f"Strata: Number of not different snippets: {len(not_diff_snippets)}")

        # TODO: Remove not diff and add new snippets

        # Create the surveys
        surveys = self.craft_sheets(stratas_with_methods)

        # Log information about the methods
        for stratum in stratas_with_methods.values():
            logging.info(f"{stratum.name}: Number of methods: {len(stratum.methods)}")

        # self._write_output(surveys)

    def craft_stratas(self) -> dict[str, Stratum]:
        """
        Craft the stratas from the input directory.
        :return: The stratas.
        """
        # Load the stratas and rdhs
        strata_names = self._load_stratas()
        rdh_names = self._load_rdhs(strata_names)

        # Convert the strats and rdhs to objects
        strata = {}
        for strata_name in strata_names:
            rdhs = {}
            for rdh_name in rdh_names[strata_name]:
                # Skip the nomod and original rdh
                if rdh_name == self.nomod_name or rdh_name == self.original_name:
                    continue

                # Add the rdh
                rdhs[rdh_name] = self._create_rdh(strata_name, rdh_name)

            # Add the original and nomod rdh
            original_rdh = self._create_rdh(strata_name, self.original_name)
            nomod_rdh = self._create_rdh(strata_name, self.nomod_name)

            # Create the methods from the rdhs, original and nomod
            methods = self._create_methods(rdhs, original_rdh, nomod_rdh)

            # Add the stratum
            strata[strata_name] = Stratum(strata_name, methods)

        # Remove empty rdhs and stratas
        # for stratum in strata:
        #     stratum.rdhs = {rdh_name: rdh for rdh_name, rdh in
        #                     stratum.rdhs.values() if len(rdh.snippets) > 0}
        # strata = {stratum_name: stratum for stratum_name, stratum in
        #           strata.values() if len(stratum.rdhs) > 0}

        return strata

    @staticmethod
    def _create_methods(rdhs: dict[str, RDH], original_rdh: RDH,
                        nomod_rdh: RDH) -> list[Method]:
        """
        Create the methods from the given rdhs, original and nomod.
        :param rdhs: The rdhs to create the methods from.
        :param original_rdh: The original rdh.
        :param nomod_rdh: The nomod rdh.
        :return: The methods.
        """
        methods = []
        for name, original_method in original_rdh.snippets.items():
            nomod_method = nomod_rdh.snippets[name]
            rdh_methods = {}
            for rdh in rdhs.values():
                rdh_methods[rdh.name] = rdh.snippets[name]
            methods.append(Method(original_method, nomod_method, rdh_methods))
        return methods

    def _create_rdh(self, strata_name: str, rdh_name: str) -> RDH:
        """
        Create a rdh from the given rdh name and strata name.
        :param rdh_name: The name of the rdh.
        :param strata_name: The name of the strata.
        :return: The rdh.
        """
        snippet_names = list_non_hidden(
            os.path.join(self.input_dir, strata_name, rdh_name))
        unused_snippets = {snippet_name: Snippet(snippet_name) for snippet_name in
                           snippet_names}
        return RDH(rdh_name, unused_snippets)

    def _load_rdhs(self, strata_names: list[str]) -> dict[str, list[str]]:
        """
        Load the rdhs from the input directory.
        :param strata_names: The names of the stratas.
        :return: The rdh names and probabilities.
        """
        # Load the rdh names as the names of the subdirectories
        rdh_names = {}
        for strata_name in strata_names:
            rdh_names[strata_name] = list_non_hidden(os.path.join(self.input_dir,
                                                                  strata_name))

        return rdh_names

    def _load_stratas(self) -> list[str]:
        """
        Load the stratas from the input directory.
        :return: The strata names and probabilities.
        """
        # Load the strata names as the names of the subdirectories
        strata_names = list_non_hidden(self.input_dir)
        return strata_names

    def _write_output(self, surveys: list[Survey]) -> None:
        """
        Write the output to the output directory.
        :param surveys: The surveys to write to the output directory.
        :return: The surveys.
        """
        # Create num_sheets output subdirectories
        for i in range(self.num_sheets):
            os.makedirs(os.path.join(self.output_dir, f"sheet_{i}"), exist_ok=True)

        # Copy the snippets to the output subdirectories with name "stratum_rdh_oldName"
        for i, survey in enumerate(surveys):
            for j, snippet in enumerate(survey.snippets):
                stratum = snippet.stratum.name
                rdh = snippet.rdh.name
                old_name = snippet.name
                new_name = f"{stratum}_{rdh}_{old_name}"
                shutil.copy(
                    os.path.join(self.input_dir, stratum, rdh, old_name),
                    os.path.join(self.output_dir, f"sheet_{i}", new_name),
                )

    def craft_sheets(self, strata: dict[str, Stratum]) -> list[Survey]:
        """
        Craft the surveys from the given strata. Each survey contains only one variant
        of each method. This is done as follows:
        sheet0 = [stratum0_methods_0, stratum0_none_1, stratum0_rdh0_2, stratum0_rdh1_3
        sheet1 = [stratum3_rdhx_x, stratum0_methods_1, stratum0_none_2, stratum0_rdh0_3
        sheet2 = [stratum3_rdhx_x-1, stratum3_rdhx_x, stratum0_methods_2, stratum0_none_3
        :param strata: The strata to sample from.
        :return: The sampled surveys.
        """
        # Create num_sheet surveys with different snippets according to the probs
        surveys = []
        for i in range(self.num_sheets):
            snippets = []
            for j in range(self.snippets_per_sheet):

                # Select a stratum, a rdh and a snippet
                stratum = _select_stratum(strata)
                rdh = _select_rdh(stratum.rdhs)
                snippet = _select(rdh.snippets)

                # Add the snippet to the list of snippets
                snippets.append(snippet)
                rdh.snippets.remove(snippet)

                # If there are no more strata, stop
                if len(strata) == 0:
                    logging.info(f"Strata: No more strata left.")
                    break

            # Add the survey to the list of surveys
            surveys.append(Survey(snippets))

            # If there are no more strata, stop
            if len(strata) == 0:
                logging.info(f"Strata: No more strata left.")
                break

        return surveys

    def sample_methods(self, strata: dict[str, Stratum],
                       sample_amount: dict[str, int] = None) -> dict[str, Stratum]:
        """
        Sample methods from the given rdh name.
        :param strata: The strata to sample from.
        :param sample_amount: The amount of methods to sample per stratum.
        :return: The sampled methods.
        """
        # Initialize the sample amount
        sample_amount = (sample_amount or self.sample_amount.copy())

        # Create empty sampled dict of strata
        sampled = {stratum_name: Stratum(stratum_name, []) for stratum_name in
                   strata.keys()}

        # Iterate over the strata and sample the methods
        for stratum in strata.values():
            methods = stratum.methods
            sampled_methods = []
            for i in range(sample_amount[stratum.name]):
                sampled_methods.append(methods.pop(np.random.randint(len(methods))))
            sampled[stratum.name].methods = sampled_methods

        return sampled
