"""Add ml models table

Revision ID: 20260418_0004
Revises: 20260418_0003
Create Date: 2026-04-18 22:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260418_0004"
down_revision = "20260418_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ml_models",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("artifact_path", sa.String(length=255), nullable=False),
        sa.Column("target_name", sa.String(length=100), nullable=False),
        sa.Column("features_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ml_models_id", "ml_models", ["id"])


def downgrade() -> None:
    op.drop_index("ix_ml_models_id", table_name="ml_models")
    op.drop_table("ml_models")
