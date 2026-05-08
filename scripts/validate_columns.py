import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
from tabulate import tabulate

def validate_columns(directory):
    print(f"\n--- Validating files in: {directory} ---")
    files = [f for f in os.listdir(directory) if f.endswith('.tsv') or f.endswith('.csv')]

    if not files:
        print("No data files found.")
        return

    results = []
    all_columns = set()
    file_cols = {}

    for file in files:
        path = os.path.join(directory, file)
        try:
            # Assuming TSV based on previous check, fallback to CSV if needed
            sep = '\t' if file.endswith('.tsv') else ','
            df = pd.read_csv(path, sep=sep, nrows=0)
            cols = list(df.columns)
            file_cols[file] = set(cols)
            all_columns.update(cols)
            results.append({
                'File': file,
                'Col Count': len(cols),
                'Columns': ", ".join(cols[:5]) + ("..." if len(cols) > 5 else "")
            })
        except Exception as e:
            results.append({'File': file, 'Col Count': 'Error', 'Columns': str(e)})

    print(tabulate(results, headers="keys", tablefmt="grid"))

    # Check for consistency
    if len(file_cols) > 1:
        print("\nConsistency Check (Common vs Unique Columns):")
        common_cols = set.intersection(*file_cols.values())
        print(f"Common columns across all files ({len(common_cols)}): {sorted(list(common_cols))}")

        for file, cols in file_cols.items():
            unique = cols - common_cols
            if unique:
                print(f"File '{file}' has unique columns: {sorted(list(unique))}")

if __name__ == "__main__":
    for folder in ['../data/raw', '../data/processed']:
        if os.path.exists(folder):
            validate_columns(folder)
        else:
            print(f"Directory {folder} does not exist.")
