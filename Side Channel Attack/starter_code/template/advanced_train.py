#!/usr/bin/env python3
"""
Advanced Model Training for Large-Scale Side-Channel Data
Trains sophisticated models on comprehensive datasets collected via advanced_collect.py

Usage:
    python3 advanced_train.py --dataset Datasets/advanced_dataset.json --models all
    python3 advanced_train.py --dataset Datasets/advanced_dataset.json --models ensemble,adversarial --epochs 100
"""

import argparse
import json
import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, Subset
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import sqlite3

# Import model architectures and training functions
from train import (
    FingerprintClassifier, ComplexFingerprintClassifier,
    AttentionFingerprintClassifier, DeepResidualClassifier,
    EnsembleClassifier, AdversarialFingerprintClassifier,
    train_advanced, train_with_mixup, evaluate, plot_training_history
)

class AdvancedTraceDataset(Dataset):
    """Dataset class for advanced side-channel traces with enhanced features"""
    
    def __init__(self, data_file: str, min_samples_per_class: int = 10):
        """
        Initialize dataset from advanced collection JSON file
        
        Args:
            data_file: Path to JSON dataset file
            min_samples_per_class: Minimum samples required per website class
        """
        self.data_file = data_file
        self.min_samples_per_class = min_samples_per_class
        
        print(f"📂 Loading advanced dataset from: {data_file}")
        
        with open(data_file, 'r') as f:
            raw_data = json.load(f)
        
        print(f"📊 Raw data entries: {len(raw_data)}")
        
        # Process and filter data
        self.samples = []
        self.labels = []
        self.website_names = []
        self.metadata = []
        
        # Group by website and count samples
        website_counts = {}
        website_samples = {}
        
        for item in raw_data:
            website = item["website"]
            trace_data = item["trace_data"]
            
            if len(trace_data) == 1000:  # Ensure correct size
                if website not in website_counts:
                    website_counts[website] = 0
                    website_samples[website] = []
                
                website_counts[website] += 1
                website_samples[website].append(item)
        
        # Filter websites with sufficient samples
        valid_websites = {w: count for w, count in website_counts.items() 
                         if count >= min_samples_per_class}
        
        print(f"📈 Website sample counts:")
        for website, count in website_counts.items():
            status = "✅" if count >= min_samples_per_class else "❌"
            print(f"  {status} {website}: {count} samples")
        
        # Build final dataset
        website_to_index = {}
        for website, samples in website_samples.items():
            if website in valid_websites:
                if website not in website_to_index:
                    website_to_index[website] = len(self.website_names)
                    self.website_names.append(website)
                
                website_idx = website_to_index[website]
                
                for sample in samples:
                    self.samples.append(sample["trace_data"])
                    self.labels.append(website_idx)
                    self.metadata.append({
                        "website": website,
                        "timestamp": sample.get("timestamp"),
                        "session_id": sample.get("metadata", {}).get("session_id"),
                        "load_time": sample.get("metadata", {}).get("load_time", 0)
                    })
        
        self.samples = np.array(self.samples, dtype=np.float32)
        self.labels = np.array(self.labels, dtype=np.int64)
        
        print(f"✅ Dataset loaded successfully:")
        print(f"   📊 Total samples: {len(self.samples)}")
        print(f"   🌐 Websites: {len(self.website_names)}")
        print(f"   📏 Feature size: {self.samples.shape[1]}")
        print(f"   🎯 Classes: {list(website_to_index.keys())}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        return torch.FloatTensor(self.samples[idx]), torch.LongTensor([self.labels[idx]])[0]
    
    def get_class_distribution(self):
        """Get distribution of samples per class"""
        unique, counts = np.unique(self.labels, return_counts=True)
        return {self.website_names[i]: count for i, count in zip(unique, counts)}

def analyze_dataset(dataset: AdvancedTraceDataset):
    """Analyze and visualize dataset characteristics"""
    
    print("\n📊 Dataset Analysis")
    print("=" * 50)
    
    # Class distribution
    distribution = dataset.get_class_distribution()
    print("🎯 Class Distribution:")
    for website, count in distribution.items():
        print(f"   {website}: {count} samples")
    
    # Sample statistics
    samples = dataset.samples
    print(f"\n📈 Feature Statistics:")
    print(f"   Min value: {np.min(samples):.3f}")
    print(f"   Max value: {np.max(samples):.3f}")
    print(f"   Mean: {np.mean(samples):.3f}")
    print(f"   Std: {np.std(samples):.3f}")
    
    # Save distribution plot
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    websites = list(distribution.keys())
    counts = list(distribution.values())
    plt.bar(range(len(websites)), counts)
    plt.xlabel('Website')
    plt.ylabel('Number of Samples')
    plt.title('Dataset Class Distribution')
    plt.xticks(range(len(websites)), [w.split('/')[-1] for w in websites], rotation=45)
    
    plt.subplot(1, 2, 2)
    plt.hist(samples.flatten(), bins=50, alpha=0.7)
    plt.xlabel('Feature Value')
    plt.ylabel('Frequency')
    plt.title('Feature Value Distribution')
    
    plt.tight_layout()
    os.makedirs("analysis", exist_ok=True)
    plt.savefig("analysis/advanced_dataset_analysis.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Analysis plot saved: analysis/advanced_dataset_analysis.png")

def train_advanced_models(dataset: AdvancedTraceDataset, args):
    """Train advanced models on the comprehensive dataset"""
    
    print(f"\n🚀 Advanced Model Training")
    print("=" * 50)
    
    # Split dataset
    splitter = StratifiedShuffleSplit(n_splits=1, train_size=0.8, random_state=42)
    train_idx, test_idx = next(splitter.split(dataset.samples, dataset.labels))
    
    # Create data loaders with larger batch sizes for efficiency
    batch_size = min(128, len(train_idx) // 10)  # Adaptive batch size
    train_loader = DataLoader(Subset(dataset, train_idx), batch_size=batch_size, shuffle=True, drop_last=True, num_workers=4)
    test_loader = DataLoader(Subset(dataset, test_idx), batch_size=batch_size, drop_last=True, num_workers=4)
    
    print(f"🎯 Training set: {len(train_idx)} samples")
    print(f"🎯 Test set: {len(test_idx)} samples") 
    print(f"🎯 Batch size: {batch_size}")
    
    input_size = dataset.samples.shape[1]
    num_classes = len(dataset.website_names)
    hidden_size = 256  # Larger hidden size for complex data
    
    models_dir = "saved_models_advanced"
    os.makedirs(models_dir, exist_ok=True)
    
    # Model configurations for advanced training
    model_configs = {
        'ensemble': {
            'class': EnsembleClassifier,
            'lr': 0.0001,
            'epochs': args.epochs,
            'train_func': train_with_mixup,
            'description': 'Advanced Ensemble with MixUp augmentation'
        },
        'adversarial': {
            'class': AdversarialFingerprintClassifier,
            'lr': 0.0005,
            'epochs': args.epochs,
            'train_func': train_advanced,
            'description': 'Adversarial training with domain adaptation'
        },
        'attention': {
            'class': AttentionFingerprintClassifier,
            'lr': 0.0003,
            'epochs': args.epochs,
            'train_func': train_advanced,
            'description': 'Multi-head attention mechanisms'
        },
        'residual': {
            'class': DeepResidualClassifier,
            'lr': 0.0002,
            'epochs': args.epochs,
            'train_func': train_advanced,
            'description': 'Deep residual connections'
        },
        'complex': {
            'class': ComplexFingerprintClassifier,
            'lr': 0.001,
            'epochs': args.epochs,
            'train_func': train_advanced,
            'description': 'Enhanced CNN with BatchNorm'
        }
    }
    
    # Filter requested models
    if 'all' in args.models:
        selected_models = list(model_configs.keys())
    else:
        selected_models = [m for m in args.models if m in model_configs]
    
    print(f"🎯 Training models: {selected_models}")
    
    results = {}
    
    for model_name in selected_models:
        config = model_configs[model_name]
        
        print(f"\n🧠 Training {model_name.upper()} Model")
        print(f"📋 {config['description']}")
        print("-" * 40)
        
        # Initialize model
        model = config['class'](input_size, hidden_size, num_classes=num_classes)
        optimizer = optim.Adam(model.parameters(), lr=config['lr'], weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()
        
        save_path = os.path.join(models_dir, f"advanced_{model_name}_classifier.pth")
        
        # Train model
        start_time = datetime.now()
        
        if config['train_func'] == train_with_mixup:
            best_accuracy = train_with_mixup(
                model, train_loader, test_loader, criterion, optimizer,
                config['epochs'], save_path, alpha=0.3
            )
            training_time = (datetime.now() - start_time).total_seconds()
            
        else:  # train_advanced
            _, train_losses, train_accs, test_accs = train_advanced(
                model, train_loader, test_loader, criterion, optimizer,
                config['epochs'], save_path
            )
            
            training_time = (datetime.now() - start_time).total_seconds()
            best_accuracy = max(test_accs)
            
            # Save training plot
            plot_path = f"analysis/advanced_{model_name}_training.png"
            plot_training_history(train_losses, train_accs, test_accs, plot_path)
        
        # Evaluate final model
        model.load_state_dict(torch.load(save_path)['model_state_dict'] if 'model_state_dict' in torch.load(save_path) else torch.load(save_path))
        
        print(f"\n📊 {model_name.upper()} Model Evaluation:")
        evaluate(model, test_loader, dataset.website_names)
        
        results[model_name] = {
            'accuracy': best_accuracy,
            'training_time': training_time,
            'model_path': save_path
        }
        
        print(f"⏱️  Training time: {training_time:.1f}s")
        print(f"🎯 Best accuracy: {best_accuracy:.4f}")
    
    # Summary
    print(f"\n🎉 Advanced Training Complete!")
    print("=" * 50)
    print("📊 Model Performance Summary:")
    
    for model_name, result in results.items():
        print(f"   🧠 {model_name:12}: {result['accuracy']:.4f} ({result['training_time']:.1f}s)")
    
    print(f"\n💾 Models saved in: {models_dir}")
    print(f"📈 Analysis plots in: analysis/")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Advanced Side-Channel Model Training')
    parser.add_argument('--dataset', '-d', type=str, default='Datasets/advanced_dataset.json',
                       help='Path to advanced dataset JSON file')
    parser.add_argument('--models', '-m', nargs='+', default=['all'],
                       choices=['all', 'ensemble', 'adversarial', 'attention', 'residual', 'complex'],
                       help='Models to train')
    parser.add_argument('--epochs', '-e', type=int, default=50,
                       help='Training epochs')
    parser.add_argument('--min-samples', type=int, default=10,
                       help='Minimum samples per website class')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only analyze dataset, skip training')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset):
        print(f"❌ Dataset file not found: {args.dataset}")
        print(f"💡 Run: python3 advanced_collect.py --traces 100 --websites all")
        return
    
    # Load dataset
    try:
        dataset = AdvancedTraceDataset(args.dataset, min_samples_per_class=args.min_samples)
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return
    
    # Analyze dataset
    analyze_dataset(dataset)
    
    if args.analyze_only:
        print("📊 Dataset analysis complete!")
        return
    
    # Check if we have enough data for training
    if len(dataset.website_names) < 2:
        print(f"❌ Insufficient classes for training (need ≥2, got {len(dataset.website_names)})")
        print(f"💡 Collect more data with: python3 advanced_collect.py --traces 50")
        return
    
    if len(dataset) < 50:
        print(f"⚠️  Small dataset ({len(dataset)} samples). Consider collecting more data.")
    
    # Train models
    try:
        results = train_advanced_models(dataset, args)
        
        print(f"\n🚀 Training successful! Best model accuracies:")
        best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
        print(f"🏆 Champion: {best_model[0]} ({best_model[1]['accuracy']:.4f})")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
