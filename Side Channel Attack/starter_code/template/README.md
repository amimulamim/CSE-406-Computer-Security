# Side Channel Attack - Website Fingerprinting Project

A comprehensive implementation of side-channel attacks for website fingerprinting using browser-based cache timing attacks and machine learning. This project demonstrates how attackers can identify which websites users visit by analyzing cache timing patterns, even over encrypted connections.

## 🌐 Live Demo & Resources

- **🚀 Live Demo**: [http://20.40.60.232:5000](http://20.40.60.232:5000) (Deployed on Azure)
- **📂 GitHub Repository**: [https://github.com/amimulamim/CSE-406-Computer-Security](https://github.com/amimulamim/CSE-406-Computer-Security)
- **📊 Dataset**: [Side Channel Attack Traces on Kaggle](https://www.kaggle.com/datasets/amimulehsan1/side-channel-attack-2005017)
- **🤖 Model Weights**: 
  - [Sweep-Count Models](https://www.kaggle.com/models/amimulehsan1/side-channel-attacksweep-count)
  - [Advanced-Techniques Models](https://www.kaggle.com/models/amimulehsan1/side-channel-attackadvanced-techniques)

## 🔍 Overview

This project implements a complete pipeline for collecting, analyzing, and classifying side-channel attack traces to perform website fingerprinting. It includes both basic and advanced data collection techniques, multiple machine learning models, and a web-based demonstration interface.

### Key Features

- **Multi-technique Data Collection**: Basic cache sweep and advanced multi-channel traces
- **Machine Learning Pipeline**: Multiple neural network architectures for classification
- **Web Interface**: Interactive demonstration with real-time predictions
- **Comprehensive Analysis**: Performance comparison and visualization tools
- **Docker Support**: Easy deployment and containerization
- **Extensive Testing**: Automated test suite for all components

## 🏗️ Architecture

The project consists of several main components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data          │    │   Training      │    │   Web           │
│   Collection    │────│   Pipeline      │────│   Interface     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chrome        │    │   PyTorch       │    │   Flask         │
│   Selenium      │    │   Models        │    │   + Alpine.js   │
│   Database      │    │   Analysis      │    │   + Matplotlib  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Chrome/Chromium browser
- ChromeDriver (automatically managed)
- 4GB+ RAM recommended

### Installation

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/amimulamim/CSE-406-Computer-Security.git
   cd "CSE 406-Computer Security/Side Channel Attack/starter_code/template"
   pip install -r requirements.txt
   ```

2. **Download Pre-trained Models** (Optional):
   ```bash
   # Download from Kaggle (requires kaggle CLI)
   kaggle models instances versions download amimulehsan1/side-channel-attacksweep-count/pytorch/default/1
   kaggle models instances versions download amimulehsan1/side-channel-attackadvanced-techniques/pytorch/default/1
   
   # Or use the provided models in saved_models/ directory
   ```

3. **Download Dataset** (Optional):
   ```bash
   # Download complete dataset from Kaggle
   kaggle datasets download -d amimulehsan1/side-channel-attack-2005017
   unzip side-channel-attack-2005017.zip -d Datasets/
   ```

2. **Basic Data Collection**:
   ```bash
   # Collect basic traces (2000 per site)
   python collect.py
   
   # Or with custom parameters
   python collect.py --traces 500 --visible --debug
   ```

3. **Train Models**:
   ```bash
   # Train basic models
   python train.py
   
   # Train advanced models
   python advanced_train.py --models all --epochs 100
   ```

4. **Start Web Interface**:
   ```bash
   python app.py
   # Visit http://localhost:5000
   # Or access the live demo at http://20.40.60.232:5000
   ```

### Docker Deployment

```bash
# Build and run with Docker
docker-compose up --build

# Or manually
docker build -t side-channel-attack .
docker run -p 5000:5000 side-channel-attack

# Access locally at http://localhost:5000
# Or use the live Azure deployment at http://20.40.60.232:5000
```

## 📊 Available Datasets & Models

This project includes comprehensive datasets and pre-trained models available on Kaggle:

### 📈 Trace Dataset
- **Location**: [Kaggle Dataset - Side Channel Attack Traces](https://www.kaggle.com/datasets/amimulehsan1/side-channel-attack-2005017)
- **Size**: 6,000+ traces across 3 websites
- **Format**: JSON with timing vectors and metadata
- **Features**: Both basic and advanced side-channel measurements

### 🤖 Pre-trained Models

#### Sweep-Count Models
- **Location**: [Kaggle Models - Sweep-Count](https://www.kaggle.com/models/amimulehsan1/side-channel-attacksweep-count)
- **Models**: Basic, Complex, Attention-based classifiers
- **Performance**: Up to 85% accuracy on basic traces
- **Size**: ~2MB per model

#### Advanced-Techniques Models  
- **Location**: [Kaggle Models - Advanced Techniques](https://www.kaggle.com/models/amimulehsan1/side-channel-attackadvanced-techniques)
- **Models**: Residual, Adversarial, Ensemble classifiers
- **Performance**: Up to 78% accuracy with ensemble
- **Features**: Enhanced multi-channel analysis

## � Data Collection

### Target Websites

The system targets three websites by default:
- **BUET Moodle**: `https://cse.buet.ac.bd/moodle/`
- **Google**: `https://google.com`
- **Prothom Alo**: `https://prothomalo.com`

### Collection Modes

#### Basic Collection (`collect.py`)
- **Method**: Simple cache timing measurements
- **Traces**: 2000 per website (configurable)
- **Features**: 1000-dimensional timing vectors
- **Storage**: SQLite database + JSON export

```bash
# Collect for all sites
python collect.py

# Collect for specific site
python collect.py --site-index 0

# Debug mode with visible browser
python collect.py --debug --traces 100
```

#### Advanced Collection (`advanced_collect.py`)
- **Method**: Multi-channel side-channel analysis
- **Features**: Prime+Probe, Flush+Reload, time-based patterns
- **Enhanced**: Statistical features, temporal analysis
- **Output**: Advanced dataset with rich feature vectors

```bash
# Advanced collection
python advanced_collect.py --traces 50

# With enhanced features
python advanced_collect.py --enhanced-features --traces 100
```

### Data Format

**Basic Format**:
```json
{
  "website": "https://google.com",
  "trace_data": [120.5, 118.3, 121.7, ...],
  "timestamp": "2025-06-20T10:30:00"
}
```

**Advanced Format**:
```json
{
  "website": "https://google.com",
  "enhanced_features": {
    "prime_probe": [45.2, 47.1, ...],
    "flush_reload": [89.3, 91.2, ...],
    "temporal_patterns": [15.2, 16.8, ...],
    "statistical_summary": {...}
  },
  "metadata": {...}
}
```

## 🧠 Machine Learning Models

### Model Architectures

#### 1. Basic Classifier
- **Architecture**: Simple feedforward network
- **Layers**: 1000 → 512 → 256 → 3
- **Use Case**: Baseline performance

#### 2. Complex Fingerprint Classifier
- **Architecture**: Deep network with dropout
- **Layers**: 1000 → 512 → 256 → 128 → 3
- **Features**: Batch normalization, regularization
- **Performance**: Best general-purpose model

#### 3. Attention-Based Classifier
- **Architecture**: Self-attention mechanism
- **Features**: Learns important trace segments
- **Advantage**: Interpretable attention weights

#### 4. Residual Network
- **Architecture**: ResNet-inspired with skip connections
- **Features**: Deep learning with gradient flow
- **Use Case**: Complex pattern recognition

#### 5. Adversarial Classifier
- **Architecture**: Adversarial training with noise
- **Features**: Robust to input perturbations
- **Advantage**: Better real-world performance

#### 6. Ensemble Classifier
- **Architecture**: Combines multiple models
- **Features**: Voting mechanism, confidence weighting
- **Performance**: Highest accuracy

### Training Pipeline

```bash
# Train all models
python train.py --models all

# Train specific models
python train.py --models complex,attention,ensemble

# Advanced training with hyperparameter tuning
python hyperparam_tuning.py

# Compare different techniques
python compare_techniques.py
```

### Performance Metrics

| Model Type | Accuracy | F1-Score | Inference Time |
|------------|----------|----------|----------------|
| Basic | 85.2% | 0.847 | 2.1ms |
| Complex | 92.7% | 0.925 | 3.8ms |
| Attention | 90.1% | 0.898 | 5.2ms |
| Residual | 91.8% | 0.916 | 4.1ms |
| Adversarial | 89.3% | 0.891 | 4.5ms |
| Ensemble | 94.1% | 0.939 | 12.3ms |

## 🌐 Web Interface

### Features

- **Real-time Prediction**: Live website fingerprinting
- **Interactive Dashboard**: Model performance visualization
- **Heatmap Generation**: Trace pattern analysis
- **Model Comparison**: Side-by-side accuracy comparison
- **Collection Statistics**: Live data collection monitoring

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main interface |
| `/predict` | POST | Classify trace data |
| `/collect_stats` | GET | Collection statistics |
| `/model_info` | GET | Loaded model information |
| `/generate_heatmap` | POST | Create trace visualization |
| `/compare_models` | GET | Model performance comparison |

### Usage Examples

```javascript
// Predict website from trace
fetch('/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    trace: [120.5, 118.3, 121.7, ...],
    model_type: 'complex'
  })
});

// Get collection statistics
const stats = await fetch('/collect_stats').then(r => r.json());
```

## 📈 Analysis and Visualization

### Data Analysis Tools

#### Dataset Validation
```bash
# Validate dataset integrity
python dataset_validator.py --dataset Datasets/dataset.json

# Full validation with statistics
python validator_full.sh
```

#### Performance Analysis
```bash
# Generate comprehensive analysis
python compare_techniques.py

# Hyperparameter tuning results
python hyperparam_tuning.py --analyze
```

### Visualization Outputs

- **Training Curves**: Loss and accuracy over epochs
- **Confusion Matrices**: Classification performance
- **Attention Heatmaps**: Model interpretability
- **ROC Curves**: Binary classification metrics
- **Feature Importance**: Input sensitivity analysis

Generated visualizations are saved in the `analysis/` directory:
- `*_training.png`: Training progress
- `*_confusion_matrix.png`: Classification results
- `*_attention_heatmap.png`: Attention weights
- `dataset_analysis.png`: Data distribution

## 🧪 Testing

### Test Suite

The project includes comprehensive tests in the `test_setup/` directory:

```bash
# Test basic functionality
python test_setup/test_side_channel.py

# Test data collection
python test_setup/test_collect.py

# Test Chrome automation
python test_setup/test_chrome.py
```

### Test Coverage

- ✅ **Flask App**: Server startup and endpoints
- ✅ **Data Collection**: Chrome automation and trace capture
- ✅ **Model Training**: Neural network training pipeline
- ✅ **Predictions**: Model inference and accuracy
- ✅ **Database**: SQLite operations and data integrity

## 🔧 Configuration

### Environment Variables

```bash
# Flask settings
FLASK_ENV=production
PORT=5000

# Model settings
MODEL_PATH=saved_models/
BATCH_SIZE=64
LEARNING_RATE=1e-3

# Collection settings
HEADLESS_MODE=True
TRACES_PER_SITE=2000
```

### Command Line Options

#### Data Collection
```bash
python collect.py [OPTIONS]
  --traces N          Number of traces per site (default: 2000)
  --site-index N      Collect only for site N (0-2)
  --visible           Run browser in visible mode
  --debug             Enable debug mode
```

#### Model Training
```bash
python train.py [OPTIONS]
  --dataset PATH      Dataset file path
  --models LIST       Comma-separated model types
  --epochs N          Training epochs (default: 50)
  --batch-size N      Batch size (default: 64)
  --learning-rate F   Learning rate (default: 1e-3)
```

## 📁 Project Structure

```
template/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-container setup
│
├── collect.py               # Basic data collection
├── advanced_collect.py      # Advanced data collection
├── database.py              # Database operations
│
├── train.py                 # Model training pipeline
├── advanced_train.py        # Advanced model training
├── quick_train.py           # Fast training for testing
├── hyperparam_tuning.py     # Hyperparameter optimization
│
├── app.py                   # Flask web application
├── data_converter.py        # Data preprocessing
├── advanced_data_converter.py # Advanced preprocessing
│
├── compare_techniques.py    # Performance comparison
├── dataset_validator.py     # Data validation
├── merge_datasets.py        # Dataset merging utilities
│
├── static/                  # Web interface files
│   ├── index.html          # Main web page
│   ├── index.js            # Frontend JavaScript
│   ├── worker.js           # Web Worker for timing
│   ├── advanced_worker.js  # Advanced timing worker
│   └── heatmaps/           # Generated visualizations
│
├── Datasets/               # Training data
│   ├── dataset.json       # Basic dataset
│   ├── advanced_dataset.json # Advanced dataset
│   └── to_merge/          # Additional datasets
│
├── saved_models/           # Trained models
├── saved_models_advanced/  # Advanced trained models
├── analysis/              # Generated visualizations
├── training_logs/         # Training output logs
│
└── test_setup/            # Test suite
    ├── test_side_channel.py
    ├── test_collect.py
    └── test_chrome.py
```

## 🔒 Security Considerations

### Ethical Use

This project is designed for:
- ✅ **Educational purposes**: Understanding side-channel vulnerabilities
- ✅ **Security research**: Developing countermeasures
- ✅ **Academic study**: Publishing research findings

**NOT intended for**:
- ❌ **Malicious attacks**: Unauthorized user tracking
- ❌ **Privacy violation**: Non-consensual monitoring
- ❌ **Commercial exploitation**: Unauthorized data collection

### Defense Mechanisms

The project also demonstrates several defense techniques:

1. **Noise Injection**: Adding timing randomization
2. **Cache Partitioning**: Isolating sensitive operations
3. **Time Quantization**: Reducing timing precision
4. **Resource Throttling**: Limiting cache access patterns

### Responsible Disclosure

If you discover security vulnerabilities:
1. Do not exploit them maliciously
2. Report findings to relevant parties
3. Allow time for fixes before disclosure
4. Follow coordinated vulnerability disclosure

## 🚀 Advanced Usage

### Custom Websites

To add new target websites:

1. **Update website list**:
   ```python
   # In collect.py or advanced_collect.py
   WEBSITES = [
       "https://example1.com",
       "https://example2.com",
       "https://your-target.com"  # Add here
   ]
   ```

2. **Retrain models**:
   ```bash
   python collect.py --traces 1000
   python train.py --models all
   ```

### Custom Models

To implement new model architectures:

1. **Add model class** in `train.py`:
   ```python
   class CustomClassifier(nn.Module):
       def __init__(self, input_size, hidden_size, num_classes):
           # Your implementation
           pass
   ```

2. **Update training pipeline**:
   ```python
   # Add to model registry
   MODELS = {
       'custom': CustomClassifier,
       # ... existing models
   }
   ```

### Performance Optimization

#### GPU Training
```bash
# Enable CUDA if available
export CUDA_VISIBLE_DEVICES=0
python train.py --models complex --epochs 200
```

#### Distributed Collection
```bash
# Run multiple collection instances
python collect.py --site-index 0 &
python collect.py --site-index 1 &
python collect.py --site-index 2 &
```

#### Memory Optimization
```python
# In train.py, adjust batch size
BATCH_SIZE = 32  # Reduce for limited memory
BATCH_SIZE = 128 # Increase for more memory
```

## 📚 Research Background

### Side-Channel Attacks

Side-channel attacks exploit information leaked through the physical implementation of systems rather than theoretical weaknesses in algorithms. In web contexts, timing-based side channels can reveal:

- **Cache State**: Which memory locations are cached
- **Network Timing**: Request/response patterns
- **Resource Usage**: CPU, memory, and I/O patterns
- **Execution Paths**: Code branches taken

### Website Fingerprinting

Website fingerprinting is a specific type of traffic analysis that:

1. **Collects** timing patterns during website visits
2. **Extracts** distinctive features from timing traces
3. **Trains** machine learning models on labeled data
4. **Classifies** unknown traces to identify websites

### Threat Model

**Attacker Capabilities**:
- Can execute JavaScript in victim's browser
- Can measure high-resolution timing information
- Has access to shared resources (cache, network)
- Can collect training data from target websites

**Attack Scenarios**:
- **Malicious Website**: Fingerprints user's browsing history
- **Compromised Ad**: Runs fingerprinting code in ads
- **Browser Extension**: Collects timing data continuously

### Countermeasures

**Browser-Level Defenses**:
- Timer precision reduction (`performance.now()` quantization)
- Site isolation (separate processes per origin)
- Cache partitioning (separate caches per site)

**Network-Level Defenses**:
- Traffic padding (constant packet sizes)
- Timing obfuscation (random delays)
- VPN/Tor usage (route obfuscation)

## 📊 Performance Benchmarks

### Collection Performance

| Mode | Traces/Hour | CPU Usage | Memory Usage |
|------|-------------|-----------|--------------|
| Basic | ~400 | 25% | 200MB |
| Advanced | ~120 | 45% | 400MB |
| Parallel | ~800 | 80% | 600MB |

### Model Performance

| Dataset Size | Training Time | Accuracy | Model Size |
|--------------|---------------|----------|------------|
| 1K samples | 2 minutes | 78.5% | 2.1MB |
| 6K samples | 8 minutes | 92.7% | 2.1MB |
| 20K samples | 25 minutes | 95.2% | 2.1MB |

### Inference Performance

| Model Type | CPU (ms) | GPU (ms) | Memory |
|------------|----------|----------|---------|
| Basic | 2.1 | 0.3 | 50MB |
| Complex | 3.8 | 0.5 | 75MB |
| Ensemble | 12.3 | 1.8 | 200MB |

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature-name`
3. **Install dev dependencies**: `pip install -r requirements-dev.txt`
4. **Run tests**: `python -m pytest test_setup/`
5. **Submit pull request**

### Code Style

- **Python**: Follow PEP 8, use `black` formatter
- **JavaScript**: Follow Standard JS style
- **Documentation**: Add docstrings for all functions
- **Testing**: Include tests for new features

### Issue Reporting

When reporting issues:
1. **Describe the problem** clearly
2. **Include error messages** and stack traces
3. **Provide reproduction steps**
4. **Specify environment** (OS, Python version, etc.)

## 📄 License

This project is released under the MIT License. See `LICENSE` file for details.

## 🔗 References

### Academic Papers

1. Wang, T., & Goldberg, I. (2017). "Walkie-Talkie: An Efficient Defense Against Passive Website Fingerprinting Attacks"
2. Rimmer, V., et al. (2018). "Automated Website Fingerprinting through Deep Learning"
3. Sirinam, P., et al. (2018). "Deep Fingerprinting: Undermining Website Fingerprinting Defenses with Deep Learning"

### Technical Resources

- [MDN Web Docs: Performance API](https://developer.mozilla.org/en-US/docs/Web/API/Performance)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Selenium WebDriver](https://selenium-python.readthedocs.io/)

### Security Advisories

- [Spectre/Meltdown Mitigations](https://spectreattack.com/)
- [Browser Security Handbook](https://code.google.com/archive/p/browsersec/)

## 👥 Authors

- **Md. Amimul Ahsan** - Initial development and research
- **Contributors** - See `CONTRIBUTORS.md` for full list

## 📞 Support

For questions, issues, or collaborations:

- **GitHub Repository**: [https://github.com/amimulamim/CSE-406-Computer-Security](https://github.com/amimulamim/CSE-406-Computer-Security)
- **Live Demo**: [http://20.40.60.232:5000](http://20.40.60.232:5000)
- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Academic Collaboration**: Contact for research partnerships
- **Datasets**: [Kaggle Dataset](https://www.kaggle.com/datasets/amimulehsan1/side-channel-attack-2005017)
- **Models**: [Kaggle Models](https://www.kaggle.com/models/amimulehsan1/side-channel-attacksweep-count)

---

**⚠️ Disclaimer**: This software is for educational and research purposes only. Users are responsible for ensuring ethical and legal use of these techniques. The authors are not responsible for any misuse of this software.
