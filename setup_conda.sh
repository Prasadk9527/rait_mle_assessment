#!/bin/bash
# setup_conda.sh - Conda environment setup for RAIT Assessment

echo "========================================="
echo "RAIT MLE Assessment - Conda Setup"
echo "========================================="

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo " Conda not found! Please install conda first (Miniconda or Anaconda)"
    exit 1
fi

# Create conda environment (if not exists)
ENV_NAME="rait_assessment"
if conda env list | grep -q "$ENV_NAME"; then
    echo " Environment '$ENV_NAME' already exists"
    read -p "Do you want to recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing environment..."
        conda env remove -n $ENV_NAME
        echo "Creating fresh environment..."
        conda create -n $ENV_NAME python=3.10 -y
    else
        echo "Using existing environment"
    fi
else
    echo "Creating new conda environment: $ENV_NAME"
    conda create -n $ENV_NAME python=3.10 -y
fi

# Activate environment
echo "Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

# Upgrade pip
pip install --upgrade pip

# Install PyTorch (CPU version for Ubuntu - no GPU required)
echo "Installing PyTorch (CPU version)..."
pip install torch==2.0.0 --index-url https://download.pytorch.org/whl/cpu

# Install all requirements
echo "Installing Python packages..."
pip install -r requirements.txt

# Create project directories
echo "Creating project directories..."
mkdir -p data/supplier_a
mkdir -p data/supplier_b
mkdir -p data/supplier_c
mkdir -p data/red_team
mkdir -p docs
mkdir -p tests
mkdir -p src/schema
mkdir -p src/adapters
mkdir -p src/metrics
mkdir -p src/adversarial
mkdir -p src/coverage
mkdir -p src/utils

# Create __init__.py files
touch src/__init__.py
touch src/schema/__init__.py
touch src/adapters/__init__.py
touch src/metrics/__init__.py
touch src/adversarial/__init__.py
touch src/coverage/__init__.py
touch src/utils/__init__.py

# Download models (first time)
echo ""
echo "========================================="
echo "Downloading AI Models (this may take 5-10 minutes)..."
echo "========================================="

# Download embedding model
echo "Downloading sentence-transformers model..."
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); print(' Embedding model downloaded')" 2>/dev/null

# Download LLM model (smaller version for faster download)
echo "Downloading LLM model (Zephyr-7B - this is ~4GB, may take time)..."
echo "If you want to skip LLM model for now, press Ctrl+C and run without part 3"
python -c "from transformers import pipeline; pipe = pipeline('text-generation', model='HuggingFaceH4/zephyr-7b-beta', device='cpu'); print(' LLM model downloaded')" 2>/dev/null

# Create a test to verify setup
echo ""
echo "========================================="
echo "Testing Installation..."
echo "========================================="
python -c "import torch; import transformers; import sentence_transformers; import pandas; print(' All packages imported successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo " Setup completed successfully!"
else
    echo "  Some packages may have issues, but we can proceed"
fi

echo ""
echo "========================================="
echo "Setup Complete! Next steps:"
echo "========================================="
echo ""
echo "1. Activate environment:"
echo "   conda activate $ENV_NAME"
echo ""
echo "2. Generate synthetic data and run assessment:"
echo "   python run_assessment.py --generate-data"
echo ""
echo "3. Run individual parts:"
echo "   python run_assessment.py --part 1"
echo "   python run_assessment.py --part 2"
echo "   python run_assessment.py --part 3"
echo ""
echo "Note: For LLM model (Part 3), if download takes too long,"
echo "you can use a smaller model by modifying the code"
echo "========================================="