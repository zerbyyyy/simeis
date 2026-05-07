import sys
import time
import random
import math  # Déplacé en haut pour corriger E402

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
            print("Test", f.__name__, i, "OK")
        except AssertionError as err:
            print("Test", f.__name__, "failed with seed", seed)
            print(err)
            sys.exit(1)
        i += 1

### Example

def get_dist(a, b):
    return math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))

def addition():
    # Utilisation de _ pour les variables inutilisées afin de corriger F841
    _ = random.randrange(0, 10000)
    _ = random.randrange(0, 10000)
    _ = random.randrange(0, 10000)

    # Exercice: Tester les additions (ton code de test viendra ici)

def distance():
    x1 = random.randrange(-100, 100)
    y1 = random.randrange(-100, 100)
    z1 = random.randrange(-100, 100)
    _ = (x1, y1, z1) # Corrigé F841 (a n'était pas utilisé)

    x2 = random.randrange(-100, 100)
    y2 = random.randrange(-100, 100)
    z2 = random.randrange(-100, 100)
    _ = (x2, y2, z2) # Corrigé F841 (b n'était pas utilisé)

    # Exercice: Tester la distance entre le point A et le point B

if __name__ == "__main__":
    create_property_based_test(addition, time_test=3)
    create_property_based_test(distance, regressions=[4480881574280375424], time_test=10)