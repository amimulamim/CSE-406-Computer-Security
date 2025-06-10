# hyperparam_tuning.py

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from sklearn.model_selection import StratifiedShuffleSplit

# Import your existing classes and train() from train.py
from train import TraceDataset, FingerprintClassifier, train as train_model

# Configuration
DATASET_PATH   = "converted_dataset.json"
INPUT_SIZE     = 1000
HIDDEN_SIZE    = 128
TRAIN_SPLIT    = 0.8
EPOCHS         = 50
REPEATS        = 10
LEARNING_RATES = [1e-2, 5e-3, 1e-3, 5e-4, 1e-4]
BATCH_SIZES    = [16, 32, 64, 128, 256]

# Ensure analysis folder exists
OUT_DIR = "analysis"
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    # 1) Load & split dataset
    dataset = TraceDataset(DATASET_PATH)
    splitter = StratifiedShuffleSplit(n_splits=1, train_size=TRAIN_SPLIT, random_state=42)
    train_idx, test_idx = next(splitter.split(dataset.samples, dataset.labels))
    train_ds = Subset(dataset, train_idx)
    test_ds  = Subset(dataset, test_idx)

    results = []

    # 2) Outer loop: hyperparameter grid
    total_configs = len(LEARNING_RATES) * len(BATCH_SIZES)
    for lr, bs in tqdm(product(LEARNING_RATES, BATCH_SIZES),
                       total=total_configs,
                       desc="Grid Search"):
        accs = []
        # 3) Inner loop: repeats per config
        for _ in tqdm(range(REPEATS),
                      desc=f"LR={lr}, BS={bs}",
                      leave=False):
            train_loader = DataLoader(train_ds, batch_size=bs, shuffle=True)
            test_loader  = DataLoader(test_ds,  batch_size=bs)

            model     = FingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes=len(dataset.website_names))
            optimizer = optim.Adam(model.parameters(), lr=lr)
            criterion = nn.CrossEntropyLoss()

            # Pass os.devnull so train_model won't save intermediate models
            acc = train_model(model, train_loader, test_loader, criterion, optimizer, EPOCHS, os.devnull)
            accs.append(acc)

        mean_acc = np.mean(accs)
        std_acc  = np.std(accs)
        results.append((lr, bs, mean_acc, std_acc))

    # 4) Organize for plotting
    arr = np.array(results)
    lrs = sorted({r[0] for r in results})
    bss = sorted({r[1] for r in results})
    acc_mat = np.zeros((len(lrs), len(bss)))
    std_mat = np.zeros_like(acc_mat)

    for lr, bs, mean_acc, std_acc in results:
        i, j = lrs.index(lr), bss.index(bs)
        acc_mat[i, j], std_mat[i, j] = mean_acc, std_acc

    # 5) Plot with error bars
    plt.figure(figsize=(10,6))
    for j, bs in enumerate(bss):
        plt.errorbar(lrs, acc_mat[:, j], yerr=std_mat[:, j],
                     marker='o', label=f'BS={int(bs)}')

    plt.xscale('log')
    plt.xlabel('Learning Rate (log scale)')
    plt.ylabel('Mean Test Accuracy')
    plt.title('Hyperparameter Tuning Results')
    plt.legend(title="Batch Sizes")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 6) Save plot into analysis/
    out_img = os.path.join(OUT_DIR, "hyperparam_tuning_results.png")
    plt.savefig(out_img, dpi=150)
    print(f"🔖 Plot saved to {out_img}")

    # 7) Display on screen
    plt.show()

if __name__ == "__main__":
    main()
