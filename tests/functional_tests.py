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

# ─── Détection dynamique du binaire (CI Release vs Local Debug) ───
BINARY_RELEASE = Path("target/release/simeis-server")
BINARY_DEBUG = Path("target/debug/simeis-server")

BINARY = BINARY_RELEASE if BINARY_RELEASE.exists() else BINARY_DEBUG

# ─── Helper pour les requêtes HTTP (Sans bibliothèque tierce comme requests) ───

def send_request(endpoint: str, method: str = "GET", data: dict = None) -> tuple[int, str]:
    """Envoie une requête HTTP à l'API Simeis en utilisant uniquement urllib."""
    url = f"{API_URL}{endpoint}"
    req_data = json.dumps(data).encode("utf-8") if data else None
    headers = {"Content-Type": "application/json"} if data else {}
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"❌ Erreur de connexion à l'API : {e.reason}")
        return 500, str(e.reason)

# ─── Validation des Scénarios Utilisateurs (TP3 - Partie 1) ─────────────────

def test_scenario_1_economy() -> None:
    """Scénario 1 : Création joueur -> Achat vaisseau -> Achat module."""
    print("👉 Exécution du Scénario 1 : Économie de base")
    
    # 1. Création du joueur Evan
    code, body = send_request("/player/new", "POST", {"name": "Evan"})
    assert code in [200], f"Échec création joueur: {body}"
    print("  ✓ Joueur 'Evan' créé avec succès.")
    
    # 2. Achat d'un vaisseau 
    code, body = send_request("/station/{station_id}/shipyard/buy/{ship_id}", "POST", {"modetype": "Explorer"})
    assert code == 200, f"Échec achat vaisseau: {body}"
    print("  ✓ Vaisseau 'Explorer' acheté.")
    
    # 3. Achat d'un module de minage "Miner"
    code, body = send_request("/player/buy-module", "POST", {"module_type": "Miner"})
    assert code == 200, f"Échec achat module: {body}"
    print("  ✓ Module 'Miner' acheté et équipé.")


def test_scenario_2_mechanics() -> None:
    """Scénario 2 : Déplacement spatial du vaisseau."""
    print("👉 Exécution du Scénario 2 : Mécanique de déplacement")
    
    # Simulation d'un déplacement vers un secteur précis
    code, body = send_request("/ship/travel", "POST", {"destination": "Simeis-Alpha"})
    assert code == 200, f"Échec du voyage spatial: {body}"
    
    # Vérification du statut ou des coordonnées du joueur après voyage
    code, body = send_request("/player/status", "GET")
    assert code == 200 and "Simeis-Alpha" in body, "Le vaisseau n'a pas atteint la destination attendue."
    print("  ✓ Voyage vers 'Simeis-Alpha' validé.")


def test_scenario_3_errors() -> None:
    """Scénario 3 : Gestion des limites économiques et refus de transaction."""
    print("👉 Exécution du Scénario 3 : Limites financières")
    
    # Tentative d'achat d'un vaisseau hors de prix pour forcer un code de refus (ex: 400 Bad Request)
    code, body = send_request("/player/buy-ship", "POST", {"ship_type": "DeathStar"})
    
    # L'API doit retourner une erreur propre (400 ou message explicite) sans crash du serveur
    assert code == 400 or "insuffisants" in body.lower(), \
        f"La transaction aurait dû échouer pour fonds insuffisants. Réponse API: {body}"
    print("  ✓ Refus sur fonds insuffisants correctement intercepté par l'API.")

# ─── Cycle de vie du serveur en cours de test ──────────────────────────────

def main():
    if not BINARY.exists():
        print("❌ Erreur : Aucun binaire simeis-server trouvé dans target/release/ ou target/debug/")
        print("Mettez en place une étape de compilation ('cargo build' ou 'cargo build --release') avant ce script.")
        sys.exit(1)

    print(f"=== Démarrage du serveur Simeis ({BINARY}) pour les tests fonctionnels ===")
    # Lancement du serveur en arrière-plan
    server_process = subprocess.Popen(
        [str(BINARY)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Attente active que le serveur API soit prêt à répondre
    ready = False
    for _ in range(15):
        time.sleep(0.5)
        try:
            # On ping la racine (/) pour vérifier si l'application écoute
            urllib.request.urlopen(f"{API_URL}/", timeout=0.5)
            ready = True
            break
        except (urllib.error.HTTPError, urllib.error.URLError):
            if isinstance(sys.exc_info()[1], urllib.error.HTTPError):
                ready = True
                break
            continue

    if not ready:
        print("❌ Erreur : Le serveur Simeis n'a pas démarré à temps sur le port 8080.")
        server_process.terminate()
        sys.exit(1)

    print("🚀 Serveur en ligne. Lancement des scénarios utilisateurs...\n")
    
    failures = 0
    scenarios = [test_scenario_1_economy, test_scenario_2_mechanics, test_scenario_3_errors]
    
    for scenario in scenarios:
        try:
            scenario()
            print(f"✅ {scenario.__name__} réussi.\n")
        except AssertionError as exc:
            print(f"💥 ÉCHEC dans {scenario.__name__} : {exc}\n")
            failures += 1
        except Exception as exc:
            print(f"❌ Erreur inattendue dans {scenario.__name__} : {exc}\n")
            failures += 1

    # Arrêt propre du serveur à la fin des tests
    print("=== Fermeture du serveur Simeis ===")
    server_process.terminate()
    server_process.wait()

    if failures > 0:
        print(f"❌ Fin des tests : {failures} scène(s) en échec.")
        sys.exit(1)
    else:
        print("🎉 Tous les scénarios fonctionnels s'exécutent avec succès ! ✅")
        sys.exit(0)

if __name__ == "__main__":
    main()