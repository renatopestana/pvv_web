"""add status_id to project

Revision ID: 37e291d5372a
Revises: xxxx_add_tipos_cadastro_to_status
Create Date: 2025-09-03 19:44:15.881806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37e291d5372a'
down_revision = 'xxxx_add_tipos_cadastro_to_status'
branch_labels = None
depends_on = None


def upgrade():
    # Se a sua tabela for 'project' (singular), troque 'projects' por 'project'
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status_id', sa.Integer(), nullable=True))

        # Nome explícito para o índice
        batch_op.create_index('ix_projects_status_id', ['status_id'], unique=False)

        # Nome explícito para a FK (e ajuste o segundo argumento para 'status' ou 'statuses')
        batch_op.create_foreign_key(
            'fk_projects_status',
            'statuses',
            ['status_id'],
            ['id'],
            ondelete='SET NULL',
        )

def downgrade():
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_constraint('fk_projects_status', type_='foreignkey')
        batch_op.drop_index('ix_projects_status_id')
        batch_op.drop_column('status_id')