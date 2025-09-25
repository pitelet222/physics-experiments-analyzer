import os
import pandas as pd

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def read_csv(path, **kwargs):
    return pd.read_csv(path, **kwargs)

def save_csv(df, path):
    df.to_csv(path, index=False)
