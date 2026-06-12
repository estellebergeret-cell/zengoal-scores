"""
ZenGoal — Script automatique de mise à jour des scores
Récupère les résultats CDM 2026 via football-data.org
et les envoie dans Firebase en temps réel
 
Déployer sur Railway.app (gratuit) — tourne toutes les heures
"""
 
import requests
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from datetime import datetime
 
# ══════════════════════════════════════════════
# CONFIGURATION — NE PAS MODIFIER
# ══════════════════════════════════════════════
FOOTBALL_API_KEY = "ddc9f37577c54712919ada74ce59e5ae"
FIREBASE_URL     = "https://zengoal-2026-default-rtdb.firebaseio.com"
 
# Mapping IDs football-data.org → IDs matchs ZenGoal
# (sera complété automatiquement au 1er lancement)
MATCH_MAPPING = {}
 
# ══════════════════════════════════════════════
# CONNEXION FIREBASE
# ══════════════════════════════════════════════
def init_firebase():
    """Initialise la connexion Firebase"""
    # Sur Railway, les credentials Firebase sont dans une variable d'environnement
    firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
    if firebase_creds:
        cred_dict = json.loads(firebase_creds)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
    else:
        # Mode local — utilise le fichier serviceAccountKey.json
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
    print("✅ Firebase connecté")
 
# ══════════════════════════════════════════════
# RÉCUPÉRATION DES MATCHS CDM 2026
# ══════════════════════════════════════════════
def get_matches():
    """Récupère tous les matchs CDM 2026 depuis football-data.org"""
    headers = {'X-Auth-Token': FOOTBALL_API_KEY}
    
    # Code compétition CDM 2026 sur football-data.org
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('matches', [])
        elif resp.status_code == 429:
            print("⚠️ Rate limit atteint — attendre 1 minute")
            return []
        else:
            print(f"❌ Erreur API: {resp.status_code} — {resp.text[:200]}")
            return []
    except Exception as e:
        print(f"❌ Erreur réseau: {e}")
        return []
 
