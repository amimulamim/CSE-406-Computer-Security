import os
import json
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, Subset
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedShuffleSplit

# Configuration
DEFAULT_DATASET_PATH = "Datasets/dataset.json"
MODELS_DIR = "saved_models"
BATCH_SIZE = 64
EPOCHS = 50  
LEARNING_RATE = 1e-3
TRAIN_SPLIT = 0.8 
INPUT_SIZE = 1000  
HIDDEN_SIZE = 128

os.makedirs(MODELS_DIR, exist_ok=True)

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

    return all_preds, all_labels

def main():
    # Get dataset path from command line argument or use default
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATASET_PATH
    
    print(f"📂 Loading dataset from: {dataset_path}")
    dataset = TraceDataset(dataset_path)
    print(f"✅ Loaded {len(dataset)} traces from {len(dataset.website_names)} websites")

    splitter = StratifiedShuffleSplit(n_splits=1, train_size=TRAIN_SPLIT, random_state=42)
    train_idx, test_idx = next(splitter.split(dataset.samples, dataset.labels))

    # Use drop_last=True to prevent BatchNorm issues with single-sample batches
    train_loader = DataLoader(Subset(dataset, train_idx), batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
    test_loader = DataLoader(Subset(dataset, test_idx), batch_size=BATCH_SIZE, drop_last=True)

    print("\n📶 Training baseline FingerprintClassifier...")
    model = FingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes=len(dataset.website_names))
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()
    save_path = os.path.join(MODELS_DIR, "fingerprint_classifier.pth")
    train(model, train_loader, test_loader, criterion, optimizer, EPOCHS, save_path)

    model.load_state_dict(torch.load(save_path))
    evaluate(model, test_loader, dataset.website_names)

    print("\n🧠 Training ComplexFingerprintClassifier...")
    model2 = ComplexFingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes=len(dataset.website_names))
    optimizer = optim.Adam(model2.parameters(), lr=LEARNING_RATE)
    save_path = os.path.join(MODELS_DIR, "complex_fingerprint_classifier.pth")
    train(model2, train_loader, test_loader, criterion, optimizer, EPOCHS, save_path)

    model2.load_state_dict(torch.load(save_path))
    evaluate(model2, test_loader, dataset.website_names)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(f"Usage: {sys.argv[0]} [dataset_path]")
        print(f"Example: {sys.argv[0]} Datasets/dataset_merged.json")
        print(f"Default dataset: {DEFAULT_DATASET_PATH}")
        sys.exit(1)
    
    main()
