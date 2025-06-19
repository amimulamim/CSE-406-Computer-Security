#!/bin/bash

# Advanced Side-Channel Attack Demo Script
# This script demonstrates the sophisticated side-channel techniques

echo "🚀 Advanced Side-Channel Attack Techniques Demo"
echo "================================================"
echo ""

# Check if required files exist
echo "📋 Checking system requirements..."

required_files=(
    "app.py"
    "train.py"
    "advanced_data_converter.py"
    "static/advanced_worker.js"
    "static/worker.js"
    "static/index.html"
    "static/index.js"
)

missing_files=0
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Missing: $file"
        missing_files=$((missing_files + 1))
    else
        echo "✅ Found: $file"
    fi
done

if [[ $missing_files -gt 0 ]]; then
    echo ""
    echo "❌ $missing_files required files are missing. Please ensure all files are present."
    exit 1
fi

echo ""
echo "✅ All required files found!"
echo ""

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
python3 -c "
import sys
required_modules = ['torch', 'numpy', 'sklearn', 'flask', 'matplotlib', 'seaborn']
missing = []
for module in required_modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')
        missing.append(module)

if missing:
    print(f'\\n❌ Missing modules: {\", \".join(missing)}')
    print('Install with: pip install torch scikit-learn flask matplotlib seaborn')
    sys.exit(1)
else:
    print('\\n✅ All Python dependencies satisfied!')
"

if [[ $? -ne 0 ]]; then
    echo ""
    echo "❌ Python dependencies check failed. Please install missing modules."
    exit 1
fi

echo ""

# Offer different demo modes
echo "🎯 Select demonstration mode:"
echo "1. Full Advanced Demo (Recommended)"
echo "2. Quick Feature Test"
echo "3. Training Only"
echo "4. Data Collection Only"
echo "5. Exit"
echo ""

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting Full Advanced Demo..."
        echo "================================="
        echo ""
        
        echo "📡 Step 1: Starting Flask server in background..."
        python3 app.py &
        SERVER_PID=$!
        echo "Server PID: $SERVER_PID"
        
        # Wait for server to start
        echo "⏳ Waiting for server to initialize..."
        sleep 5
        
        # Check if server is running
        if curl -s http://localhost:5000 > /dev/null; then
            echo "✅ Server is running!"
        else
            echo "❌ Server failed to start. Check for port conflicts."
            kill $SERVER_PID 2>/dev/null
            exit 1
        fi
        
        echo ""
        echo "🌐 Step 2: Open your browser and navigate to:"
        echo "   http://localhost:5000"
        echo ""
        echo "🎯 Step 3: Try the advanced features:"
        echo "   • Click '🚀 Collect Advanced Trace' to test sophisticated techniques"
        echo "   • Use 'Predict with Advanced Techniques' for enhanced prediction"
        echo "   • Compare with legacy methods to see improvements"
        echo ""
        echo "📊 Step 4: Training advanced models..."
        echo "   (This will run in the background while you test the interface)"
        echo ""
        
        # Start training in background
        python3 train.py > training_log.txt 2>&1 &
        TRAIN_PID=$!
        echo "Training PID: $TRAIN_PID"
        echo "Training output: tail -f training_log.txt"
        echo ""
        
        echo "🎮 Demo is now running!"
        echo "Press ENTER when you're done testing to cleanup..."
        read
        
        echo ""
        echo "🧹 Cleaning up..."
        kill $SERVER_PID 2>/dev/null
        kill $TRAIN_PID 2>/dev/null
        echo "✅ Demo complete!"
        ;;
        
    2)
        echo ""
        echo "⚡ Quick Feature Test..."
        echo "======================"
        echo ""
        
        echo "🧪 Testing advanced worker functionality..."
        
        # Create a simple test HTML file
        cat > test_advanced.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Advanced Worker Test</title></head>
<body>
<script>
const worker = new Worker('static/advanced_worker.js');
worker.onmessage = function(e) {
    console.log('Advanced techniques result:', e.data);
    const attacks = e.data.attacks || {};
    
    console.log('Techniques tested:');
    console.log('- Prime+Probe:', attacks.primeProbe ? '✅' : '❌');
    console.log('- Bus Contention:', attacks.busContention ? '✅' : '❌');
    console.log('- Cache Conflict:', attacks.cacheConflict ? '✅' : '❌');
    console.log('- Timing Attack:', attacks.timing ? '✅' : '❌');
    console.log('- Branch Predictor:', attacks.branch ? '✅' : '❌');
    console.log('- TLB Attack:', attacks.tlb ? '✅' : '❌');
    console.log('- Combined Attack:', attacks.combined ? '✅' : '❌');
    console.log('- Legacy Support:', attacks.legacy ? '✅' : '❌');
    
    document.body.innerHTML = '<h1>Test Complete!</h1><p>Check console for results.</p>';
};
worker.postMessage('start');
</script>
<h1>Testing Advanced Techniques...</h1>
<p>Check browser console for results.</p>
</body>
</html>
EOF
        
        echo "✅ Test file created: test_advanced.html"
        echo "🌐 Open test_advanced.html in your browser to test advanced worker"
        echo "📊 Check browser console for detailed results"
        echo ""
        echo "Press ENTER to continue..."
        read
        rm -f test_advanced.html
        ;;
        
    3)
        echo ""
        echo "🧠 Training Advanced Models..."
        echo "============================="
        echo ""
        
        if [[ ! -f "Datasets/dataset.json" ]]; then
            echo "⚠️  No dataset found. Creating sample dataset..."
            
            # Create a minimal sample dataset for testing
            mkdir -p Datasets
            cat > Datasets/dataset.json << 'EOF'
[
    {
        "website": "https://google.com",
        "trace_data": [1.5, 2.1, 1.8, 2.3, 1.9, 2.0, 1.7, 2.2, 1.6, 2.4]
    },
    {
        "website": "https://prothomalo.com", 
        "trace_data": [3.1, 2.8, 3.2, 2.9, 3.0, 2.7, 3.3, 2.6, 3.4, 2.5]
    }
]
EOF
            echo "✅ Sample dataset created"
        fi
        
        echo "🚀 Starting training with advanced techniques..."
        python3 train.py
        echo ""
        echo "✅ Training complete! Check saved_models/ directory for results."
        ;;
        
    4)
        echo ""
        echo "📡 Data Collection Mode..."
        echo "========================="
        echo ""
        
        echo "🌐 Starting Flask server for data collection..."
        python3 app.py &
        SERVER_PID=$!
        
        sleep 3
        
        if curl -s http://localhost:5000 > /dev/null; then
            echo "✅ Server running at http://localhost:5000"
            echo ""
            echo "📊 Use the web interface to:"
            echo "   • Collect advanced multi-channel traces"
            echo "   • Compare with legacy trace collection"
            echo "   • Download and analyze results"
            echo ""
            echo "Press ENTER to stop the server..."
            read
            
            kill $SERVER_PID 2>/dev/null
            echo "✅ Server stopped"
        else
            echo "❌ Failed to start server"
            kill $SERVER_PID 2>/dev/null
        fi
        ;;
        
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📚 For more information, see:"
echo "   • ADVANCED_TECHNIQUES.md - Detailed documentation"
echo "   • training_log.txt - Training output"
echo "   • saved_models/ - Trained model files"
echo ""
echo "🎯 Advanced side-channel techniques demonstration complete!"
