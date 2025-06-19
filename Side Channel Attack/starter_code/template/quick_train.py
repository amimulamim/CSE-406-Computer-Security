#!/usr/bin/env python3
"""
Quick Training Script - Train specific models easily
Usage examples:
  python3 quick_train.py --model basic
  python3 quick_train.py --model complex
  python3 quick_train.py --model attention --epochs 20
  python3 quick_train.py --model ensemble --quick
"""

import argparse
import sys
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from sklearn.model_selection import StratifiedShuffleSplit

# Import from the main training file
from train import (
    TraceDataset, FingerprintClassifier, ComplexFingerprintClassifier,
    AttentionFingerprintClassifier, DeepResidualClassifier, 
    EnsembleClassifier, AdversarialFingerprintClassifier,
    train, train_advanced, train_with_mixup, evaluate, plot_training_history
)

# Configuration
DEFAULT_DATASET_PATH = "Datasets/dataset.json"
MODELS_DIR = "saved_models"
BATCH_SIZE = 64
LEARNING_RATE = 1e-3
TRAIN_SPLIT = 0.8
INPUT_SIZE = 1000
HIDDEN_SIZE = 128

def get_model_and_config(model_name, num_classes):
    """Get model instance and training configuration"""
    configs = {
        'basic': {
            'model': FingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes),
            'epochs': 30,
            'lr': LEARNING_RATE,
            'save_path': os.path.join(MODELS_DIR, "basic_classifier.pth"),
            'train_func': train,
            'description': "Basic CNN classifier"
        },
        'complex': {
            'model': ComplexFingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes),
            'epochs': 40,
            'lr': LEARNING_RATE,
            'save_path': os.path.join(MODELS_DIR, "complex_classifier.pth"),
            'train_func': train,
            'description': "Complex CNN with batch normalization"
        },
        'attention': {
            'model': AttentionFingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes),
            'epochs': 50,
            'lr': LEARNING_RATE,
            'save_path': os.path.join(MODELS_DIR, "attention_classifier.pth"),
            'train_func': train_advanced,
            'description': "Multi-head attention classifier"
        },
        'residual': {
            'model': DeepResidualClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes),
            'epochs': 40,
            'lr': LEARNING_RATE * 0.5,  # Lower LR for deeper model
            'save_path': os.path.join(MODELS_DIR, "residual_classifier.pth"),
            'train_func': train_advanced,
            'description': "Deep residual network"
        },
        'ensemble': {
            'model': EnsembleClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes),
            'epochs': 25,
            'lr': LEARNING_RATE * 0.3,  # Lower LR for ensemble
            'save_path': os.path.join(MODELS_DIR, "ensemble_classifier.pth"),
            'train_func': train_with_mixup,
            'description': "Ensemble of multiple architectures"
        },
        'adversarial': {
            'model': AdversarialFingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes),
            'epochs': 30,
            'lr': LEARNING_RATE,
            'save_path': os.path.join(MODELS_DIR, "adversarial_classifier.pth"),
            'train_func': train_advanced,
            'description': "Adversarial training classifier"
        }
    }
    
    return configs.get(model_name)

def main():
    parser = argparse.ArgumentParser(description='Train specific side-channel attack models')
    parser.add_argument('--model', '-m', 
                       choices=['basic', 'complex', 'attention', 'residual', 'ensemble', 'adversarial'],
                       required=True,
                       help='Model to train')
    parser.add_argument('--dataset', '-d', 
                       default=DEFAULT_DATASET_PATH,
                       help='Path to dataset JSON file')
    parser.add_argument('--epochs', '-e', 
                       type=int, 
                       help='Number of epochs (overrides default)')
    parser.add_argument('--quick', '-q', 
                       action='store_true',
                       help='Quick training with fewer epochs')
    parser.add_argument('--lr', 
                       type=float,
                       help='Learning rate (overrides default)')
    parser.add_argument('--batch-size', '-b',
                       type=int,
                       default=BATCH_SIZE,
                       help='Batch size')
    
    args = parser.parse_args()
    
    print(f"🚀 Quick Training: {args.model.upper()} Model")
    print("=" * 50)
    
    # Load dataset
    print(f"📂 Loading dataset from: {args.dataset}")
    try:
        dataset = TraceDataset(args.dataset)
        print(f"✅ Loaded {len(dataset)} traces from {len(dataset.website_names)} websites")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        sys.exit(1)
    
    # Get model configuration
    config = get_model_and_config(args.model, len(dataset.website_names))
    if not config:
        print(f"❌ Unknown model: {args.model}")
        sys.exit(1)
    
    print(f"🧠 Model: {config['description']}")
    
    # Override epochs if specified
    if args.epochs:
        config['epochs'] = args.epochs
    elif args.quick:
        config['epochs'] = min(10, config['epochs'] // 3)
        print(f"⚡ Quick mode: reducing epochs to {config['epochs']}")
    
    # Override learning rate if specified
    if args.lr:
        config['lr'] = args.lr
    
    print(f"⚙️  Training configuration:")
    print(f"   - Epochs: {config['epochs']}")
    print(f"   - Learning rate: {config['lr']}")
    print(f"   - Batch size: {args.batch_size}")
    print()
    
    # Prepare data loaders
    splitter = StratifiedShuffleSplit(n_splits=1, train_size=TRAIN_SPLIT, random_state=42)
    train_idx, test_idx = next(splitter.split(dataset.samples, dataset.labels))
    
    train_loader = DataLoader(Subset(dataset, train_idx), 
                             batch_size=args.batch_size, 
                             shuffle=True, 
                             drop_last=True, 
                             num_workers=2)
    test_loader = DataLoader(Subset(dataset, test_idx), 
                            batch_size=args.batch_size, 
                            drop_last=True, 
                            num_workers=2)
    
    # Initialize model, optimizer, and criterion
    model = config['model']
    optimizer = optim.Adam(model.parameters(), lr=config['lr'], weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    print(f"🎯 Starting training...")
    print()
    
    # Train the model
    try:
        if config['train_func'] == train_advanced:
            result = train_advanced(model, train_loader, test_loader, criterion, optimizer, 
                                  config['epochs'], config['save_path'])
            if len(result) == 4:  # Returns training history
                best_accuracy, train_losses, train_accs, test_accs = result
                
                # Save training plot
                plot_name = f"{args.model}_training_plot.png"
                plot_training_history(train_losses, train_accs, test_accs, plot_name)
                print(f"📊 Training plot saved: {plot_name}")
            else:
                best_accuracy = result
                
        elif config['train_func'] == train_with_mixup:
            best_accuracy = train_with_mixup(model, train_loader, test_loader, criterion, optimizer,
                                           config['epochs'], config['save_path'], alpha=0.2)
        else:  # Regular train function
            best_accuracy = train(model, train_loader, test_loader, criterion, optimizer,
                                config['epochs'], config['save_path'])
        
        print()
        print(f"✅ Training completed!")
        print(f"🎯 Best accuracy: {best_accuracy:.4f}")
        print(f"💾 Model saved: {config['save_path']}")
        
        # Load best model and evaluate
        if config['train_func'] == train_advanced:
            # Load from checkpoint format
            checkpoint = torch.load(config['save_path'])
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            # Load from simple state dict
            model.load_state_dict(torch.load(config['save_path']))
        
        print()
        print("📊 Final evaluation:")
        evaluate(model, test_loader, dataset.website_names)
        
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("🎉 Training session complete!")

if __name__ == "__main__":
    main()