# ══════════════════════════════════════════════
# MAPPING ÉQUIPES → DRAPEAUX
# ══════════════════════════════════════════════
# ══════════════════════════════════════════════
# LISTE DES MATCHS ZENGOAL (copie de l'app)
# ══════════════════════════════════════════════
ZENGOAL_MATCHES = [
    {"id":1,  "e1":"Mexique",           "e2":"Afrique du Sud"},
    {"id":2,  "e1":"Corée du Sud",       "e2":"Tchéquie"},
    {"id":3,  "e1":"Tchéquie",           "e2":"Afrique du Sud"},
    {"id":4,  "e1":"Mexique",            "e2":"Corée du Sud"},
    {"id":5,  "e1":"Tchéquie",           "e2":"Mexique"},
    {"id":6,  "e1":"Afrique du Sud",     "e2":"Corée du Sud"},
    {"id":7,  "e1":"Canada",             "e2":"Bosnie-Herzégovine"},
    {"id":8,  "e1":"Qatar",              "e2":"Suisse"},
    {"id":9,  "e1":"Suisse",             "e2":"Bosnie-Herzégovine"},
    {"id":10, "e1":"Canada",             "e2":"Qatar"},
    {"id":11, "e1":"Suisse",             "e2":"Canada"},
    {"id":12, "e1":"Bosnie-Herzégovine", "e2":"Qatar"},
    {"id":13, "e1":"Brésil",             "e2":"Maroc"},
    {"id":14, "e1":"Haïti",              "e2":"Écosse"},
    {"id":15, "e1":"Écosse",             "e2":"Maroc"},
    {"id":16, "e1":"Brésil",             "e2":"Haïti"},
    {"id":17, "e1":"Écosse",             "e2":"Brésil"},
    {"id":18, "e1":"Maroc",              "e2":"Haïti"},
    {"id":19, "e1":"États-Unis",         "e2":"Paraguay"},
    {"id":20, "e1":"Australie",          "e2":"Turquie"},
    {"id":21, "e1":"États-Unis",         "e2":"Australie"},
    {"id":22, "e1":"Turquie",            "e2":"Paraguay"},
    {"id":23, "e1":"Turquie",            "e2":"États-Unis"},
    {"id":24, "e1":"Paraguay",           "e2":"Australie"},
    {"id":25, "e1":"Allemagne",          "e2":"Curaçao"},
    {"id":26, "e1":"Côte d'Ivoire",      "e2":"Équateur"},
    {"id":27, "e1":"Allemagne",          "e2":"Côte d'Ivoire"},
    {"id":28, "e1":"Équateur",           "e2":"Curaçao"},
    {"id":29, "e1":"Équateur",           "e2":"Allemagne"},
    {"id":30, "e1":"Curaçao",            "e2":"Côte d'Ivoire"},
    {"id":31, "e1":"Pays-Bas",           "e2":"Japon"},
    {"id":32, "e1":"Suède",              "e2":"Tunisie"},
    {"id":33, "e1":"Pays-Bas",           "e2":"Suède"},
    {"id":34, "e1":"Tunisie",            "e2":"Japon"},
    {"id":35, "e1":"Tunisie",            "e2":"Pays-Bas"},
    {"id":36, "e1":"Japon",              "e2":"Suède"},
    {"id":37, "e1":"Belgique",           "e2":"Égypte"},
    {"id":38, "e1":"Iran",               "e2":"Nouvelle-Zélande"},
    {"id":39, "e1":"Belgique",           "e2":"Iran"},
    {"id":40, "e1":"Nouvelle-Zélande",   "e2":"Égypte"},
    {"id":41, "e1":"Nouvelle-Zélande",   "e2":"Belgique"},
    {"id":42, "e1":"Égypte",             "e2":"Iran"},
    {"id":43, "e1":"Espagne",            "e2":"Cap-Vert"},
    {"id":44, "e1":"Arabie Saoudite",    "e2":"Uruguay"},
    {"id":45, "e1":"Espagne",            "e2":"Arabie Saoudite"},
    {"id":46, "e1":"Uruguay",            "e2":"Cap-Vert"},
    {"id":47, "e1":"Uruguay",            "e2":"Espagne"},
    {"id":48, "e1":"Cap-Vert",           "e2":"Arabie Saoudite"},
    {"id":49, "e1":"France",             "e2":"Sénégal"},
    {"id":50, "e1":"Irak",               "e2":"Norvège"},
    {"id":51, "e1":"France",             "e2":"Irak"},
    {"id":52, "e1":"Norvège",            "e2":"Sénégal"},
    {"id":53, "e1":"Norvège",            "e2":"France"},
    {"id":54, "e1":"Sénégal",            "e2":"Irak"},
    {"id":55, "e1":"Argentine",          "e2":"Algérie"},
    {"id":56, "e1":"Autriche",           "e2":"Jordanie"},
    {"id":57, "e1":"Argentine",          "e2":"Autriche"},
    {"id":58, "e1":"Jordanie",           "e2":"Algérie"},
    {"id":59, "e1":"Jordanie",           "e2":"Argentine"},
    {"id":60, "e1":"Algérie",            "e2":"Autriche"},
    {"id":61, "e1":"Portugal",           "e2":"RD Congo"},
    {"id":62, "e1":"Ouzbékistan",        "e2":"Colombie"},
    {"id":63, "e1":"Portugal",           "e2":"Ouzbékistan"},
    {"id":64, "e1":"Colombie",           "e2":"RD Congo"},
    {"id":65, "e1":"Colombie",           "e2":"Portugal"},
    {"id":66, "e1":"RD Congo",           "e2":"Ouzbékistan"},
    {"id":67, "e1":"Angleterre",         "e2":"Croatie"},
    {"id":68, "e1":"Ghana",              "e2":"Panama"},
    {"id":69, "e1":"Angleterre",         "e2":"Ghana"},
    {"id":70, "e1":"Panama",             "e2":"Croatie"},
    {"id":71, "e1":"Panama",             "e2":"Angleterre"},
    {"id":72, "e1":"Croatie",            "e2":"Ghana"},
]
 
