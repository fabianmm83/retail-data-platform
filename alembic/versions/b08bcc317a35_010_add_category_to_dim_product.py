"""010 add category to dim_product

Revision ID: b08bcc317a35
Revises: 581f5d76a9b8
Create Date: 2026-10-23 00:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b08bcc317a35'
down_revision: Union[str, Sequence[str], None] = '581f5d76a9b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega category_code y category_name a dim_product.

    Estrategia en 3 pasos:
    1. Agregar columnas como nullable.
    2. Rellenar con los valores actuales (JOIN con staging.categories).
    3. Hacer NOT NULL.
    """

    # Paso 1: agregar columnas nullable
    op.add_column(
        'dim_product',
        sa.Column(
            'category_code',
            sa.String(length=20),
            nullable=True,
            comment='Código de categoría (PLAYERAS, TENIS, ...)',
        ),
        schema='analytical',
    )
    op.add_column(
        'dim_product',
        sa.Column(
            'category_name',
            sa.String(length=100),
            nullable=True,
        ),
        schema='analytical',
    )

    # Paso 2: rellenar con JOIN a staging
    op.execute(
        """
        UPDATE analytical.dim_product dp
        SET
            category_code = c.code,
            category_name = c.name
        FROM staging.products p
        INNER JOIN staging.categories c ON c.id = p.category_id
        WHERE dp.product_id = p.id
        """
    )

    # Paso 3: hacer NOT NULL
    op.alter_column(
        'dim_product',
        'category_code',
        nullable=False,
        schema='analytical',
    )
    op.alter_column(
        'dim_product',
        'category_name',
        nullable=False,
        schema='analytical',
    )

    # Índice
    op.create_index(
        'ix_dim_product_category',
        'dim_product',
        ['category_code'],
        unique=False,
        schema='analytical',
    )


def downgrade() -> None:
    """Revierte los cambios."""
    op.drop_index('ix_dim_product_category', table_name='dim_product', schema='analytical')
    op.drop_column('dim_product', 'category_name', schema='analytical')
    op.drop_column('dim_product', 'category_code', schema='analytical')