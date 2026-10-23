"""CLI del runner de STAGING.

Uso:

    python -m app.staging --entities all
    python -m app.staging --entities customers
    python -m app.staging --entities customers,orders
"""

import argparse
import logging
import sys

from app.db.session import TargetSessionLocal
from app.staging.runner import run_staging


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retail data platform — STAGING runner.",
    )
    parser.add_argument(
        "--entities",
        type=str,
        default="all",
        help=(
            "Entidades a transformar, separadas por coma. "
            "Ej: 'orders' o 'orders,order_items' o 'all'"
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
    print("Retail Data Platform — STAGING")
    print("=" * 70)
    print(f"Entidades: {entities or ['customers', 'orders', 'order_items']}")
    print("=" * 70)

    with TargetSessionLocal() as db:
        try:
            run_id = run_staging(db=db, entities=entities)
        except Exception as exc:
            print(f"\n✗ Staging falló: {exc}")
            sys.exit(1)

    print()
    print("=" * 70)
    print(f"Staging run completado: {run_id}")
    print("=" * 70)


if __name__ == "__main__":
    main()