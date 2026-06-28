"""Add prediction_metrics table for forecast accuracy tracking.

Revision ID: a3c448b4e9db
Revises: 0002
Create Date: 2026-06-05 11:37:57.536922

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a3c448b4e9db"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prediction_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker_id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_close", sa.Float(), nullable=False),
        sa.Column("predicted_close", sa.Float(), nullable=False),
        sa.Column("absolute_error", sa.Float(), nullable=False),
        sa.Column("percentage_error", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ticker_id"],
            ["tickers.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ticker_id",
            "model_name",
            "date",
            name="uix_prediction_metrics_ticker_model_date",
        ),
    )
    op.create_index(
        "ix_prediction_metrics_ticker_date",
        "prediction_metrics",
        ["ticker_id", "date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_prediction_metrics_ticker_date", table_name="prediction_metrics")
    op.drop_table("prediction_metrics")
