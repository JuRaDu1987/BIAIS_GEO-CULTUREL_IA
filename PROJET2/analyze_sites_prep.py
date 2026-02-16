
import pyarrow.parquet as pq
import pandas as pd

parquet_file = r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET1\conversations (1).parquet'
benchmark_file = r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET2\BENCHMARK_TOTAL_SMART_2.csv'

# 1. Inspect one row to understand 'content' column
try:
    pf = pq.ParquetFile(parquet_file)
    first_batch = next(pf.iter_batches(batch_size=1))
    df_head = first_batch.to_pandas()
    print("Content Type:", type(df_head['content'].iloc[0]))
    print("Content Sample:", df_head['content'].iloc[0])
except Exception as e:
    print(f"Error inspecting parquet: {e}")

# 2. Get Site Names
try:
    df_bench = pd.read_csv(benchmark_file)
    sites = df_bench['site_nom'].dropna().unique().tolist()
    print(f"\nFound {len(sites)} unique sites in Atlas.")
    print(f"Sample sites: {sites[:5]}")
except Exception as e:
    print(f"Error reading benchmark: {e}")
