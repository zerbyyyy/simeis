#!/usr/bin/env python3
"""
tests/functional_tests.py
Tests fonctionnels automatiques pour le workspace Simeis.
"""

import subprocess
import sys
from pathlib import Path

# ─── Chemin vers le binaire compilé du workspace ───────────────────────────
BINARY = Path("target/debug/simeis-server")


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
    """Vérifie que le binaire simeis-server a bien été compilé."""
    assert BINARY.exists(), f"Binaire introuvable : {BINARY}. Lancez 'cargo build' d'abord."


def test_scenario_1_economy() -> None:
    """Scénario 1 : Création joueur -> Achat vaisseau -> Achat module."""
    # 1. Création du joueur
    # Ajuste les arguments ("player", "create", etc.) selon tes structures Rust
    res_player = run([str(BINARY), "player", "create", "Evan"])
    assert_exit_code(res_player, 0)
    assert "Evan" in res_player.stdout, "Le joueur n'a pas été créé correctement"
    
    # 2. Achat du vaisseau
    res_ship = run([str(BINARY), "player", "buy-ship", "Explorer"])
    assert_exit_code(res_ship, 0)
    assert "Succès" in res_ship.stdout or "réussi" in res_ship.stdout, "L'achat du vaisseau a échoué"
    
    # 3. Achat d'un module de minage
    res_module = run([str(BINARY), "player", "buy-module", "Miner"])
    assert_exit_code(res_module, 0)


def test_scenario_2_mechanics() -> None:
    """Scénario 2 : Deuxième mécanique (ex: Voyage ou Minage)."""
    # Remplace "travel" ou "mine" par une vraie commande de ton application
    res = run([str(BINARY), "ship", "travel", "Simeis-Alpha"])
    assert_exit_code(res, 0)


def test_scenario_3_errors() -> None:
    """Scénario 3 : Troisième mécanique - Test des limites économiques."""
    # Tenter d'acheter un objet trop cher pour forcer un refus propre
    res = run([str(BINARY), "player", "buy-ship", "DeathStar"])
    
    # On attend un code d'erreur ou un message "Fonds insuffisants"
    assert "insuffisants" in res.stdout or "insuffisants" in res.stderr, \
        "La transaction aurait dû être refusée pour manque de fonds"


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
    print("=== Tests fonctionnels (simeis-server) ===")
    nb_failures = run_all_tests()
    print(f"\n{'OK' if nb_failures == 0 else 'ÉCHEC'} — {nb_failures} échec(s)")
    sys.exit(0 if nb_failures == 0 else 1)