"""
Biais Géo-Culturel IA
Dashboard d'analyse des biais géographiques et culturels des modèles d'IA
Créé avec Streamlit - Version accessible aux daltoniens
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# Configuration de la page
st.set_page_config(
    page_title="Biais Géo-Culturel IA",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé - couleurs sobres et accessibles
st.markdown("""
<style>
    /* Thème général sobre */
    .main {
        background-color: #f8f9fa;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #e9ecef;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #495057;
        color: white;
    }
    
    h1, h2, h3 {
        color: #212529;
    }
    
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Palette de couleurs accessible aux daltoniens (IBM Design + Wong palette)
COLORBLIND_PALETTE = [
    "#648FFF",  # Bleu
    "#FFB000",  # Orange/Jaune
    "#785EF0",  # Violet
    "#DC267F",  # Magenta
    "#FE6100",  # Orange foncé
    "#000000",  # Noir
    "#808080",  # Gris
]

# Palette pour carte choroplèthe (séquentielle accessible)
SEQUENTIAL_PALETTE = [
    "#f7fbff",
    "#deebf7", 
    "#c6dbef",
    "#9ecae1",
    "#6baed6",
    "#4292c6",
    "#2171b5",
    "#08519c",
    "#08306b"
]


@st.cache_data
def load_data():
    """Charge les données du benchmark"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "BENCHMARK_3VARIANTES_CONSOLIDE.csv")
    df = pd.read_csv(file_path)
    return df


@st.cache_data
def load_eco_data():
    """Charge les données écologiques et de performance"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "model_stats.csv")
        df = pd.read_csv(file_path)
        
        # Filtrage des noms de modèles suspects (tentatives d'injection XSS dans le dataset)
        df = df[~df['model_name'].astype(str).str.contains('<|>|script|alert', case=False, na=False)]
        
        # Calcul de l'efficience (Tokens / KWh)
        # Gestion des divisions par zéro
        df['efficiency'] = df.apply(lambda row: row['total_tokens'] / row['total_kwh'] if row['total_kwh'] > 0 else 0, axis=1)
        return df
    except Exception as e:
        st.error(f"Erreur chargement stats eco: {e}")
        return pd.DataFrame()


