"""Store revoked access tokens.

Revision ID: 8dbe0c31a923
Revises: 44791ec6011f
Create Date: 2026-11-17 18:02:00
"""
from alembic import op
import sqlalchemy as sa


revision = "8dbe0c31a923"
down_revision = "44791ec6011f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "revoked_tokens",
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("jti"),
    )
    op.create_index("ix_revoked_tokens_expires_at", "revoked_tokens", ["expires_at"])


def downgrade():
    op.drop_index("ix_revoked_tokens_expires_at", table_name="revoked_tokens")
    op.drop_table("revoked_tokens")
