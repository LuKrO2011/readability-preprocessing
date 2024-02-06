from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt, pyplot
import scipy.stats as stats

from readability_preprocessing.evaluation.utils import DEFAULT_SURVEY_DIR, \
    load_json_file, SURVEY_DATA_DIR, PLOT_DIR

DEMOGRAPHICS_FILE_NAME = "demographics.json"
PLOT_X_LABEL = 'Applied Readability Decreasing Heuristic'
PLOT_Y_LABEL = 'Readability Rating'


class Rate:
    """
    A class representing a single rate.
    """

    def __init__(self, comment, rate, rater, solutions):
        self.comment = comment
        self.rate = rate
        self.rater = rater
        self.solutions = solutions

    def __str__(self):
        return (f"Rate(comment={self.comment}, rate={self.rate}, rater={self.rater}, "
                f"solutions={self.solutions})")


class SnippetData:
    """
    A class representing the data from a single JSON file containing the survey data
    of a single snippet.
    """

    def __init__(self, path, from_line, to_line, questions, rates):
        self.path = path
        self.from_line = from_line
        self.to_line = to_line
        self.questions = questions
        self.rates = [Rate(**rate_data) for rate_data in rates if
                      rate_data.get('rate') is not None]
        self.stratum = None
        self.rdh = None

    def __str__(self):
        return (f"JsonData(path={self.path}, from_line={self.from_line}, "
                f"to_line={self.to_line}, questions={self.questions}, "
                f"rates={self.rates})")

    @staticmethod
    def from_json(path, fromLine, toLine, questions, rates):
        """
        Create a SnippetData object from the JSON data
        :param path: The path to the snippet
        :param fromLine: The starting line of the snippet
        :param toLine: The ending line of the snippet
        :param questions: The questions asked in the survey
        :param rates: The rates given by the raters
        :return: The SnippetData object
        """
        return SnippetData(path, fromLine, toLine, questions, rates)

    def create_box_plot(self,
                        title: str = None):
        """
        Create a box plot for the rates of the snippet
        :param title: The title of the box plot
        """
        if title is None:
            title = f"Snippet: {self.path}"

        # Get the rates
        rates = [rate.rate for rate in self.rates]

        # Plotting
        plt.figure(figsize=(6, 8))
        plt.boxplot(rates)
        plt.xticks([1], ['Overall'])
        plt.ylabel('Rate')
        plt.title(title)

        # Update y-axis labels
        plt.yticks(plt.yticks()[0], ['{:.2f}'.format(rate) for rate in plt.yticks()[0]])

        # Show the plot
        plt.show()

    def calculate_statistics(self) -> dict[str, float]:
        """
        Calculate the statistics of the rates of the snippet
        :return: A dictionary containing the statistics
        """
        # Get the rates
        rates = [rate.rate for rate in self.rates]

        # Calculate the statistics
        statistics = {
            'min': min(rates),
            'max': max(rates),
            'mean': sum(rates) / len(rates),
            'median': sorted(rates)[len(rates) // 2],
            'std': (sum([(rate - sum(rates) / len(rates)) ** 2 for rate in rates]) / (
                len(rates) - 1)) ** 0.5
        }

        return statistics


class RDH:

    def __init__(self, name: str):
        """
        Initialize the RDH.
        :param name: The name of the RDH.
        """
        self.name = name
        self.snippets = {}

    def add_snippet(self, snippet):
        """
        Add a snippet to the RDH.
        :param snippet: The snippet to add.
        :return: None
        """
        self.snippets[snippet.path] = snippet

    def get_ratings(self):
        """
        Get the ratings of the snippets in the RDH
        :return: A list of ratings
        """
        ratings = []
        for snippet in self.snippets.values():
            ratings.extend([rate.rate for rate in snippet.rates])
        return ratings

    def calculate_statistics(self, mode: str = 'mean') -> dict[str, float]:
        """
        Calculate the statistics of the rates of the RDH.
        The mode can be 'mean', 'median', 'min', 'max', 'std'.
        For each snippet, the mode value is taken and all statistics are calculated
        for this RDH.
        :return: A dictionary containing the statistics
        """
        # Get the snippet statistics
        snippet_statistics = [snippet.calculate_statistics() for snippet in
                              self.snippets.values()]

        # Get the mode value for each statistic
        mode_values = []
        for statistic in snippet_statistics:
            mode_values.append(statistic[mode])

        # Calculate the statistics
        statistics = {
            'min': min(mode_values),
            'max': max(mode_values),
            'mean': sum(mode_values) / len(mode_values),
            'median': sorted(mode_values)[len(mode_values) // 2],
            'std': (sum([(value - sum(mode_values) / len(mode_values)) ** 2 for value in
                         mode_values]) / (len(mode_values) - 1)) ** 0.5
        }

        return statistics


class Stratum:

    def __init__(self, name: str):
        """
        Initialize the stratum.
        :param name: The name of the stratum.
        """
        self.name = name
        self.rdhs = {}

    def add_rdh(self, rdh: RDH):
        """
        Add an RDH to the stratum.
        :param rdh: The RDH to add.
        :return: None
        """
        self.rdhs[rdh.name] = rdh


def load_snippet_datas(input_path: Path = DEFAULT_SURVEY_DIR,
                       assign_stratum_and_rdh: bool = True) -> list[SnippetData]:
    """
    Load all json files in the directory and return a list of SnippetData objects
    :param input_path: The path to the directory containing the JSON files
    :param assign_stratum_and_rdh: Whether to assign stratum and RDH to the snippets
    :return: A list of SnippetData objects
    """
    # Get all the file paths
    file_paths = [file_path for file_path in input_path.iterdir()
                  if file_path.suffix == '.json'
                  and file_path.name != DEMOGRAPHICS_FILE_NAME]

    # Load the JSON data
    json_objects = [SnippetData.from_json(**load_json_file(file_path)) for file_path in
                    file_paths]

    if assign_stratum_and_rdh:
        for json_object in json_objects:
            split_path = json_object.path.split('_')
            json_object.stratum = split_path[1]
            json_object.rdh = split_path[2]

    return json_objects


def group_into_strats(json_objects: list[SnippetData]) -> dict[str, Stratum]:
    """
    Group the snippets into strata and RDHs
    :param json_objects: The list of all snippets
    :return: A dictionary containing the strata
    """
    # Create stratas
    stratas = {}
    for json_object in json_objects:
        if json_object.stratum not in stratas:
            stratas[json_object.stratum] = Stratum(json_object.stratum)

    # Create RDHs
    for json_object in json_objects:
        if json_object.rdh not in stratas[json_object.stratum].rdhs:
            stratas[json_object.stratum].add_rdh(RDH(json_object.rdh))

    # Add snippets to RDHs
    for json_object in json_objects:
        stratas[json_object.stratum].rdhs[
            json_object.rdh].add_snippet(json_object)

    return stratas


def data_and_cat_from_ratings(ratings: dict[list[int]],
                              order: list[str] = None) -> tuple[
    list[list[int]], list[str]]:
    """
    Extract the data and categories from the ratings
    :param ratings: The ratings as a dictionary of lists
    :param order: The order of the categories
    :return: A tuple containing the data and categories
    """
    if order is None:
        order = ['methods', 'none']

    # Sort the ratings by name
    ratings = {
        k: v for k, v in sorted(ratings.items(), key=lambda item: (
            order.index(item[0]) if item[0] in order else float('inf'), item[0]))
    }

    # Extract the data and categories
    data = list(ratings.values())
    categories = list(map(str, ratings.keys()))
    return data, categories


def create_box_plot(ratings: dict[list[int]],
                    title: str = 'Box Plot of Ratings') -> pyplot:
    """
    Create a box plot for the given ratings
    :param ratings: The ratings as a dictionary of lists
    :param title: The title of the box plot
    :return: None
    """
    data, categories = data_and_cat_from_ratings(ratings)

    # Create box plot
    plt.boxplot(data, labels=categories)
    plt.title(title)
    plt.xlabel(PLOT_X_LABEL)
    plt.ylabel(PLOT_Y_LABEL)

    # Adjust category label display
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.5)

    # Add a mean line
    means = [np.mean(values) for values in data]
    plt.plot(range(1, len(categories) + 1), means, marker='o', linestyle='-',
             color='red', label='Mean')

    return plt


def create_bar_plot(ratings: dict[list[int]],
                    title: str = 'Bar Plot of Ratings') -> pyplot:
    """
    Create a bar plot for the mean of the given ratings
    :param ratings: The ratings as a dictionary of lists
    :param title: The title of the bar plot
    :return: None
    """
    data, categories = data_and_cat_from_ratings(ratings)

    # Create bar plot
    means = [np.mean(values) for values in data]
    plt.bar(categories, means)
    plt.title(title)
    plt.xlabel(PLOT_X_LABEL)
    plt.ylabel(PLOT_Y_LABEL)

    # Adjust category label display
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.5)

    return plt


