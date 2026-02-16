import pandas as pd

df = pd.read_csv(r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET2\BENCHMARK_3VARIANTES_CONSOLIDE.csv')

# Trouver la région TOM
for region in df['region'].unique():
    if 'outre' in region.lower() or 'territ' in region.lower():
        print(f"Region trouvée: '{region}'")
        tom_df = df[df['region'] == region]
        print(f"Nombre de lignes: {len(tom_df)}")
        print(f"\nSites uniques ({len(tom_df['site_nom'].unique())}):")
        for site in tom_df['site_nom'].unique()[:15]:
            print(f"  - {site}")
        print(f"\nExemple de question:")
        print(tom_df['question'].iloc[0][:200])
