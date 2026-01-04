# migrations/versions/<rev>_update_check_for_stakeholders_tipo_rel.py
from alembic import op
import sqlalchemy as sa

# preencha com os ids corretos
revision = "20260103_ck_fix"
down_revision = "dfd019ff6eb3"
branch_labels = None
depends_on = None

def upgrade():
    # Em SQLite, usar batch_alter_table recria a tabela de forma segura
    with op.batch_alter_table('stakeholders', schema=None) as batch_op:
        # Remove a CHECK anterior
        batch_op.drop_constraint('ck_stakeholders_tipo_rel', type_='check')
        # Cria a nova CHECK com a regra atualizada:
        # - INTERNO: exige position_id
        # - EXTERNO: exige client_id
        # - (não proíbe o outro campo)
        batch_op.create_check_constraint(
            'ck_stakeholders_tipo_rel',
            "((tipo = 'INTERNO' AND position_id IS NOT NULL) OR "
            "(tipo = 'EXTERNO' AND client_id IS NOT NULL))"
        )

def downgrade():
    with op.batch_alter_table('stakeholders', schema=None) as batch_op:
        batch_op.drop_constraint('ck_stakeholders_tipo_rel', type_='check')
        # Regra antiga (se quiser reverter): geralmente proibia o outro campo
        batch_op.create_check_constraint(
            'ck_stakeholders_tipo_rel',
            "((tipo = 'INTERNO' AND position_id IS NOT NULL AND client_id IS NULL) OR "
            "(tipo = 'EXTERNO' AND client_id IS NOT NULL AND position_id IS NULL))"
        )