def create_violin_plot(ratings: dict[list[int]],
                       title: str = 'Violin Plot of Ratings') -> pyplot:
    """
    Create a violin plot for the given ratings
    :param ratings: The ratings as a dictionary of lists
    :param title: The title of the violin plot
    :return: None
    """
    data, categories = data_and_cat_from_ratings(ratings)

    # Create violin plot
    plt.violinplot(data, showmeans=True, showmedians=False)
    plt.xticks(range(1, len(categories) + 1), categories)
    plt.title(title)
    plt.xlabel(PLOT_X_LABEL)
    plt.ylabel(PLOT_Y_LABEL)

    # Adjust category label display
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.5)

    # Add mean values as text
    for i, category in enumerate(categories):
        mean_value = round(sum(data[i]) / len(data[i]), 2)
        plt.text(i + 1, mean_value + 0.1, f' {mean_value:.2f}', color='black')

    # Add a horizontal line at the mean value of the first category
    first_category_mean = round(sum(data[0]) / len(data[0]), 2)
    plt.axhline(y=first_category_mean, color='red', linestyle='--',
                label=f'Mean of {categories[0]}', alpha=0.5)

    return plt


def normalize_ratings(ratings: dict[list[int]], sub: float = 0, div: float = 1) -> dict[
    list[int]]:
    """
    Normalize the ratings by the given key
    :param ratings: The ratings as a dictionary of lists
    :param sub: The amount to subtract from each rating
    :param div: The amount to divide each rating by
    :return: The normalized ratings
    """
    # Normalize the ratings
    normalized_ratings = {}
    for key, value in ratings.items():
        if key not in normalized_ratings:
            normalized_ratings[key] = []
        normalized_ratings[key].extend(
            [(rating - sub) / div for rating in value])
    return normalized_ratings


