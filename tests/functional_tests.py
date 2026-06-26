#!/usr/bin/env python3
"""
tests/functional_tests.py
Tests fonctionnels automatiques (Scénarios utilisateurs API) pour Simeis.
"""

import subprocess
import sys
import time
import urllib.request
import urllib.error
import json
from pathlib import Path

# URL locale du serveur API Simeis (Port 8081)
API_URL = "http://127.0.0.1:8081"

# Variables globales dynamiques (Remplies par le serveur)
PLAYER_ID = None
AUTH_KEY = None
STATION_ID = None     # Trouvé dynamiquement
REAL_SHIP_ID = None   # Capturé à l'achat du vaisseau

# ─── Détection dynamique du binaire (CI Release vs Local Debug) ───
BINARY_RELEASE = Path("target/release/simeis-server")
BINARY_DEBUG = Path("target/debug/simeis-server")
BINARY = BINARY_RELEASE if BINARY_RELEASE.exists() else BINARY_DEBUG

# ─── Helper pour les requêtes HTTP ───

def send_request(endpoint: str, method: str = "GET", data: dict = None) -> tuple[int, str]:
    """Envoie une requête HTTP à l'API Simeis en utilisant uniquement urllib."""
    url = f"{API_URL}{endpoint}"
    req_data = json.dumps(data).encode("utf-8") if data else None
    
    headers = {"Content-Type": "application/json"}
    if AUTH_KEY:
        headers["Simeis-Key"] = AUTH_KEY
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"❌ Erreur de connexion à l'API : {e.reason}")
        return 500, str(e.reason)

# ─── Helper pour récupérer l'argent actuel du joueur ───

def get_player_money() -> float:
    """Récupère le solde actuel du joueur depuis /gamestats."""
    code, body = send_request("/gamestats", "GET")
    if code == 200:
        stats = json.loads(body)
        player_str_id = str(PLAYER_ID)
        if player_str_id in stats:
            return float(stats[player_str_id].get("money", 0.0))
    return 0.0

# ─── Validation des Scénarios Utilisateurs ─────────────────────────────────

def test_scenario_1_economy() -> bool:
    """Scénario 1 : Validation de l'économie réelle (Création -> Recherche -> Achat -> Module)."""
    global PLAYER_ID, AUTH_KEY, STATION_ID, REAL_SHIP_ID
    print("👉 Exécution du Scénario 1 : Économie de base")
    
    # 1. On crée un nouveau joueur
    code, body = send_request("/player/new/Evan", "POST")
    if code == 200:
        response_data = json.loads(body)
        PLAYER_ID = response_data.get("playerId")
        AUTH_KEY = response_data.get("key")
        print(f"  ✓ Joueur 'Evan' créé (ID: {PLAYER_ID}).")
    else:
        print(f"  ❌ Échec création joueur. Code reçu: {code}")
        return False
        
    # 2. Récupération de l'argent de départ et de la station de départ du joueur
    code, body = send_request("/gamestats", "GET")
    if code == 200:
        stats = json.loads(body)
        player_info = stats.get(str(PLAYER_ID), {})
        argent_depart = player_info.get("money", 0.0)
        print(f"  ✓ Argent de départ détecté : {argent_depart} crédits.")
        
        # On regarde les stations possédées ou associées au joueur dans les stats
        stations_joueur = player_info.get("stations", {})
        if len(stations_joueur) > 0:
            # On récupère le premier ID de station disponible pour ce joueur
            STATION_ID = list(stations_joueur.keys())[0]
            print(f"  ✓ Station de départ détectée dynamiquement : {STATION_ID}")
        else:
            # Si le joueur n'a pas de station directement liée, on prend celle de l'exemple du prof
            STATION_ID = "27524"
            print(f"  ⚠️ Aucune station liée au joueur. Utilisation de la station par défaut : {STATION_ID}")
    else:
        print("  ❌ Impossible de lire /gamestats pour l'initialisation.")
        return False

    # 3. Recherche d'un vrai vaisseau disponible à la vente
    target_ship_type = None
    
    # On teste d'abord le shipyard de notre station actuelle
    code_list, body_list = send_request(f"/station/{STATION_ID}/shipyard/list", "GET")
    if code_list == 200:
        ships_available = json.loads(body_list).get("ships", [])
        if len(ships_available) > 0:
            target_ship_type = ships_available[0].get("id")
            
    # Si le shipyard de notre station est vide, on scanne pour trouver d'autres stations de l'univers !
    if target_ship_type is None:
        print(f"  🔍 Shipyard de la station {STATION_ID} vide. Lancement d'un scan spatial...")
        code_scan, body_scan = send_request(f"/station/{STATION_ID}/scan", "POST")
        
        if code_scan == 200:
            scan_data = json.loads(body_scan)
            stations_autour = scan_data.get("stations", [])
            
            # On parcourt les stations trouvées par le scanner pour checker leur catalogue
            for st in stations_autour:
                proche_id = str(st.get("id"))
                code_st, body_st = send_request(f"/station/{proche_id}/shipyard/list", "GET")
                if code_st == 200:
                    ships = json.loads(body_st).get("ships", [])
                    if len(ships) > 0:
                        STATION_ID = proche_id
                        target_ship_type = ships[0].get("id")
                        print(f"  🎯 Station avec catalogue trouvé ! Nouvelle STATION_ID : {STATION_ID}")
                        break

    # Si après le scan complet, rien n'est trouvé, le serveur est vide au démarrage
    if target_ship_type is None:
        print("  ❌ Échec : Aucun vaisseau n'est disponible à la vente dans tout l'univers Simeis.")
        return False

    # 4. Achat réel du vaisseau trouvé
    print(f"  🛒 Tentative d'achat du vaisseau {target_ship_type} sur la station {STATION_ID}...")
    url_shipyard = f"/station/{STATION_ID}/shipyard/buy/{target_ship_type}"
    code_buy, body_buy = send_request(url_shipyard, "POST")
    
    if code_buy == 200:
        REAL_SHIP_ID = json.loads(body_buy).get("id")
        print(f"  ✓ Transaction réussie. Vaisseau acheté (ID Instance: {REAL_SHIP_ID}).")
    else:
        print(f"  ❌ Échec de la transaction d'achat du vaisseau. Code serveur: {code_buy}")
        return False
        
    # 5. Vérification réelle de la diminution de l'argent
    argent_apres_vaisseau = get_player_money()
    if argent_apres_vaisseau < argent_depart:
        print(f"  ✓ L'argent a diminué ({argent_depart} -> {argent_apres_vaisseau}).")
    else:
        print(f"  ❌ TRANSACTION INVALIDÉE : L'argent n'a pas baissé après l'achat du vaisseau ! ({argent_apres_vaisseau})")
        return False
        
    # 6. Achat réel d'un module de Miner
    url_module = f"/station/{STATION_ID}/shop/modules/{REAL_SHIP_ID}/buy/Miner"
    code_mod, body_mod = send_request(url_module, "POST")
    
    if code_mod == 200:
        print("  ✓ Transaction réussie. Module 'Miner' acheté et équipé.")
    else:
        print(f"  ❌ Échec de la transaction d'achat du module. Code serveur: {code_mod}")
        return False
        
    # 7. Vérification finale de la nouvelle baisse d'argent
    argent_final = get_player_money()
    if argent_final < argent_apres_vaisseau:
        print(f"  ✓ L'argent a encore diminué ({argent_apres_vaisseau} -> {argent_final}).")
        return True
    else:
        print(f"  ❌ TRANSACTION INVALIDÉE : L'argent n'a pas baissé après le module ! ({argent_final})")
        return False


