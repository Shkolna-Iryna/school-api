"""add voice_url to tasks

Revision ID: ghi456jkl789
Revises: previous_revision_id
Create Date: 2026-03-07 12:50:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ghi456jkl789'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    # Додавання поля voice_url у tasks
    op.add_column('tasks', sa.Column('voice_url', sa.String(), nullable=True))

def downgrade():
    # Видалення поля voice_url у tasks
    op.drop_column('tasks', 'voice_url')