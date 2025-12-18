"""add functional areas, positions and stakeholders
Revision ID: 6429a2e6ab9a
Revises: 37e291d5372a
Create Date: 2025-09-06 12:26:52.613382
"""
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
revision = '6429a2e6ab9a'
down_revision = '37e291d5372a'
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return insp.has_table(name)


def upgrade():
    # --- functional_areas ----------------------------------------------------
    if not _has_table('functional_areas'):
        op.create_table(
            'functional_areas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=120), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    # --- positions -----------------------------------------------------------
    if not _has_table('positions'):
        op.create_table(
            'positions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=120), nullable=False),
            sa.Column('functional_area_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['functional_area_id'], ['functional_areas.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name', 'functional_area_id', name='uq_positions_name_area')
        )

    # --- stakeholders --------------------------------------------------------
    if not _has_table('stakeholders'):
        op.create_table(
            'stakeholders',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=150), nullable=False),
            sa.Column('tipo', sa.Enum('INTERNO', 'EXTERNO', name='tipo_stakeholder'), nullable=False),
            sa.Column('client_id', sa.Integer(), nullable=True),
            sa.Column('position_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.CheckConstraint(
                "(tipo = 'INTERNO' AND position_id IS NOT NULL AND client_id IS NULL) "
                "OR (tipo = 'EXTERNO' AND client_id IS NOT NULL AND position_id IS NULL)",
                name='ck_stakeholders_tipo_rel'
            ),
            sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )

    # --- projects: FK nomeada ------------------------------------------------
    with op.batch_alter_table('projects', schema=None) as batch_op:
        # esses dois podem falhar dependendo do estado anterior; ignore se não existirem
        try:
            batch_op.drop_index(batch_op.f('ix_projects_status_id'))
        except Exception:
            pass
        try:
            batch_op.drop_constraint(batch_op.f('fk_projects_status'), type_='foreignkey')
        except Exception:
            pass

        # cria FK com NOME explícito (obrigatório em SQLite batch mode)
        batch_op.create_foreign_key(
            'fk_projects_status_id_statuses',
            'statuses',
            ['status_id'],
            ['id']
        )

    # --- statuses: widen cols + UQ nomeada ----------------------------------
    with op.batch_alter_table('statuses', schema=None) as batch_op:
        batch_op.alter_column(
            'nome',
            existing_type=sa.VARCHAR(length=80),
            type_=sa.String(length=180),
            existing_nullable=False
        )
        batch_op.alter_column(
            'codigo',
            existing_type=sa.VARCHAR(length=50),
            type_=sa.String(length=180),
            nullable=False
        )
        batch_op.alter_column(
            'descricao',
            existing_type=sa.VARCHAR(length=300),
            type_=sa.Text(),
            existing_nullable=True
        )
        batch_op.alter_column(
            'tipos_cadastro',
            existing_type=sa.VARCHAR(length=64),
            type_=sa.String(length=255),
            existing_nullable=True,
            existing_server_default=sa.text("('')")
        )
        # drop index se existir
        try:
            batch_op.drop_index(batch_op.f('ix_statuses_codigo'))
        except Exception:
            pass
        # cria unique constraint com NOME explícito
        # (se já existir, ignore o erro)
        try:
            batch_op.create_unique_constraint('uq_statuses_codigo', ['codigo'])
        except Exception:
            pass


def downgrade():
    # desfaz alterações em 'statuses'
    with op.batch_alter_table('statuses', schema=None) as batch_op:
        # remove UQ se existir
        try:
            batch_op.drop_constraint('uq_statuses_codigo', type_='unique')
        except Exception:
            pass
        # recria o índice simples
        try:
            batch_op.create_index(batch_op.f('ix_statuses_codigo'), ['codigo'], unique=1)
        except Exception:
            pass
        batch_op.alter_column(
            'tipos_cadastro',
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=64),
            existing_nullable=True,
            existing_server_default=sa.text("('')")
        )
        batch_op.alter_column(
            'descricao',
            existing_type=sa.Text(),
            type_=sa.VARCHAR(length=300),
            existing_nullable=True
        )
        batch_op.alter_column(
            'codigo',
            existing_type=sa.String(length=180),
            type_=sa.VARCHAR(length=50),
            nullable=True
        )
        batch_op.alter_column(
            'nome',
            existing_type=sa.String(length=180),
            type_=sa.VARCHAR(length=80),
            existing_nullable=False
        )

    # desfaz alterações em 'projects'
    with op.batch_alter_table('projects', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('fk_projects_status_id_statuses', type_='foreignkey')
        except Exception:
            pass
        try:
            batch_op.create_foreign_key(
                batch_op.f('fk_projects_status'),
                'statuses',
                ['status_id'],
                ['id'],
                ondelete='SET NULL'
            )
        except Exception:
            pass
        try:
            batch_op.create_index(batch_op.f('ix_projects_status_id'), ['status_id'], unique=False)
        except Exception:
            pass
    # drop tables (se existirem)
    if _has_table('stakeholders'):
        op.drop_table('stakeholders')
    if _has_table('positions'):
        op.drop_table('positions')
    if _has_table('functional_areas'):
        op.drop_table('functional_areas')
