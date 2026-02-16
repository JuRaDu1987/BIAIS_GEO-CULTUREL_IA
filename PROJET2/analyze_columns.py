
import pyarrow.parquet as pq
import pandas as pd

parquet_file = r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET1\conversations (1).parquet'

try:
    pf = pq.ParquetFile(parquet_file)
    first_batch = next(pf.iter_batches(batch_size=1))
    df_head = first_batch.to_pandas()
    print("Columns:", list(df_head.columns))
    
    # Try to identify text columns
    for col in df_head.columns:
        if 'content' in col or 'msg' in col or 'turns' in col:
            val = df_head[col].iloc[0]
            print(f"--- {col} ---")
            print(str(val)[:200] + "...") # Print first 200 chars
            
except Exception as e:
    print(f"Error: {e}")
