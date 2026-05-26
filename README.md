# Simeis

Jeu par APIDémonstration du système de propagation automatique

## Quick Start

### Compilation

```bash
# Build en développement
make build

# Build en production (optimisé)
make release
```

### Tests

```bash
# Tests unitaires Rust
make test

# Tests fonctionnels (tests lourds avec API complète)
pip install requests
python tests/functional_tests.py

# Valider la configuration des tests
bash tests/validate_tests.sh
```

## Documentation des Tests Fonctionnels

Les tests fonctionnels automatisés valident les principales mécaniques du jeu en simulant des scénarios utilisateur réalistes.

**3 Scénarios couverts** :
1. **Achat de vaisseau** - Système économique et transactions
2. **Extraction de ressources** - Système d'équipage et exploitation minière
3. **Trading sur le marché** - Commerce et économie

Pour plus de détails, consultez [tests/README_FUNCTIONAL_TESTS.md](tests/README_FUNCTIONAL_TESTS.md)

## CI/CD Pipeline

### Workflows disponibles

- **ci.yml** : Linting, tests unitaires, build (sur PR)
- **heavy_tests.yml** : Tests fonctionnels lourds (avant release, sur demande)
- **check-todos.yml** : Vérification des TODOs
- **propagation.yml** : Système de propagation

### Déclencher les tests fonctionnels

**Avant une release** :
```bash
git push origin release/vX.Y.Z
```

**Manuellement** :
1. GitHub Actions → "Tests Fonctionnels Lourds" 
2. Click "Run workflow"

Ou via CLI (si autorisé) :
```bash
gh workflow run heavy_tests.yml
```
