import pandas as pd

df = pd.read_csv(r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET2\BENCHMARK_3VARIANTES_CONSOLIDE.csv')

# Sites dans "Territoires et départements d'outre-mer"
tom_df = df[df['region'].str.contains('outre-mer', case=False, na=False)]
sites_tom = set(tom_df['site_nom'].unique())

print(f"=== SITES DANS 'Territoires et départements d'outre-mer' ===")
print(f"Nombre de sites: {len(sites_tom)}")
print()

# Régions DOM individuelles
regions_dom = ['Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte']

for region in regions_dom:
    region_df = df[df['region'].str.contains(region, case=False, na=False)]
    sites_region = set(region_df['site_nom'].unique())
    
    # Vérifier les sites en commun
    sites_communs = sites_tom.intersection(sites_region)
    
    print(f"=== {region} ===")
    print(f"Nombre de sites: {len(sites_region)}")
    print(f"Sites en commun avec TOM: {len(sites_communs)}")
    if sites_communs:
        print(f"Sites communs: {list(sites_communs)[:5]}")
    print()

print("=== CONCLUSION ===")
# Vérifier si les sites TOM existent ailleurs
tous_sites_dom = set()
for region in regions_dom:
    region_df = df[df['region'].str.contains(region, case=False, na=False)]
    tous_sites_dom.update(region_df['site_nom'].unique())

sites_uniques_tom = sites_tom - tous_sites_dom
print(f"Sites TOM qui N'EXISTENT PAS dans les autres régions DOM: {len(sites_uniques_tom)}")
if sites_uniques_tom:
    print("Ces sites sont UNIQUES à la catégorie TOM:")
    for site in list(sites_uniques_tom)[:10]:
        print(f"  - {site}")
