"""drop global_constraints table

Revision ID: f497885fdb89
Revises: 5b37f0a8237b
Create Date: 2026-02-20 21:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f497885fdb89"
down_revision: str | None = "5b37f0a8237b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(
        op.f("ix_global_constraints_user_id"), table_name="global_constraints"
    )
    op.drop_table("global_constraints")


def downgrade() -> None:
    op.create_table(
        "global_constraints",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "total_weekly_hours",
            sa.Float(),
            nullable=False,
            server_default=sa.text("168.0"),
        ),
        sa.Column(
            "min_sleep_hours",
            sa.Float(),
            nullable=False,
            server_default=sa.text("7.0"),
        ),
        sa.Column(
            "overutilization_threshold",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0.9"),
        ),
        sa.Column(
            "underutilization_threshold",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0.5"),
        ),
        sa.Column(
            "wasted_time_threshold",
            sa.Float(),
            nullable=False,
            server_default=sa.text("2.0"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="global_constraints_user_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_global_constraints_user_id"),
        "global_constraints",
        ["user_id"],
        unique=True,
    )
