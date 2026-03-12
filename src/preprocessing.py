import pandas as pd
import numpy as np
import glob
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

def load_and_merge(input_dir):
    print(f"Loading CSV files from {input_dir}...")
    files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    if not files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")
        
    df_list = []
    for file in files:
        print(f"Reading {file}...")
        try:
            # Some files might have leading spaces in column names
            df = pd.read_csv(file, skipinitialspace=True)
            df.columns = df.columns.str.strip()
            df_list.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            
    if not df_list:
        raise ValueError("No data could be loaded.")
        
    merged_data = pd.concat(df_list, ignore_index=True)
    print(f"Merged dataset shape: {merged_data.shape}")
    return merged_data

def clean_data(df):
    print("Cleaning data...")
    # Replace inf with nan
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Drop rows with missing values
    initial_len = len(df)
    df.dropna(inplace=True)
    print(f"Dropped {initial_len - len(df)} rows with missing values.")
    
    # Drop duplicates
    initial_len = len(df)
    df.drop_duplicates(inplace=True)
    print(f"Dropped {initial_len - len(df)} duplicate rows.")
    
    return df

def feature_engineering(df):
    print("Performing feature engineering...")
    # Optionally drop irrelevant features here like IP/Ports if they cause overfitting
    # We will keep it standard as per prompt for now.
    
    # Make sure we don't scale the label column
    x = df.drop(columns=['Label'])
    y = df['Label']
    
    return x, y

def scale_and_encode(x, y, model_save_dir):
    print("Encoding labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print("Scaling features...")
    # Ensure numerical features only
    x = x.select_dtypes(include=[np.number])
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
    
    # Save transformers for inference
    os.makedirs(model_save_dir, exist_ok=True)
    joblib.dump(scaler, os.path.join(model_save_dir, 'scaler.pkl'))
    joblib.dump(label_encoder, os.path.join(model_save_dir, 'label_encoder.pkl'))
    print(f"Saved scaler and label encoder to {model_save_dir}")
    
    return x_scaled, y_encoded

def preprocess_pipeline(raw_dir="data/raw/MachineLearningCSV", output_dir="data/processed", model_dir="models"):
    os.makedirs(output_dir, exist_ok=True)
    
    df = load_and_merge(raw_dir)
    df = clean_data(df)
    
    X, y = feature_engineering(df)
    X_scaled, y_encoded = scale_and_encode(X, y, model_dir)
    
    # Save processed dataframe (optional, might be huge, maybe save as parquet or just the split data)
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)
    
    print("Saving processed arrays...")
    np.save(os.path.join(output_dir, "X_train.npy"), X_train)
    np.save(os.path.join(output_dir, "X_test.npy"), X_test)
    np.save(os.path.join(output_dir, "y_train.npy"), y_train)
    np.save(os.path.join(output_dir, "y_test.npy"), y_test)
    
    # Save the original dataframe for EDA later
    df.to_pickle(os.path.join(output_dir, "cleaned_dataset.pkl"))
    
    print("Preprocessing completed successfully!")

if __name__ == "__main__":
    preprocess_pipeline()
