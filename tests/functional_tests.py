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

# Variables globales pour l'enchaînement dynamique des scénarios
PLAYER_ID = None
AUTH_KEY = None
STATION_ID = "27524"  # ID par défaut extrait du Swagger
REAL_SHIP_ID = None   # Capturé à l'achat du vaisseau

# ─── Détection dynamique du binaire (CI Release vs Local Debug) ───
BINARY_RELEASE = Path("target/release/simeis-server")
BINARY_DEBUG = Path("target/debug/simeis-server")
BINARY = BINARY_RELEASE if BINARY_RELEASE.exists() else BINARY_DEBUG

# ─── Helper pour récupérer l'argent actuel du joueur depuis /gamestats ───

def get_player_money() -> float:
    """Récupère le solde actuel du joueur en interrogeant /gamestats."""
    url = f"{API_URL}/gamestats"
    req = urllib.request.Request(url, method="GET")
    if AUTH_KEY:
        req.add_header("Simeis-Key", AUTH_KEY)
        
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            stats = json.loads(response.read().decode("utf-8"))
            player_str_id = str(PLAYER_ID)
            if player_str_id in stats:
                return float(stats[player_str_id].get("money", 0.0))
            else:
                return 0.0
    except Exception:
        return 0.0

# ─── Helper pour les requêtes HTTP (Avec injection de la clé Simeis-Key) ───

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

# ─── Validation des Scénarios Utilisateurs ─────────────────────────────────

def test_scenario_1_economy() -> bool:
    """Scénario 1 : Validation stricte de l'économie selon les exigences."""
    global PLAYER_ID, AUTH_KEY, REAL_SHIP_ID
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
        
    # 2. Vérification de son argent de départ X
    argent_depart = get_player_money()
    print(f"  ✓ Argent de départ détecté : {argent_depart} crédits.")
    
    # On récupère le catalogue du shipyard pour savoir quoi acheter
    code_list, body_list = send_request(f"/station/{STATION_ID}/shipyard/list", "GET")
    if code_list != 200:
        print("  ❌ Impossible de lister le shipyard pour trouver un vaisseau.")
        return False
        
    ships_available = json.loads(body_list).get("ships", [])
    if len(ships_available) == 0:
        print("  ❌ Le catalogue du shipyard est vide. Impossible de tester l'achat.")
        return False
        
    target_ship_type = ships_available[0].get("id")
    
    # 3. On achète un vaisseau
    url_shipyard = f"/station/{STATION_ID}/shipyard/buy/{target_ship_type}"
    code_buy, body_buy = send_request(url_shipyard, "POST")
    
    # 4. La transaction doit réussir (Code 200)
    if code_buy == 200:
        REAL_SHIP_ID = json.loads(body_buy).get("id")
        print(f"  ✓ Transaction réussie. Vaisseau acheté (ID Instance: {REAL_SHIP_ID}).")
    else:
        print(f"  ❌ Échec de la transaction d'achat du vaisseau. Code: {code_buy}")
        return False
        
    # 5. Notre argent doit avoir diminué
    argent_apres_vaisseau = get_player_money()
    if argent_apres_vaisseau < argent_depart:
        print(f"  ✓ Vérification : L'argent a diminué ({argent_depart} -> {argent_apres_vaisseau}).")
    else:
        print(f"  ❌ Erreur : L'argent n'a pas diminué après l'achat du vaisseau ! ({argent_apres_vaisseau})")
        return False
        
    # 6. On achète un module de Miner
    url_module = f"/station/{STATION_ID}/shop/modules/{REAL_SHIP_ID}/buy/Miner"
    code_mod, body_mod = send_request(url_module, "POST")
    
    # 7. La transaction doit réussir (Code 200)
    if code_mod == 200:
        print("  ✓ Transaction réussie. Module 'Miner' acheté et équipé.")
    else:
        print(f"  ❌ Échec de la transaction d'achat du module. Code: {code_mod}")
        return False
        
    # 8. Notre argent doit avoir encore diminué
    argent_final = get_player_money()
    if argent_final < argent_apres_vaisseau:
        print(f"  ✓ Vérification : L'argent a encore diminué ({argent_apres_vaisseau} -> {argent_final}).")
        return True
    else:
        print(f"  ❌ Erreur : L'argent n'a pas bougé après l'achat du module ! ({argent_final})")
        return False


def test_scenario_2_mechanics() -> bool:
    """Scénario 2 : Déplacement spatial du vaisseau."""
    print("👉 Exécution du Scénario 2 : Mécanique de déplacement")
    
    if REAL_SHIP_ID is None:
        print("  ❌ Aucun ID de vaisseau en mémoire (Scénario 1 requis).")
        return False
    else:
        url_navigate = f"/ship/{REAL_SHIP_ID}/navigate/100/200/0"
        code, body = send_request(url_navigate, "POST")
        if code == 200:
            print("  ✓ Ordre de voyage vers la position XYZ [100, 200, 0] validé.")
            return True
        else:
            print(f"  ❌ Échec du voyage spatial. Code reçu: {code}")
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