def create_normalized_bar_plot(ratings: dict[list[int]], normalize_by: str = 'methods',
                               title: str = 'Box Plot of Ratings') -> pyplot:
    """
    Create a normalized box plot for the given ratings
    :param ratings: The ratings as a dictionary of lists
    :param normalize_by: The key to normalize the ratings by
    :param title: The title of the box plot
    :return: None
    """
    # Get the mean value of the ratings "normalize_by"
    mean_value = sum(ratings[normalize_by]) / len(ratings[normalize_by])
    normalized_ratings = normalize_ratings(ratings, sub=mean_value)
    return create_bar_plot(normalized_ratings, title)


def extract_name(path: str) -> str:
    """
    Extract the name of the snippet from the path. The path is separated by
    underscores.
    :param path: The path to the snippet
    :return: The name of the snippet
    """
    return path.split('_')[-1]


def load_stratas(input_path: Path) -> dict[str, Stratum]:
    """
    Load the snippets from the JSON files and group them into stratas
    :param input_path: The path to the directory containing the JSON files
    :return: A dictionary containing the stratas
    """
    snippet_datas = []
    for survey_file in input_path.iterdir():
        snippet_datas.extend(load_snippet_datas(survey_file))

    return group_into_strats(snippet_datas)


def plot_rdhs_of_stratum(stratas: dict[str, Stratum], stratum: str) -> None:
    """
    Plot the RDHs of the stratum
    :param stratas: The stratas
    :param stratum: The stratum to plot
    :return: None
    """
    # Get the ratings for each RDH in the stratum
    ratings = {}
    for rdh in stratas[stratum].rdhs.values():
        ratings[rdh.name] = rdh.get_ratings()

    # Create a box plot for the ratings of each RDH in the stratum
    title = f"Violin Plot of Ratings for '{stratum}'"
    plt = create_violin_plot(ratings, title)

    # Store the violin plot
    plt.savefig(PLOT_DIR / f"{stratum}_violin_plot.png")
    plt.show()


