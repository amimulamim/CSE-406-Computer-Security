#!/bin/bash

echo "🚀 Creating separate repository for deployment..."

# Create a new directory for the standalone project
cd ../../../../../
mkdir -p side-channel-attack-deploy
cd side-channel-attack-deploy

# Copy all necessary files from the template directory
echo "📁 Copying project files..."
cp -r "/home/amim/4-1/CSE 406-Computer Security/Side Channel Attack/starter_code/template/"* .

# Initialize git repository
echo "🔧 Setting up git repository..."
git init
git add .
git commit -m "Initial commit - Side Channel Attack Project"

echo ""
echo "✅ Project prepared for deployment!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Push this code:"
echo "   git remote add origin https://github.com/yourusername/your-repo-name.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Then deploy to Railway or Render using the new repo"
echo ""
echo "📍 Your deployment-ready project is in: $(pwd)"
