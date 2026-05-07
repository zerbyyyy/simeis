#!/usr/bin/env python3
"""
tests/functional_tests.py
Squelette des tests fonctionnels automatiques.

Exécution :
    python tests/functional_tests.py

Le script doit retourner le code de sortie 0 pour que le workflow CI
considère les tests comme réussis (vérification implicite par GitHub Actions).

Conventions :
- Chaque cas de test est une fonction préfixée par `test_`.
- run_all_tests() appelle toutes les fonctions de test et agrège les résultats.
- En cas d'échec, le script se termine avec sys.exit(1).
"""

import subprocess
import sys
from pathlib import Path

# ─── Chemin vers le binaire compilé en debug ────────────────────────────────
# Adapter le nom du binaire selon le champ `name` de [package] dans Cargo.toml
BINARY = Path("target/debug/my_project")


# ─── Helpers ────────────────────────────────────────────────────────────────

def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Lance une commande et retourne le résultat."""
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def assert_exit_code(result: subprocess.CompletedProcess, expected: int = 0) -> None:
    """Lève une AssertionError si le code de retour ne correspond pas."""
    assert result.returncode == expected, (
        f"Code de sortie attendu : {expected}, obtenu : {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ─── Tests fonctionnels ─────────────────────────────────────────────────────

def test_binary_exists() -> None:
    """Vérifie que le binaire debug a bien été compilé."""
    assert BINARY.exists(), f"Binaire introuvable : {BINARY}"


def test_placeholder() -> None:
    """Test fonctionnel à compléter — retourne toujours succès pour l'instant."""
    # TODO remplacer par un vrai scénario fonctionnel
    pass


# ─── Runner ─────────────────────────────────────────────────────────────────

def run_all_tests() -> int:
    """Exécute tous les tests et retourne le nombre d'échecs."""
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failures = 0

    for test in tests:
        try:
            test()
            print(f"  ✓  {test.__name__}")
        except Exception as exc:
            print(f"  ✗  {test.__name__} : {exc}")
            failures += 1

    return failures


if __name__ == "__main__":
    print("=== Tests fonctionnels ===")
    nb_failures = run_all_tests()
    print(f"\n{'OK' if nb_failures == 0 else 'ÉCHEC'} — {nb_failures} échec(s)")
    sys.exit(0 if nb_failures == 0 else 1)
