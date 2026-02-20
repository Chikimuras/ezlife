"""migrate user id from integer to uuid

Revision ID: 4c5bbe1e33cb
Revises: 0b9e69fe990c
Create Date: 2026-01-26 09:07:17.783284

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4c5bbe1e33cb"
down_revision: str | Sequence[str] | None = "0b9e69fe990c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Step 1: Add new UUID columns with default values
    op.add_column(
        "users",
        sa.Column(
            "id_uuid",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
    )
    op.add_column("refresh_tokens", sa.Column("user_id_uuid", sa.UUID(), nullable=True))
    op.add_column("groups", sa.Column("user_id_uuid", sa.UUID(), nullable=True))
    op.add_column("categories", sa.Column("user_id_uuid", sa.UUID(), nullable=True))
    op.add_column(
        "global_constraints", sa.Column("user_id_uuid", sa.UUID(), nullable=True)
    )
    op.add_column("activities", sa.Column("user_id_uuid", sa.UUID(), nullable=True))

    # Step 2: Populate UUID columns with generated values
    # (for existing data - will be lost in dev)
    # In production, you'd want to preserve mappings. For dev, we're starting fresh.
    op.execute("UPDATE users SET id_uuid = uuid_generate_v4()")

    # Step 3: Drop foreign key constraints
    op.drop_constraint(
        "refresh_tokens_user_id_fkey", "refresh_tokens", type_="foreignkey"
    )
    op.drop_constraint("groups_user_id_fkey", "groups", type_="foreignkey")
    op.drop_constraint("categories_user_id_fkey", "categories", type_="foreignkey")
    op.drop_constraint(
        "global_constraints_user_id_fkey", "global_constraints", type_="foreignkey"
    )
    op.drop_constraint("activities_user_id_fkey", "activities", type_="foreignkey")

    # Step 4: Drop primary key constraint from users
    op.drop_constraint("users_pkey", "users", type_="primary")

    # Step 5: Drop old integer columns
    op.drop_column("users", "id")
    op.drop_column("refresh_tokens", "user_id")
    op.drop_column("groups", "user_id")
    op.drop_column("categories", "user_id")
    op.drop_column("global_constraints", "user_id")
    op.drop_column("activities", "user_id")

    # Step 6: Rename UUID columns to original names
    op.alter_column("users", "id_uuid", new_column_name="id")
    op.alter_column("refresh_tokens", "user_id_uuid", new_column_name="user_id")
    op.alter_column("groups", "user_id_uuid", new_column_name="user_id")
    op.alter_column("categories", "user_id_uuid", new_column_name="user_id")
    op.alter_column("global_constraints", "user_id_uuid", new_column_name="user_id")
    op.alter_column("activities", "user_id_uuid", new_column_name="user_id")

    # Step 7: Make user_id columns NOT NULL (except already set)
    op.alter_column("refresh_tokens", "user_id", nullable=False)
    op.alter_column("groups", "user_id", nullable=False)
    op.alter_column("categories", "user_id", nullable=False)
    op.alter_column("global_constraints", "user_id", nullable=False)
    op.alter_column("activities", "user_id", nullable=False)

    # Step 8: Recreate primary key and foreign keys
    op.create_primary_key("users_pkey", "users", ["id"])
    op.create_foreign_key(
        "refresh_tokens_user_id_fkey",
        "refresh_tokens",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "groups_user_id_fkey",
        "groups",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "categories_user_id_fkey",
        "categories",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "global_constraints_user_id_fkey",
        "global_constraints",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "activities_user_id_fkey",
        "activities",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema - WARNING: This will lose all user data."""
    # This is a destructive operation - downgrade not fully supported
    # You would need to recreate integer IDs which is not feasible
    raise NotImplementedError(
        "Downgrade from UUID to INTEGER is not supported. "
        "This would require regenerating integer IDs and is a destructive operation. "
        "If you need to rollback, restore from backup."
    )
