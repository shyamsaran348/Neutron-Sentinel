import pandas as pd
import numpy as np
df = pd.read_pickle('data/processed/cleaned_dataset.pkl')
attack = df[df['Label'] != 'BENIGN'].iloc[0]
benign = df[df['Label'] == 'BENIGN'].iloc[0]

print("--- ATTACK (", attack['Label'], ") ---")
print(attack.drop('Label').values.tolist()[:20])

print("--- BENIGN ---")
print(benign.drop('Label').values.tolist()[:20])
