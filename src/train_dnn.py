import numpy as np
import os
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

def load_data(data_dir="data/processed"):
    print(f"Loading arrays from {data_dir}...")
    X_train = np.load(os.path.join(data_dir, "X_train.npy"))
    X_test = np.load(os.path.join(data_dir, "X_test.npy"))
    y_train = np.load(os.path.join(data_dir, "y_train.npy"))
    y_test = np.load(os.path.join(data_dir, "y_test.npy"))
    return X_train, X_test, y_train, y_test

def run_dnn(models_dir="models"):
    os.makedirs(models_dir, exist_ok=True)
    X_train, X_test, y_train, y_test = load_data()
    
    from collections import Counter
    from imblearn.under_sampling import RandomUnderSampler
    from imblearn.over_sampling import SMOTE
    
    print(f"Original training distribution: {Counter(y_train)}")
    
    # Cap majority classes to 30,000 to prevent OOM
    max_samples = 30000
    class_counts = Counter(y_train)
    under_strategy = {k: min(v, max_samples) for k, v in class_counts.items()}
    
    print("Applying Random UnderSampling for majority classes...")
    rus = RandomUnderSampler(sampling_strategy=under_strategy, random_state=42)
    X_res, y_res = rus.fit_resample(X_train, y_train)
    
    # Upsample minority classes to 30,000 using SMOTE
    print("Applying SMOTE for minority classes...")
    over_strategy = {k: max_samples for k in class_counts.keys()}
    smote = SMOTE(sampling_strategy=over_strategy, k_neighbors=3, random_state=42) # k=3 for smaller classes like Infiltration/Heartbleed
    X_train_sub, y_train_sub = smote.fit_resample(X_res, y_res)
    
    print(f"Balanced training distribution: {Counter(y_train_sub)}")
    print(f"Total balanced training samples: {len(y_train_sub)}")
    
    print(f"\nTraining Deep Neural Network (MLP) on {len(y_train_sub)} samples...")
    # Architecture: 128 -> 64 -> 32
    mlp = MLPClassifier(hidden_layer_sizes=(128, 64, 32), 
                        activation='relu', 
                        solver='adam', 
                        batch_size=256,
                        max_iter=50, 
                        early_stopping=True,
                        validation_fraction=0.1,
                        random_state=42,
                        verbose=True)
                        
    mlp.fit(X_train_sub, y_train_sub)
    
    print("\nEvaluating the DNN model on full test set...")
    y_pred = mlp.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Deep Neural Network Accuracy: {accuracy:.4f}")
    
    model_path = os.path.join(models_dir, "dnn_model.pkl")
    joblib.dump(mlp, model_path)
    print(f"Saved DNN to {model_path}")

if __name__ == "__main__":
    run_dnn()
