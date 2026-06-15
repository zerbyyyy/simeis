#!/usr/bin/env python3
"""
tests/propertybased.py
Tests basés sur les propriétés (TP3 - Partie 3)
"""

import sys
import time
import random
import math
import argparse # Ajouté pour gérer le paramètre de temps (--heavy)

def create_property_based_test(f, regressions=[], time_test=10):
    tstart = time.time()
    i = 0
    while (time.time() - tstart) < time_test:
        if i < len(regressions):
            seed = regressions[i]
        else:
            seed = random.randrange(0, 2**64)
        random.seed(seed)
        try:
            f()
            # On print moins souvent pour ne pas flood la CI en mode lourd
            if i % 1000 == 0:
                print(f"Test {f.__name__} {i} OK (running...)")
        except AssertionError as err:
            print(f"\n[FAILURE] Test {f.__name__} failed with seed {seed}")
            print(err)
            sys.exit(1)
        i += 1
    print(f"[SUCCESS] Test {f.__name__} validé après {i} itérations.\n")

### Fonctions métier et Tests de propriétés

def get_dist(a, b):
    return math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))

def addition():
    # 1. Génération de deux nombres aléatoires
    a = random.randrange(-10000, 10000)
    b = random.randrange(-10000, 10000)

    # Propriété A : Commutativité (A + B doit être égal à B + A)
    assert a + b == b + a, f"Échec commutativité : {a} + {b} != {b} + {a}"
    
    # Propriété B : Élément neutre (A + 0 doit être égal à A)
    assert a + 0 == a, f"Échec élément neutre : {a} + 0 != {a}"

def distance():
    x1 = random.randrange(-100, 100)
    y1 = random.randrange(-100, 100)
    z1 = random.randrange(-100, 100)
    a = (x1, y1, z1) 

    x2 = random.randrange(-100, 100)
    y2 = random.randrange(-100, 100)
    z2 = random.randrange(-100, 100)
    b = (x2, y2, z2) 

    # Calcul des distances dans les deux sens
    d_ab = get_dist(a, b)
    d_ba = get_dist(b, a)

    # Propriété A : Symétrie (La distance de A à B est la même que de B à A)
    assert d_ab == d_ba, f"Échec de la symétrie : {d_ab} != {d_ba}"
    
    # Propriété B : Positivité (Une distance est toujours supérieure ou égale à zéro)
    assert d_ab >= 0, f"La distance ne peut pas être négative : {d_ab}"

    # 💡 Note sur le SEED 4480881574280375424 :
    # Sans changer le code de génération de nombres aléatoires de l'énoncé, 
    # ce seed force le générateur à choisir exactement le même point pour A et B (A == B).
    # Si un développeur écrit par erreur `assert d_ab > 0` (strictement positif), 
    # ce cas limite fait crasher le test car la distance entre deux points identiques est de 0.0 !
    if a == b:
        assert d_ab == 0.0, f"Points identiques mais distance non nulle : {d_ab}"


if __name__ == "__main__":
    # Partie 3.3 : Ajout d'un paramètre au script pour tester beaucoup plus longtemps
    parser = argparse.ArgumentParser(description="Property-based testing pour Simeis.")
    parser.add_argument("--heavy", action="store_true", help="Exécute les tests en version lourde (CI de release)")
    args = parser.parse_args()

    # Définition des temps de test (Rapide en PR vs Long en Release)
    if args.heavy:
        print("=== Mode LOURD activé (Pre-release) ===")
        duration_addition = 15  # 15 secondes d'additions intensives
        duration_distance = 30  # 30 secondes de distances intensives
    else:
        print("=== Mode RAPIDE activé (Vérification PR) ===")
        duration_addition = 2
        duration_distance = 4

    # Lancement des tests
    create_property_based_test(addition, time_test=duration_addition)
    create_property_based_test(distance, regressions=[4480881574280375424], time_test=duration_distance)