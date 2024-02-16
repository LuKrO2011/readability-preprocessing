from datasets import load_dataset, VerificationMode
from datasets import load_from_disk

# Load from hub
# ds = load_dataset("se2p/code-readability-krod", download_mode="force_redownload",
#                   verification_mode=VerificationMode.NO_CHECKS)
# ds = load_dataset("se2p/code-readability-krod")
# ds = ds['train']
# ds_as_list = ds.to_list()

# Load from disk
ds = load_from_disk("LuKrO/code-readability-krod-balanced")
ds_as_list = ds.to_list()

# Get the average "score" of the dataset
scores = [x['score'] for x in ds_as_list]
average_score = sum(scores) / len(scores)
print(average_score)

# Print the number of samples with a score of 4.5
count = 0
for x in ds_as_list:
    if x['score'] == 3.68:
        count += 1
print(f"Number of samples with a score of 3.68: {count}")

# Print the number of samples with a score of 1.5
count = 0
for x in ds_as_list:
    if x['score'] == 3.26:
        count += 1
print(f"Number of samples with a score of 3.26: {count}")

# Print the number of samples with a score of 3.26 that start with a method comment
count = 0
for x in ds_as_list:
    if x['score'] == 3.26 and x['code_snippet'].startswith("/**"):
        count += 1
print(
    f"Number of samples with a score of 3.26 that start with a method comment: {count}")
