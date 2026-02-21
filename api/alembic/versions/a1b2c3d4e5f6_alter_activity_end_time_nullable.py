"""alter activity end_time nullable

Revision ID: a1b2c3d4e5f6
Revises: f497885fdb89
Create Date: 2026-02-21 09:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "f497885fdb89"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "activities",
        "end_time",
        existing_type=sa.Time(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "activities",
        "end_time",
        existing_type=sa.Time(),
        nullable=False,
    )
