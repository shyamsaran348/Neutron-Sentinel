import numpy as np
import os
import joblib
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def load_data(data_dir="data/processed"):
    print(f"Loading arrays from {data_dir}...")
    X_train = np.load(os.path.join(data_dir, "X_train.npy"))
    X_test = np.load(os.path.join(data_dir, "X_test.npy"))
    y_train = np.load(os.path.join(data_dir, "y_train.npy"))
    y_test = np.load(os.path.join(data_dir, "y_test.npy"))
    return X_train, X_test, y_train, y_test

def run_autoencoder(models_dir="models"):
    os.makedirs(models_dir, exist_ok=True)
    X_train, X_test, y_train, y_test = load_data()
    
    label_encoder = joblib.load(os.path.join(models_dir, 'label_encoder.pkl'))
    
    # Autoencoders train ONLY on BENIGN traffic
    try:
        benign_label = label_encoder.transform(['BENIGN'])[0]
    except Exception:
        # If uppercase 'BENIGN' not there, try finding it
        for cls in label_encoder.classes_:
            if 'benign' in cls.lower():
                benign_label = label_encoder.transform([cls])[0]
                break
                
    print(f"Benign label encoded as {benign_label}")
    
    # Filter training data for benign only
    X_train_benign = X_train[y_train == benign_label]
    print(f"Training Autoencoder on {len(X_train_benign)} BENIGN samples...")
    
    # For speed, sample if very large
    sample_size = min(200000, len(X_train_benign))
    indices = np.random.choice(len(X_train_benign), sample_size, replace=False)
    X_train_sub = X_train_benign[indices]
    
    # Architecture: 64 -> 32 -> 64
    # Note: Scikit-learn MLPRegressor represents standard autoencoder when fitting X to X
    autoencoder = MLPRegressor(hidden_layer_sizes=(64, 32, 64), 
                               activation='relu', 
                               solver='adam', 
                               batch_size=256,
                               learning_rate_init=0.001,
                               max_iter=30, 
                               early_stopping=True,
                               validation_fraction=0.1,
                               random_state=42,
                               verbose=True)
                               
    autoencoder.fit(X_train_sub, X_train_sub)
    
    print("\nEvaluating Reconstruction Error on Test Set...")
    X_test_pred = autoencoder.predict(X_test)
    
    # Calculate Mean Squared Error element-wise
    mse = np.mean(np.power(X_test - X_test_pred, 2), axis=1)
    
    # Define a threshold (e.g., 95th percentile of validation error)
    # Simple threshold here just for demonstration; ideally tuned
    val_pred = autoencoder.predict(X_train_sub)
    val_mse = np.mean(np.power(X_train_sub - val_pred, 2), axis=1)
    threshold = np.percentile(val_mse, 95)
    
    print(f"Calculated Anomaly Threshold (95th percentile of normal): {threshold:.4f}")
    
    model_path = os.path.join(models_dir, "autoencoder_model.pkl")
    joblib.dump(autoencoder, model_path)
    joblib.dump(threshold, os.path.join(models_dir, "autoencoder_threshold.pkl"))
    print(f"Saved Autoencoder and Threshold to {model_path}")

if __name__ == "__main__":
    run_autoencoder()
