"""add role to users

Revision ID: add_role_to_users_001
Revises: 9627256df3cf
Create Date: 2026-03-08 15:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_role_to_users_001'
down_revision = '9627256df3cf'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column(
            'role',
            sa.String(length=20),
            nullable=False,
            server_default='student'
        )
    )
    op.execute("UPDATE users SET role = 'student' WHERE role IS NULL")


def downgrade():
    op.drop_column('users', 'role')