FLAG_MAP = {
    "Mexico": "🇲🇽", "South Africa": "🇿🇦", "Korea Republic": "🇰🇷", "Czechia": "🇨🇿",
    "Canada": "🇨🇦", "Bosnia and Herzegovina": "🇧🇦", "Qatar": "🇶🇦", "Switzerland": "🇨🇭",
    "Brazil": "🇧🇷", "Morocco": "🇲🇦", "Haiti": "🇭🇹", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "USA": "🇺🇸", "United States": "🇺🇸", "Paraguay": "🇵🇾", "Australia": "🇦🇺", "Turkey": "🇹🇷",
    "Germany": "🇩🇪", "Curaçao": "🇨🇼", "Côte d'Ivoire": "🇨🇮", "Ecuador": "🇪🇨",
    "Netherlands": "🇳🇱", "Japan": "🇯🇵", "Sweden": "🇸🇪", "Tunisia": "🇹🇳",
    "Belgium": "🇧🇪", "Egypt": "🇪🇬", "Iran": "🇮🇷", "New Zealand": "🇳🇿",
    "Spain": "🇪🇸", "Cabo Verde": "🇨🇻", "Saudi Arabia": "🇸🇦", "Uruguay": "🇺🇾",
    "France": "🇫🇷", "Senegal": "🇸🇳", "Iraq": "🇮🇶", "Norway": "🇳🇴",
    "Argentina": "🇦🇷", "Algeria": "🇩🇿", "Austria": "🇦🇹", "Jordan": "🇯🇴",
    "Portugal": "🇵🇹", "DR Congo": "🇨🇩", "Uzbekistan": "🇺🇿", "Colombia": "🇨🇴",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Croatia": "🇭🇷", "Ghana": "🇬🇭", "Panama": "🇵🇦",
}
 
NAME_MAP = {
    "Mexico": "Mexique", "South Africa": "Afrique du Sud", "Korea Republic": "Corée du Sud",
    "Czechia": "Tchéquie", "Canada": "Canada", "Bosnia and Herzegovina": "Bosnie-Herzégovine",
    "Qatar": "Qatar", "Switzerland": "Suisse", "Brazil": "Brésil", "Morocco": "Maroc",
    "Haiti": "Haïti", "Scotland": "Écosse", "United States": "États-Unis", "USA": "États-Unis",
    "Paraguay": "Paraguay", "Australia": "Australie", "Turkey": "Turquie",
    "Germany": "Allemagne", "Côte d'Ivoire": "Côte d'Ivoire", "Ecuador": "Équateur",
    "Netherlands": "Pays-Bas", "Japan": "Japon", "Sweden": "Suède", "Tunisia": "Tunisie",
    "Belgium": "Belgique", "Egypt": "Égypte", "Iran": "Iran", "New Zealand": "Nouvelle-Zélande",
    "Spain": "Espagne", "Cabo Verde": "Cap-Vert", "Saudi Arabia": "Arabie Saoudite",
    "Uruguay": "Uruguay", "France": "France", "Senegal": "Sénégal", "Iraq": "Irak",
    "Norway": "Norvège", "Argentina": "Argentine", "Algeria": "Algérie", "Austria": "Autriche",
    "Jordan": "Jordanie", "Portugal": "Portugal", "DR Congo": "RD Congo",
    "Uzbekistan": "Ouzbékistan", "Colombia": "Colombie", "England": "Angleterre",
    "Croatia": "Croatie", "Ghana": "Ghana", "Panama": "Panama",
}
 
def fr_name(en_name):
    return NAME_MAP.get(en_name, en_name)
 
def flag(en_name):
    return FLAG_MAP.get(en_name, "🏳️")
 
# ══════════════════════════════════════════════
# CALCUL DES POINTS
# ══════════════════════════════════════════════
def calc_pts(prono_s1, prono_s2, real_s1, real_s2):
    if prono_s1 == real_s1 and prono_s2 == real_s2:
        return 3
    sign = lambda v: 1 if v > 0 else (-1 if v < 0 else 0)
    if sign(prono_s1 - prono_s2) == sign(real_s1 - real_s2):
        return 1
    return 0
 
