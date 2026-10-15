"""CLI del pipeline.

Uso:

    python -m app.pipeline --entities all
    python -m app.pipeline --entities orders
    python -m app.pipeline --entities orders,order_items
    python -m app.pipeline --entities customers
"""

import argparse
import logging
import sys

from app.db.session import SourceSessionLocal, TargetSessionLocal
from app.pipeline.runner import run_pipeline


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retail data platform pipeline runner.",
    )
    parser.add_argument(
        "--entities",
        type=str,
        default="all",
        help=(
            "Entidades a procesar, separadas por coma. "
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

    entities = [e.strip() for e in args.entities.split(",")]

    print("=" * 70)
    print("Retail Data Platform — Pipeline")
    print("=" * 70)
    print(f"Entidades: {entities}")
    print("=" * 70)

    with SourceSessionLocal() as source_db, TargetSessionLocal() as target_db:
        try:
            run_id = run_pipeline(
                source_db=source_db,
                target_db=target_db,
                entities=entities,
            )
        except Exception as exc:
            print(f"\n✗ Pipeline falló: {exc}")
            sys.exit(1)

    print()
    print("=" * 70)
    print(f"Run completado: {run_id}")
    print("=" * 70)


if __name__ == "__main__":
    main()