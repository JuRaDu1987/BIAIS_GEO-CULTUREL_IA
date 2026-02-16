import pyarrow.parquet as pq
import pandas as pd
import os

file_path = r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET1\conversations (1).parquet'
output_path = r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET2\model_stats.csv'

columns = [
    'model_a_name', 'model_b_name',
    'total_conv_a_kwh', 'total_conv_b_kwh',
    'total_conv_a_output_tokens', 'total_conv_b_output_tokens',
    'model_a_active_params', 'model_b_active_params'
]

print("Starting processing...")

try:
    parquet_file = pq.ParquetFile(file_path)
    
    # Accumulators
    model_stats = {}
    
    def update_stats(name, kwh, tokens, params):
        if not name:
            return
        if name not in model_stats:
            model_stats[name] = {
                'count': 0,
                'total_kwh': 0.0,
                'total_tokens': 0,
                'params': params
            }
        
        stats = model_stats[name]
        stats['count'] += 1
        if pd.notna(kwh): stats['total_kwh'] += kwh
        if pd.notna(tokens): stats['total_tokens'] += tokens
        if pd.notna(params) and (stats['params'] is None or pd.isna(stats['params'])):
             stats['params'] = params

    # Process in batches
    for batch in parquet_file.iter_batches(batch_size=10000, columns=columns):
        df_batch = batch.to_pandas()
        
        # Process Model A
        for _, row in df_batch.iterrows():
            update_stats(
                row['model_a_name'], 
                row['total_conv_a_kwh'], 
                row['total_conv_a_output_tokens'],
                row['model_a_active_params']
            )
            
            # Process Model B
            update_stats(
                row['model_b_name'], 
                row['total_conv_b_kwh'], 
                row['total_conv_b_output_tokens'],
                row['model_b_active_params']
            )
        
        print(f"Processed batch... Total models found so far: {len(model_stats)}")

    # Convert to DataFrame
    data = []
    for name, stats in model_stats.items():
        avg_kwh = stats['total_kwh'] / stats['count'] if stats['count'] > 0 else 0
        avg_tokens = stats['total_tokens'] / stats['count'] if stats['count'] > 0 else 0
        
        # Avoid division by zero for efficiency
        # Efficiency: Tokens / KWh (TOKENS PER KWH)
        # Or KWh / 1k Tokens?
        # Let's simple store the raw avgs and calculating derived metrics in dashboard
        
        data.append({
            'model_name': name,
            'count': stats['count'],
            'total_kwh': stats['total_kwh'],
            'total_tokens': stats['total_tokens'],
            'avg_kwh': avg_kwh,
            'avg_tokens': avg_tokens,
            'active_params_b': stats['params']
        })
        
    df_stats = pd.DataFrame(data)
    df_stats.to_csv(output_path, index=False)
    print(f"Stats saved to {output_path}")
    print(df_stats.head())

except Exception as e:
    print(f"Error: {e}")
