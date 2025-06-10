#!/usr/bin/env python3
import json
import sys
from collections import defaultdict

# --- Configuration: your allowed sites in order ---
WEBSITES = [
    "https://cse.buet.ac.bd/moodle/",
    "https://google.com",
    "https://prothomalo.com",
]

def validate_and_count(path):
    errors = []
    counts = defaultdict(int)

    # 1) load JSON
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"✗ Failed to load JSON: {e}")
        return 1

    # 2) must be a list
    if not isinstance(data, list):
        print(f"✗ Top‐level JSON is a {type(data).__name__}, expected a list")
        return 1

    # 3) iterate entries
    for i, item in enumerate(data):
        prefix = f"Item #{i}"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: not an object (got {type(item).__name__})")
            continue

        # required keys
        for key in ('website', 'website_index', 'trace_data'):
            if key not in item:
                errors.append(f"{prefix}: missing key '{key}'")

        # website must be string
        url = item.get('website')
        if not isinstance(url, str):
            errors.append(f"{prefix}: 'website' is {type(url).__name__}, expected string")

        # website_index must be int and valid
        idx = item.get('website_index')
        if not isinstance(idx, int):
            errors.append(f"{prefix}: 'website_index' is {type(idx).__name__}, expected int")
        else:
            if not (0 <= idx < len(WEBSITES)):
                errors.append(f"{prefix}: website_index {idx} out of range [0..{len(WEBSITES)-1}]")
            else:
                # check that the URL matches
                if WEBSITES[idx] != url:
                    errors.append(f"{prefix}: website_index {idx} points to '{WEBSITES[idx]}', but found URL '{url}'")
                else:
                    # only count if mapping is correct
                    counts[idx] += 1

        # trace_data checks
        td = item.get('trace_data')
        if isinstance(td, list):
            if len(td) != 1000:
                errors.append(f"{prefix}: trace_data length is {len(td)}, expected 1000")
            else:
                bad = [j for j, x in enumerate(td) if not isinstance(x, int)]
                if bad:
                    sample = bad[:5]
                    errors.append(f"{prefix}: trace_data non-int at positions {sample}{'...' if len(bad)>5 else ''}")
        else:
            errors.append(f"{prefix}: trace_data is {type(td).__name__}, expected list")

    # 4) report
    if errors:
        print("✗ Validation FAILED with these issues:")
        for e in errors:
            print("  -", e)
        print()
    else:
        print("✓ All validation checks passed!\n")

    # 5) print counts by index
    print("Website counts:")
    for idx, site in enumerate(WEBSITES):
        print(f"  [{idx}] {site} → {counts.get(idx, 0)} items")

    # exit code: non-zero if there were any errors
    return 0 if not errors else 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} dataset.json")
        sys.exit(1)
    sys.exit(validate_and_count(sys.argv[1]))
