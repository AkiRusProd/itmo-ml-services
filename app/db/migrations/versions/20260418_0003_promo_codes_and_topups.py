"""Add promo codes and activations

Revision ID: 20260418_0003
Revises: 20260418_0002
Create Date: 2026-04-18 19:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260418_0003"
down_revision = "20260418_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "promo_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("credit_amount", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("max_activations", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("activation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_promo_codes_id", "promo_codes", ["id"])
    op.create_index("ix_promo_codes_code", "promo_codes", ["code"], unique=True)

    op.create_table(
        "promo_code_activations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("promo_code_id", sa.Integer(), sa.ForeignKey("promo_codes.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("promo_code_id", "user_id", name="uq_promo_code_activations_promo_user"),
    )
    op.create_index("ix_promo_code_activations_id", "promo_code_activations", ["id"])
    op.create_index("ix_promo_code_activations_promo_code_id", "promo_code_activations", ["promo_code_id"])
    op.create_index("ix_promo_code_activations_user_id", "promo_code_activations", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_promo_code_activations_user_id", table_name="promo_code_activations")
    op.drop_index("ix_promo_code_activations_promo_code_id", table_name="promo_code_activations")
    op.drop_index("ix_promo_code_activations_id", table_name="promo_code_activations")
    op.drop_table("promo_code_activations")
    op.drop_index("ix_promo_codes_code", table_name="promo_codes")
    op.drop_index("ix_promo_codes_id", table_name="promo_codes")
    op.drop_table("promo_codes")
