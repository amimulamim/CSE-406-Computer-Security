# Quick Training Guide

## 🚀 Train Specific Models Efficiently

Instead of training all models at once (which takes a long time), you can now train specific models when needed using the `quick_train.py` script.

## Available Models

1. **basic** - Basic CNN classifier (fastest)
2. **complex** - Complex CNN with batch normalization 
3. **attention** - Multi-head attention classifier (advanced)
4. **residual** - Deep residual network (advanced)
5. **ensemble** - Ensemble of multiple architectures (slow but accurate)
6. **adversarial** - Adversarial training classifier (advanced)

## Usage Examples

### Quick Training (Recommended for testing)
```bash
# Train basic model quickly (10 epochs)
python3 quick_train.py --model basic --quick

# Train complex model quickly
python3 quick_train.py --model complex --quick

# Train attention model quickly
python3 quick_train.py --model attention --quick
```

### Full Training
```bash
# Train basic model with default epochs (30)
python3 quick_train.py --model basic

# Train attention model with default epochs (50)
python3 quick_train.py --model attention

# Train ensemble model (25 epochs by default)
python3 quick_train.py --model ensemble
```

### Custom Training
```bash
# Train with specific number of epochs
python3 quick_train.py --model complex --epochs 20

# Train with custom learning rate
python3 quick_train.py --model attention --lr 0.0005

# Train with custom batch size
python3 quick_train.py --model residual --batch-size 32

# Use custom dataset
python3 quick_train.py --model basic --dataset my_dataset.json
```

## Performance Comparison

Based on training results:

| Model | Quick Epochs | Full Epochs | Expected Accuracy | Training Time |
|-------|-------------|-------------|------------------|---------------|
| basic | 10 | 30 | ~82% | Fast |
| complex | 13 | 40 | ~85% | Medium |
| attention | 17 | 50 | ~74% | Medium |
| residual | 13 | 40 | ~72% | Medium |
| ensemble | 8 | 25 | ~84% | Slow |
| adversarial | 10 | 30 | ~75% | Medium |

## Recommendations

### For Quick Testing
```bash
python3 quick_train.py --model basic --quick      # 2-3 minutes
python3 quick_train.py --model complex --quick    # 3-4 minutes
```

### For Best Accuracy
```bash
python3 quick_train.py --model complex           # Best balance of speed/accuracy
python3 quick_train.py --model ensemble          # Highest accuracy but slower
```

### For Research/Advanced Features
```bash
python3 quick_train.py --model attention         # Attention mechanisms
python3 quick_train.py --model residual         # Deep residual learning
python3 quick_train.py --model adversarial      # Adversarial training
```

## Advanced Usage

### Training Multiple Models in Sequence
```bash
# Train best performing models
python3 quick_train.py --model basic --quick
python3 quick_train.py --model complex --quick
python3 quick_train.py --model ensemble --epochs 15
```

### Hyperparameter Tuning
```bash
# Test different learning rates
python3 quick_train.py --model attention --lr 0.001 --epochs 20
python3 quick_train.py --model attention --lr 0.0005 --epochs 20
python3 quick_train.py --model attention --lr 0.0001 --epochs 20
```

### Model Comparison
```bash
# Train same epochs for fair comparison
python3 quick_train.py --model basic --epochs 20
python3 quick_train.py --model complex --epochs 20
python3 quick_train.py --model attention --epochs 20
```

## Output Files

Each training session creates:
- **Model file**: `saved_models/{model}_classifier.pth`
- **Training plot**: `{model}_training_plot.png` (for advanced models)
- **Console output**: Real-time training progress and final evaluation

## Tips

1. **Start with basic model** to verify your dataset works
2. **Use --quick flag** for initial testing
3. **Complex model** usually gives the best accuracy/speed balance
4. **Ensemble model** for maximum accuracy when you have time
5. **Save your results** - model files are automatically saved

## Troubleshooting

### If training is too slow:
- Use `--quick` flag
- Reduce `--epochs`
- Increase `--batch-size` (if you have enough GPU memory)

### If accuracy is too low:
- Remove `--quick` flag
- Increase `--epochs`
- Try different models (complex or ensemble)
- Check your dataset quality

### If you get memory errors:
- Reduce `--batch-size`
- Use simpler models (basic instead of ensemble)

## Integration with Web Interface

After training, your models are automatically available in the web interface:
1. Start the web server: `python3 app.py`
2. Open http://localhost:5000
3. Use the prediction features with your trained models

This flexible approach lets you experiment efficiently and train only what you need!
