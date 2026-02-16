import pyarrow.parquet as pq

file_path = r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET1\conversations (1).parquet'

try:
    parquet_file = pq.ParquetFile(file_path)
    print("=== Column Names ===")
    for name in parquet_file.schema.names:
        print(f"- {name}")

except Exception as e:
    print(f"Error: {e}")
