import json
from collections import defaultdict

with open("dataset.json", "r") as f:
    raw_data = json.load(f)

grouped = defaultdict(list)
for item in raw_data:
    grouped[item["website"]].append(item["trace_data"])

# Convert to grouped format
converted = [{"website": website, "traces": traces} for website, traces in grouped.items()]

with open("converted_dataset.json", "w") as f:
    json.dump(converted, f, indent=2)

print("✅ Converted to grouped format: converted_dataset.json")
