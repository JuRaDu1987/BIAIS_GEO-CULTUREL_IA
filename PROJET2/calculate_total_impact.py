import pandas as pd
df = pd.read_csv(r"c:\Users\stagiaire\Desktop\PROJET_IA\PROJET2\BENCHMARK_3VARIANTES_CONSOLIDE.csv")
avg_co2 = df['gCO2_estime'].mean()
total_queries_project = 23940 + 600
estimated_total_co2 = avg_co2 * total_queries_project
print(f"Average CO2 per query: {avg_co2:.6f} g")
print(f"Total project queries: {total_queries_project}")
print(f"Estimated total CO2 for the project: {estimated_total_co2:.2f} g")
