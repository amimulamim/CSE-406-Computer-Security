#!/usr/bin/bash

# Full Dataset Validation Script
# Validates all JSON dataset files in the to_merge directory

echo "🔍 Starting full dataset validation..."
echo "=" * 50

# Check if to_merge directory exists
if [ ! -d "Datasets/to_merge" ]; then
    echo "❌ Error: Datasets/to_merge directory not found!"
    echo "💡 Please ensure the directory structure is correct."
    exit 1
fi

cd Datasets/to_merge

# Count JSON files
json_count=$(ls -1 *.json 2>/dev/null | wc -l)
if [ $json_count -eq 0 ]; then
    echo "⚠️  No JSON files found in Datasets/to_merge/"
    echo "💡 Place dataset files to validate in this directory."
    cd - > /dev/null
    exit 0
fi

echo "📊 Found $json_count JSON files to validate"
echo ""

# Validate each JSON file
success_count=0
error_count=0

for file in *.json; do
    if [ -f "$file" ]; then
        echo "🔍 Validating $file..."
        
        # Check if dataset_validator.py exists
        if [ ! -f "../../dataset_validator.py" ]; then
            echo "❌ Error: dataset_validator.py not found!"
            echo "💡 Please ensure dataset_validator.py exists in the template directory."
            cd - > /dev/null
            exit 1
        fi
        
        # Run validation
        if python3 ../../dataset_validator.py "$file"; then
            echo "✅ $file - Valid"
            ((success_count++))
        else
            echo "❌ $file - Invalid"
            ((error_count++))
        fi
        echo ""
    fi
done

# Return to original directory
cd - > /dev/null

# Summary
echo "🎉 Validation Complete!"
echo "=" * 50
echo "✅ Valid files: $success_count"
echo "❌ Invalid files: $error_count"
echo "📊 Total processed: $((success_count + error_count))"

if [ $error_count -eq 0 ]; then
    echo "🎊 All dataset files are valid!"
    exit 0
else
    echo "⚠️  Some files have validation errors. Please check the output above."
    exit 1
fi