def test_scenario_2_mechanics() -> bool:
    """Scénario 2 : Déplacement spatial du vaisseau."""
    print("👉 Exécution du Scénario 2 : Mécanique de déplacement")
    
    if REAL_SHIP_ID is None:
        print("  ❌ Aucun ID de vaisseau en mémoire.")
        return False
    
    url_navigate = f"/ship/{REAL_SHIP_ID}/navigate/100/200/0"
    code, body = send_request(url_navigate, "POST")
    if code == 200:
        print("  ✓ Déplacement spatial validé par le serveur.")
        return True
    else:
        print(f"  ❌ Échec du déplacement spatial. Code reçu: {code}")
        return False


def test_scenario_3_errors() -> bool:
    """Scénario 3 : Gestion des refus de transaction."""
    print("👉 Exécution du Scénario 3 : Limites financières")
    
    url_invalid = "/station/999999/shipyard/buy/VaisseauInexistant"
    code, body = send_request(url_invalid, "POST")
    
    if code in [400, 404, 403, 500] or "error" in body.lower():
        print(f"  ✓ Refus de transaction correctement intercepté par l'API (Code reçu: {code}).")
        return True
    else:
        print(f"  ❌ Le serveur aurait dû refuser la transaction, mais a répondu avec le code: {code}")
        return False

# ─── Cycle de vie du serveur en cours de test ──────────────────────────────

def main():
    if not BINARY.exists():
        print("❌ Erreur : Aucun binaire simeis-server trouvé.")
        sys.exit(1)

    print(f"=== Démarrage du serveur Simeis ({BINARY}) ===")
    
    log_file = open("simeis_server.log", "w")
    server_process = subprocess.Popen([str(BINARY)], stdout=log_file, stderr=log_file)
    
    ready = False
    for _ in range(15):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(f"{API_URL}/ping", timeout=0.5)
            ready = True
            break
        except (urllib.error.HTTPError, urllib.error.URLError):
            continue

    if not ready:
        print(f"❌ Erreur : Le serveur Simeis n'a pas démarré à temps sur {API_URL}.")
        server_process.terminate()
        log_file.close()
        sys.exit(1)

    print("🚀 Serveur en ligne. Lancement des scénarios...\n")
    failures = 0
    
    if test_scenario_1_economy():
        print("✅ test_scenario_1_economy réussi.\n")
    else:
        failures += 1
        print("💥 ÉCHEC dans test_scenario_1_economy\n")
        
    if test_scenario_2_mechanics():
        print("✅ test_scenario_2_mechanics réussi.\n")
    else:
        failures += 1
        print("💥 ÉCHEC dans test_scenario_2_mechanics\n")
        
    if test_scenario_3_errors():
        print("✅ test_scenario_3_errors réussi.\n")
    else:
        failures += 1
        print("💥 ÉCHEC dans test_scenario_3_errors\n")

    print("=== Fermeture du serveur Simeis ===")
    server_process.terminate()
    server_process.wait()
    log_file.close()

    if failures > 0:
        print(f"❌ Fin des tests : {failures} scène(s) en échec.")
        sys.exit(1)
    else:
        print("🎉 Tous les scénarios fonctionnels s'exécutent avec succès ! ✅")
        sys.exit(0)

if __name__ == "__main__":
    main()