@st.cache_data
def load_france_test_data():
    """Charge les données du test France pour l'analyse du biais de centralisation"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "TEST_FRANCE_WISHMELUCK.csv")
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Erreur chargement TEST_FRANCE_WISHMELUCK.csv: {e}")
        return pd.DataFrame()


def analyze_centralization_bias(df_france):
    """
    Analyse le biais de centralisation vers Paris dans les réponses des IA.
    Retourne un DataFrame avec les métriques de biais par modèle.
    """
    import re
    
    # Mapping des colonnes aux noms de modèles affichés (6 IA)
    model_columns = {
        'reponse_smollm2:1.7b': 'smollm2:1.7b',
        'reponse_llama3.2:1b': 'llama3.2:1b',
        'reponse_qwen2.5:1.5b': 'qwen2.5:1.5b',
        'reponse_mistral': 'mistral',
        'reponse_llama3': 'llama3',
        'reponse_phi3': 'phi3'
    }
    
    # Liste étendue incluant villes, régions, départements et lieux emblématiques
    lieux_france = [
        # Grandes villes
        'paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes', 'strasbourg',
        'montpellier', 'bordeaux', 'lille', 'rennes', 'reims', 'toulon', 
        'saint-étienne', 'le havre', 'grenoble', 'dijon', 'angers', 'nîmes',
        'villeurbanne', 'clermont-ferrand', 'aix-en-provence', 'brest', 'tours',
        'amiens', 'limoges', 'perpignan', 'metz', 'besançon', 'orléans', 'rouen',
        'caen', 'nancy', 'avignon', 'cannes', 'saint-tropez', 'monaco',
        # Régions
        'normandie', 'bretagne', 'provence', 'alsace', 'bourgogne', 'auvergne',
        'corse', 'aquitaine', 'lorraine', 'picardie', 'champagne', 'languedoc',
        'roussillon', 'savoie', 'dauphiné', 'vendée', 'charentes', 'limousin',
        'poitou', 'touraine', 'anjou', 'beauce', 'sologne', 'gascogne', 'béarn',
        # Zones géographiques
        'côte d\'azur', 'riviera', 'alpes', 'pyrénées', 'jura', 'vosges', 
        'massif central', 'camargue', 'luberon', 'verdon', 'ardèche',
        'dordogne', 'périgord', 'lot', 'gironde', 'méditerranée',
        # Lieux emblématiques
        'mont-saint-michel', 'mont saint-michel', 'mont st-michel',
        'versailles', 'chambord', 'chenonceau', 'fontainebleau', 'amboise',
        'louvre', 'tour eiffel', 'eiffel', 'notre-dame', 'sacré-coeur',
        'mont blanc', 'gorges du verdon', 'pont du gard', 'carcassonne',
        'lascaux', 'rocamadour', 'saint-malo', 'dinard', 'deauville',
        'biarritz', 'arcachon', 'la rochelle', 'île de ré', 'oléron',
        # Vallées et terroirs célèbres
        'loire', 'rhône', 'seine', 'garonne', 'val de loire', 'beaujolais',
        'médoc', 'saint-émilion', 'cognac', 'armagnac', 'champagne',
        'palais-royal', 'saint-denis', 'disneyland', 'arc de triomphe', 'champs-élysées'
    ]
    
    # Lieux considérés comme "Paris" pour le biais de centralisation
    lieux_parisiens = [
        'paris', 'louvre', 'tour eiffel', 'eiffel', 'notre-dame', 'sacré-coeur', 
        'versailles', 'fontainebleau', 'disneyland', 'arc de triomphe', 'champs-élysées',
        'palais-royal', 'saint-denis'
    ]
    
    def find_city_positions(text):
        """Trouve les positions des lieux dans le texte"""
        text_lower = str(text).lower()
        city_positions = {}
        
        for lieu in lieux_france:
            # Recherche du lieu dans le texte (en tenant compte des variantes)
            pattern = r'\b' + re.escape(lieu) + r'\b'
            match = re.search(pattern, text_lower)
            if match:
                city_positions[lieu] = match.start()
        
        return city_positions
    
    def is_paris_first(text):
        """Vérifie si un lieu parisien est le premier mentionné"""
        positions = find_city_positions(text)
        if not positions:
            return False
        
        # Trouver le premier lieu mentionné
        first_lieu = min(positions, key=positions.get)
        return first_lieu in lieux_parisiens
    
    def is_paris_only(text):
        """Vérifie si seuls des lieux parisiens sont mentionnés"""
        positions = find_city_positions(text)
        if not positions:
            return False
        
        # Tous les lieux mentionnés sont-ils parisiens ?
        villes_mentionnees = list(positions.keys())
        return all(v in lieux_parisiens for v in villes_mentionnees)
    
    def count_paris_mentions(text):
        """Compte le nombre de fois que Paris est mentionné"""
        text_lower = str(text).lower()
        return len(re.findall(r'\bparis\b', text_lower))
    
    def count_other_cities(text):
        """Compte le nombre de villes autres que Paris mentionnées"""
        positions = find_city_positions(text)
        other_cities = [c for c in positions.keys() if c != 'paris']
        return len(other_cities)
    
    results = []
    
    for col, model_name in model_columns.items():
        if col not in df_france.columns:
            continue
        
        responses = df_france[col].dropna()
        total_responses = len(responses)
        
        if total_responses == 0:
            continue
        
        # Calcul des métriques
        paris_first_count = sum(responses.apply(is_paris_first))
        paris_only_count = sum(responses.apply(is_paris_only))
        avg_paris_mentions = responses.apply(count_paris_mentions).mean()
        avg_other_cities = responses.apply(count_other_cities).mean()
        
        results.append({
            'Modèle': model_name,
            'Paris en 1er (%)': (paris_first_count / total_responses) * 100,
            'Paris uniquement (%)': (paris_only_count / total_responses) * 100,
            'Mentions Paris (moy)': avg_paris_mentions,
            'Autres villes (moy)': avg_other_cities,
            'Total réponses': total_responses
        })
    
    return pd.DataFrame(results)


def classifier_type_erreur(row):
    """
    Classifie le type d'erreur d'une réponse IA
    Retourne une catégorie parmi:
    - Réponse correcte
    - Hallucination
    - Erreur géographique
    - Refus de répondre
    - Réponse vague/incomplète
    - Question ambiguë
    """
    score = row['score_precision']
    reponse_ia = str(row['reponse_ia']).lower()
    reponse_attendue = str(row['reponse_attendue']).lower()
    site_nom = str(row['site_nom']).lower()
    
    # Si le score est bon, c'est une réponse correcte
    if score >= 0.65:
        return "Réponse correcte"
    
    # Détection des questions ambiguës (sites génériques)
    sites_generiques = [
        'château', 'chateau', 'cimetière', 'cimetiere', 'maison', 'musée', 'musee',
        'hôtel de ville', 'hotel de ville', 'mairie', 'église', 'eglise', 'gare',
        'bibliothèque', 'bibliotheque', 'stade', 'pont', 'place', 'jardin', 'parc',
        'chapelle', 'monument', 'site', 'domaine', 'halles', 'halle'
    ]
    
    # Si le nom du site est très court ou composé uniquement de termes génériques
    site_clean = site_nom.strip().lower()
    is_ambigu = site_clean in sites_generiques or \
                (len(site_clean.split()) <= 4 and all(word in sites_generiques or word in ['et', 'sa', 'le', 'la', 'de', 'du'] for word in site_clean.replace('-', ' ').split()))
    
    if is_ambigu:
        return "Question ambiguë"
    
    # Détection du refus de répondre
    refus_patterns = [
        "je ne peux pas", "je n'ai pas accès", "je suis désolé", "je ne suis pas en mesure",
        "vous devriez chercher", "faire une recherche", "google maps", "internet",
        "je ne possède pas", "pas de fonctionnalité", "i don't have access",
        "i'm sorry", "i cannot", "vous pouvez faire une recherche",
        "consulter", "vérifier sur", "service officiel", "site officiel"
    ]
    for pattern in refus_patterns:
        if pattern in reponse_ia:
            return "Refus de répondre"
    
    # Détection des hallucinations (réponses complètement hors sujet)
    hallucination_patterns = [
        "aruba", "algérie", "algerie", "pays-bas", "néerlandais", "neerlandais",
        "duc de savoie", "chiffrement", "code territorial", "contrats",
        "vous rencontrer", "parfaitment informé"
    ]
    for pattern in hallucination_patterns:
        if pattern in reponse_ia:
            return "Hallucination"
    
    # Détection des erreurs géographiques (mauvaise localisation citée)
    villes_fr = ['paris', 'lyon', 'marseille', 'bordeaux', 'toulouse', 'nantes', 
                 'strasbourg', 'lille', 'nice', 'rennes', 'rouen', 'tours', 
                 'montpellier', 'avignon', 'grenoble', 'dijon', 'angers', 'reims', 
                 'le mans', 'brest', 'amiens', 'limoges', 'clermont-ferrand', 'vezelay', 'vézelay']
    
    for ville in villes_fr:
        if ville in reponse_ia and ville not in reponse_attendue:
            return "Erreur géographique"

    # Si le score est bas mais que l'IA affirme quelque chose (pas un refus)
    if score > 0 and score < 0.4:
        # Si la réponseIA ne partage aucun mot clé avec la réponse attendue
        words_ia = set(reponse_ia.replace('.', ' ').split())
        words_att = set(reponse_attendue.replace('.', ' ').split())
        if not (words_ia & words_att):
            return "Erreur de connaissance"

    # Détection des réponses vagues/incomplètes
    if score > 0 and score < 0.5:
        if len(reponse_ia) < 30:
            return "Réponse vague/incomplète"
        return "Erreur de connaissance"
    
    # Hallucination par défaut pour les scores très bas
    if score < 0.3:
        return "Hallucination"
    
    return "Erreur de connaissance"


@st.cache_data
def get_france_regions_geojson():
    """Retourne le GeoJSON des régions françaises avec leurs formes complètes"""
    # URL du GeoJSON officiel des régions françaises
    geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson"
    
    try:
        import urllib.request
        with urllib.request.urlopen(geojson_url, timeout=10) as response:
            geojson_data = json.loads(response.read().decode())
        return geojson_data
    except:
        # GeoJSON de secours simplifié si le téléchargement échoue
        return None


def get_region_name_mapping():
    """Mapping des noms de régions pour correspondance avec les données"""
    return {
        "Auvergne-Rhône-Alpes": "Auvergne-Rhône-Alpes",
        "Bourgogne-Franche-Comté": "Bourgogne-Franche-Comté",
        "Bretagne": "Bretagne",
        "Centre-Val de Loire": "Centre-Val de Loire",
        "Corse": "Corse",
        "Grand Est": "Grand Est",
        "Hauts-de-France": "Hauts-de-France",
        "Île-de-France": "Île-de-France",
        "Normandie": "Normandie",
        "Nouvelle-Aquitaine": "Nouvelle-Aquitaine",
        "Occitanie": "Occitanie",
        "Pays de la Loire": "Pays de la Loire",
        "Provence-Alpes-Côte d'Azur": "Provence-Alpes-Côte d'Azur",
        # Outre-mer
        "Guadeloupe": "Guadeloupe",
        "Martinique": "Martinique",
        "Guyane": "Guyane",
        "La Réunion": "La Réunion",
        "Mayotte": "Mayotte",
        "Territoires et départements d'outre-mer": "Territoires et départements d'outre-mer",
    }


def calculate_precision_by_region(df, mode="tous"):
    """
    Calcule les scores de précision par région
    mode: 'tous' pour la moyenne générale, ou le nom d'un modèle spécifique
    """
    if mode == "tous":
        precision_df = df.groupby('region').agg({
            'score_precision': 'mean',
            'site_nom': 'count'
        }).reset_index()
    else:
        filtered_df = df[df['modele_nom'] == mode]
        precision_df = filtered_df.groupby('region').agg({
            'score_precision': 'mean',
            'site_nom': 'count'
        }).reset_index()
    
    precision_df.columns = ['region', 'score_precision_moyen', 'nombre_evaluations']
    precision_df['score_precision_pct'] = precision_df['score_precision_moyen'] * 100
    
    return precision_df


def create_interactive_map(precision_df, title="Score de précision par région"):
    """Crée une carte choroplèthe interactive avec les régions colorées selon leur score"""
    
    # Charger le GeoJSON des régions
    geojson_data = get_france_regions_geojson()
    
    # Coordonnées centrales des régions (pour les labels et l'outre-mer)
    region_coords = {
        "Auvergne-Rhône-Alpes": {"lat": 45.5, "lon": 4.5},
        "Bourgogne-Franche-Comté": {"lat": 47.2, "lon": 4.8},
        "Bretagne": {"lat": 48.2, "lon": -3.0},
        "Centre-Val de Loire": {"lat": 47.5, "lon": 1.5},
        "Corse": {"lat": 42.0, "lon": 9.0},
        "Grand Est": {"lat": 48.7, "lon": 5.5},
        "Guadeloupe": {"lat": 16.2, "lon": -61.5},
        "Guyane": {"lat": 4.0, "lon": -53.0},
        "Hauts-de-France": {"lat": 49.9, "lon": 2.8},
        "Île-de-France": {"lat": 48.8, "lon": 2.5},
        "La Réunion": {"lat": -21.1, "lon": 55.5},
        "Martinique": {"lat": 14.6, "lon": -61.0},
        "Mayotte": {"lat": -12.8, "lon": 45.2},
        "Normandie": {"lat": 49.2, "lon": -0.3},
        "Nouvelle-Aquitaine": {"lat": 45.0, "lon": -0.5},
        "Occitanie": {"lat": 43.6, "lon": 2.0},
        "Pays de la Loire": {"lat": 47.4, "lon": -1.0},
        "Provence-Alpes-Côte d'Azur": {"lat": 43.9, "lon": 6.0},
        "Territoires et départements d'outre-mer": {"lat": 5.5, "lon": -53.0},
    }
    
    # Ajouter les coordonnées au DataFrame
    precision_df['lat'] = precision_df['region'].map(lambda x: region_coords.get(x, {}).get('lat', 0))
    precision_df['lon'] = precision_df['region'].map(lambda x: region_coords.get(x, {}).get('lon', 0))
    
    if geojson_data is not None:
        # Ajouter une colonne formatée pour l'affichage
        precision_df['score_format'] = precision_df['score_precision_pct'].apply(lambda x: f"{x:.1f}%")
        
        # Calculer la plage dynamique des scores pour mieux voir les différences
        score_min = precision_df['score_precision_pct'].min()
        score_max = precision_df['score_precision_pct'].max()
        
        # Élargir légèrement la plage pour un meilleur contraste
        range_padding = (score_max - score_min) * 0.1
        range_min = max(0, score_min - range_padding)
        range_max = min(100, score_max + range_padding)
        
        # Si la plage est trop petite, utiliser une plage fixe
        if (range_max - range_min) < 10:
            range_min = max(0, score_min - 5)
            range_max = min(100, score_max + 5)
        
        # Palette de couleurs adaptée aux daltoniens
        # Utilisation de la palette "Viridis" modifiée pour une meilleure lisibilité
        # Cette palette est scientifiquement conçue pour être perceptuellement uniforme
        # et accessible aux personnes atteintes de daltonisme
        colorscale_daltonien = [
            [0.0, '#440154'],    # Violet foncé (score bas)
            [0.25, '#3b528b'],   # Bleu-violet
            [0.5, '#21918c'],    # Turquoise
            [0.75, '#5ec962'],   # Vert clair
            [1.0, '#fde725']     # Jaune vif (score élevé)
        ]
        
        # Créer la carte choroplèthe avec les régions colorées
        fig = px.choropleth(
            precision_df,
            geojson=geojson_data,
            locations='region',
            featureidkey='properties.nom',
            color='score_precision_pct',
            color_continuous_scale=colorscale_daltonien,
            range_color=[range_min, range_max],
            hover_name='region',
            custom_data=['score_format', 'nombre_evaluations'],
            labels={
                'score_precision_pct': 'Score (%)',
                'nombre_evaluations': 'Evaluations'
            }
        )
        
        # Personnaliser le template du hover
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br><br>" +
                         "Score: %{customdata[0]}<br>" +
                         "Evaluations: %{customdata[1]}<extra></extra>"
        )
        
        # Mise à jour du layout pour la France métropolitaine
        fig.update_geos(
            fitbounds="locations",
            visible=True,
            showland=True,
            landcolor='#f5f5f5',
            showocean=True,
            oceancolor='#e6f2ff',
            showcountries=True,
            countrycolor='#999999',
            showcoastlines=True,
            coastlinecolor='#666666',
            showframe=False,
            projection_type='mercator'
        )
        
        fig.update_traces(
            marker_line_width=1.5,
            marker_line_color='#333333'
        )
        
        # Générer les ticks de la colorbar dynamiquement
        tick_step = (range_max - range_min) / 4
        tick_vals = [range_min + i * tick_step for i in range(5)]
        tick_text = [f"{v:.0f}%" for v in tick_vals]
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=20, color='#212529'),
                x=0.5,
                xanchor='center'
            ),
            coloraxis_colorbar=dict(
                title="Score (%)",
                thickness=20,
                len=0.7,
                tickformat=".0f",
                tickvals=tick_vals,
                ticktext=tick_text
            ),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor='white'
        )
        
    else:
        # Fallback: carte avec marqueurs si le GeoJSON n'est pas disponible
        precision_df_valid = precision_df[precision_df['lat'] != 0].copy()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scattergeo(
            lon=precision_df_valid['lon'],
            lat=precision_df_valid['lat'],
            text=precision_df_valid.apply(
                lambda row: f"<b>{row['region']}</b><br>" +
                           f"Score: {row['score_precision_pct']:.1f}%<br>" +
                           f"Evaluations: {row['nombre_evaluations']}",
                axis=1
            ),
            hoverinfo='text',
            mode='markers',
            marker=dict(
                size=precision_df_valid['score_precision_pct'] / 2 + 10,
                color=precision_df_valid['score_precision_pct'],
                colorscale=[
                    [0, '#d73027'],
                    [0.25, '#fc8d59'],
                    [0.5, '#fee08b'],
                    [0.75, '#91cf60'],
                    [1, '#1a9850']
                ],
                colorbar=dict(
                    title="Score (%)",
                    thickness=15,
                    len=0.7,
                    tickformat=".0f"
                ),
                line=dict(width=1, color='#333333'),
                opacity=0.85
            ),
            showlegend=False
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=20, color='#212529'),
                x=0.5,
                xanchor='center'
            ),
            geo=dict(
                scope='europe',
                showland=True,
                landcolor='#f0f0f0',
                showocean=True,
                oceancolor='#e6f2ff',
                showcountries=True,
                countrycolor='#999999',
                center=dict(lat=46.5, lon=2.5),
            ),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor='white'
        )
    
    return fig


@st.cache_data
def get_outremer_geojson():
    """Télécharge les GeoJSON des départements d'outre-mer"""
    base_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements"
    
    # Mapping des codes départements pour les DOM-TOM
    dom_tom_codes = {
        "Guadeloupe": "971",
        "Martinique": "972",
        "Guyane": "973",
        "La Réunion": "974",
        "Mayotte": "976"
    }
    
    geojson_data = {}
    
    for nom, code in dom_tom_codes.items():
        try:
            import urllib.request
            url = f"{base_url}/{code}-{nom.lower().replace(' ', '-').replace('é', 'e')}/departement-{code}.geojson"
            # URL alternative plus simple
            url_alt = f"https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions/{nom.lower().replace(' ', '-').replace('é', 'e')}/region-{nom.lower().replace(' ', '-').replace('é', 'e')}.geojson"
            
            with urllib.request.urlopen(url_alt, timeout=5) as response:
                data = json.loads(response.read().decode())
                geojson_data[nom] = data
        except:
            geojson_data[nom] = None
    
    return geojson_data