# ══════════════════════════════════════════════
# MISE À JOUR FIREBASE
# ══════════════════════════════════════════════
def update_scores():
    """
    Récupère les résultats terminés et les enregistre dans Firebase
    sous la clé resultats/{matchId} = {s1: X, s2: Y, e1: "...", e2: "..."}
    """
    print(f"\n🔄 Mise à jour des scores — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    matches = get_matches()
    if not matches:
        print("Aucun match récupéré")
        return
 
    ref = db.reference('resultats')
    existing = ref.get() or {}
    
    updated = 0
    for match in matches:
        status = match.get('status', '')
        
        # Ne traiter que les matchs terminés
        if status not in ['FINISHED', 'AWARDED']:
            continue
        
        match_id_api = match.get('id')
        home = match.get('homeTeam', {}).get('name', '')
        away = match.get('awayTeam', {}).get('name', '')
        score = match.get('score', {})
        full_time = score.get('fullTime', {})
        
        home_goals = full_time.get('home')
        away_goals = full_time.get('away')
        
        if home_goals is None or away_goals is None:
            continue
        
        # Trouver le match ZenGoal correspondant par nom d'équipe
        home_fr = fr_name(home)
        away_fr = fr_name(away)
        
        zengoal_id = None
        
        # Chercher dans le mapping sauvegardé
        mapping_ref = db.reference(f'mapping/{match_id_api}')
        saved_id = mapping_ref.get()
        
        if saved_id:
            zengoal_id = saved_id
        else:
            # Chercher par nom d'équipe dans la liste des matchs ZenGoal
            for m in ZENGOAL_MATCHES:
                if (m['e1'] == home_fr and m['e2'] == away_fr) or \
                   (m['e1'] == away_fr and m['e2'] == home_fr):
                    zengoal_id = m['id']
                    # Si les équipes sont inversées, inverser les scores
                    if m['e1'] == away_fr:
                        home_goals, away_goals = away_goals, home_goals
                    mapping_ref.set(zengoal_id)
                    break
        
        if not zengoal_id:
            continue
        
        # Vérifier si le résultat a changé
        existing_result = existing.get(str(zengoal_id))
        if existing_result and \
           existing_result.get('s1') == home_goals and \
           existing_result.get('s2') == away_goals:
            continue  # Pas de changement
        
        # Enregistrer le résultat
        db.reference(f'resultats/{zengoal_id}').set({
            's1': home_goals,
            's2': away_goals,
            'e1': home_fr,
            'e2': away_fr,
            'updatedAt': datetime.now().isoformat()
        })
        
        print(f"✅ Match {zengoal_id}: {home_fr} {home_goals}-{away_goals} {away_fr}")
        updated += 1
    
    print(f"📊 {updated} résultat(s) mis à jour sur Firebase")
    
    # Mettre à jour les phases finales avec les bons noms d'équipes
    update_knockout_names(matches)
 
def update_knockout_names(matches):
    """
    Met à jour les noms des équipes qualifiées pour les phases finales
    directement dans Firebase pour que l'app les affiche
    """
    ko_updates = {}
    for match in matches:
        status = match.get('status', '')
        if status not in ['FINISHED', 'AWARDED', 'SCHEDULED', 'TIMED']:
            continue
        home = fr_name(match.get('homeTeam', {}).get('name', ''))
        away = fr_name(match.get('awayTeam', {}).get('name', ''))
        home_flag = flag(match.get('homeTeam', {}).get('name', ''))
        away_flag = flag(match.get('awayTeam', {}).get('name', ''))
        if home and home != '' and '1er' not in home and 'V.' not in home:
            ko_updates[f"knockout_teams/{home}"] = home_flag
        if away and away != '' and '1er' not in away and 'V.' not in away:
            ko_updates[f"knockout_teams/{away}"] = away_flag
    
    if ko_updates:
        db.reference('/').update(ko_updates)
 
# ══════════════════════════════════════════════
# POINT D'ENTRÉE
# ══════════════════════════════════════════════
if __name__ == '__main__':
    init_firebase()
    update_scores()
    print("\n🏁 Mise à jour terminée")
