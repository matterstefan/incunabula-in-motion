"""Build all Swiss holdings from the reviewed local snapshot (no network)."""
from build_zurich_map import main
if __name__ == "__main__":
    main(swiss=True)
