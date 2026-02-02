"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-29
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'items',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('source_id', sa.String(255), nullable=False),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('url', sa.Text, nullable=True),
        sa.Column('text', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )


def downgrade():
    op.drop_table('items')
