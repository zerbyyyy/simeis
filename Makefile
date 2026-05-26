# --- CONFIGURATION DIRECTE ---
export RUSTFLAGS = -C codegen-units=1 -C code-model=kernel

# --- CIBLES ---

all: build optimize

# Build standard
build:
	cargo build --verbose

# Build de production (utilisé par la CI)
release:
	cargo build --release --verbose
	strip target/release/simeis-server

# Optimisation
optimize:
	strip target/debug/simeis-server

# Documentation
doc:
	typst compile doc/manual.typ manuel.pdf

# Checks
check:
	cargo check

test:
	cargo test

# Tests fonctionnels lourds
functional-tests: release
	@echo "Running functional tests..."
	python tests/functional_tests.py

# Valider la configuration des tests
validate-tests:
	bash tests/validate_tests.sh

# Nettoyage
clean:
	cargo clean
	rm -f manuel.pdf

.PHONY: all build release optimize doc check test functional-tests validate-tests clean