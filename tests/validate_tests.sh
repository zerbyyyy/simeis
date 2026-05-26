#!/bin/bash
# tests/validate_tests.sh
# Script de validation des tests fonctionnels
# Vérifie que le script et la configuration CI/CD sont corrects

set -e

echo "=== Validation des Tests Fonctionnels Simeis ==="
echo

# 1. Vérifier que les fichiers existent
echo "[1/5] Vérification des fichiers..."
files=(
    "tests/functional_tests.py"
    "tests/README_FUNCTIONAL_TESTS.md"
    ".github/workflows/heavy_tests.yml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done
echo

# 2. Vérifier la syntaxe Python
echo "[2/5] Vérification de la syntaxe Python..."
if python -m py_compile tests/functional_tests.py 2>/dev/null; then
    echo "  ✓ Syntax valid"
else
    echo "  ✗ Syntax error"
    exit 1
fi
echo

# 3. Vérifier les dépendances Python
echo "[3/5] Vérification des dépendances Python..."
if python -c "import requests, json, subprocess, pathlib, random, string, time" 2>/dev/null; then
    echo "  ✓ All dependencies available"
else
    echo "  ✗ Missing dependencies (requires: requests)"
    exit 1
fi
echo

# 4. Vérifier le YAML du workflow
echo "[4/5] Vérification de la configuration du workflow..."
if command -v python &> /dev/null; then
    if python -c "import yaml; yaml.safe_load(open('.github/workflows/heavy_tests.yml'))" 2>/dev/null; then
        echo "  ✓ Workflow YAML valid"
    else
        # Python yaml n'est pas installé, vérification manuelle
        if grep -q "name: Tests Fonctionnels Lourds" .github/workflows/heavy_tests.yml; then
            echo "  ✓ Workflow structure looks correct (yaml validation skipped)"
        else
            echo "  ✗ Workflow config error"
            exit 1
        fi
    fi
else
    echo "  ⚠ Yaml validation skipped (python not available)"
fi
echo

# 5. Compter les scénarios
echo "[5/5] Vérification des scénarios de test..."
scenario_count=$(grep -c "def test_scenario_" tests/functional_tests.py)
if [ "$scenario_count" -ge 3 ]; then
    echo "  ✓ $scenario_count test scenarios found (expected: ≥3)"
else
    echo "  ✗ Only $scenario_count scenarios (expected: ≥3)"
    exit 1
fi
echo

echo "=== ✓ All validations passed! ==="
echo
echo "To run tests locally:"
echo "  pip install requests"
echo "  make release"
echo "  python tests/functional_tests.py"
echo
echo "To trigger CI workflow:"
echo "  git push origin release/vX.Y.Z"
echo "  or use GitHub Actions UI"
