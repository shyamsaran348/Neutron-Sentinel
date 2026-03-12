import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_data(data_path="data/processed/cleaned_dataset.pkl"):
    print(f"Loading data from {data_path}...")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"{data_path} not found. Please run preprocessing first.")
    return pd.read_pickle(data_path)

def plot_attack_distribution(df, output_dir="notebooks/plots"):
    print("Plotting attack distribution...")
    plt.figure(figsize=(12, 6))
    sns.countplot(y='Label', hue='Label', data=df, order=df['Label'].value_counts().index, palette='viridis', legend=False)
    plt.xscale('log')
    plt.title('Distribution of Network Attacks vs Benign Traffic (Log Scale)')
    plt.xlabel('Count (Log Scale)')
    plt.ylabel('Attack Type')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'attack_distribution.png'))
    plt.close()

def plot_correlation_heatmap(df, output_dir="notebooks/plots"):
    print("Plotting feature correlation heatmap...")
    # Select only numeric columns and sample to avoid memory crash
    numeric_df = df.select_dtypes(include=[np.number])
    if len(numeric_df) > 100000:
        numeric_df = numeric_df.sample(100000, random_state=42)
        
    corr = numeric_df.corr()
    
    # We'll just plot the top 20 most correlated features with each other for visibility
    # Get top 20 features with highest variance
    top_features = numeric_df.var().nlargest(20).index
    top_corr = numeric_df[top_features].corr()

    plt.figure(figsize=(14, 12))
    sns.heatmap(top_corr, annot=False, cmap='coolwarm', linewidths=0.5)
    plt.title('Correlation Map of Top 20 High Variance Features')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
    plt.close()

def plot_feature_importance(df, output_dir="notebooks/plots"):
    print("Plotting initial feature importance using a quick Random Forest on a sample...")
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    
    sample_df = df.sample(50000, random_state=42)
    X = sample_df.drop('Label', axis=1).select_dtypes(include=[np.number])
    y = LabelEncoder().fit_transform(sample_df['Label'])
    
    rf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    
    importances = rf.feature_importances_
    indices = np.argsort(importances)[::-1][:20] # Top 20
    
    plt.figure(figsize=(12, 8))
    plt.title("Top 20 Feature Importances (Random Forest)")
    plt.bar(range(20), importances[indices], align="center", color='teal')
    plt.xticks(range(20), X.columns[indices], rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'feature_importance.png'))
    plt.close()

def run_eda(output_dir="notebooks/plots"):
    os.makedirs(output_dir, exist_ok=True)
    df = load_data()
    
    plot_attack_distribution(df, output_dir)
    plot_correlation_heatmap(df, output_dir)
    plot_feature_importance(df, output_dir)
    print(f"EDA plots saved to {output_dir}")

if __name__ == "__main__":
    run_eda()
