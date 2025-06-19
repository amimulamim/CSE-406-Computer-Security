#!/usr/bin/env python3
import json
import sys
import os
import glob

def discover_input_files():
    """Discover JSON files in the to_merge directory."""
    to_merge_dir = "Datasets/to_merge"
    if not os.path.isdir(to_merge_dir):
        print(f"✗ Directory not found: {to_merge_dir}")
        return []
    
    input_files = glob.glob(os.path.join(to_merge_dir, "*.json"))
    input_files.sort()  # Sort for consistent processing order
    print(f"📁 Auto-discovered {len(input_files)} JSON files in {to_merge_dir}:")
    
    # Show first few and last few files if there are many
    if len(input_files) <= 10:
        for file_path in input_files:
            print(f"   - {os.path.basename(file_path)}")
    else:
        for file_path in input_files[:5]:
            print(f"   - {os.path.basename(file_path)}")
        print(f"   ... and {len(input_files) - 10} more files ...")
        for file_path in input_files[-5:]:
            print(f"   - {os.path.basename(file_path)}")
    
    return input_files

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

def merge_json_files(input_files=None, output_file="Datasets/dataset_merged.json"):
    """Merge multiple JSON files into one."""
    merged_data = []
    
    # If no input files specified, automatically find files in to_merge directory
    if input_files is None:
        input_files = discover_input_files()
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
    """Automatically merge all JSON files in Datasets/to_merge/"""
    print("🔄 Auto-merging datasets from Datasets/to_merge/")
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
