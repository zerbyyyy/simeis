# Documentation CI/CD du projet Simeis

Ce document décrit l'intégration continue et le déploiement continu mis en place pour le projet **Simeis**. Il couvre le pipeline GitHub Actions, les cibles `Makefile`, les tests fonctionnels et les choix de résilience réseau.

---

## 1. Vue d'ensemble du pipeline CI/CD

Le pipeline principal est défini dans :

- `.github/workflows/ci.yml`

Il contient :

- l'intégration continue pour les pull requests,
- la validation de la qualité du code,
- la mesure de la couverture,
- la compilation de release et la génération de documentation sur `main`.

---

## 2. Déclencheurs GitHub Actions

Le workflow se déclenche sur :

- `pull_request` vers `main` ou `release/*`
- `pull_request_target` vers `main`
- `push` sur `main`

### Pourquoi ces déclencheurs ?

- `pull_request` exécute la CI sur toute proposition de modification.
- `pull_request_target` permet au workflow de s'exécuter dans le contexte de la branche cible (`main`) pour des actions qui modifient la PR.
- `push` sur `main` lance la phase de build production et la génération de documentation.

---

## 3. Résilience réseau et configuration Cargo globale

Le workflow définit des variables d'environnement globales pour améliorer la robustesse :

- `CARGO_TERM_COLOR: always`
  - Force l'affichage coloré de Cargo en CI.
- `CARGO_INCREMENTAL: "0"`
  - Désactive la compilation incrémentale pour éviter des artefacts de cache inutiles.
- `CARGO_NET_RETRY: "10"`
  - Relance plusieurs fois les téléchargements en cas d'échec réseau.
- `CARGO_NET_GIT_FETCH_WITH_CLI: "true"`
  - Utilise le client Git natif, plus stable sur la CI.
- `CARGO_HTTP_MULTIPLEXING: "false"`
  - Désactive HTTP/2 multiplexé pour éviter les erreurs de framing sur crates.io.

Ces paramètres rendent le pipeline plus fiable sur GitHub Actions.

---

## 4. Concurrency et annulation de builds

Le workflow utilise la stratégie suivante :

- `group: ${{ github.workflow }}-${{ github.head_ref || github.run_id }}`
- `cancel-in-progress: true`

Ainsi, si plusieurs commits arrivent sur la même PR ou branche, GitHub annule automatiquement l'ancienne exécution pour ne conserver que la plus récente.

---

## 5. Permissions du workflow

Les permissions demandées sont :

- `pull-requests: write`
- `contents: read`

Cela permet au job `coverage` d'ajouter un label à la PR via `gh pr edit` lorsqu'il détecte une couverture insuffisante.

---

## 6. Jobs du pipeline CI

### 6.1 Job `lint`

Condition : `pull_request` ou `pull_request_target`

Objectif : vérifier le style Python et le format Rust.

Étapes :

- `actions/checkout@v4`
- `pip install ruff --break-system-packages`
- `ruff check .`
- `cargo fmt --check`

### 6.2 Job `test`

Condition : `pull_request`

Objectif : exécuter les tests Rust et Python.

Étapes :

- `actions/checkout@v4`
- Installer `sccache` précompilé
- Définir `RUSTC_WRAPPER=sccache`
- `make test`
- `python3 tests/propertybased.py`
- `sccache --show-stats`

### 6.3 Job `build_dev`

Condition : `pull_request`

Objectif : compiler le projet en mode développement.

Étapes :

- `actions/checkout@v4`
- Installer `sccache`
- `make build`
- `sccache --show-stats`

### 6.4 Job `quality`

Condition : `pull_request`

Objectif : vérifier le code Rust avec Clippy.

Étapes :

- `actions/checkout@v4`
- `cargo clippy -- -D warnings`

### 6.5 Job `coverage`

Condition : `pull_request`

Objectif : mesurer la couverture de code et ajouter un label si elle est insuffisante.

Étapes :

- `actions/checkout@v4`
- `actions-rs/cargo@v1` pour installer `cargo-tarpaulin`
- `cargo tarpaulin --out stdout > coverage_report.txt`
- Extraction du pourcentage de couverture
- Ajout du label `not enough tests` si la couverture entière est inférieure à 50%

---

## 7. Job de production / CD

### Job `release_and_doc`

Condition : `push` sur `main`

Objectif : compiler la release et générer la documentation.

Étapes :

- `actions/checkout@v4`
- Installer `typst`
- `make release`
- `make doc`

Ce job est exécuté uniquement lors d'un push direct sur `main` et non sur les PRs.

---

## 8. Makefile et cibles de build

Le `Makefile` centralise les commandes de build et de documentation.

### Cibles principales

- `make build`
  - `cargo build --verbose`
  - Build de développement.
- `make release`
  - `cargo build --release --verbose`
  - `strip target/release/simeis-server`
  - Build de production.
- `make optimize`
  - `strip target/debug/simeis-server`
- `make doc`
  - `typst compile doc/manual.typ manuel.pdf`
- `make check`
  - `cargo check`
- `make test`
  - `cargo test`
- `make clean`
  - `cargo clean`
  - `rm -f manuel.pdf`

### Pourquoi `make release` est important

Le binaire produit par `make release` est celui utilisé en production. La commande `strip` supprime les symboles de débogage pour réduire la taille du binaire.

---

## 9. Tests fonctionnels

Le script de tests fonctionnels principal est :

- `tests/functional_tests.py`

Il effectue un test end-to-end sur l'API :

- démarre le serveur `simeis-server`
- vérifie la création de joueur
- achète un vaisseau
- achète un module
- valide que le solde baisse correctement
- teste la navigation spatiale
- vérifie la gestion d'erreurs sur une transaction invalide

### Points clés du script

- Il utilise `urllib` pour faire des requêtes HTTP simples.
- Il démarre le serveur localement avec `subprocess.Popen`.
- Il attend que `/ping` soit disponible avant de lancer les scénarios.
- Il arrête proprement le serveur à la fin.

---

## 10. Recommandations pour l'exécution locale

Pour reproduire le pipeline localement :

- `make test`
- `make build`
- `make release`
- `make doc`
- `python3 tests/functional_tests.py`

Pour vérifier uniquement le style :

- `ruff check .`
- `cargo fmt --check`
- `cargo clippy -- -D warnings`

---

## 11. Conclusion

La CI/CD du projet Simeis couvre :

- lint Python et format Rust,
- tests unitaires et property-based,
- build de développement,
- qualité Clippy,
- mesure de couverture et signalement des PRs trop faibles,
- build de production et génération de documentation sur `main`.

Cette organisation assure une livraison fiable et reproductible pour le projet.
