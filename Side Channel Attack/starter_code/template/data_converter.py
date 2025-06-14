import json
import sys
from collections import defaultdict

# Get input file name from command line or default to 'dataset.json'
input_file = sys.argv[1] if len(sys.argv) > 1 else "dataset.json"
# output_file = "converted_" + input_file
output_file = "converted_dataset.json"

# Load data
with open(input_file, "r") as f:
    raw_data = json.load(f)

# Group trace data by website
grouped = defaultdict(list)
for item in raw_data:
    grouped[item["website"]].append(item["trace_data"])

# Convert to new format
converted = [{"website": website, "traces": traces} for website, traces in grouped.items()]

# Save to output file
with open(output_file, "w") as f:
    json.dump(converted, f, indent=2)

print(f"✅ Converted to grouped format: {output_file}")