def create_outremer_maps(precision_df, title_prefix=""):
    """Crée des visualisations pour les régions d'outre-mer sous forme de cartes visuelles"""
    
    outremer_regions = ["Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte"]
    outremer_data = precision_df[precision_df['region'].isin(outremer_regions)].copy()
    
    if outremer_data.empty:
        return None
    
    # Obtenir les scores pour chaque territoire
    scores_dict = {}
    for _, row in outremer_data.iterrows():
        scores_dict[row['region']] = {
            'score': row['score_precision_pct'],
            'evals': row['nombre_evaluations']
        }
    
    # Calculer la plage dynamique des scores (tous les territoires, pas seulement outre-mer)
    all_scores = precision_df['score_precision_pct'].values
    score_min = min(all_scores)
    score_max = max(all_scores)
    
    # Palette Viridis adaptée aux daltoniens (5 couleurs)
    viridis_colors = [
        '#440154',  # Violet foncé (score bas)
        '#3b528b',  # Bleu-violet
        '#21918c',  # Turquoise
        '#5ec962',  # Vert clair
        '#fde725'   # Jaune vif (score élevé)
    ]
    
    # Fonction pour obtenir la couleur basée sur le score avec palette Viridis
    def get_color_for_score(score, score_min, score_max):
        # Normaliser le score entre 0 et 1 selon la plage dynamique
        if score_max == score_min:
            normalized = 0.5
        else:
            normalized = (score - score_min) / (score_max - score_min)
        
        # Limiter entre 0 et 1
        normalized = max(0, min(1, normalized))
        
        # Sélectionner la couleur selon le score normalisé
        if normalized < 0.2:
            return viridis_colors[0]
        elif normalized < 0.4:
            return viridis_colors[1]
        elif normalized < 0.6:
            return viridis_colors[2]
        elif normalized < 0.8:
            return viridis_colors[3]
        else:
            return viridis_colors[4]
    
    # Créer les données pour chaque territoire
    territories_data = []
    
    for region in outremer_regions:
        if region in scores_dict:
            score = scores_dict[region]['score']
            evals = scores_dict[region]['evals']
            color = get_color_for_score(score, score_min, score_max)
            
            territories_data.append({
                'region': region,
                'score': score,
                'evals': evals,
                'color': color
            })
    
    return territories_data


def create_bar_chart_regions(precision_df, title="Score de précision par région"):
    """Crée un graphique en barres des scores par région"""
    
    # Trier par score
    precision_df_sorted = precision_df.sort_values('score_precision_pct', ascending=True)
    
    # Calculer la plage dynamique des scores
    score_min = precision_df_sorted['score_precision_pct'].min()
    score_max = precision_df_sorted['score_precision_pct'].max()
    
    # Palette Viridis adaptée aux daltoniens (5 couleurs)
    viridis_colors = [
        '#440154',  # Violet foncé (score bas)
        '#3b528b',  # Bleu-violet
        '#21918c',  # Turquoise
        '#5ec962',  # Vert clair
        '#fde725'   # Jaune vif (score élevé)
    ]
    
    # Créer les couleurs basées sur le score avec la palette Viridis
    colors = []
    for score in precision_df_sorted['score_precision_pct']:
        # Normaliser le score entre 0 et 1
        if score_max == score_min:
            normalized = 0.5
        else:
            normalized = (score - score_min) / (score_max - score_min)
        
        # Sélectionner la couleur selon le score normalisé
        if normalized < 0.2:
            colors.append(viridis_colors[0])
        elif normalized < 0.4:
            colors.append(viridis_colors[1])
        elif normalized < 0.6:
            colors.append(viridis_colors[2])
        elif normalized < 0.8:
            colors.append(viridis_colors[3])
        else:
            colors.append(viridis_colors[4])
    
    fig = go.Figure(go.Bar(
        x=precision_df_sorted['score_precision_pct'],
        y=precision_df_sorted['region'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='#333333', width=0.5)
        ),
        text=precision_df_sorted['score_precision_pct'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}%<br>Evaluations: %{customdata}<extra></extra>',
        customdata=precision_df_sorted['nombre_evaluations']
    ))
    
    # Définir la plage de l'axe X dynamiquement
    x_range_min = max(0, score_min - 5)
    x_range_max = min(100, score_max + 10)
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='#212529', weight='bold'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Score de précision (%)",
            range=[x_range_min, x_range_max],
            tickformat=".0f",
            gridcolor='#e0e0e0'
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=11)
        ),
        height=max(400, len(precision_df) * 28),
        margin=dict(l=200, r=50, t=50, b=50),
        paper_bgcolor='white',
        plot_bgcolor='#fafafa'
    )
    
    return fig


