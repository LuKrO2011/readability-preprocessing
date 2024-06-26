import json
import os
from pathlib import Path

import matplotlib.pyplot as plt

from readability_preprocessing.evaluation.font_utils import set_custom_font

set_custom_font()

CURR_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = CURR_DIR / "../../../"
# INPUT_PATH = ROOT_DIR / 'tests/res/sampled/merge_distances.json'
INPUT_PATH = ROOT_DIR / "src/res/merge_distances.json"

REVERSE_X_AXIS = True
PLOT_DIFF_TO_PREV = True

title = None

with open(INPUT_PATH) as file:
    data = json.load(file)

# Remove last entries
data = data[:-2]

# Extract merge distances and create a list for x-axis (number of stratas)
num_stratas = [entry["new_num_stratas"] for entry in data]
merge_distances = [entry["merge_distance"] for entry in data]
diff_to_prev = [entry["diff_to_prev"] for entry in data]

# make diff to prev absolute
diff_to_prev = [abs(i) for i in diff_to_prev]

# Invert the x-axis if specified
if REVERSE_X_AXIS:
    fig, ax1 = plt.subplots(figsize=(6, 3))

    # Plot merge distances on the first y-axis
    ax1.plot(
        num_stratas,
        merge_distances,
        marker="o",
        markersize=5,
        linestyle="-",
        label="Merge distances",
    )
    ax1.set_xlabel("Number of strata")
    ax1.set_ylabel("Merge distances")
    ax1.tick_params("y")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.plot(
        num_stratas,
        diff_to_prev,
        marker="s",
        markersize=5,
        linestyle="-",
        color="tab:grey",
        label="Difference to previous",
    )
    ax2.set_ylabel("Difference to previous")
    ax2.tick_params("y")

    # Invert the x-axis for ax1
    ax1.invert_xaxis()

    # Highlight points at x=4
    highlight_points = [4]
    highlight_color = "red"
    for i, x in enumerate(num_stratas):
        if x in highlight_points:
            ax2.scatter(
                x,
                diff_to_prev[i],
                color=highlight_color,
                zorder=5,
                s=30,
                marker="s",
            )

    # Combine legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()

    if PLOT_DIFF_TO_PREV:
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2)
    else:
        ax1.legend(lines_1, labels_1, loc="center left")

    plt.xticks(list(reversed(num_stratas)), [str(i) for i in reversed(num_stratas)])

    # plt.title(title)
    plt.tight_layout()
    plt.savefig("strata_merge_distances.pdf", format="pdf", bbox_inches="tight")
    plt.show()

else:
    print("Not implemented yet")
