"""001 create schemas

Revision ID: <hash>
Revises:
Create Date: <fecha>

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d3d7d8a42b5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SCHEMAS = ["raw", "staging", "analytical", "kpis", "dq", "meta"]


def upgrade() -> None:
    """Crea los 6 schemas del data platform."""
    for schema in SCHEMAS:
        op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")


def downgrade() -> None:
    """Elimina los 6 schemas."""
    for schema in reversed(SCHEMAS):
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")