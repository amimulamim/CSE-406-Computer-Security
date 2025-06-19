# Advanced Data Collection & Training Guide

## 🚀 Quick Start for Large-Scale Data Collection

### Prerequisites

```bash
# Install required packages (if not already installed)
pip install selenium chromedriver-autoinstaller
sudo apt-get install chromium-browser  # On Ubuntu/Debian
```

### 1. Automated Data Collection

#### Quick Collection (Recommended for Testing)
```bash
# Collect 50 traces from 3 main websites (fast)
python3 advanced_collect.py --traces 50 --websites "google.com,prothomalo.com,cse.buet.ac.bd/moodle" --headless

# Expected output: ~150 traces in ~10-15 minutes
```

#### Comprehensive Collection (Research Quality)
```bash
# Collect 100 traces from all 10 default websites
python3 advanced_collect.py --traces 100 --websites all --headless

# Expected output: ~1000 traces in ~60-90 minutes
```

#### Custom Collection
```bash
# Specific websites with custom parameters
python3 advanced_collect.py \
  --traces 200 \
  --websites "github.com,stackoverflow.com,reddit.com" \
  --output Datasets/custom_dataset.json \
  --delay-traces 1.5 \
  --delay-websites 3.0 \
  --headless
```

### 2. Advanced Model Training

#### Train on Collected Data
```bash
# Train all advanced models on collected data
python3 advanced_train.py --dataset Datasets/advanced_dataset.json --models all --epochs 100

# Train specific models with fewer epochs
python3 advanced_train.py --dataset Datasets/advanced_dataset.json --models ensemble,adversarial --epochs 50
```

#### Analysis Only
```bash
# Just analyze the dataset without training
python3 advanced_train.py --dataset Datasets/advanced_dataset.json --analyze-only
```

### 3. Collection Parameters

| Parameter | Description | Default | Recommended |
|-----------|-------------|---------|-------------|
| `--traces` | Traces per website | 100 | 50-200 |
| `--websites` | Target websites | all | "all" or comma-separated URLs |
| `--headless` | Browser mode | GUI | Use for automation |
| `--delay-traces` | Delay between traces (s) | 2.0 | 1.5-3.0 |
| `--delay-websites` | Delay between websites (s) | 5.0 | 3.0-10.0 |

### 4. Advanced Training Features

#### Model Types Available:
- **ensemble**: Multi-architecture ensemble with MixUp
- **adversarial**: Domain-adaptive training for robustness  
- **attention**: Multi-head attention mechanisms
- **residual**: Deep residual connections
- **complex**: Enhanced CNN with BatchNorm

#### Output Files:
- `advanced_dataset.json` - ML-ready dataset
- `advanced_webfingerprint.db` - SQLite database with metadata
- `saved_models_advanced/` - Trained model checkpoints
- `analysis/` - Training plots and dataset analysis

### 5. Integration with Web Interface

After collecting advanced data, update the web application:

```python
# In app.py, update the model loading to use advanced models:
model_pattern = os.path.join("saved_models_advanced", "advanced_ensemble_classifier*.pth")
```

### 6. Performance Expectations

#### Data Collection:
- **Rate**: ~1-2 traces per minute per website
- **Success Rate**: 85-95% (depends on network/sites)
- **Storage**: ~1MB per 100 traces

#### Model Training:
- **Ensemble Model**: 90%+ accuracy with 100+ traces per site
- **Adversarial Model**: High robustness against defenses
- **Attention Model**: Best for complex timing patterns

### 7. Troubleshooting

#### ChromeDriver Issues:
```bash
# Install ChromeDriver automatically
pip install chromedriver-autoinstaller
python3 -c "import chromedriver_autoinstaller; chromedriver_autoinstaller.install()"
```

#### Memory Issues:
```bash
# Reduce batch size or traces per collection
python3 advanced_collect.py --traces 25 --websites "google.com,github.com"
```

#### Timeout Issues:
```bash
# Increase delays for slow networks
python3 advanced_collect.py --delay-traces 5.0 --delay-websites 10.0
```

### 8. Example Full Workflow

```bash
# 1. Collect comprehensive dataset (30-60 minutes)
python3 advanced_collect.py --traces 100 --websites all --headless

# 2. Analyze the collected data
python3 advanced_train.py --analyze-only

# 3. Train advanced models (20-40 minutes)
python3 advanced_train.py --models ensemble,adversarial --epochs 75

# 4. Test in web interface
python3 app.py
# Navigate to http://localhost:5000
# Use "Collect Advanced Trace" and "Predict Current Website"
```

### 9. Database Queries

Query the SQLite database for analysis:

```sql
-- View collection statistics
SELECT website, COUNT(*) as traces, AVG(load_time) as avg_load_time 
FROM advanced_traces 
GROUP BY website;

-- View session information
SELECT session_id, total_traces, successful_traces, 
       (successful_traces * 100.0 / total_traces) as success_rate
FROM collection_stats;
```

### 10. Research Applications

This advanced collection system enables:

- **Large-scale fingerprinting studies** (1000+ traces)
- **Defense evaluation** (adversarial robustness testing)
- **Cross-browser analysis** (different user agents)
- **Temporal analysis** (website changes over time)
- **Advanced ML research** (novel architectures)

## 🎯 Getting Started Now

**Minimal setup for immediate results:**

```bash
# 1. Quick test collection (5 minutes)
python3 advanced_collect.py --traces 20 --websites "google.com,github.com" --headless

# 2. Train a model (5 minutes)  
python3 advanced_train.py --models ensemble --epochs 10

# 3. See results
ls saved_models_advanced/
ls analysis/
```

This will give you a working advanced model in ~10 minutes!
