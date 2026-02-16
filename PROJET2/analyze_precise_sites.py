import pandas as pd
import re

df = pd.read_csv(r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET2\BENCHMARK_3VARIANTES_CONSOLIDE.csv')

def classifier_type_erreur(row):
    score = row['score_precision']
    reponse_ia = str(row['reponse_ia']).lower()
    reponse_attendue = str(row['reponse_attendue']).lower()
    site_nom = str(row['site_nom']).lower()
    
    if score >= 0.65:
        return "Réponse correcte"
    
    sites_generiques = [
        'château', 'chateau', 'cimetière', 'cimetiere', 'maison', 'musée', 'musee',
        'hôtel de ville', 'hotel de ville', 'mairie', 'église', 'eglise', 'gare',
        'bibliothèque', 'bibliotheque', 'stade', 'pont', 'place', 'jardin', 'parc',
        'chapelle', 'monument', 'site', 'domaine'
    ]
    
    site_clean = site_nom.strip().lower()
    is_ambigu = site_clean in sites_generiques or \
                (len(site_clean.split()) <= 4 and all(word in sites_generiques or word in ['et', 'sa', 'le', 'la', 'de', 'du'] for word in site_clean.replace('-', ' ').split()))
    
    if is_ambigu:
        return "Question ambiguë"
    
    refus_patterns = ["je ne peux pas", "je n'ai pas accès", "je suis désolé", "je ne suis pas en mesure", "i don't have access", "i'm sorry", "i cannot"]
    for pattern in refus_patterns:
        if pattern in reponse_ia:
            return "Refus de répondre"
    
    hallucination_patterns = ["aruba", "algérie", "algerie", "pays-bas", "néerlandais", "duc de savoie"]
    for pattern in hallucination_patterns:
        if pattern in reponse_ia:
            return "Hallucination"
            
    villes_fr = ['paris', 'lyon', 'marseille', 'bordeaux', 'toulouse', 'nantes', 'strasbourg', 'lille', 'nice', 'rennes', 'rouen', 'tours']
    for ville in villes_fr:
        if ville in reponse_ia and ville not in reponse_attendue:
            return "Erreur géographique"

    return "Erreur de connaissance"

# Apply classification
df['type_resultat'] = df.apply(classifier_type_erreur, axis=1)

# Stats for "precise" sites (not Question ambiguë)
precise_sites = df[df['type_resultat'] != "Question ambiguë"]

print(f"--- Analyse des sites PRECIS (excluant les noms génériques) ---")
print(f"Total de réponses analysées: {len(precise_sites)}")
print(f"\nRépartition des résultats:")
stats = precise_sites['type_resultat'].value_counts(normalize=True) * 100
for category, percentage in stats.items():
    print(f"  - {category}: {percentage:.1f}%")

print(f"\nPrécision moyenne sur sites précis: {precise_sites['score_precision'].mean()*100:.1f}%")

# Par modèle
print(f"\nPrécision par modèle (sites précis):")
print(precise_sites.groupby('modele_nom')['score_precision'].mean().sort_values(ascending=False) * 100)
