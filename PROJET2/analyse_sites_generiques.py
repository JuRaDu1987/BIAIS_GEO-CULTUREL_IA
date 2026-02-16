import pandas as pd
import re

df = pd.read_csv(r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET2\BENCHMARK_3VARIANTES_CONSOLIDE.csv')

# Termes génériques à rechercher (noms de sites seuls ou presque)
termes_generiques = ['cimetière', 'cimetiere', 'maison', 'château', 'chateau', 'musée', 'musee']

# Fonction pour vérifier si le nom du site est trop générique
def est_generique(site_nom):
    site_lower = str(site_nom).lower().strip()
    for terme in termes_generiques:
        # Vérifie si le site est juste le terme seul
        if site_lower == terme:
            return True
        # Vérifie si c'est un terme avec juste un article
        patterns = [
            f'^{terme}$',
            f'^le {terme}$',
            f'^la {terme}$',
            f'^les {terme}s?$',
        ]
        for pattern in patterns:
            if re.match(pattern, site_lower):
                return True
    return False

# Trouver les sites génériques
df['est_generique'] = df['site_nom'].apply(est_generique)
sites_generiques = df[df['est_generique']]

print(f'=== ANALYSE DES SITES GÉNÉRIQUES ===')
print(f'Nombre total de lignes dans le benchmark: {len(df)}')
print(f'Nombre de questions avec sites génériques: {len(sites_generiques)}')
print(f'')

# Compter par nom de site
sites_uniques = sites_generiques['site_nom'].value_counts()
print(f'Sites génériques trouvés:')
for site, count in sites_uniques.items():
    print(f'  - "{site}": {count} questions')

print(f'')
print(f'Nombre de sites uniques génériques: {len(sites_uniques)}')

# Afficher quelques exemples de questions
print(f'\n=== EXEMPLES DE QUESTIONS AVEC SITES GÉNÉRIQUES ===')
for site in sites_uniques.index[:5]:
    exemple = sites_generiques[sites_generiques['site_nom'] == site].iloc[0]
    print(f'\nSite: "{site}"')
    print(f'  Région: {exemple["region"]}')
    print(f'  Question: {exemple["question"][:100]}...')
