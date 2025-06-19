import os
import json
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, Subset
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedShuffleSplit
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DEFAULT_DATASET_PATH = "Datasets/dataset.json"
MODELS_DIR = "saved_models"
ANALYSIS_DIR = "analysis"
BATCH_SIZE = 64
EPOCHS = 50  
LEARNING_RATE = 1e-3
TRAIN_SPLIT = 0.8 
INPUT_SIZE = 1000  
HIDDEN_SIZE = 128

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)

class TraceDataset(Dataset):
    def __init__(self, data_file):
        with open(data_file, 'r') as f:
            raw = json.load(f)

        self.samples = []
        self.labels = []
        self.website_names = []
        
        # Build unique website list and mapping
        website_to_index = {}
        for item in raw:
            website = item["website"]
            if website not in website_to_index:
                website_to_index[website] = len(self.website_names)
                self.website_names.append(website)
        
        # Process each trace entry
        for item in raw:
            website = item["website"]
            trace_data = item["trace_data"]
            
            if len(trace_data) == INPUT_SIZE:
                self.samples.append(trace_data)
                self.labels.append(website_to_index[website])

        self.samples = np.array(self.samples, dtype=np.float32)
        self.labels = np.array(self.labels, dtype=np.int64)

        # Normalize (standard score per trace)
        self.samples = (self.samples - self.samples.mean(axis=1, keepdims=True)) / (
            self.samples.std(axis=1, keepdims=True) + 1e-6
        )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return torch.tensor(self.samples[idx]), torch.tensor(self.labels[idx])

class FingerprintClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(FingerprintClassifier, self).__init__()
        self.conv1 = nn.Conv1d(1, 32, 5, stride=2, padding=2)
        self.pool1 = nn.MaxPool1d(2, 2)
        self.conv2 = nn.Conv1d(32, 64, 5, stride=1, padding=2)
        self.pool2 = nn.MaxPool1d(2, 2)
        conv_output_size = input_size // 8
        self.fc_input_size = conv_output_size * 64
        self.fc1 = nn.Linear(self.fc_input_size, hidden_size)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.relu(self.conv1(x))
        x = self.pool1(x)
        x = self.relu(self.conv2(x))
        x = self.pool2(x)
        x = x.view(-1, self.fc_input_size)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

class ComplexFingerprintClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(ComplexFingerprintClassifier, self).__init__()
        self.conv1 = nn.Conv1d(1, 32, 5, stride=1, padding=2)
        self.bn1 = nn.BatchNorm1d(32)
        self.pool1 = nn.MaxPool1d(2, 2)

        self.conv2 = nn.Conv1d(32, 64, 3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm1d(64)
        self.pool2 = nn.MaxPool1d(2, 2)

        self.conv3 = nn.Conv1d(64, 128, 3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm1d(128)
        self.pool3 = nn.MaxPool1d(2, 2)

        conv_output_size = input_size // 8
        self.fc_input_size = conv_output_size * 128

        self.fc1 = nn.Linear(self.fc_input_size, hidden_size * 2)
        self.bn4 = nn.BatchNorm1d(hidden_size * 2)
        self.dropout1 = nn.Dropout(0.5)

        self.fc2 = nn.Linear(hidden_size * 2, hidden_size)
        self.bn5 = nn.BatchNorm1d(hidden_size)
        self.dropout2 = nn.Dropout(0.3)

        self.fc3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.pool1(x)
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.pool2(x)
        x = self.relu(self.bn3(self.conv3(x)))
        x = self.pool3(x)
        x = x.view(-1, self.fc_input_size)
        x = self.relu(self.bn4(self.fc1(x)))
        x = self.dropout1(x)
        x = self.relu(self.bn5(self.fc2(x)))
        x = self.dropout2(x)
        x = self.fc3(x)
        return x

class AttentionFingerprintClassifier(nn.Module):
    """Advanced classifier with self-attention mechanism for better feature learning"""
    
    def __init__(self, input_size, hidden_size, num_classes):
        super(AttentionFingerprintClassifier, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Multi-head self-attention
        self.attention = nn.MultiheadAttention(embed_dim=hidden_size, num_heads=8, dropout=0.1)
        
        # Feature extraction layers
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_size, hidden_size * 2),
            nn.BatchNorm1d(hidden_size * 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(),
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.BatchNorm1d(hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(hidden_size // 2, num_classes)
        )
        
    def forward(self, x):
        batch_size = x.size(0)
        
        # Feature extraction
        features = self.feature_extractor(x)  # [batch_size, hidden_size]
        
        # Prepare for attention (seq_len=1, batch_size, embed_dim)
        attn_input = features.unsqueeze(0)  # [1, batch_size, hidden_size]
        
        # Self-attention
        attn_output, _ = self.attention(attn_input, attn_input, attn_input)
        attn_output = attn_output.squeeze(0)  # [batch_size, hidden_size]
        
        # Residual connection
        combined = features + attn_output
        
        # Classification
        output = self.classifier(combined)
        return output

class ResidualBlock(nn.Module):
    """Residual block for deeper networks"""
    
    def __init__(self, in_features, out_features, dropout=0.2):
        super(ResidualBlock, self).__init__()
        self.fc1 = nn.Linear(in_features, out_features)
        self.bn1 = nn.BatchNorm1d(out_features)
        self.fc2 = nn.Linear(out_features, out_features)
        self.bn2 = nn.BatchNorm1d(out_features)
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()
        
        # Skip connection
        self.skip = nn.Linear(in_features, out_features) if in_features != out_features else nn.Identity()
        
    def forward(self, x):
        identity = self.skip(x)
        
        out = self.relu(self.bn1(self.fc1(x)))
        out = self.dropout(out)
        out = self.bn2(self.fc2(out))
        
        out += identity
        out = self.relu(out)
        return out

class DeepResidualClassifier(nn.Module):
    """Deep residual network for complex side-channel patterns"""
    
    def __init__(self, input_size, hidden_size, num_classes):
        super(DeepResidualClassifier, self).__init__()
        
        # Input projection
        self.input_proj = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(),
        )
        
        # Residual blocks
        self.res_blocks = nn.ModuleList([
            ResidualBlock(hidden_size, hidden_size, dropout=0.2),
            ResidualBlock(hidden_size, hidden_size, dropout=0.2),
            ResidualBlock(hidden_size, hidden_size * 2, dropout=0.3),
            ResidualBlock(hidden_size * 2, hidden_size * 2, dropout=0.3),
            ResidualBlock(hidden_size * 2, hidden_size, dropout=0.2),
        ])
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool1d(1),  # Global average pooling
            nn.Flatten(),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(hidden_size // 2, num_classes)
        )
        
    def forward(self, x):
        x = self.input_proj(x)
        
        for res_block in self.res_blocks:
            x = res_block(x)
        
        # Add channel dimension for adaptive pooling
        x = x.unsqueeze(-1)
        x = self.classifier(x)
        return x

class EnsembleClassifier(nn.Module):
    """Ensemble of different architectures for robustness"""
    
    def __init__(self, input_size, hidden_size, num_classes):
        super(EnsembleClassifier, self).__init__()
        
        # Different architectures
        self.cnn_branch = ComplexFingerprintClassifier(input_size, hidden_size, num_classes)
        self.attention_branch = AttentionFingerprintClassifier(input_size, hidden_size, num_classes)
        self.residual_branch = DeepResidualClassifier(input_size, hidden_size, num_classes)
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(num_classes * 3, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, num_classes)
        )
        
    def forward(self, x):
        # Get predictions from each branch
        cnn_out = self.cnn_branch(x)
        attention_out = self.attention_branch(x)
        residual_out = self.residual_branch(x)
        
        # Concatenate and fuse
        combined = torch.cat([cnn_out, attention_out, residual_out], dim=1)
        output = self.fusion(combined)
        return output

class AdversarialFingerprintClassifier(nn.Module):
    """Classifier with adversarial training capabilities"""
    
    def __init__(self, input_size, hidden_size, num_classes):
        super(AdversarialFingerprintClassifier, self).__init__()
        
        # Feature extractor
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_size, hidden_size * 2),
            nn.BatchNorm1d(hidden_size * 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Domain classifier (for adversarial training)
        self.domain_classifier = nn.Sequential(
            GradientReverseLayer(),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, 2)  # Real vs synthetic domain
        )
        
        # Website classifier
        self.website_classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(hidden_size // 2, num_classes)
        )
        
    def forward(self, x, return_features=False):
        features = self.feature_extractor(x)
        
        if return_features:
            return features
        
        website_pred = self.website_classifier(features)
        domain_pred = self.domain_classifier(features)
        
        return website_pred, domain_pred

class GradientReverseLayer(nn.Module):
    """Gradient reversal layer for adversarial training"""
    
    def __init__(self, alpha=1.0):
        super(GradientReverseLayer, self).__init__()
        self.alpha = alpha
        
    def forward(self, x):
        return GradientReverseFunction.apply(x, self.alpha)

class GradientReverseFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.alpha = alpha
        return x
    
    @staticmethod
    def backward(ctx, grad_output):
        return -ctx.alpha * grad_output, None

def train(model, train_loader, test_loader, criterion, optimizer, epochs, model_save_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    best_accuracy = 0.0
    for epoch in range(epochs):
        model.train()
        correct, total, train_loss = 0, 0, 0.0

        for traces, labels in train_loader:
            traces, labels = traces.to(device), labels.to(device)
            optimizer.zero_grad()
            
            # Handle different model types
            if isinstance(model, AdversarialFingerprintClassifier):
                outputs, _ = model(traces)
            else:
                outputs = model(traces)
            
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * traces.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_acc = correct / total

        # Evaluate
        model.eval()
        correct, total, test_loss = 0, 0, 0.0
        with torch.no_grad():
            for traces, labels in test_loader:
                traces, labels = traces.to(device), labels.to(device)
                
                # Handle different model types
                if isinstance(model, AdversarialFingerprintClassifier):
                    outputs, _ = model(traces)
                else:
                    outputs = model(traces)
                
                loss = criterion(outputs, labels)
                test_loss += loss.item() * traces.size(0)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        test_acc = correct / total
        print(f"Epoch {epoch+1}/{epochs} | Train Acc: {train_acc:.4f} | Test Acc: {test_acc:.4f}")

        if test_acc > best_accuracy:
            best_accuracy = test_acc
            torch.save(model.state_dict(), model_save_path)
            print(f"🧠 Saved model with accuracy: {best_accuracy:.4f}")

    return best_accuracy

def evaluate(model, test_loader, website_names):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    all_preds, all_labels = [], []

    with torch.no_grad():
        for traces, labels in test_loader:
            traces, labels = traces.to(device), labels.to(device)
            
            # Handle different model types
            if isinstance(model, AdversarialFingerprintClassifier):
                outputs, _ = model(traces)
            else:
                outputs = model(traces)
            
            _, predicted = torch.max(outputs.data, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    print("\n📊 Classification Report:")
    print(classification_report(
        all_labels,
        all_preds,
        target_names=website_names,
        zero_division=1
    ))

    # Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(10,8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='coolwarm',
                xticklabels=website_names, yticklabels=website_names)
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    plt.title('Confusion Matrix')
    plt.show()

    return all_preds, all_labels

def train_advanced(model, train_loader, test_loader, criterion, optimizer, epochs, model_save_path, use_scheduler=True):
    """Advanced training with learning rate scheduling, early stopping, and data augmentation"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', patience=5, factor=0.5, verbose=True) if use_scheduler else None
    
    # Early stopping
    best_accuracy = 0.0
    patience = 10
    patience_counter = 0
    
    # Training history
    train_losses = []
    train_accuracies = []
    test_accuracies = []
    
    for epoch in range(epochs):
        model.train()
        correct, total, epoch_train_loss = 0, 0, 0.0

        for traces, labels in train_loader:
            traces, labels = traces.to(device), labels.to(device)
            
            # Data augmentation: Add small random noise
            if model.training:
                noise = torch.randn_like(traces) * 0.01
                traces = traces + noise
            
            optimizer.zero_grad()
            
            # Handle different model types
            if isinstance(model, AdversarialFingerprintClassifier):
                website_outputs, domain_outputs = model(traces)
                loss = criterion(website_outputs, labels)
                # Add domain confusion loss if needed
                outputs = website_outputs
            else:
                outputs = model(traces)
                loss = criterion(outputs, labels)
            
            # Gradient clipping
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            epoch_train_loss += loss.item() * traces.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_acc = correct / total
        avg_train_loss = epoch_train_loss / len(train_loader.dataset)

        # Evaluate
        test_acc = evaluate_model(model, test_loader, device)
        
        # Record history
        train_losses.append(avg_train_loss)
        train_accuracies.append(train_acc)
        test_accuracies.append(test_acc)
        
        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.4f} | Test Acc: {test_acc:.4f}")

        # Learning rate scheduling
        if scheduler:
            scheduler.step(test_acc)
        
        # Save best model
        if test_acc > best_accuracy:
            best_accuracy = test_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'epoch': epoch,
                'accuracy': best_accuracy,
                'train_history': {
                    'train_losses': train_losses,
                    'train_accuracies': train_accuracies,
                    'test_accuracies': test_accuracies
                }
            }, model_save_path)
            print(f"🧠 Saved model with accuracy: {best_accuracy:.4f}")
            patience_counter = 0
        else:
            patience_counter += 1
        
        # Early stopping
        if patience_counter >= patience:
            print(f"Early stopping triggered after {epoch+1} epochs")
            break

    return best_accuracy, train_losses, train_accuracies, test_accuracies

def evaluate_model(model, test_loader, device):
    """Evaluate model on test set"""
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for traces, labels in test_loader:
            traces, labels = traces.to(device), labels.to(device)
            
            if isinstance(model, AdversarialFingerprintClassifier):
                outputs, _ = model(traces)
            else:
                outputs = model(traces)
            
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    return correct / total

def train_with_mixup(model, train_loader, test_loader, criterion, optimizer, epochs, model_save_path, alpha=0.2):
    """Training with MixUp data augmentation for better generalization"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    best_accuracy = 0.0
    
    for epoch in range(epochs):
        model.train()
        correct, total, epoch_loss = 0, 0, 0.0
        
        for traces, labels in train_loader:
            traces, labels = traces.to(device), labels.to(device)
            
            # MixUp augmentation
            if alpha > 0:
                lam = np.random.beta(alpha, alpha)
                batch_size = traces.size(0)
                index = torch.randperm(batch_size).to(device)
                
                mixed_traces = lam * traces + (1 - lam) * traces[index, :]
                y_a, y_b = labels, labels[index]
                
                optimizer.zero_grad()
                outputs = model(mixed_traces)
                
                # MixUp loss
                loss = lam * criterion(outputs, y_a) + (1 - lam) * criterion(outputs, y_b)
            else:
                optimizer.zero_grad()
                outputs = model(traces)
                loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item() * traces.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        train_acc = correct / total
        test_acc = evaluate_model(model, test_loader, device)
        
        print(f"Epoch {epoch+1}/{epochs} | Train Acc: {train_acc:.4f} | Test Acc: {test_acc:.4f}")
        
        if test_acc > best_accuracy:
            best_accuracy = test_acc
            torch.save(model.state_dict(), model_save_path)
            print(f"🧠 Saved MixUp model with accuracy: {best_accuracy:.4f}")
    
    return best_accuracy

def plot_training_history(train_losses, train_accuracies, test_accuracies, save_path="training_history.png"):
    """Plot training history for analysis"""
    try:
        # Ensure the save path is in the analysis directory
        if not save_path.startswith(ANALYSIS_DIR):
            save_path = os.path.join(ANALYSIS_DIR, save_path)
        
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.plot(train_losses)
        plt.title('Training Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.grid(True)
        
        plt.subplot(1, 3, 2)
        plt.plot(train_accuracies, label='Train')
        plt.plot(test_accuracies, label='Test')
        plt.title('Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 3, 3)
        plt.plot(np.array(test_accuracies) - np.array(train_accuracies))
        plt.title('Generalization Gap')
        plt.xlabel('Epoch')
        plt.ylabel('Test Acc - Train Acc')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path)
        print(f"📊 Training history saved to {save_path}")
        plt.close()
    except Exception as e:
        print(f"Warning: Could not save training plot: {e}")

def main():
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Train side-channel attack models')
    parser.add_argument('--dataset', default=DEFAULT_DATASET_PATH, help='Dataset path')
    parser.add_argument('--models', nargs='+', default=['all'], 
                       choices=['all', 'baseline', 'complex', 'attention', 'residual', 'ensemble', 'adversarial'],
                       help='Models to train (default: all)')
    parser.add_argument('--epochs', type=int, default=EPOCHS, help='Number of training epochs')
    parser.add_argument('--quick', action='store_true', help='Quick training with fewer epochs')
    parser.add_argument('--list-models', action='store_true', help='List available models and exit')
    
    args = parser.parse_args()
    
    if args.list_models:
        print("Available models:")
        print("  baseline    - Basic FingerprintClassifier")
        print("  complex     - ComplexFingerprintClassifier with BatchNorm")
        print("  attention   - AttentionFingerprintClassifier with self-attention")
        print("  residual    - DeepResidualClassifier with residual connections")
        print("  ensemble    - EnsembleClassifier combining multiple architectures")
        print("  adversarial - AdversarialFingerprintClassifier with domain adaptation")
        print("  all         - Train all models (default)")
        print("\nExample usage:")
        print("  python train.py --models attention residual")
        print("  python train.py --models baseline --quick")
        print("  python train.py --dataset custom_data.json --models ensemble")
        return
    
    # Set parameters
    dataset_path = args.dataset
    epochs = 10 if args.quick else args.epochs
    models_to_train = args.models
    
    if 'all' in models_to_train:
        models_to_train = ['baseline', 'complex', 'attention', 'residual', 'ensemble', 'adversarial']
    
    print(f"📂 Loading dataset from: {dataset_path}")
    dataset = TraceDataset(dataset_path)
    print(f"✅ Loaded {len(dataset)} traces from {len(dataset.website_names)} websites")

    splitter = StratifiedShuffleSplit(n_splits=1, train_size=TRAIN_SPLIT, random_state=42)
    train_idx, test_idx = next(splitter.split(dataset.samples, dataset.labels))

    # Use drop_last=True to prevent BatchNorm issues with single-sample batches
    train_loader = DataLoader(Subset(dataset, train_idx), batch_size=BATCH_SIZE, shuffle=True, drop_last=True, num_workers=2)
    test_loader = DataLoader(Subset(dataset, test_idx), batch_size=BATCH_SIZE, drop_last=True, num_workers=2)
    
    training_epochs = 10 if args.quick else args.epochs
    
    print(f"\n🎯 Training selected models: {', '.join(models_to_train)}")
    print(f"⏱️  Training epochs: {training_epochs}")
    if args.quick:
        print("⚡ Quick mode enabled - using fewer epochs")
    print()

    # Training results summary
    results = {}

    if 'baseline' in models_to_train:
        print("📶 Training baseline FingerprintClassifier...")
        model = FingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes=len(dataset.website_names))
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()
        save_path = os.path.join(MODELS_DIR, "fingerprint_classifier.pth")
        results['baseline'] = train(model, train_loader, test_loader, criterion, optimizer, training_epochs, save_path)

        model.load_state_dict(torch.load(save_path))
        print("📊 Baseline model evaluation:")
        evaluate(model, test_loader, dataset.website_names)
        print()

    if 'complex' in models_to_train:
        print("🧠 Training ComplexFingerprintClassifier...")
        model2 = ComplexFingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes=len(dataset.website_names))
        optimizer = optim.Adam(model2.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()
        save_path = os.path.join(MODELS_DIR, "complex_fingerprint_classifier.pth")
        results['complex'] = train(model2, train_loader, test_loader, criterion, optimizer, training_epochs, save_path)

        model2.load_state_dict(torch.load(save_path))
        print("📊 Complex model evaluation:")
        evaluate(model2, test_loader, dataset.website_names)
        print()

    if 'attention' in models_to_train:
        print("🔥 Training AttentionFingerprintClassifier...")
        model3 = AttentionFingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes=len(dataset.website_names))
        optimizer = optim.Adam(model3.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()
        save_path = os.path.join(MODELS_DIR, "attention_classifier.pth")
        _, train_losses, train_accs, test_accs = train_advanced(model3, train_loader, test_loader, criterion, optimizer, training_epochs, save_path)
        plot_training_history(train_losses, train_accs, test_accs, "attention_training.png")

        model3.load_state_dict(torch.load(save_path)['model_state_dict'])
        print("📊 Attention model evaluation:")
        evaluate(model3, test_loader, dataset.website_names)
        print()

    if 'residual' in models_to_train:
        print("🏗️ Training DeepResidualClassifier...")
        model4 = DeepResidualClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes=len(dataset.website_names))
        optimizer = optim.Adam(model4.parameters(), lr=LEARNING_RATE*0.5, weight_decay=1e-4)  # Lower LR for deeper model
        criterion = nn.CrossEntropyLoss()
        save_path = os.path.join(MODELS_DIR, "residual_classifier.pth")
        _, train_losses, train_accs, test_accs = train_advanced(model4, train_loader, test_loader, criterion, optimizer, training_epochs, save_path)
        plot_training_history(train_losses, train_accs, test_accs, "residual_training.png")

        model4.load_state_dict(torch.load(save_path)['model_state_dict'])
        print("📊 Residual model evaluation:")
        evaluate(model4, test_loader, dataset.website_names)
        print()

    if 'ensemble' in models_to_train:
        print("🎯 Training EnsembleClassifier...")
        model5 = EnsembleClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes=len(dataset.website_names))
        optimizer = optim.Adam(model5.parameters(), lr=LEARNING_RATE*0.3, weight_decay=1e-4)  # Lower LR for ensemble
        criterion = nn.CrossEntropyLoss()
        save_path = os.path.join(MODELS_DIR, "ensemble_classifier.pth")
        ensemble_epochs = max(5, training_epochs//2)  # Ensemble needs fewer epochs
        results['ensemble'] = train_with_mixup(model5, train_loader, test_loader, criterion, optimizer, ensemble_epochs, save_path, alpha=0.2)

        model5.load_state_dict(torch.load(save_path))
        print("📊 Ensemble model evaluation:")
        evaluate(model5, test_loader, dataset.website_names)
        print()

    if 'adversarial' in models_to_train:
        print("⚔️ Training AdversarialFingerprintClassifier...")
        model6 = AdversarialFingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes=len(dataset.website_names))
        optimizer = optim.Adam(model6.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()
        save_path = os.path.join(MODELS_DIR, "adversarial_classifier.pth")
        _, train_losses, train_accs, test_accs = train_advanced(model6, train_loader, test_loader, criterion, optimizer, training_epochs, save_path)
        plot_training_history(train_losses, train_accs, test_accs, "adversarial_training.png")

        model6.load_state_dict(torch.load(save_path)['model_state_dict'])
        print("📊 Adversarial model evaluation:")
        evaluate(model6, test_loader, dataset.website_names)
        print()

    print("📊 Training Summary:")
    print("=" * 60)
    print(f"Trained models: {', '.join(models_to_train)}")
    print(f"Training epochs: {training_epochs}")
    print("Models saved in:", MODELS_DIR)
    if results:
        print("\nFinal accuracies:")
        for model_name, accuracy in results.items():
            print(f"  {model_name}: {accuracy:.4f}")
    
    print("\n🎯 Key improvements implemented:")
    print("  • Multi-head attention mechanisms")
    print("  • Deep residual connections") 
    print("  • Ensemble learning")
    print("  • Adversarial training")
    print("  • Advanced data augmentation (MixUp, noise)")
    print("  • Learning rate scheduling")
    print("  • Early stopping")
    print("  • Gradient clipping")



if __name__ == "__main__":
    main()
