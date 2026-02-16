import pandas as pd

file_path = r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET2\conversations (1).parquet'

try:
    # Use read_parquet with a limited number of rows if possible, 
    # but pandas read_parquet doesn't support 'nrows' directly like read_csv.
    # However, we can use pyarrow to read only a few rows.
    import pyarrow.parquet as pq
    
    # Read the metadata/schema first
    parquet_file = pq.ParquetFile(file_path)
    print("=== Metadata ===")
    print(f"Number of rows: {parquet_file.metadata.num_rows}")
    print(f"Number of columns: {parquet_file.metadata.num_columns}")
    print("\n=== Schema ===")
    print(parquet_file.schema)
    
    # Read first 5 rows
    df_head = next(pq.ParquetFile(file_path).iter_batches(batch_size=5)).to_pandas()
    print("\n=== First 5 rows ===")
    print(df_head)
    print("\n=== Columns ===")
    print(df_head.columns.tolist())

except Exception as e:
    print(f"Error: {e}")
