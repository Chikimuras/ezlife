"""add_webauthn_credentials_table

Revision ID: d8f1a2b3c4e5
Revises: f497885fdb89
Create Date: 2026-05-22 12:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "d8f1a2b3c4e5"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "webauthn_credentials",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("credential_id", sa.LargeBinary(), nullable=False),
        sa.Column("public_key", sa.LargeBinary(), nullable=False),
        sa.Column("sign_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "transports",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("device_name", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_webauthn_credentials_id"),
        "webauthn_credentials",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_webauthn_credentials_user_id"),
        "webauthn_credentials",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_webauthn_credentials_credential_id"),
        "webauthn_credentials",
        ["credential_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_webauthn_credentials_credential_id"),
        table_name="webauthn_credentials",
    )
    op.drop_index(
        op.f("ix_webauthn_credentials_user_id"),
        table_name="webauthn_credentials",
    )
    op.drop_index(
        op.f("ix_webauthn_credentials_id"),
        table_name="webauthn_credentials",
    )
    op.drop_table("webauthn_credentials")
