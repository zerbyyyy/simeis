#!/usr/bin/env python3
"""
tests/propertybased.py
"""

import sys
import time
import random
import math
import argparse # Gère le paramètre de temps (--heavy)

def create_property_based_test(f, regressions=[], time_test=10):
    tstart = time.time()
    i = 0
    while (time.time() - tstart) < time_test:
        # Partie 3.1 & 3.3 : On injecte d'abord les seeds de régression connus, puis de l'aléatoire[cite: 5, 8]
        if i < len(regressions):
            seed = regressions[i]
        else:
            seed = random.randrange(0, 2**64)
            
        random.seed(seed)
        try:
            f()
            # Optimisation (TP4) : On affiche un log toutes les 50 000 itérations pour éviter le flood de la CI[cite: 11]
            if i % 50000 == 0 and i > 0:
                print(f"  -> Test {f.__name__} : {i} itérations validées...")
        except AssertionError as err:
            print(f"\n[FAILURE] Test {f.__name__} failed with seed {seed}")
            print(err)
            sys.exit(1)
        i += 1
    print(f"[SUCCESS] Test {f.__name__} validé avec succès après {i} itérations. ✅\n")

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

    # CORRECTION SÉCURITÉ : Utilisation de math.isclose() au lieu de '=='
    # Cela évite que les micro-variations d'arrondis des types flottants (norme IEEE 754) fassent crash la CI.
    assert math.isclose(d_ab, d_ba, rel_tol=1e-9), f"Échec de la symétrie : {d_ab} != {d_ba}"
    
    # Propriété B : Positivité (Une distance est toujours supérieure ou égale à zéro)
    assert d_ab >= 0, f"La distance ne peut pas être négative : {d_ab}"

    # 💡 Note sur le SEED 4480881574280375424 (Demandé au TP3.1) :
    # Ce seed force le générateur à choisir exactement le même point pour A et B (a == b).[cite: 8]
    # Si on écrivait 'assert d_ab > 0', ce cas limite provoquerait un échec car la distance vaut 0.0.[cite: 8]
    if a == b:
        assert math.isclose(d_ab, 0.0, abs_tol=1e-9), f"Points identiques mais distance non nulle : {d_ab}"


if __name__ == "__main__":
    # Partie 3.3 : Ajout d'un paramètre au script pour tester beaucoup plus longtemps[cite: 8]
    parser = argparse.ArgumentParser(description="Property-based testing pour Simeis.")
    parser.add_argument("--heavy", action="store_true", help="Exécute les tests en version lourde (CI de release)")
    args = parser.parse_args()

    # Définition des temps de test (Rapide en PR vs Long en Release / TP3.3 & TP4)
    if args.heavy:
        print("=== Mode LOURD activé (Pre-release) ===")
        duration_addition = 10  # En adéquation avec les contraintes du TP4[cite: 11]
        duration_distance = 15  
    else:
        print("=== Mode RAPIDE activé (Vérification PR) ===")
        duration_addition = 1
        duration_distance = 2

    # Lancement des tests
    print("Exécution du test d'addition...")
    create_property_based_test(addition, time_test=duration_addition)
    
    print("Exécution du test de distance géométrique...")
    create_property_based_test(distance, regressions=[4480881574280375424], time_test=duration_distance)