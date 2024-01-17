import json
from pathlib import Path

from matplotlib import pyplot as plt

from readability_preprocessing.evaluation.utils import DEFAULT_SURVEY_DIR


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


def load_json_file(file_path):
    """
    Load and parse JSON content from a file
    :param file_path: The path to the JSON file
    :return: A Python object parsed from the JSON file
    """
    with open(file_path, 'r') as file:
        content = json.load(file)
    return content


def load_snippet_datas(input_path: Path = DEFAULT_SURVEY_DIR) -> list[SnippetData]:
    """
    Load all json files in the directory and return a list of SnippetData objects
    :param input_path: The path to the directory containing the JSON files
    :return: A list of SnippetData objects
    """
    # Get all the file paths
    file_paths = [file_path for file_path in input_path.iterdir()
                  if file_path.suffix == '.json']

    # Load the JSON data
    json_objects = [SnippetData.from_json(**load_json_file(file_path)) for file_path in
                    file_paths]

    return json_objects


def create_combined_box_plot(snippet_datas: list[SnippetData]) -> None:
    """
    Create a single plot with multiple box plots for the rates of all snippets
    :param snippet_datas: The list of all snippets
    :return: None
    """
    # Extract the ratings for each snippet
    ratings = [[rate.rate for rate in snippet_data.rates] for snippet_data in
               snippet_datas]

    # Create the box plot
    plt.figure(figsize=(6, 8))
    plt.boxplot(ratings)
    plt.xticks(range(1, len(snippet_datas) + 1),
               [snippet_data.path for snippet_data in snippet_datas])
    plt.ylabel('Rating')
    plt.title('Rating of the snippets')

    # Show the plot
    plt.show()


def create_combined_violin_plot(snippet_datas: list[SnippetData]) -> None:
    """
    Create a single plot with multiple violin plots for the rates of all snippets
    :param snippet_datas: The list of all snippets
    :return: None
    """
    # Extract the ratings for each snippet
    ratings = [[rate.rate for rate in snippet_data.rates] for snippet_data in
               snippet_datas]

    # Create the violin plot
    plt.figure(figsize=(6, 8))
    plt.violinplot(ratings)
    plt.xticks(range(1, len(snippet_datas) + 1),
               [snippet_data.path for snippet_data in snippet_datas])
    plt.ylabel('Rating')
    plt.title('Rating of the snippets')

    # Show the plot
    plt.show()


def extract_name(path: str) -> str:
    """
    Extract the name of the snippet from the path. The path is separated by
    underscores.
    :param path: The path to the snippet
    :return: The name of the snippet
    """
    return path.split('_')[-1]


def create_mean_plot(snippet_datas: list[SnippetData]) -> None:
    """
    Create a plot of the mean of the ratings for each snippet
    :param snippet_datas: The list of all snippets
    :return: None
    """
    # Extract the ratings for each snippet
    ratings = [[rate.rate for rate in snippet_data.rates] for snippet_data in
               snippet_datas]

    # Calculate the mean of the ratings for each snippet
    means = [sum(rating) / len(rating) for rating in ratings]

    # Create the plot
    plt.figure(figsize=(6, 8))
    plt.plot(range(1, len(snippet_datas) + 1), means, 'o')
    plt.xticks(range(1, len(snippet_datas) + 1),
               [str(x) for x in range(1, len(snippet_datas) + 1)])
    plt.ylim(1, 5)
    plt.ylabel('Rating')
    plt.title('Rating of the snippets')

    # Annotate each point with the snippet name
    # for i, mean in enumerate(means):
    #     plt.annotate(extract_name(snippet_datas[i].path), (i + 1, mean))

    # Show the plotIch
    plt.show()


snippet_datas = load_snippet_datas()
# create_mean_plot(snippet_datas)
for snippet_data in snippet_datas:
    print(snippet_data.path)
    print(snippet_data.calculate_statistics())
    print()