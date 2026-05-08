import os 
import sys
from pathlib import Path
import tabulate
# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd



def data_discover(directory):
    print(f"\n--- Data Discovery in: {directory} ---")
    files = [f for f in os.listdir(directory) if f.endswith('.tsv') or f.endswith('.csv')]
    if not files:
        print("No data files found.")
        return
    
    file_cols = {}

    for file in files:
        path = os.path.join(directory, file)
        try:
            # Assuming TSV based on previous check, fallback to CSV if needed
            sep = '\t' if file.endswith('.tsv') else ','
            df = pd.read_csv(path, sep=sep,nrows=1)
            cols = list(df.columns)
            file_cols[file] = set(cols)
            print(f"File: {file}")
            print(f"Columns: {cols}")
            print("\n")
            if len(df)>0:
                print("Data exists")
        except Exception as e:
            print(f"Error reading file {file}: {e}")
            print("\n")

    



if __name__ == "__main__":
    for folder in ['../data/raw', '../data/processed']: 
        if os.path.exists(folder):
            data_discover(folder)
        else:
            print(f"Directory {folder} does not exist.")