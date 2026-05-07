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
	typst compile doc/manuel.typ manuel.pdf

# Checks
check:
	cargo check

test:
	cargo test

# Nettoyage
clean:
	cargo clean
	rm -f manuel.pdf

.PHONY: all build release optimize doc check test clean