def main():
    """Fonction principale du dashboard"""
    
    # Titre principal
    st.title("Analyse de Biais Géo-Culturel")
    st.markdown("---")
    
    # Chargement des données
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return
    
    # Calcul des métriques moyennes par modèle pour les analyses croisées et synthèse
    perf_metrics = df.groupby('modele_nom').agg({
        'temps_secondes': 'mean',
        'gCO2_estime': 'mean',
        'score_precision': 'mean',
        'site_nom': 'count'
    }).reset_index()
    
    # Mapping des spécifications techniques
    model_specs = {
        'smollm2:1.7b': {'Params': '1.7B', 'Poids': '1.0 Go'},
        'llama3.2:1b': {'Params': '1.2B', 'Poids': '1.3 Go'},
        'qwen2.5:1.5b': {'Params': '1.5B', 'Poids': '1.6 Go'},
        'mistral': {'Params': '7.2B', 'Poids': '4.1 Go'},
        'llama3': {'Params': '8.0B', 'Poids': '4.7 Go'},
        'phi3': {'Params': '3.8B', 'Poids': '2.2 Go'}
    }
    perf_metrics['Params'] = perf_metrics['modele_nom'].map(lambda x: model_specs.get(x, {}).get('Params', 'N/A'))
    perf_metrics['Poids'] = perf_metrics['modele_nom'].map(lambda x: model_specs.get(x, {}).get('Poids', 'N/A'))
    perf_metrics.columns = ['Modèle', 'Temps moyen (s)', 'CO2 moyen (g)', 'Précision', 'Évaluations', 'Paramètres (Milliards)', 'Taille (Fichier)']
    
    # Métriques globales pour les KPI
    metrics_avg_time = df['temps_secondes'].mean()
    metrics_avg_co2 = df['gCO2_estime'].mean()
    metrics_total_co2 = df['gCO2_estime'].sum()
    
    # Création des onglets
    tabs = st.tabs(["Connaissances Culturelles", "Biais de Centralisation", "Performance & Écologie", "Lacunes IA", "Synthèse & Impact"])
    
    # ===========================================
    # ONGLET 1 : Analyse des connaissances culturelles
    # ===========================================
    with tabs[0]:
        st.header("Évaluation des Connaissances Culturelles sur la France")
        
        # Sidebar pour les informations générales
        # Ajouter l'image TERRE3
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(base_dir, "TERRE3.jpg")
            st.sidebar.image(img_path, use_container_width=True)
        except Exception as e:
            pass  # Si l'image n'est pas trouvée, on continue sans erreur
        
        st.sidebar.markdown("**Modèles étudiés:**")
        
        # Liste des modèles disponibles
        modeles_disponibles = df['modele_nom'].unique().tolist()
        for modele in modeles_disponibles:
            st.sidebar.markdown(f"- {modele}")
        
        # Calcul des données de précision pour les métriques globales (moyenne de tous)
        precision_df = calculate_precision_by_region(df, "tous")
        
        # Métriques globales
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            score_global = precision_df['score_precision_pct'].mean()
            st.metric(
                label="Score moyen global",
                value=f"{score_global:.1f}%"
            )
        
        with col2:
            meilleure_region = precision_df.loc[precision_df['score_precision_pct'].idxmax()]
            st.metric(
                label="Meilleure région",
                value=f"{meilleure_region['score_precision_pct']:.1f}%",
                delta=meilleure_region['region'][:20]
            )
        
        with col3:
            pire_region = precision_df.loc[precision_df['score_precision_pct'].idxmin()]
            st.metric(
                label="Région à améliorer",
                value=f"{pire_region['score_precision_pct']:.1f}%",
                delta=pire_region['region'][:20]
            )
        
        with col4:
            total_evals = precision_df['nombre_evaluations'].sum()
            st.metric(
                label="Total évaluations",
                value=f"{total_evals:,}"
            )
            
        with col5:
            evals_par_region = int(precision_df['nombre_evaluations'].mean())
            st.metric(
                label="Évaluations par Région",
                value=f"{evals_par_region:,}"
            )
        
        st.markdown("---")
        
        # Classement des modèles IA (tableau simple) - EN PREMIER
        st.subheader("Classement des modèles IA")
        
        # Calculer les scores moyens par modèle
        scores_par_modele = df.groupby('modele_nom').agg({
            'score_precision': 'mean',
            'site_nom': 'count'
        }).reset_index()
        scores_par_modele.columns = ['Modele', 'Score moyen', 'Nombre evaluations']
        
        # Définition des concepteurs et nationalités des modèles
        def get_company(model_name):
            name = str(model_name).lower()
            if 'mistral' in name:
                return 'Mistral AI'
            elif 'llama' in name:
                return 'Meta'
            elif 'phi' in name:
                return 'Microsoft'
            elif 'smollm' in name:
                return 'Hugging Face'
            elif 'qwen' in name:
                return 'Alibaba'
            else:
                return 'Autre'

        def get_nationality(model_name):
            name = str(model_name).lower()
            if 'mistral' in name:
                return '🇫🇷 France'
            elif any(x in name for x in ['llama', 'phi', 'gemma', 'gpt']):
                return '🇺🇸 USA'
            elif 'smollm' in name:
                return '🇫🇷/🇺🇸 Hugging Face'
            elif 'qwen' in name:
                return '🇨🇳 Chine'
            else:
                return '🌍 International'
                
        scores_par_modele['Concepteur'] = scores_par_modele['Modele'].apply(get_company)
        scores_par_modele['Nationalité'] = scores_par_modele['Modele'].apply(get_nationality)
        scores_par_modele['Score moyen (%)'] = scores_par_modele['Score moyen'] * 100
        scores_par_modele = scores_par_modele.sort_values('Score moyen (%)', ascending=False).reset_index(drop=True)
        
        # Récupérer le nombre d'évaluations (identique pour tous les modèles)
        if not scores_par_modele.empty:
            nb_evals_par_modele = int(scores_par_modele['Nombre evaluations'].iloc[0])
        else:
            nb_evals_par_modele = 0
        
        # Créer le tableau simple avec les places 1 à 6
        classement_modeles = scores_par_modele.head(6).copy()
        classement_modeles['Place'] = range(1, len(classement_modeles) + 1)
        classement_modeles['Score moyen (%)'] = classement_modeles['Score moyen (%)'].apply(lambda x: f"{x:.1f}%")
        
        # Réorganiser les colonnes pour inclure le Concepteur
        classement_modeles = classement_modeles[['Place', 'Modele', 'Concepteur', 'Nationalité', 'Score moyen (%)']]
        
        # Afficher le tableau et la note côte à côte
        col_tableau, col_note = st.columns([3, 1])
        
        with col_tableau:
            st.dataframe(classement_modeles, use_container_width=True, hide_index=True)
        
        with col_note:
            st.info(f"**{nb_evals_par_modele:,}** évaluations par modèle")
        
        st.markdown("---")
        
        # Carte interactive
        st.subheader("Carte interactive des scores de précision")
        
        # Menu déroulant pour sélectionner le modèle directement au-dessus de la carte
        options_modeles = ["Moyenne de tous les modèles"] + modeles_disponibles
        modele_carte = st.selectbox(
            "Sélectionnez le modèle à afficher sur la carte",
            options=options_modeles,
            index=0,
            key="modele_carte_select"
        )
        
        # Calculer les données de précision selon le modèle sélectionné
        if modele_carte == "Moyenne de tous les modèles":
            precision_carte_df = calculate_precision_by_region(df, "tous")
            titre_carte = "Moyenne de tous les modèles"
        else:
            precision_carte_df = calculate_precision_by_region(df, modele_carte)
            titre_carte = f"Modèle : {modele_carte}"
        
        # Affichage Carte + Outre-mer côte à côte
        col_main_map, col_om = st.columns([4, 1])
        
        with col_main_map:
            map_fig = create_interactive_map(
                precision_carte_df.copy(),
                title=titre_carte
            )
            st.plotly_chart(map_fig, use_container_width=True)
        
        with col_om:
            # Carte des territoires d'outre-mer (utilise les mêmes données que la carte principale)
            outremer_data = create_outremer_maps(precision_carte_df.copy(), title_prefix="")
            if outremer_data is not None and len(outremer_data) > 0:
                st.markdown("<h4 style='text-align: center; margin-bottom: 20px;'>Outre-mer</h4>", unsafe_allow_html=True)
                
                for idx, territory in enumerate(outremer_data):
                    # Déterminer la couleur du texte selon le fond
                    bg_color = territory['color']
                    text_color = '#FFFFFF' if bg_color in ['#d73027', '#1a9850', '#440154', '#3b528b'] else '#333333'
                    
                    st.markdown(f"""
                    <div style="
                        background-color: {bg_color};
                        border-radius: 10px;
                        padding: 10px;
                        text-align: center;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                        margin-bottom: 10px;
                    ">
                        <p style="color: {text_color}; margin: 0; font-size: 0.9em; font-weight: bold;">{territory['region']}</p>
                        <p style="color: {text_color}; font-size: 1.4em; font-weight: bold; margin: 2px 0;">{territory['score']:.1f}%</p>
                        <p style="color: {text_color}; font-size: 0.7em; margin: 0; opacity: 0.8;">{int(territory['evals']):,} évaluations</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Graphique en barres
        st.subheader("Classement des régions")
        
        bar_fig = create_bar_chart_regions(
            precision_carte_df.copy(),
            title=titre_carte
        )
        st.plotly_chart(bar_fig, use_container_width=True)
        
        st.markdown("---")
        
        # Option de téléchargement des données complètes
        csv = precision_df.to_csv(index=False)
        st.download_button(
            label="Télécharger les données par région (CSV)",
            data=csv,
            file_name=f"precision_par_region_{'tous' if modele_carte == 'Moyenne de tous les modèles' else modele_carte}.csv",
            mime="text/csv"
        )

    # ===========================================
    # ONGLET 2 : Analyse des lacunes des IA
    # ===========================================
    with tabs[3]:
        st.header("Lacunes IA")
        st.markdown("Identifiez les questions où les modèles IA ont les scores les plus faibles.")
        
        # Deux colonnes pour les filtres
        col_region, col_modele = st.columns(2)
        
        with col_region:
            # Liste des régions disponibles
            regions_disponibles = ["Toutes les régions"] + sorted(df['region'].unique().tolist())
            region_selectionnee = st.selectbox(
                "Sélectionnez une région",
                options=regions_disponibles,
                index=0,
                key="lacunes_region_select"
            )
        
        with col_modele:
            # Liste des modèles disponibles
            modeles_disponibles = ["Tous les modèles"] + sorted(df['modele_nom'].unique().tolist())
            modele_selectionne = st.selectbox(
                "Sélectionnez un modèle IA",
                options=modeles_disponibles,
                index=0,
                key="lacunes_modele_select"
            )
        
        st.markdown("---")
        
        # Filtrer les données selon les sélections
        df_filtre = df.copy()
        
        if region_selectionnee != "Toutes les régions":
            df_filtre = df_filtre[df_filtre['region'] == region_selectionnee]
        
        if modele_selectionne != "Tous les modèles":
            df_filtre = df_filtre[df_filtre['modele_nom'] == modele_selectionne]
        
        # Trier par score croissant (les pires scores en premier)
        df_lacunes = df_filtre.sort_values('score_precision', ascending=True).reset_index(drop=True)
        
        # Préparer le tableau à afficher
        df_affichage = df_lacunes[['region', 'site_nom', 'question', 'modele_nom', 'score_precision', 'reponse_attendue', 'reponse_ia']].copy()
        df_affichage.columns = ['Région', 'Site', 'Question', 'Modèle', 'Score', 'Réponse attendue', 'Réponse IA']
        df_affichage['Score'] = df_affichage['Score'].apply(lambda x: f"{x*100:.1f}%")
        
        # Pas de rang ajouté
        
        # Classification des types d'erreurs
        st.subheader("Répartition des types de réponses")
        
        # Appliquer la classification à toutes les lignes filtrées
        df_lacunes['type_erreur'] = df_lacunes.apply(classifier_type_erreur, axis=1)
        
        # Compter les types d'erreurs
        types_erreurs = df_lacunes['type_erreur'].value_counts()
        
        # Créer deux colonnes : camembert à gauche, tableau à droite
        col_pie, col_table = st.columns([1, 1])
        
        with col_pie:
            # Palette de couleurs sobre et accessible
            colors_erreurs = {
                "Réponse correcte": "#2E7D32",      # Vert foncé
                "Erreur géographique": "#1565C0",  # Bleu
                "Hallucination": "#C62828",         # Rouge foncé
                "Refus de répondre": "#FF8F00",     # Orange Ambré (plus vif)
                "Erreur de connaissance": "#757575", # Gris Moyen (pour bien contraster avec l'orange)
                "Réponse vague/incomplète": "#7B1FA2",  # Violet
                "Question ambiguë": "#455A64"       # Gris-bleu foncé
            }
            
            # Logique d'affichage conditionnelle selon le filtre "Modèle"
            if modele_selectionne == "Tous les modèles":
                # MODE COMPARAISON : Histogramme empilé par modèle
                
                # Grouper par modèle et type d'erreur
                df_comparaison = df_lacunes.groupby(['modele_nom', 'type_erreur']).size().reset_index(name='Nombre')
                
                # Calculer les pourcentages par modèle pour les tooltips
                total_per_model = df_comparaison.groupby('modele_nom')['Nombre'].transform('sum')
                df_comparaison['Pourcentage'] = (df_comparaison['Nombre'] / total_per_model * 100)
                
                # Créer le graphique empilé
                fig_bar = px.bar(
                    df_comparaison,
                    x="modele_nom",
                    y="Nombre",
                    color="type_erreur",
                    title=None,
                    labels={'modele_nom': 'Modèle', 'Nombre': 'Nombre de réponses', 'type_erreur': 'Type de réponse'},
                    color_discrete_map=colors_erreurs,
                    category_orders={"type_erreur": ["Réponse correcte", "Réponse vague/incomplète", "Erreur de connaissance", "Question ambiguë", "Refus de répondre", "Erreur géographique", "Hallucination"]},
                    hover_data=['Pourcentage'] # Important : Lier correctement les données pour le survol
                )
                
                fig_bar.update_layout(
                    height=450,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor='white',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    xaxis={'categoryorder':'total descending'}
                )
                
                # Personnaliser le tooltip (customdata[0] correspond maintenant automatiquement à la première colonne de hover_data)
                fig_bar.update_traces(
                    hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>Nombre: %{y}<br>Part: %{customdata[0]:.1f}%<extra></extra>"
                )
                
            else:
                # MODE FOCUS : Graphique en barres horizontales par type d'erreur (Code existant amélioré)
                
                # Créer le graphique en barres horizontales
                df_bar = pd.DataFrame({
                    'Type': types_erreurs.index,
                    'Nombre': types_erreurs.values,
                    'Pourcentage': (types_erreurs.values / len(df_lacunes) * 100)
                })
                
                # Trier par nombre croissant (pour affichage décroissant du haut vers le bas)
                df_bar = df_bar.sort_values('Nombre', ascending=True)
                
                fig_bar = go.Figure(go.Bar(
                    x=df_bar['Nombre'],
                    y=df_bar['Type'],
                    orientation='h',
                    marker=dict(
                        color=[colors_erreurs.get(t, "#808080") for t in df_bar['Type']]
                    ),
                    text=[f"{n} ({p:.1f}%)" for n, p in zip(df_bar['Nombre'], df_bar['Pourcentage'])],
                    textposition='outside', # Outside pour meilleure lisibilité
                    hovertemplate="<b>%{y}</b><br>Nombre: %{x}<br>Part: %{customdata:.1f}%<extra></extra>",
                    customdata=df_bar['Pourcentage']
                ))
                
                fig_bar.update_layout(
                    title=f"Profil de réponses : {modele_selectionne}",
                    showlegend=False,
                    height=400,
                    margin=dict(l=0, r=20, t=40, b=0),
                    paper_bgcolor='white',
                    xaxis=dict(title="Nombre de réponses", gridcolor='#f0f0f0'),
                    yaxis=dict(title="")
                )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_table:
            # Tableau récapitulatif des types d'erreurs
            df_types = pd.DataFrame({
                'Type de réponse': types_erreurs.index.tolist(),
                'Nombre': types_erreurs.values.tolist(),
                'Pourcentage': [f"{v/len(df_lacunes)*100:.1f}%" for v in types_erreurs.values]
            })
            st.dataframe(df_types, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Afficher le tableau des lacunes
        st.subheader("Question/Réponses")
        
        # Filtre par type de lacune
        types_disponibles = ["Tous les types"] + sorted(df_lacunes['type_erreur'].unique().tolist())
        type_selectionne = st.selectbox(
            "Filtrer par type de lacune",
            options=types_disponibles,
            index=0,
            key="lacunes_type_select"
        )
        
        # Filtrer le DataFrame final
        df_final = df_lacunes.copy()
        if type_selectionne != "Tous les types":
            df_final = df_final[df_final['type_erreur'] == type_selectionne]
        
        # Préparer le tableau à afficher
        df_affichage_final = df_final[['region', 'site_nom', 'question', 'modele_nom', 'score_precision', 'reponse_attendue', 'reponse_ia', 'type_erreur']].copy()
        df_affichage_final.columns = ['Région', 'Site', 'Question', 'Modèle', 'Score', 'Réponse attendue', 'Réponse IA', 'Type de lacune']
        df_affichage_final['Score'] = df_affichage_final['Score'].apply(lambda x: f"{x*100:.1f}%")
        
        # Limiter l'affichage pour les performances
        nb_questions = len(df_affichage_final)
        if nb_questions > 0:
            nb_lignes = st.slider("Nombre de questions à afficher", min_value=1, max_value=min(500, nb_questions), value=min(50, nb_questions), step=1)
            
            # Afficher le tableau avec toutes les colonnes
            df_affichage_limite = df_affichage_final.head(nb_lignes)
            st.dataframe(df_affichage_limite, use_container_width=True, hide_index=True)
            
            # Option de téléchargement
            csv_lacunes = df_affichage_final.to_csv(index=False)
            st.download_button(
                label="Télécharger les données filtrées (CSV)",
                data=csv_lacunes,
                file_name=f"lacunes_ia_{type_selectionne.replace(' ', '_')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucune question ne correspond à ce type de lacune pour la sélection actuelle.")
        
        st.markdown("---")
        
        pass

    # ===========================================
    # ONGLET 3 : Analyse Performance & Écologie
    # ===========================================
    with tabs[2]:
        st.header("Analyse Performance & Écologie")
        st.markdown("Analyse des performances techniques (temps de réponse) et de l'impact écologique (CO2) des modèles lors du benchmark.")
        
        # Utilisation des données préparées (perf_metrics)
        # Tri par efficacité pour cet onglet spécifique
        perf_metrics_sort = perf_metrics.sort_values('Temps moyen (s)', ascending=True)
        
        # 1. KPIs Globaux du Benchmark
        col1, col2, col3 = st.columns(3)
        
        fastest_model = perf_metrics_sort.iloc[0]['Modèle']
        
        with col1:
            st.metric("Temps de réponse moyen", f"{metrics_avg_time:.2f} s")
        with col2:
            st.metric("CO2 moyen / requête", f"{metrics_avg_co2:.4f} g")
        with col3:
            st.metric("Modèle le plus rapide", fastest_model)
            
        st.markdown("---")
        
        # 2. Graphiques
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            # Graphique Temps de réponse
            fig_time = px.bar(
                perf_metrics_sort,
                x='Temps moyen (s)',
                y='Modèle',
                orientation='h',
                title="Temps de réponse moyen (plus court est mieux)",
                labels={'Temps moyen (s)': 'Temps (secondes)', 'Modèle': 'Modèle'},
                color='Temps moyen (s)',
                color_continuous_scale='RdYlGn_r'  # Rouge pour lent, Vert pour rapide (reverse)
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
        with col_g2:
            # Graphique CO2
            fig_co2 = px.bar(
                perf_metrics.sort_values('CO2 moyen (g)', ascending=True),
                x='CO2 moyen (g)',
                y='Modèle',
                orientation='h',
                title="Emissions CO2 estimées par requête",
                labels={'CO2 moyen (g)': 'Grammes de CO2', 'Modèle': 'Modèle'},
                color='CO2 moyen (g)',
                color_continuous_scale='RdYlGn_r'  # Rouge pour polluant, Vert pour éco
            )
            st.plotly_chart(fig_co2, use_container_width=True)
            
        st.markdown("---")
        
        # 3. Analyse Croisée : Performance vs Précision
        st.subheader("Compromis Performance / Précision")
        
        fig_scatter = px.scatter(
            perf_metrics_sort,
            x='Temps moyen (s)',
            y='Précision',
            size='Évaluations',
            color='Modèle',
            text='Modèle',
            title="Positionnement des modèles : Rapidité vs Précision",
            labels={'Temps moyen (s)': 'Temps de réponse moyen (s)', 'Précision': 'Score de précision moyenne'},
            hover_data=['CO2 moyen (g)']
        )
        
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(
            xaxis=dict(autorange="reversed"), # Axe des temps inversé (plus rapide à droite)
            height=500,
            paper_bgcolor='white'
        )
        
        # Note explicative pour l'axe inversé
        st.caption("Note : L'axe horizontal est inversé (les modèles les plus rapides sont à droite). Le quadrant haut-droit représente le meilleur compromis (rapide et précis).")
        
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Tableau récapitulatif
        st.subheader("Données détaillées")
        
        # Tri par précision décroissante pour l'affichage
        display_df = perf_metrics.sort_values('Précision', ascending=False).copy()
        display_df['Précision'] = display_df['Précision'].apply(lambda x: f"{x*100:.1f}%")
        display_df['Temps moyen (s)'] = display_df['Temps moyen (s)'].apply(lambda x: f"{x:.3f} s")
        display_df['CO2 moyen (g)'] = display_df['CO2 moyen (g)'].apply(lambda x: f"{x:.5f} g")
        
        # Réordonner les colonnes pour l'affichage (Données techniques en premier)
        cols_ordre = ['Modèle', 'Paramètres (Milliards)', 'Taille (Fichier)', 'Précision', 'Temps moyen (s)', 'CO2 moyen (g)', 'Évaluations']
        display_df = display_df[cols_ordre]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 4. Méthodologie et Calculs
        with st.expander("ℹ️ Méthodologie : Comment ces chiffres sont-ils obtenus ?", expanded=False):
            st.markdown("""
            ### Origine des données
            
            1. **Temps de réponse (Performance)** : 
               - **Donnée réelle** mesurée pendant l'exécution du test.
            
            2. **Empreinte Carbone (gCO2)** :
               - **Estimation extrapolée** :
               - **Base de référence** : Profil énergétique moyen extrait du dataset "conversations" du site comparIA.
               - **Calcul** : Profil de consommation appliqué au temps de réponse calculé pour estimer l'énergie consommée, puis converti en CO2 (Mix électrique français **52g CO2/kWh**, source RTE).
               - **Formule** : `(Temps réel × Puissance de référence) × Mix Carbone France`.
            
            3. **Compromis Précision/Performance** :
               - Le graphique croise la qualité des réponses (Score de précision) avec la rapidité d'exécution.
               - L'objectif est d'identifier les modèles les plus directs (rapides et économes) qui ne sacrifient pas la pertinence géographique.
            """)

    # ===========================================
    # ONGLET 4 : Biais de Centralisation
    # ===========================================
    with tabs[1]:
        st.header("Paris vs Régions")
        st.markdown("""
        Tendance à privilégier Paris comme première réponse lorsqu'on leur pose des questions génériques sur la France.
        """)
        
        # Charger les données du test France
        df_france = load_france_test_data()
        
        if df_france.empty:
            st.error("Impossible de charger le fichier TEST_FRANCE_WISHMELUCK.csv")
        else:
            # Analyser le biais de centralisation
            bias_df = analyze_centralization_bias(df_france)
            
            if bias_df.empty:
                st.warning("Aucune donnée d'analyse disponible")
            else:
                # Métriques globales
                m1, m2, m3 = st.columns(3)
                with m1:
                    avg_paris_first = bias_df['Paris en 1er (%)'].mean()
                    st.metric(
                        label="Moyenne Paris en 1er",
                        value=f"{avg_paris_first:.1f}%"
                    )
                
                with m2:
                    avg_paris_only = bias_df['Paris uniquement (%)'].mean()
                    st.metric(
                        label="Moyenne Paris uniquement",
                        value=f"{avg_paris_only:.1f}%"
                    )
                
                with m3:
                    total_responses = int(bias_df['Total réponses'].sum())
                    st.metric(
                        label="Total réponses analysées",
                        value=f"{total_responses:,}"
                    )
                
                st.markdown("---")
                
                # Tableau récapitulatif (déplacé avant les graphiques)
                st.subheader("Données détaillées du biais de centralisation")
                
                # Trier par Paris en 1er (%) en ordre décroissant et formater les données
                display_bias = bias_df.sort_values('Paris en 1er (%)', ascending=False).copy()
                display_bias['Paris en 1er (%)'] = display_bias['Paris en 1er (%)'].apply(lambda x: f"{x:.1f}%")
                display_bias['Paris uniquement (%)'] = display_bias['Paris uniquement (%)'].apply(lambda x: f"{x:.1f}%")
                # Supprimer les colonnes non nécessaires
                display_bias = display_bias.drop(columns=['Total réponses', 'Mentions Paris (moy)', 'Autres villes (moy)'])
                
                st.dataframe(display_bias, use_container_width=True, hide_index=True)
                
                
                st.markdown("---")
                
                # Graphiques côte à côte
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    # Graphique 1 : Paris cité en premier
                    st.subheader("Paris cité en premier")
                    st.markdown("*Tendance à mentionner Paris avant toute autre ville*")
                    
                    # Trier par pourcentage décroissant
                    bias_sorted_first = bias_df.sort_values('Paris en 1er (%)', ascending=True)
                    
                    fig_paris_first = go.Figure(go.Bar(
                        x=bias_sorted_first['Paris en 1er (%)'],
                        y=bias_sorted_first['Modèle'],
                        orientation='h',
                        marker=dict(
                            color=bias_sorted_first['Paris en 1er (%)'],
                            colorscale=[
                                [0, '#21918c'],    # Turquoise (peu de biais)
                                [0.5, '#fde725'],  # Jaune
                                [1, '#dc267f']     # Magenta (beaucoup de biais)
                            ],
                            line=dict(color='#333333', width=0.5)
                        ),
                        text=bias_sorted_first['Paris en 1er (%)'].apply(lambda x: f'{x:.1f}%'),
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>Paris en 1er: %{x:.1f}%<extra></extra>'
                    ))
                    
                    fig_paris_first.update_layout(
                        xaxis=dict(
                            title="Pourcentage (%)",
                            range=[0, max(100, bias_sorted_first['Paris en 1er (%)'].max() + 10)],
                            tickformat=".0f",
                            gridcolor='#e0e0e0'
                        ),
                        yaxis=dict(title="", tickfont=dict(size=10)),
                        height=400,
                        margin=dict(l=100, r=40, t=20, b=50),
                        paper_bgcolor='white',
                        plot_bgcolor='#fafafa',
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_paris_first, use_container_width=True)
                
                with col_chart2:
                    # Graphique 2 : Paris cité uniquement
                    st.subheader("Paris seul lieu cité")
                    st.markdown("*Tendance à ne mentionner que Paris*")
                    
                    bias_sorted_only = bias_df.sort_values('Paris uniquement (%)', ascending=True)
                    
                    fig_paris_only = go.Figure(go.Bar(
                        x=bias_sorted_only['Paris uniquement (%)'],
                        y=bias_sorted_only['Modèle'],
                        orientation='h',
                        marker=dict(
                            color=bias_sorted_only['Paris uniquement (%)'],
                            colorscale=[
                                [0, '#21918c'],    # Turquoise (peu de biais)
                                [0.5, '#fde725'],  # Jaune
                                [1, '#dc267f']     # Magenta (beaucoup de biais)
                            ],
                            line=dict(color='#333333', width=0.5)
                        ),
                        text=bias_sorted_only['Paris uniquement (%)'].apply(lambda x: f'{x:.1f}%'),
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>Paris uniquement: %{x:.1f}%<extra></extra>'
                    ))
                    
                    fig_paris_only.update_layout(
                        xaxis=dict(
                            title="Pourcentage (%)",
                            range=[0, max(50, bias_sorted_only['Paris uniquement (%)'].max() + 10)],
                            tickformat=".0f",
                            gridcolor='#e0e0e0'
                        ),
                        yaxis=dict(title="", tickfont=dict(size=10)),
                        height=400,
                        margin=dict(l=100, r=40, t=20, b=50),
                        paper_bgcolor='white',
                        plot_bgcolor='#fafafa',
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_paris_only, use_container_width=True)
                
                st.markdown("---")
                
                # Sections interactives côte à côte
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    # Section interactive : Explorer les réponses où Paris n'est pas cité en premier
                    st.markdown("#### Autre lieu cité avant Paris")
                    
                    # Liste des modèles disponibles pour cette section
                    model_cols_map_first = {
                        'smollm2:1.7b': 'reponse_smollm2:1.7b',
                        'llama3.2:1b': 'reponse_llama3.2:1b',
                        'qwen2.5:1.5b': 'reponse_qwen2.5:1.5b',
                        'mistral': 'reponse_mistral',
                        'llama3': 'reponse_llama3',
                        'phi3': 'reponse_phi3'
                    }
                    
                    selected_model_first = st.selectbox(
                        "Choisissez un modèle :",
                        options=list(model_cols_map_first.keys()),
                        key="model_not_paris_first"
                    )
                    
                    # Fonction pour trouver le premier lieu mentionné
                    import re
                    lieux_detect = [
                        'paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes', 'strasbourg',
                        'montpellier', 'bordeaux', 'lille', 'rennes', 'reims', 'toulon', 
                        'normandie', 'bretagne', 'provence', 'alsace', 'bourgogne', 'auvergne',
                        'corse', 'aquitaine', 'lorraine', 'champagne', 'languedoc',
                        'côte d\'azur', 'riviera', 'alpes', 'pyrénées', 'jura', 'vosges',
                        'versailles', 'chambord', 'chenonceau', 'fontainebleau', 'amboise',
                        'louvre', 'tour eiffel', 'eiffel', 'notre-dame', 'sacré-coeur',
                        'mont-saint-michel', 'mont saint-michel', 'mont blanc',
                        'loire', 'rhône', 'val de loire', 'camargue', 'luberon'
                    ]
                    
                    def get_first_location(text):
                        """Retourne le premier lieu mentionné dans le texte"""
                        text_lower = str(text).lower()
                        first_pos = float('inf')
                        first_lieu = None
                        
                        for lieu in lieux_detect:
                            pattern = r'\b' + re.escape(lieu) + r'\b'
                            match = re.search(pattern, text_lower)
                            if match and match.start() < first_pos:
                                first_pos = match.start()
                                first_lieu = lieu
                        
                        return first_lieu
                    
                    lieux_parisiens_explorer = [
                        'paris', 'louvre', 'tour eiffel', 'eiffel', 'notre-dame', 'sacré-coeur', 
                        'versailles', 'fontainebleau', 'disneyland', 'arc de triomphe', 'champs-élysées',
                        'palais-royal', 'saint-denis'
                    ]
                    
                    def is_not_paris_first(text):
                        """Vérifie si le premier lieu mentionné n'est PAS parisien"""
                        first_loc = get_first_location(text)
                        return first_loc is not None and first_loc not in lieux_parisiens_explorer
                    
                    # Récupérer les réponses où Paris n'est pas cité en premier
                    col_name_first = model_cols_map_first[selected_model_first]
                    if col_name_first in df_france.columns:
                        # Filtrer et ajouter le premier lieu détecté
                        mask = df_france[col_name_first].apply(is_not_paris_first)
                        not_paris_first_df = df_france[mask][['question', col_name_first]].copy()
                        not_paris_first_df['Premier lieu'] = not_paris_first_df[col_name_first].apply(get_first_location)
                        not_paris_first_df.columns = ['Question', 'Réponse', 'Premier lieu cité']
                        
                        n_not_paris = len(not_paris_first_df)
                        total_resp = len(df_france)
                        
                        st.info(f"**{n_not_paris}** réponse(s) sur {total_resp} ({n_not_paris/total_resp*100:.1f}%)")
                        
                        if n_not_paris > 0:
                            with st.expander(f"Voir les {n_not_paris} réponse(s)", expanded=False):
                                for idx, row in not_paris_first_df.iterrows():
                                    st.markdown(f"---")
                                    st.markdown(f"**1er lieu : {row['Premier lieu cité'].capitalize()}**")
                                    st.markdown(f"**Q :** {row['Question']}")
                                    st.markdown("**R :**")
                                    st.write(row['Réponse'])
                        else:
                            st.warning(f"Paris toujours cité en premier.")
                
                with col_exp2:
                    # Section interactive : Explorer les réponses où Paris est le seul lieu cité
                    st.markdown("#### Paris seul lieu cité")
                    
                    # Liste des modèles disponibles
                    model_columns_map = {
                        'smollm2:1.7b': 'reponse_smollm2:1.7b',
                        'llama3.2:1b': 'reponse_llama3.2:1b',
                        'qwen2.5:1.5b': 'reponse_qwen2.5:1.5b',
                        'mistral': 'reponse_mistral',
                        'llama3': 'reponse_llama3',
                        'phi3': 'reponse_phi3'
                    }
                    
                    # Sélecteur de modèle
                    selected_model = st.selectbox(
                        "Choisissez un modèle :",
                        options=list(model_columns_map.keys()),
                        key="model_paris_only"
                    )
                    
                    # Fonction pour vérifier si Paris est le seul lieu
                    import re
                    
                    # Liste étendue incluant villes, régions, départements et lieux emblématiques
                    lieux_france = [
                        # Grandes villes
                        'paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes', 'strasbourg',
                        'montpellier', 'bordeaux', 'lille', 'rennes', 'reims', 'toulon', 
                        'saint-étienne', 'le havre', 'grenoble', 'dijon', 'angers', 'nîmes',
                        'villeurbanne', 'clermont-ferrand', 'aix-en-provence', 'brest', 'tours',
                        'amiens', 'limoges', 'perpignan', 'metz', 'besançon', 'orléans', 'rouen',
                        'caen', 'nancy', 'avignon', 'cannes', 'saint-tropez', 'monaco',
                        # Régions
                        'normandie', 'bretagne', 'provence', 'alsace', 'bourgogne', 'auvergne',
                        'corse', 'aquitaine', 'lorraine', 'picardie', 'champagne', 'languedoc',
                        'roussillon', 'savoie', 'dauphiné', 'vendée', 'charentes', 'limousin',
                        'poitou', 'touraine', 'anjou', 'beauce', 'sologne', 'gascogne', 'béarn',
                        # Zones géographiques
                        'côte d\'azur', 'riviera', 'alpes', 'pyrénées', 'jura', 'vosges', 
                        'massif central', 'camargue', 'luberon', 'verdon', 'ardèche',
                        'dordogne', 'périgord', 'lot', 'gironde', 'méditerranée',
                        # Lieux emblématiques
                        'mont-saint-michel', 'mont saint-michel', 'mont st-michel',
                        'versailles', 'chambord', 'chenonceau', 'fontainebleau', 'amboise',
                        'louvre', 'tour eiffel', 'eiffel', 'notre-dame', 'sacré-coeur',
                        'mont blanc', 'gorges du verdon', 'pont du gard', 'carcassonne',
                        'lascaux', 'rocamadour', 'saint-malo', 'dinard', 'deauville',
                        'biarritz', 'arcachon', 'la rochelle', 'île de ré', 'oléron',
                        # Vallées et terroirs célèbres
                        'loire', 'rhône', 'seine', 'garonne', 'val de loire', 'beaujolais',
                        'médoc', 'saint-émilion', 'cognac', 'armagnac', 'champagne'
                    ]
                    
                    lieux_parisiens_explorer = [
                        'paris', 'louvre', 'tour eiffel', 'eiffel', 'notre-dame', 'sacré-coeur', 
                        'versailles', 'fontainebleau', 'disneyland', 'arc de triomphe', 'champs-élysées',
                        'palais-royal', 'saint-denis'
                    ]
                    
                    def check_paris_only(text):
                        """Vérifie si seuls des lieux parisiens sont mentionnés"""
                        text_lower = str(text).lower()
                        lieux_trouves = []
                        for lieu in lieux_france:
                            pattern = r'\b' + re.escape(lieu) + r'\b'
                            if re.search(pattern, text_lower):
                                lieux_trouves.append(lieu)
                        
                        if not lieux_trouves:
                            return False
                        
                        # Tous les lieux mentionnés sont-ils parisiens ?
                        return all(l in lieux_parisiens_explorer for l in lieux_trouves)
                    
                    # Récupérer les réponses où Paris est le seul lieu
                    col_name = model_columns_map[selected_model]
                    if col_name in df_france.columns:
                        paris_only_responses = df_france[df_france[col_name].apply(check_paris_only)][['question', col_name]].copy()
                        paris_only_responses.columns = ['Question', 'Réponse']
                        
                        # Afficher le nombre de réponses trouvées
                        n_paris_only = len(paris_only_responses)
                        total_responses = len(df_france)
                        
                        st.info(f"**{n_paris_only}** réponse(s) sur {total_responses} ({n_paris_only/total_responses*100:.1f}%)")
                        
                        if n_paris_only > 0:
                            # Afficher les réponses dans un expander global
                            with st.expander(f"Voir les {n_paris_only} réponse(s)", expanded=False):
                                for idx, row in paris_only_responses.iterrows():
                                    st.markdown(f"---")
                                    st.markdown(f"**Q :** {row['Question']}")
                                    st.markdown("**R :**")
                                    st.write(row['Réponse'])
                        else:
                            st.success(f"Mentionne toujours d'autres villes.")
                
                st.markdown("---")
                
                # Section 3 : OUPS IA - Réponses sans lieu français détecté
                st.subheader("OUPS IA - Réponses sans lieu français détecté")
                st.markdown("*Réponses où aucun lieu français n'a été identifié (erreurs, fautes d'orthographe, lieux hors France...)*")
                
                # Sélecteur de modèle pour OUPS IA
                model_cols_oups = {
                    'smollm2:1.7b': 'reponse_smollm2:1.7b',
                    'llama3.2:1b': 'reponse_llama3.2:1b',
                    'qwen2.5:1.5b': 'reponse_qwen2.5:1.5b',
                    'mistral': 'reponse_mistral',
                    'llama3': 'reponse_llama3',
                    'phi3': 'reponse_phi3'
                }
                
                selected_model_oups = st.selectbox(
                    "Choisissez un modèle :",
                    options=list(model_cols_oups.keys()),
                    key="model_oups_ia"
                )
                
                # Fonction pour détecter si aucun lieu n'est trouvé
                import re
                lieux_oups = [
                    'paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes', 'strasbourg',
                    'montpellier', 'bordeaux', 'lille', 'rennes', 'reims', 'toulon', 
                    'normandie', 'bretagne', 'provence', 'alsace', 'bourgogne', 'auvergne',
                    'corse', 'aquitaine', 'lorraine', 'champagne', 'languedoc',
                    'côte d\'azur', 'riviera', 'alpes', 'pyrénées', 'jura', 'vosges',
                    'versailles', 'chambord', 'chenonceau', 'fontainebleau', 'amboise',
                    'louvre', 'tour eiffel', 'eiffel', 'notre-dame', 'sacré-coeur',
                    'mont-saint-michel', 'mont saint-michel', 'mont blanc',
                    'loire', 'rhône', 'val de loire', 'camargue', 'luberon'
                ]
                
                def has_no_french_location(text):
                    """Vérifie si aucun lieu français n'est détecté"""
                    text_lower = str(text).lower()
                    for lieu in lieux_oups:
                        pattern = r'\b' + re.escape(lieu) + r'\b'
                        if re.search(pattern, text_lower):
                            return False
                    return True
                
                col_name_oups = model_cols_oups[selected_model_oups]
                if col_name_oups in df_france.columns:
                    oups_responses = df_france[df_france[col_name_oups].apply(has_no_french_location)][['question', col_name_oups]].copy()
                    oups_responses.columns = ['Question', 'Réponse']
                    
                    n_oups = len(oups_responses)
                    total_resp_oups = len(df_france)
                    
                    if n_oups > 0:
                        st.warning(f"**{selected_model_oups}** : {n_oups} réponse(s) sur {total_resp_oups} ne mentionnent aucun lieu français ({n_oups/total_resp_oups*100:.1f}%)")
                        
                        with st.expander(f"Voir les {n_oups} OUPS", expanded=False):
                            for idx, row in oups_responses.iterrows():
                                st.markdown(f"---")
                                st.markdown(f"**Question :** {row['Question']}")
                                st.markdown("**Réponse :**")
                                st.write(row['Réponse'])
                    else:
                        st.success(f"Ce modèle mentionne toujours au moins un lieu français.")
                
                st.markdown("---")
                
                # Section 4 : Analyse des citations par région
                st.subheader("Quelles régions sont citées ?")
                
                # Définir les régions françaises avec leurs mots-clés
                regions_map = {
                    'Île-de-France': ['ile-de-france', 'ile de france', 'paris', 'versailles'],
                    'Provence-Alpes-Côte d\'Azur': ['provence', 'paca', 'marseille', 'nice', 'cannes', 'cote d azur', 'côte d azur'],
                    'Auvergne-Rhône-Alpes': ['auvergne', 'rhone-alpes', 'rhône-alpes', 'lyon', 'grenoble', 'annecy'],
                    'Nouvelle-Aquitaine': ['nouvelle-aquitaine', 'aquitaine', 'bordeaux', 'biarritz', 'la rochelle'],
                    'Occitanie': ['occitanie', 'languedoc', 'toulouse', 'montpellier', 'carcassonne'],
                    'Hauts-de-France': ['hauts-de-france', 'nord', 'lille', 'amiens'],
                    'Normandie': ['normandie', 'rouen', 'caen', 'mont-saint-michel', 'mont saint-michel'],
                    'Grand Est': ['grand est', 'alsace', 'lorraine', 'strasbourg', 'reims'],
                    'Pays de la Loire': ['pays de la loire', 'nantes', 'angers'],
                    'Bretagne': ['bretagne', 'rennes', 'brest', 'saint-malo'],
                    'Bourgogne-Franche-Comté': ['bourgogne', 'franche-comte', 'franche-comté', 'dijon', 'besancon', 'besançon'],
                    'Centre-Val de Loire': ['centre-val de loire', 'centre', 'orleans', 'orléans', 'tours', 'val de loire'],
                    'Corse': ['corse', 'ajaccio', 'bastia'],
                    'Guadeloupe': ['guadeloupe', 'pointe-a-pitre', 'basse-terre'],
                    'Martinique': ['martinique', 'fort-de-france'],
                    'Guyane': ['guyane', 'cayenne', 'kourou'],
                    'La Réunion': ['reunion', 'réunion', 'saint-denis'],
                    'Mayotte': ['mayotte', 'mamoudzou']
                }
                
                # Compter les citations par région
                region_counts = {region: 0 for region in regions_map.keys()}
                
                ia_columns = ['reponse_smollm2:1.7b', 'reponse_llama3.2:1b', 'reponse_qwen2.5:1.5b', 
                             'reponse_mistral', 'reponse_llama3', 'reponse_phi3']
                
                for col in ia_columns:
                    if col in df_france.columns:
                        for response in df_france[col].dropna():
                            response_lower = str(response).lower()
                            for region, keywords in regions_map.items():
                                if any(keyword in response_lower for keyword in keywords):
                                    region_counts[region] += 1
                
                # Créer un DataFrame pour l'affichage
                total_responses = len(df_france) * len(ia_columns)
                region_df = pd.DataFrame([
                    {
                        'Région': region,
                        'Citations': count,
                        'Pourcentage': (count / total_responses) * 100
                    }
                    for region, count in region_counts.items()
                ]).sort_values('Citations', ascending=False)
                
                # Graphique en barres
                fig_regions = px.bar(
                    region_df,
                    x='Pourcentage',
                    y='Région',
                    orientation='h',
                    title=None,
                    labels={'Pourcentage': 'Pourcentage de citations (%)', 'Région': 'Région'},
                    color='Pourcentage',
                    color_continuous_scale='RdYlGn',
                    text='Pourcentage'
                )
                
                fig_regions.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_regions.update_layout(height=500, showlegend=False)
                
                # Affichage graphique et liste des régions non citées côte à côte
                col_chart, col_list = st.columns([3, 1])
                
                with col_chart:
                    st.plotly_chart(fig_regions, use_container_width=True)
                
                with col_list:
                    regions_non_citees = region_df[region_df['Citations'] == 0]['Région'].tolist()
                    if regions_non_citees:
                        st.markdown(f"""
                        <div style="background-color: #fff3f3; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-top: 25px;">
                            <h4 style="color: #ff4b4b; margin-top: 0;">🚫 Régions non citées</h4>
                            <p style="font-size: 0.9em; color: #666;">Ces régions ne sont apparues dans aucune réponse des IA :</p>
                            <ul style="margin-bottom: 0; padding-left: 20px;">
                                {"".join([f'<li style="color: #333; margin-bottom: 5px;"><b>{r}</b></li>' for r in regions_non_citees])}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background-color: #f0fff4; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745; margin-top: 25px;">
                            <h4 style="color: #28a745; margin-top: 0;">✅ Couverture totale</h4>
                            <p style="font-size: 0.9em; color: #666;">Toutes les régions ont été citées au moins une fois par les modèles IA.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Tableau détaillé
                with st.expander("📊 Voir les données détaillées par région"):
                    display_region_df = region_df.copy()
                    display_region_df['Pourcentage'] = display_region_df['Pourcentage'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_region_df, use_container_width=True, hide_index=True)
                
                
                # Option de téléchargement
                csv_bias = bias_df.to_csv(index=False)
                st.download_button(
                    label="Télécharger les données du biais de centralisation (CSV)",
                    data=csv_bias,
                    file_name="biais_centralisation_ia.csv",
                    mime="text/csv"
                )

    # ===========================================
    # ONGLET 5 : Synthèse & Impact Global
    # ===========================================
    with tabs[4]:
        st.header("Synthèse Finale & Impact Global")
        st.markdown("Récapitulatif de l'impact écologique total du projet pour votre présentation.")
        
        # 1. Bilan écologique extrapolés à tout le projet (24,540 requêtes)
        col_stats1, col_stats2 = st.columns([1, 1.5])
        
        with col_stats1:
            st.markdown("""
            <div style="background-color:#ffffff; padding:30px; border-radius:15px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;">
                <h3 style="color:#2e7d32; margin-bottom:10px;">Impact Carbone du Projet</h3>
                <p style="font-size:1.1em; color:#666;">Pour les <b>24 540</b> requêtes (Benchmark + Test Paris) :</p>
                <p style="font-size:3.5em; font-weight:900; color:#2e7d32; margin:15px 0;">18,6 g <span style="font-size:0.4em; color:#999;">CO2e</span></p>
                <hr style="border:0.5px solid #eee;">
                <p style="font-style:italic; color:#888; font-size:0.9em;">Basé sur le mix électrique français (52g/kWh)</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_stats2:
            st.subheader("Équivalence d'usage courant")
            
            c1, c2, c3 = st.columns(3)
            with c1:

                st.metric("Voiture (km)", "0.15 km")
                st.caption("Environ 150 mètres")
            with c2:

                st.metric("Smartphone", "37 charges")
                st.caption("Recharges complètes")
            with c3:

                st.metric("Éclairage", "31 h")
                st.caption("Ampoule LED 10W")

        st.markdown("---")
        
        # 2. Synthèse des résultats par IA
        st.subheader("Palmarès du Benchmark Culturel")
        
        # Calculer les meilleurs modèles
        best_precision = perf_metrics.sort_values('Précision', ascending=False).iloc[0]
        best_eco = perf_metrics.sort_values('CO2 moyen (g)', ascending=True).iloc[0]
        best_speed = perf_metrics.sort_values('Temps moyen (s)', ascending=True).iloc[0]
        
        p1, p2, p3 = st.columns(3)
        with p1:
            st.success(f"**La plus cultivée**\n\n**{best_precision['Modèle']}**\n\nScore : {best_precision['Précision']:.1%}")
        with p2:
            st.info(f"**La plus économe**\n\n**{best_eco['Modèle']}**\n\n{best_eco['CO2 moyen (g)']:.4f} g/req")
        with p3:
            st.warning(f"**La plus rapide**\n\n**{best_speed['Modèle']}**\n\n{best_speed['Temps moyen (s)']:.2f} s/req")
            



if __name__ == "__main__":
    main()

