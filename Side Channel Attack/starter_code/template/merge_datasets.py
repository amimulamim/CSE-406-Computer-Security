#!/usr/bin/env python3
import json
import sys
import os

def merge_json_files(input_files, output_file="Datasets/dataset_merged.json"):
    merged_data = []

    for file_path in input_files:
        if not os.path.isfile(file_path):
            print(f"✗ File not found: {file_path}")
            continue

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    print(f"✗ Skipped {file_path}: not a list at top level")
                    continue
                merged_data.extend(data)
                print(f"✓ Merged {len(data)} items from {file_path}")
        except Exception as e:
            print(f"✗ Failed to read {file_path}: {e}")

    # Write merged output
    with open(output_file, "w") as f:
        json.dump(merged_data, f, indent=2)

    print(f"\n✅ Merged {len(merged_data)} total items into '{output_file}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} file1.json file2.json ...")
        sys.exit(1)

    merge_json_files(sys.argv[1:])
