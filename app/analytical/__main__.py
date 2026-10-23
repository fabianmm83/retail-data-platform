"""CLI del runner de ANALYTICAL.

Uso:

    python -m app.analytical --entities all
    python -m app.analytical --entities dim_state
    python -m app.analytical --entities dim_state,dim_customer
"""

import argparse
import logging
import sys

from app.analytical.runner import run_analytical
from app.analytical.transformers import TRANSFORM_ORDER
from app.db.session import TargetSessionLocal


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retail data platform — ANALYTICAL runner.",
    )
    parser.add_argument(
        "--entities",
        type=str,
        default="all",
        help=(
            "Entidades a transformar, separadas por coma. "
            "Ej: 'dim_state' o 'dim_state,dim_customer' o 'all'"
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Logging detallado",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.entities.lower() == "all":
        entities = None
    else:
        entities = [e.strip() for e in args.entities.split(",")]

    print("=" * 70)
    print("Retail Data Platform — ANALYTICAL")
    print("=" * 70)
    print(f"Entidades: {entities or TRANSFORM_ORDER}")
    print("=" * 70)

    with TargetSessionLocal() as db:
        try:
            run_id = run_analytical(db=db, entities=entities)
        except Exception as exc:
            print(f"\n✗ Analytical falló: {exc}")
            sys.exit(1)

    print()
    print("=" * 70)
    print(f"Analytical run completado: {run_id}")
    print("=" * 70)


if __name__ == "__main__":
    main()