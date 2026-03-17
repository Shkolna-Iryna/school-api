"""add voice_url to answers

Revision ID: add_voice_url_to_answers_002
Revises: add_role_to_users_001
Create Date: 2026-03-15 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_voice_url_to_answers_002'
down_revision = 'add_role_to_users_001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'answers',
        sa.Column('voice_url', sa.String(), nullable=True)
    )


def downgrade():
    op.drop_column('answers', 'voice_url')