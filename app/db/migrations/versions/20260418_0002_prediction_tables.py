"""Add prediction tables

Revision ID: 20260418_0002
Revises: 20260418_0001
Create Date: 2026-04-18 18:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260418_0002"
down_revision = "20260418_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prediction_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("cost_credits", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("task_id", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prediction_requests_id", "prediction_requests", ["id"])
    op.create_index("ix_prediction_requests_user_id", "prediction_requests", ["user_id"])
    op.create_index("ix_prediction_requests_task_id", "prediction_requests", ["task_id"])

    op.create_table(
        "prediction_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("prediction_request_id", sa.Integer(), sa.ForeignKey("prediction_requests.id"), nullable=False),
        sa.Column("prediction_value", sa.Float(), nullable=False),
        sa.Column("target_name", sa.String(length=100), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False, server_default="v1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prediction_results_id", "prediction_results", ["id"])
    op.create_index(
        "ix_prediction_results_prediction_request_id",
        "prediction_results",
        ["prediction_request_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_prediction_results_prediction_request_id", table_name="prediction_results")
    op.drop_index("ix_prediction_results_id", table_name="prediction_results")
    op.drop_table("prediction_results")
    op.drop_index("ix_prediction_requests_task_id", table_name="prediction_requests")
    op.drop_index("ix_prediction_requests_user_id", table_name="prediction_requests")
    op.drop_index("ix_prediction_requests_id", table_name="prediction_requests")
    op.drop_table("prediction_requests")
