import pyarrow.parquet as pq
import pandas as pd

file_path = r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET1\conversations (1).parquet'

target_keywords = ['smollm', 'llama', 'qwen', 'mistral', 'phi']

try:
    table = pq.read_table(file_path, columns=['model_a_name', 'model_b_name'])
    df = table.to_pandas()
    
    unique_models = sorted(list(set(df['model_a_name'].dropna()).union(set(df['model_b_name'].dropna()))))
    
    print("=== Matching Models ===")
    for model in unique_models:
        model_lower = model.lower()
        if any(k in model_lower for k in target_keywords):
            print(model)

except Exception as e:
    print(f"Error: {e}")
