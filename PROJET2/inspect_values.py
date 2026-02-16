import pyarrow.parquet as pq
import pandas as pd

file_path = r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET1\conversations (1).parquet'

try:
    table = pq.read_table(file_path, columns=[
        'model_a_name', 'duration', 'output_tokens', 'total_conv_a_kwh',
        'model_b_name', 'total_conv_b_kwh'
    ])
    df = table.to_pandas().head(10)
    print(df)

except Exception as e:
    print(f"Error: {e}")
