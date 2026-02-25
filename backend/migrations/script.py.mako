"""Revision ID: initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

Initial migration - creates checkpoint tables
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial tables"""
    # Note: These tables are typically created by LangGraph
    # This migration is for reference only
    pass


def downgrade() -> None:
    """Drop tables"""
    pass
