# Datasets Folder

This folder contains all dataset files used in the side channel attack project.

## Files

### Core Dataset Files
- **`dataset.json`** - Raw dataset exported from the database, contains traces with website URLs and indices
- **`converted_dataset.json`** - Processed dataset grouped by website, ready for machine learning training
- **`dataset_merged.json`** - Merged dataset from multiple sources (if applicable)

### Backup/Archive Files  
- **`dataset_fixed.json`** - Backup of the dataset after corruption fix
- **`dataset_ap.json`** - Additional dataset (access point related, if applicable)

### Configuration Files
- **`tuning_checkpoint.json`** - Hyperparameter tuning checkpoint and results

## File Usage

- **collect.py** → Exports to `dataset.json`
- **data_converter.py** → Reads `dataset.json`, outputs `converted_dataset.json`
- **train.py** → Reads `converted_dataset.json`
- **hyperparam_tuning.py** → Reads `converted_dataset.json`, saves checkpoint to `tuning_checkpoint.json`
- **merge_datasets.py** → Outputs to `dataset_merged.json`
- **dataset_validator.py** → Validates any dataset JSON file

## Validation

To validate any dataset file:
```bash
python3 dataset_validator.py Datasets/dataset.json
python3 dataset_validator.py Datasets/converted_dataset.json
```

## Conversion Workflow

1. **Collect data**: `python3 collect.py` → `Datasets/dataset.json`
2. **Convert for ML**: `python3 data_converter.py` → `Datasets/converted_dataset.json`  
3. **Train model**: `python3 train.py` (reads `Datasets/converted_dataset.json`)
