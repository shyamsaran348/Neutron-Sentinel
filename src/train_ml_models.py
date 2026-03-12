import numpy as np
import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import xgboost as xgb
import lightgbm as lgb
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

def train_and_evaluate(name, model, X_train, y_train, X_test, y_test, models_dir):
    print(f"\n--- Training {name} ---")
    model.fit(X_train, y_train)
    
    print(f"Evaluating {name}...")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"{name} Accuracy: {acc:.4f}")
    
    model_path = os.path.join(models_dir, f"{name.replace(' ', '_').lower()}.pkl")
    joblib.dump(model, model_path)
    print(f"Saved {name} to {model_path}")
    
    return acc

def run_ml_pipeline(models_dir="models"):
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

    models = {
        "Logistic Regression": LogisticRegression(max_iter=500, n_jobs=-1),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1),
        # SVM is extremely slow on large datasets, even with 200k rows. 
        # "SVM": SVC(kernel='linear', max_iter=1000), 
        "XGBoost": xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', n_jobs=-1),
        "LightGBM": lgb.LGBMClassifier(n_jobs=-1, random_state=42, verbose=-1)
    }

    results = {}
    for name, model in models.items():
        try:
           acc = train_and_evaluate(name, model, X_train_sub, y_train_sub, X_test, y_test, models_dir)
           results[name] = acc
        except Exception as e:
           print(f"Error training {name}: {e}")

    print("\n--- Summary ---")
    for name, acc in results.items():
        print(f"{name}: {acc:.4f}")

if __name__ == "__main__":
    run_ml_pipeline()
