# Tests Fonctionnels Simeis

## Vue d'ensemble

Ce répertoire contient les tests fonctionnels automatiques pour le jeu Simeis. Ces tests valident les principales mécaniques du jeu en simulant des scénarios utilisateur réalistes.

## Scénarios couverts

### Scénario 1 : Achat de vaisseau
**Mécanique testée** : Système économique et transaction

- Création d'un nouveau joueur (capital initial: 72,000 crédits)
- Vérification de l'argent de départ
- Achat d'un vaisseau Light (~10,000 crédits)
- Validation du débit monétaire
- Confirmation que le vaisseau est dans l'inventaire

**Résultat attendu** : L'argent doit diminuer d'environ 10,000 crédits

### Scénario 2 : Extraction de ressources
**Mécanique testée** : Système d'équipage et extraction minière

- Création d'un nouveau joueur
- Achat d'un vaisseau Light
- Embauche d'un opérateur (nécessaire pour l'extraction)
- Vérification de l'état du vaisseau
- Préparation pour l'extraction de ressources

**Résultat attendu** : Le vaisseau est prêt pour l'extraction avec un opérateur embauché

### Scénario 3 : Trading sur le marché
**Mécanique testée** : Système de marché et commerce

- Création d'un nouveau joueur
- Récupération des prix actuels du marché
- Achat d'une ressource bon marché (Hydrogen: 4 crédits)
- Validation du débit monétaire
- Confirmation que les ressources sont stockées en station

**Résultat attendu** : L'argent doit diminuer et le cargo doit augmenter

## Exécution des tests

### Prérequis

```bash
# Installer les dépendances Python
pip install requests
```

### En développement (local)

Assurez-vous que le serveur est compilé :

```bash
# Compilation en debug
make build

# Ou en release
make release
```

Puis exécutez les tests :

```bash
# Les tests vont démarrer le serveur automatiquement
python tests/functional_tests.py
```

### En CI/CD

Les tests s'exécutent automatiquement :

1. **Avant les releases** : Le workflow s'exécute sur les branches `release/*`
2. **À la demande** : Utilisez l'onglet "Actions" → "Tests Fonctionnels Lourds" → "Run workflow"

Pour déclencher manuellement depuis la CLI :

```bash
# Si vous avez les permissions GitHub
gh workflow run heavy_tests.yml
```

## Résultats et logs

### Succès
```
[ℹ INFO] Début des tests fonctionnels Simeis
[ℹ INFO] Démarrage du serveur...
[✓ SUCCESS] Serveur démarré et prêt
[ℹ INFO] Scénario 1 : Achat de vaisseau
[✓ SUCCESS] Joueur créé (ID: 1234567890)
...
[ℹ INFO] RÉSUMÉ DES TESTS
Résultat : 3/3 scénarios réussis
[✓ SUCCESS] Tous les tests sont passés !
```

### Échec
En cas d'échec, le script affiche :
- `[✗ ERROR]` : Problème détecté
- Code de sortie : 1

## Architecture des tests

Le script `tests/functional_tests.py` est structuré ainsi :

```
├── Configuration
│   ├── Chemins de binaire
│   └── Port du serveur (8000)
├── Helpers
│   ├── start_server()  : Démarre le serveur et attend qu'il soit prêt
│   ├── stop_server()   : Arrête proprement le serveur
│   ├── api_request()   : Effectue des requêtes API avec gestion d'erreurs
│   └── log_*()         : Fonctions de logging colorisées
├── Scénarios
│   ├── test_scenario_ship_purchase()
│   ├── test_scenario_resource_extraction()
│   └── test_scenario_market_trading()
└── Main
    └── main() : Orchestrateur principal
```

## Extension des tests

### Ajouter un nouveau scénario

1. Créez une fonction `test_scenario_name()` dans le script
2. Utilisez les helpers `api_request()`, `log_info()`, etc.
3. Retournez `True` en cas de succès, `False` sinon
4. Ajoutez la fonction à la liste dans `main()`

Exemple :

```python
def test_scenario_crew_trading() -> bool:
    """Scénario : Trader professionnel"""
    try:
        # 1. Créer joueur
        player_data = api_request("POST", f"/player/new/{generate_player_name()}")
        player_key = player_data["key"]
        player_id = player_data["playerId"]
        
        # 2. Vos tests...
        log_info("Étape du test...")
        
        # 3. Retourner le résultat
        log_success("✓ Scénario réussi")
        return True
    except Exception as e:
        log_error(f"Scénario échoué : {e}")
        return False
```

## Troubleshooting

### Le serveur ne démarre pas
- Vérifiez que le binaire est bien compilé : `ls target/release/simeis-server`
- Vérifiez que le port 8000 n'est pas utilisé : `lsof -i :8000`
- Consultez les logs du serveur

### Les tests échouent aléatoirement
- Le serveur peut avoir besoin de plus de temps pour démarrer
- Les délais d'attente (`time.sleep()`) peuvent être ajustés
- Vérifiez la disponibilité des ressources système

### Erreur de connexion API
- Vérifiez que l'URL du serveur est correcte (par défaut: `http://localhost:8000`)
- Testez manuellement : `curl http://localhost:8000/ping`

## Intégration avec le workflow de release

Les tests lourds s'exécutent **avant** chaque release pour valider :
- Les mécaniques principales du jeu
- L'intégrité des transactions financières
- La création de joueurs et vaisseaux
- Le système de marché

### Exemple : Release avec tests

1. Créer une branche `release/v1.0.0`
2. GitHub Actions déclenche automatiquement `heavy_tests.yml`
3. Si les tests réussissent, la release peut être publiée
4. Si les tests échouent, la release est bloquée

## Maintenance

- **Fréquence** : Les tests s'exécutent à chaque branche release
- **Durée** : Environ 3-5 minutes (selon la machine)
- **Artifacts** : Les résultats sont archivés 7 jours

## Ressources utiles

- [Swagger UI Simeis](../doc/swagger-ui.html)
- [Documentation API](../doc/swagger.json)
- [Makefile - Cibles de build](../Makefile)
