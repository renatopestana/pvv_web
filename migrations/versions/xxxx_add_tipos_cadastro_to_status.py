# migrations/versions/xxxx_add_tipos_cadastro_to_status.py
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "xxxx_add_tipos_cadastro_to_status"  # pode manter este id
down_revision = "2d305ec2ad41"  # << CORREÇÃO: aponta para a sua revisão inicial real
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Garante idempotência se alguém já adicionou a coluna manualmente
    cols = {c["name"] for c in insp.get_columns("statuses")}
    if "tipos_cadastro" not in cols:
        op.add_column(
            "statuses",
            sa.Column("tipos_cadastro", sa.String(length=64), nullable=True, server_default="")
        )
        # Em SQLite normalmente não removemos o server_default em seguida; se quiser, comente:
        # op.alter_column("statuses", "tipos_cadastro", server_default=None)


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("statuses")}
    if "tipos_cadastro" in cols:
        op.drop_column("statuses", "tipos_cadastro")