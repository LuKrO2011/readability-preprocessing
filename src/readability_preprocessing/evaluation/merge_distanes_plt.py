import json
import os
from pathlib import Path

import matplotlib.pyplot as plt

CURR_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = CURR_DIR / '../../../'
INPUT_PATH = ROOT_DIR / 'tests/res/sampled/merge_distances.json'

REVERSE_X_AXIS = True
PLOT_DIFF_TO_PREV = True

with open(INPUT_PATH, 'r') as file:
    data = json.load(file)

# Extract merge distances and create a list for x-axis (number of stratas)
num_stratas = [entry['new_num_stratas'] for entry in data]
merge_distances = [entry['merge_distance'] for entry in data]
diff_to_prev = [entry['diff_to_prev'] for entry in data]

# Create the plot with two y-axes
fig, ax1 = plt.subplots(figsize=(8, 6))

# Plot merge distances on the first y-axis
ax1.plot(num_stratas, merge_distances, marker='o', linestyle='-', color='b',
         label='Merge Distances')
ax1.set_xlabel('Number of Stratas')
ax1.set_ylabel('Merge Distances', color='b')
ax1.tick_params('y', colors='b')
ax1.grid(True)

# Create a second y-axis for diff_to_prev
if PLOT_DIFF_TO_PREV:
    ax2 = ax1.twinx()
    ax2.plot(num_stratas, diff_to_prev, marker='s', linestyle='-', color='r',
             label='Diff to Previous')
    ax2.set_ylabel('Diff to Previous', color='r')
    ax2.tick_params('y', colors='r')

if REVERSE_X_AXIS:
    ax1.invert_xaxis()

# Combine legends
lines_1, labels_1 = ax1.get_legend_handles_labels()

if PLOT_DIFF_TO_PREV:
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')
else:
    ax1.legend(lines_1, labels_1, loc='upper right')

# Show the plot
plt.title('Merge Distances and Diff to Previous vs Number of Stratas')
plt.tight_layout()
plt.show()