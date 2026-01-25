"""add is_admin to users

Revision ID: 0002_add_is_admin
Revises: 0001_initial
Create Date: 2026-01-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_add_is_admin"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("Users", sa.Column("is_admin", sa.Boolean(),
                  nullable=False, server_default=sa.text("false")))
    op.execute("UPDATE \"Users\" SET is_admin = true WHERE username = 'admin'")
    op.alter_column("Users", "is_admin", server_default=None)


def downgrade() -> None:
    op.drop_column("Users", "is_admin")
