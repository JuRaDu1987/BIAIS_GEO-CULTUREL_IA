import pyarrow.parquet as pq

file_path = r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET1\conversations (1).parquet'

try:
    # Read only model columns to find unique models
    table = pq.read_table(file_path, columns=['model_a_name', 'model_b_name'])
    df = table.to_pandas()
    
    unique_models = set(df['model_a_name'].dropna()).union(set(df['model_b_name'].dropna()))
    print("=== Unique Models ===")
    for model in unique_models:
        print(f"- {model}")

except Exception as e:
    print(f"Error: {e}")
