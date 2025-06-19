#!/bin/bash

# Quick training examples for different models

echo "🎯 Flexible Model Training Examples"
echo "=================================="
echo ""

echo "📋 Available commands:"
echo ""

echo "1. List all available models:"
echo "   python train.py --list-models"
echo ""

echo "2. Train just the baseline model quickly:"
echo "   python train.py --models baseline --quick"
echo ""

echo "3. Train attention and residual models:"
echo "   python train.py --models attention residual"
echo ""

echo "4. Train ensemble model with custom epochs:"
echo "   python train.py --models ensemble --epochs 15"
echo ""

echo "5. Quick training of complex model:"
echo "   python train.py --models complex --quick"
echo ""

echo "6. Train adversarial model with custom dataset:"
echo "   python train.py --models adversarial --dataset custom_data.json"
echo ""

echo "7. Train all models (default, may take long):"
echo "   python train.py"
echo ""

echo "⚡ Quick mode trains with only 10 epochs for fast testing"
echo "🎯 You can specify multiple models: --models baseline complex attention"
echo ""

# Interactive selection
echo "🎮 Interactive Model Selection:"
echo "Choose what you want to do:"
echo ""
echo "1) List available models"
echo "2) Quick train baseline model (fast)"
echo "3) Train attention model" 
echo "4) Train ensemble model"
echo "5) Train custom selection"
echo "6) Exit"
echo ""

read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "📋 Listing available models..."
        python train.py --list-models
        ;;
    2)
        echo ""
        echo "⚡ Quick training baseline model..."
        python train.py --models baseline --quick
        ;;
    3)
        echo ""
        echo "🔥 Training attention model..."
        python train.py --models attention
        ;;
    4)
        echo ""
        echo "🎯 Training ensemble model..."
        python train.py --models ensemble
        ;;
    5)
        echo ""
        echo "Available models: baseline, complex, attention, residual, ensemble, adversarial"
        read -p "Enter models to train (space-separated): " models
        echo ""
        echo "🚀 Training selected models: $models"
        python train.py --models $models
        ;;
    6)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Training complete! Check saved_models/ directory for results."
