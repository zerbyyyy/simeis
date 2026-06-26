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

# URL locale du serveur API Simeis
API_URL = "http://127.0.0.1:8081"

# Variables globales pour l'enchaînement dynamique des scénarios
PLAYER_ID = None
AUTH_KEY = None
STATION_ID = "27524"  # ID par défaut extrait de la spécification OpenAPI du projet
REAL_SHIP_ID = None   # Sera capturé dynamiquement lors de l'achat du vaisseau

# ─── Détection dynamique du binaire (CI Release vs Local Debug) ───
BINARY_RELEASE = Path("target/release/simeis-server")
BINARY_DEBUG = Path("target/debug/simeis-server")
BINARY = BINARY_RELEASE if BINARY_RELEASE.exists() else BINARY_DEBUG

# ─── Helper pour les requêtes HTTP (Avec injection de la clé Simeis-Key) ───

def send_request(endpoint: str, method: str = "GET", data: dict = None) -> tuple[int, str]:
    """Envoie une requête HTTP à l'API Simeis en utilisant uniquement urllib."""
    url = f"{API_URL}{endpoint}"
    req_data = json.dumps(data).encode("utf-8") if data else None
    
    # Configuration des en-têtes requis par la doc OpenAPI
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
    """Scénario 1 : Création joueur -> Achat vaisseau -> Achat module."""
    global PLAYER_ID, AUTH_KEY, REAL_SHIP_ID
    print("👉 Exécution du Scénario 1 : Économie de base")
    
    # ── ÉTAPE 1 : Création du joueur Evan ──
    code, body = send_request("/player/new/Evan", "POST")
    if code == 200:
        response_data = json.loads(body)
        PLAYER_ID = response_data.get("playerId")
        AUTH_KEY = response_data.get("key")
        print(f"  ✓ Étape 1/4 : Joueur 'Evan' créé (ID: {PLAYER_ID}).")
    else:
        print(f"  ❌ Étape 1/4 échouée. Code reçu: {code}, Réponse: {body}")
        return False
        
    # ── ÉTAPE 2 : Récupération des vaisseaux disponibles ──
    code, body = send_request(f"/station/{STATION_ID}/shipyard/list", "GET")
    if code == 200:
        ships_available = json.loads(body).get("ships", [])
        if len(ships_available) > 0:
            target_ship_type = ships_available[0].get("id")
            print(f"  ✓ Étape 2/4 : Type de vaisseau trouvé dans le catalogue (ID: {target_ship_type}).")
        else:
            print("  ❌ Étape 2/4 échouée. Aucun vaisseau en vente dans le shipyard.")
            return False
    else:
        print(f"  ❌ Étape 2/4 échouée. Impossible de lister le shipyard. Code reçu: {code}")
        return False
        
    # ── ÉTAPE 3 : Achat effectif du vaisseau ──
    url_shipyard = f"/station/{STATION_ID}/shipyard/buy/{target_ship_type}"
    code, body = send_request(url_shipyard, "POST")
    if code == 200:
        REAL_SHIP_ID = json.loads(body).get("id")
        print(f"  ✓ Étape 3/4 : Vaisseau acheté avec succès. ID unique Instance : {REAL_SHIP_ID}")
    else:
        print(f"  ❌ Étape 3/4 échouée. Échec achat vaisseau. Code reçu: {code}, Réponse: {body}")
        return False
        
    # ── ÉTAPE 4 : Achat d'un module de minage "Miner" ──
    url_module = f"/station/{STATION_ID}/shop/modules/{REAL_SHIP_ID}/buy/Miner"
    code, body = send_request(url_module, "POST")
    if code == 200:
        print(f"  ✓ Étape 4/4 : Module 'Miner' acheté et équipé sur le vaisseau {REAL_SHIP_ID}.")
        return True
    else:
        print(f"  ❌ Étape 4/4 échouée. Échec achat module. Code reçu: {code}, Réponse: {body}")
        return False


def test_scenario_2_mechanics() -> bool:
    """Scénario 2 : Déplacement spatial du vaisseau."""
    print("👉 Exécution du Scénario 2 : Mécanique de déplacement")
    
    if REAL_SHIP_ID == None:
        print("  ❌ Échec avant déplacement : Aucun ID de vaisseau en mémoire (Scénario 1 requis).")
        return False
    else:
        # Le vaisseau existe, on envoie l'ordre de navigation vers les coordonnées XYZ
        url_navigate = f"/ship/{REAL_SHIP_ID}/navigate/100/200/0"
        code, body = send_request(url_navigate, "POST")
        
        if code == 200:
            print("  ✓ Ordre de voyage vers la position XYZ [100, 200, 0] validé par le serveur.")
            return True
        else:
            print(f"  ❌ Échec du voyage spatial. Code reçu: {code}, Réponse: {body}")
            return False


def test_scenario_3_errors() -> bool:
    """Scénario 3 : Gestion des limites économiques et refus de transaction."""
    print("👉 Exécution du Scénario 3 : Limites financières")
    
    # Tentative d'un achat invalide (on force une fausse station à dessein)
    url_invalid = f"/station/999999/shipyard/buy/VaisseauInexistant"
    code, body = send_request(url_invalid, "POST")
    
    # On attend un refus (comme un code 400, 404, 500 ou un JSON contenant "error")
    if code in [400, 404, 403, 500] or "error" in body.lower():
        print(f"  ✓ Refus de transaction correctement intercepté par l'API (Code reçu: {code}).")
        return True
    else:
        print(f"  ❌ Erreur de gestion : Le serveur aurait dû refuser la transaction, mais a répondu avec le code: {code}")
        return False

# ─── Cycle de vie du serveur en cours de test ──────────────────────────────

def main():
    if not BINARY.exists():
        print("❌ Erreur : Aucun binaire simeis-server trouvé.")
        sys.exit(1)

    print(f"=== Démarrage du serveur Simeis ({BINARY}) ===")
    
    log_file = open("simeis_server.log", "w")
    server_process = subprocess.Popen([str(BINARY)], stdout=log_file, stderr=log_file)
    
    # Attente active du serveur avec un ping de contrôle
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
    
    # --- Lancement du Scénario 1 ---
    if test_scenario_1_economy() == True:
        print("✅ test_scenario_1_economy réussi.\n")
    else:
        failures += 1
        print("💥 ÉCHEC dans test_scenario_1_economy\n")
        
    # --- Lancement du Scénario 2 ---
    if test_scenario_2_mechanics() == True:
        print("✅ test_scenario_2_mechanics réussi.\n")
    else:
        failures += 1
        print("💥 ÉCHEC dans test_scenario_2_mechanics\n")
        
    # --- Lancement du Scénario 3 ---
    if test_scenario_3_errors() == True:
        print("✅ test_scenario_3_errors réussi.\n")
    else:
        failures += 1
        print("💥 ÉCHEC dans test_scenario_3_errors\n")

    # Fermeture propre du serveur
    print("=== Fermeture du serveur Simeis ===")
    server_process.terminate()
    server_process.wait()
    log_file.close()

    if failures > 0:
        print(f"❌ Fin des tests : {failures} scène(s) en échec.")
        print("\n--- 📄 LOGS DU SERVEUR SIMEIS ---")
        try:
            with open("simeis_server.log", "r") as f:
                print(f.read())
        except Exception:
            pass
        sys.exit(1)
    else:
        print("🎉 Tous les scénarios fonctionnels s'exécutent avec succès ! ✅")
        sys.exit(0)

if __name__ == "__main__":
    main()