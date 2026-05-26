# tests/example_advanced_scenario.py
"""
Exemple : Comment ajouter de nouveaux scénarios de test au script principal

Ce fichier montre comment créer et intégrer de nouveaux tests fonctionnels
dans le script principal (functional_tests.py)
"""

import time
from typing import Optional


# ─── Exemple 1 : Scénario Simple - Vérification du Ping ───────────────────

def test_scenario_server_connectivity() -> bool:
    """
    Scénario simple : Connectivité du serveur
    
    Teste juste que le serveur répond correctement.
    Idéal comme test de "smoke test" avant les scénarios complexes.
    """
    from functional_tests import api_request, log_info, log_success, log_error
    
    log_info("=" * 70)
    log_info("SCÉNARIO EXEMPLE : Connectivité du serveur")
    log_info("=" * 70)
    
    try:
        # Faire un simple ping
        log_info("Envoi d'une requête ping...")
        response = api_request("GET", "/ping")
        
        if response.get("ping") == "pong":
            log_success("✓ Serveur opérationnel")
            log_success("✓ Scénario réussi\n")
            return True
        else:
            log_error(f"Réponse inattendue : {response}")
            return False
            
    except Exception as e:
        log_error(f"Scénario échoué : {e}")
        return False


# ─── Exemple 2 : Scénario Intermédiaire - Vérification des Ressources ──────

def test_scenario_resources_info() -> bool:
    """
    Scénario intermédiaire : Vérification des informations de ressources
    
    Teste que toutes les ressources sont disponibles et ont les bonnes propriétés.
    """
    from functional_tests import api_request, log_info, log_success, log_error, log_warning
    
    log_info("=" * 70)
    log_info("SCÉNARIO EXEMPLE : Informations des ressources")
    log_info("=" * 70)
    
    try:
        # Récupérer les informations des ressources
        log_info("Récupération des informations des ressources...")
        resources = api_request("GET", "/resources")
        
        # Compter les ressources
        resource_count = len(resources) - 1  # -1 pour "error"
        log_success(f"Ressources trouvées : {resource_count}")
        
        # Vérifier les propriétés attendues
        expected_resources = ["Hydrogen", "Carbon", "Iron", "Oxygen"]
        for resource in expected_resources:
            if resource in resources:
                res_info = resources[resource]
                log_success(f"  ✓ {resource}: price={res_info.get('base-price')}, volume={res_info.get('volume')}")
            else:
                log_warning(f"  ⚠ {resource} manquante")
        
        log_success("✓ Scénario réussi\n")
        return True
        
    except Exception as e:
        log_error(f"Scénario échoué : {e}")
        return False


# ─── Exemple 3 : Scénario Avancé - Boucle de Trading ─────────────────────

def test_scenario_trading_loop() -> bool:
    """
    Scénario avancé : Boucle de trading complète
    
    Teste une séquence plus complexe :
    1. Créer un joueur
    2. Acheter une ressource bon marché
    3. Revendre cette ressource avec profit
    4. Vérifier le gain
    """
    from functional_tests import (
        api_request, generate_player_name, log_info, log_success, 
        log_error, log_warning
    )
    
    log_info("=" * 70)
    log_info("SCÉNARIO EXEMPLE AVANCÉ : Boucle de trading avec profit")
    log_info("=" * 70)
    
    try:
        # 1. Créer un joueur
        player_name = generate_player_name()
        log_info(f"Création du joueur '{player_name}'...")
        player_data = api_request("POST", f"/player/new/{player_name}")
        player_key = player_data["key"]
        player_id = player_data["playerId"]
        log_success(f"Joueur créé (ID: {player_id})")
        
        # 2. Obtenir les stats initiales
        stats = api_request("GET", "/gamestats")
        player_stats = stats.get(str(player_id), {})
        initial_money = player_stats.get("money", 0)
        stations = player_stats.get("stations", {})
        station_id = list(stations.keys())[0]
        
        log_info(f"Argent initial : {initial_money} crédits")
        
        # 3. Acheter une ressource
        resource = "Hydrogen"
        quantity = 50
        prices = api_request("GET", "/market/prices")
        buy_price = prices.get(resource, 4)
        buy_cost = quantity * buy_price
        
        log_info(f"Achat de {quantity} {resource} @ {buy_price} crédits = {buy_cost} crédits...")
        api_request("POST", f"/market/{station_id}/buy/{resource}/{quantity}", player_key=player_key)
        log_success("Achat effectué")
        
        time.sleep(1)
        
        # 4. Revendre la ressource (prix peut avoir changé)
        log_info(f"Revente de {quantity} {resource}...")
        api_request("POST", f"/market/{station_id}/sell/{resource}/{quantity}", player_key=player_key)
        log_success("Vente effectuée")
        
        time.sleep(1)
        
        # 5. Vérifier le solde final
        stats = api_request("GET", "/gamestats")
        player_stats = stats.get(str(player_id), {})
        final_money = player_stats.get("money", 0)
        profit = final_money - initial_money
        
        log_info(f"Argent final : {final_money} crédits")
        log_info(f"Profit/Perte : {profit} crédits")
        
        if profit < 0:
            log_warning(f"Perte lors du trading : {abs(profit)} crédits (frais du marché)")
        else:
            log_success(f"Profit réalisé : {profit} crédits")
        
        log_success("✓ Scénario réussi\n")
        return True
        
    except Exception as e:
        log_error(f"Scénario échoué : {e}")
        return False


# ─── Instructions d'intégration ──────────────────────────────────────────

"""
COMMENT AJOUTER CES SCÉNARIOS AU SCRIPT PRINCIPAL :

1. Copier les fonctions `test_scenario_*()` dans `functional_tests.py`

2. Dans la fonction `main()`, ajouter les scénarios à la liste :

    results = []
    results.append(("Scénario 1 : Achat de vaisseau", test_scenario_ship_purchase()))
    results.append(("Scénario 2 : Extraction", test_scenario_resource_extraction()))
    results.append(("Scénario 3 : Trading", test_scenario_market_trading()))
    
    # Ajouter vos nouveaux scénarios :
    results.append(("Exemple : Connectivité", test_scenario_server_connectivity()))
    results.append(("Exemple : Ressources", test_scenario_resources_info()))
    results.append(("Exemple Avancé : Trading Loop", test_scenario_trading_loop()))

3. Exécuter et valider :
    python tests/functional_tests.py

CONSEILS :
- Toujours commencer par récupérer les stats avec api_request("GET", "/gamestats")
- Utiliser les logs : log_info(), log_success(), log_error(), log_warning()
- Gérer les erreurs API avec try/except
- Ajouter des délais (time.sleep()) si nécessaire pour laisser le serveur mettre à jour
- Retourner toujours True/False à la fin

STRUCTURE DE TEST RECOMMANDÉE :
1. log_info("=" * 70)
2. log_info("Description du test")
3. log_info("=" * 70)
4. try:
   - Étape 1: log_info() + api_request() + log_success()
   - Étape 2: ...
   - Étape n: ...
   - log_success("✓ Scénario réussi\\n")
   - return True
5. except: log_error() + return False
"""