def combine_by_rdh(stratas: dict[str, Stratum]) -> dict[str, list[int]]:
    """
    Combine the ratings of all strata by RDH
    :param stratas: The stratas
    :return: A dictionary containing the combined ratings
    """
    # Combine the ratings of all strata by RDH
    ratings = {}
    for stratum in stratas.values():
        for rdh in stratum.rdhs.values():
            if rdh.name not in ratings:
                ratings[rdh.name] = []
            ratings[rdh.name].extend(rdh.get_ratings())
    return ratings


def calculate_overall_score(ratings: dict[str, list[int]]) -> float:
    """
    Calculate the overall score of the ratings
    :param ratings: The ratings
    :return: The overall score
    """
    return sum([sum(rating) for rating in ratings.values()]) / sum(
        [len(rating) for rating in ratings.values()])


def plot_rdhs(stratas: dict[str, Stratum]) -> None:
    """
    Plot the RDHs over all strata
    :param stratas: The stratas
    :return: None
    """
    ratings = combine_by_rdh(stratas)

    # Create a box plot for the ratings of each RDH
    title = "Violin Plot of Ratings for All Strata"
    plt = create_violin_plot(ratings, title)

    # Store the violin plot
    plt.savefig(PLOT_DIR / "all_strata_violin_plot.png")
    plt.show()

    # Create a normalized box plot for the ratings of each RDH
    plt = create_normalized_bar_plot(ratings, normalize_by='methods',
                                     title="Box Plot of Relative Ratings with 'methods' as Baseline")

    # Store the normalized box plot
    plt.savefig(PLOT_DIR / "all_strata_normalized_bar_plot.png")
    plt.show()


def anova(ratings: dict[str, list[int]]) -> tuple[float, float]:
    """
    Perform a one-way ANOVA on the ratings
    :param ratings: The ratings
    :return: The F-statistic and the p-value
    """
    groups = list(ratings.values())
    statistic, p_value = stats.f_oneway(*groups)

    # Display the results
    print("One-Way ANOVA Results:")
    print("F-statistic:", statistic)
    print("P-value:", p_value)

    # Check for statistical significance
    alpha = 0.05
    if p_value < alpha:
        print(
            "Reject the null hypothesis; there are significant differences between group means.")
    else:
        print(
            "Fail to reject the null hypothesis; there are no significant differences between group means.")

    return statistic, p_value


def tukey(ratings: dict[str, list[int]], alpha: float = 0.05) -> None:
    """
    Perform pairwise Turkey's HSD test on the ratings
    :param ratings: The ratings
    :param alpha: The significance level
    :return: The results of the test
    """

    # Compare none to methods
    none = ratings['none']
    methods = ratings['methods']
    # results = stats.tukey_hsd(none, methods)
    results = stats.ttest_ind(none, methods)
    rejected = results[1] < alpha
    print("none-methods")
    print(results)
    print("Rejected:", rejected)
    print()

    # Compare none to all others pairwise
    for key, value in ratings.items():
        if key != 'none':
            # results = stats.tukey_hsd(none, value)
            results = stats.ttest_ind(none, value)
            rejected = results[1] < alpha
            print(f"none-{key}")
            print(results)
            print("Rejected:", rejected)
            print()


stratas = load_stratas(SURVEY_DATA_DIR)
# plot_rdhs(stratas)
# for stratum in stratas.keys():
#     plot_rdhs_of_stratum(stratas, stratum)

ratings = combine_by_rdh(stratas)
print("Overall Score:", calculate_overall_score(ratings))
anova(ratings)
print()
tukey(ratings)

# for stratum in stratas.keys():
#     ratings = {}
#     for rdh in stratas[stratum].rdhs.values():
#         ratings[rdh.name] = rdh.get_ratings()
#     print(f"Stratum: {stratum}")
#     anova(ratings)
#     print()