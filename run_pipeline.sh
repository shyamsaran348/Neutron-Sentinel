#!/bin/bash
set -e

echo "============================================="
echo "   Starting NIDS Pipeline Rerun"
echo "============================================="

# Ensure we're in the right directory
cd "$(dirname "$0")"

echo "[1/4] Running Data Preprocessing..."
python3 src/preprocessing.py

echo "[2/4] Running Exploratory Data Analysis..."
python3 src/eda.py

echo "[3/4] Training Baseline ML Models..."
python3 src/train_ml_models.py

echo "[4/4] Training Deep Learning Model (MLP/DNN)..."
python3 src/train_dnn.py

echo "[5/4] Training Anomaly Autoencoder..."
python3 src/train_autoencoder.py

echo "============================================="
echo "   Pipeline Execution Complete!"
echo "   You can now start the dashboard!"
echo "============================================="
