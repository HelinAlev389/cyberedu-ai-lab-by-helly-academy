"""Add Lesson model

Revision ID: 89d7e2277279
Revises: d15ca02ea8c8
Create Date: 2025-06-24 14:15:19.279880

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '89d7e2277279'
down_revision = 'd15ca02ea8c8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ai_memory', schema=None) as batch_op:
        batch_op.add_column(sa.Column('session_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_aimemory_session_id',  # 🔧 добавено име
            'ai_session',
            ['session_id'],
            ['id']
        )

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('ai_memory', schema=None) as batch_op:
        batch_op.drop_constraint('fk_aimemory_session_id', type_='foreignkey')
        batch_op.drop_column('session_id')

    # ### end Alembic commands ###
