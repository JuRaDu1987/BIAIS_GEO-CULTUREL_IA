import pandas as pd

df = pd.read_csv(r'c:\Users\stagiaire\Desktop\PROJET_IA\PROJET2\BENCHMARK_3VARIANTES_CONSOLIDE.csv')

# Regarder quelques exemples d'erreurs (score < 0.5)
erreurs = df[df['score_precision'] < 0.5].head(20)

for idx, row in erreurs.iterrows():
    print("="*80)
    print(f"Score: {row['score_precision']*100:.1f}%")
    print(f"Site: {row['site_nom']}")
    print(f"Région: {row['region']}")
    print(f"Question: {row['question'][:150]}...")
    print(f"Réponse attendue: {row['reponse_attendue']}")
    print(f"Réponse IA: {str(row['reponse_ia'])[:300]}...")
    print()
