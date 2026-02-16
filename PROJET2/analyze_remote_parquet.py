import pandas as pd
import sys

url = "https://huggingface.co/datasets/ministere-culture/comparia-conversations/resolve/main/conversations.parquet"

print(f"Tentative de lecture du fichier depuis: {url}")

try:
    df = pd.read_parquet(url)
    print("\n--- Infos du fichier ---")
    print(f"Nombre de lignes: {len(df)}")
    print(f"Nombre de colonnes: {len(df.columns)}")
    print("\n--- Colonnes ---")
    for col in df.columns:
        print(f"- {col}")
    
    print("\n--- Aperçu des données (5 premières lignes) ---")
    print(df.head().to_string())

except Exception as e:
    print(f"\nERREUR: Impossible de lire le fichier. {e}")
    # Si c'est gated, on peut essayer le format CSV/preview si disponible ou juste signaler
    print("Si le dataset est 'gated' (nécessite acceptation des conditions), ce script ne peut pas le lire directement sans token.")
