"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-24 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "Users",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, nullable=False),
        sa.Column("username", sa.String(length=150),
                  nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
    )

    op.create_table(
        "TodoLists",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("Users.id"), nullable=False),
    )

    op.create_table(
        "TodoTasks",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("todo_list_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("TodoLists.id"), nullable=False),
    )

    op.create_table(
        "Posts",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("todo_list_as_json", sa.Text(), nullable=False),
        sa.Column("likes_count", sa.BigInteger(),
                  nullable=False, server_default="0"),
    )

    op.create_table(
        "PostComments",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, nullable=False),
        sa.Column("comment_text", sa.Text(), nullable=False),
        sa.Column("likes_count", sa.BigInteger(),
                  nullable=False, server_default="0"),
        sa.Column("post_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("Posts.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("Users.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("PostComments")
    op.drop_table("Posts")
    op.drop_table("TodoTasks")
    op.drop_table("TodoLists")
    op.drop_table("Users")
