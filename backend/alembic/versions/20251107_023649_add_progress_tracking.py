"""Add progress tracking to jobs table

Revision ID: 20251107_023649
Revises: 
Create Date: 2025-11-07 02:36:49

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251107_023649'
down_revision = None  # Update this if you have previous migrations
branch_labels = None
depends_on = None


def upgrade():
    """Add progress and current_step columns to jobs table."""
    # Add progress column (percentage 0-100)
    op.add_column('jobs', sa.Column('progress', sa.Integer(), nullable=False, server_default='0'))
    
    # Add current_step column (description of current processing step)
    op.add_column('jobs', sa.Column('current_step', sa.String(length=255), nullable=True))
    
    # Remove server_default after adding the column (so new rows use Python default)
    op.alter_column('jobs', 'progress', server_default=None)


def downgrade():
    """Remove progress tracking columns."""
    op.drop_column('jobs', 'current_step')
    op.drop_column('jobs', 'progress')


