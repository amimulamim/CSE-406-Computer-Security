#!/usr/bin/env python3
import json
import sys
import os
import glob
import subprocess

def validate_file(file_path):
    """Validate a dataset file using dataset_validator.py. Returns True if valid."""
    try:
        # Run the validator and capture the return code
        result = subprocess.run([
            sys.executable, 'dataset_validator.py', file_path
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # Return True if validation passed (exit code 0)
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  Error running validator on {os.path.basename(file_path)}: {e}")
        return False

def discover_and_validate_files():
    """Discover JSON files in the to_merge directory and validate them."""
    to_merge_dir = "Datasets/to_merge"
    if not os.path.isdir(to_merge_dir):
        print(f"✗ Directory not found: {to_merge_dir}")
        return []
    
    all_files = glob.glob(os.path.join(to_merge_dir, "*.json"))
    all_files.sort()  # Sort for consistent processing order
    
    print(f"📁 Found {len(all_files)} JSON files in {to_merge_dir}")
    print("🔍 Validating files before merging...")
    print("")
    
    valid_files = []
    invalid_files = []
    
    for file_path in all_files:
        filename = os.path.basename(file_path)
        print(f"🔍 Validating {filename}...", end=" ")
        
        if validate_file(file_path):
            print("✅ Valid")
            valid_files.append(file_path)
        else:
            print("❌ Invalid - SKIPPED")
            invalid_files.append(file_path)
    
    print("")
    print(f"📊 Validation Summary:")
    print(f"   ✅ Valid files: {len(valid_files)}")
    print(f"   ❌ Invalid files: {len(invalid_files)}")
    
    if invalid_files:
        print(f"   🚫 Skipped files:")
        for file_path in invalid_files:
            print(f"      - {os.path.basename(file_path)}")
    
    print("")
    
    if len(valid_files) == 0:
        print("❌ No valid files found to merge!")
        return []
    
    print(f"✅ Will merge {len(valid_files)} valid files:")
    for file_path in valid_files:
        print(f"   - {os.path.basename(file_path)}")
    
    return valid_files

def process_single_file(file_path, file_index, total_files):
    """Process a single JSON file and return its data."""
    # Show progress for every 10 files or if it's one of the first/last files
    if file_index <= 5 or file_index % 10 == 0 or file_index > total_files - 5:
        progress = f"[{file_index}/{total_files}]"
    else:
        progress = ""
        
    if not os.path.isfile(file_path):
        if progress:
            print(f"✗ {progress} File not found: {os.path.basename(file_path)}")
        return []

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            if not isinstance(data, list):
                if progress:
                    print(f"✗ {progress} Skipped {os.path.basename(file_path)}: not a list")
                return []
            
            if progress:
                print(f"✓ {progress} Merged {len(data)} items from {os.path.basename(file_path)}")
            elif file_index % 50 == 0:  # Show progress every 50 files even without detailed output
                print(f"   ... processed {file_index}/{total_files} files ...")
            
            return data
    except Exception as e:
        if progress:
            print(f"✗ {progress} Failed to read {os.path.basename(file_path)}: {e}")
        return []

def merge_json_files(input_files=None, output_file="Datasets/dataset_merged.json", validate_files=True):
    """Merge multiple JSON files into one, with optional validation."""
    merged_data = []
    
    # If no input files specified, automatically find and validate files in to_merge directory
    if input_files is None:
        if validate_files:
            input_files = discover_and_validate_files()
        else:
            # Legacy behavior - discover without validation
            input_files = glob.glob("Datasets/to_merge/*.json")
            input_files.sort()
            print(f"📁 Found {len(input_files)} JSON files (validation skipped)")
        
        if not input_files:
            return

    print(f"\n🔄 Processing {len(input_files)} files...")
    
    for i, file_path in enumerate(input_files, 1):
        file_data = process_single_file(file_path, i, len(input_files))
        merged_data.extend(file_data)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write merged output
    with open(output_file, "w") as f:
        json.dump(merged_data, f, indent=2)

    print(f"\n✅ Successfully merged {len(merged_data)} total items from {len(input_files)} files")
    print(f"📄 Output saved to: {output_file}")

def auto_merge_to_merge_directory():
    """Automatically merge all valid JSON files in Datasets/to_merge/"""
    print("🔄 Auto-merging datasets from Datasets/to_merge/ (with validation)")
    merge_json_files()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided - auto-merge from to_merge directory
        auto_merge_to_merge_directory()
    elif len(sys.argv) == 2 and sys.argv[1] in ["--auto", "-a"]:
        # Explicit auto-merge flag
        auto_merge_to_merge_directory()
    else:
        # Manual file specification
        if len(sys.argv) < 2:
            print(f"Usage: {sys.argv[0]} [--auto|-a] OR {sys.argv[0]} file1.json file2.json ...")
            print("Examples:")
            print(f"  {sys.argv[0]}                    # Auto-merge from Datasets/to_merge/")
            print(f"  {sys.argv[0]} --auto             # Auto-merge from Datasets/to_merge/") 
            print(f"  {sys.argv[0]} file1.json file2.json  # Manual file specification")
            sys.exit(1)
        merge_json_files(sys.argv[1:])
