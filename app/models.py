# app/models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from .extensions import db
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


# ---------------------------
# Users
# ---------------------------
class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    cpf = db.Column(db.String(14), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(50), default="user")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


# ---------------------------
# Clients
# ---------------------------
class Client(TimestampMixin, db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(2), nullable=False)  # PF ou PJ
    org_id = db.Column(db.String(64), unique=False, index=True, nullable=True)

    # Comuns
    nome_razao = db.Column(db.String(180), nullable=False, index=True)
    endereco = db.Column(db.String(300), nullable=False)

    # PF
    nacionalidade = db.Column(db.String(80))
    estado_civil = db.Column(db.String(60))
    profissao = db.Column(db.String(120))
    rg = db.Column(db.String(30))
    orgao_emissor_rg = db.Column(db.String(50))
    cpf = db.Column(db.String(14))
    email = db.Column(db.String(255))
    telefone = db.Column(db.String(30))

    # PJ
    cnpj = db.Column(db.String(18))
    representante_nome = db.Column(db.String(180))
    representante_email = db.Column(db.String(255))
    representante_telefone = db.Column(db.String(30))
    representante_funcao = db.Column(db.String(120))

    __table_args__ = (
        # Garante valores válidos para tipo (útil inclusive no SQLite)
        db.CheckConstraint("tipo IN ('PF','PJ')", name="ck_clients_tipo"),
        # OBS: Unicidade condicional (cpf p/ PF, cnpj p/ PJ) só é plenamente suportada no Postgres
        # via partial unique indexes (configure em migração específica).
        # Em SQLite, faça validação na camada de aplicação.
    )
    
    # app/models.py (dentro de class Client)
    @property
    def name(self) -> str:
        """Alias somente-leitura para uso em templates/labels."""
        return self.nome_razao or ""

    def __repr__(self) -> str:
        return f"<Client id={self.id} tipo={self.tipo} nome={self.nome_razao!r}>"


# ---------------------------
# Dealers
# ---------------------------
class Dealer(TimestampMixin, db.Model):
    __tablename__ = "dealers"

    id = db.Column(db.Integer, primary_key=True)
    razao_social = db.Column(db.String(180), nullable=False)
    endereco = db.Column(db.String(300), nullable=False)
    cnpj = db.Column(db.String(18), nullable=False, unique=True)
    representante_nome = db.Column(db.String(180), nullable=False)
    representante_email = db.Column(db.String(255), nullable=False)
    representante_telefone = db.Column(db.String(30), nullable=False)
    representante_funcao = db.Column(db.String(120), nullable=False)

    def __repr__(self) -> str:
        return f"<Dealer id={self.id} razao_social={self.razao_social!r}>"


# ---------------------------
# Projects
# ---------------------------
class Project(TimestampMixin, db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), unique=True, nullable=False)
    description = db.Column(db.Text)
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"), nullable=True)
    status = db.relationship("Status", backref="projects")

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r}>"


# ---------------------------
# Statuses
# ---------------------------
# app/models.py (trecho do modelo Status)
# class Status(db.Model):
#     __tablename__ = "statuses"  # ajuste se seu nome for diferente

#     id = db.Column(db.Integer, primary_key=True)
#     nome = db.Column(db.String(80), nullable=False)
#     codigo = db.Column(db.String(50))          # se você tiver
#     cor = db.Column(db.String(7))              # se você tiver (#RRGGBB)
#     descricao = db.Column(db.String(300))      # se você tiver
#     ativo = db.Column(db.Boolean, default=True)

#     # NOVO: armazena as seleções como CSV (ex.: "equipamentos,projetos")
#     tipos_cadastro = db.Column(db.String(64), nullable=True, default="")

#     # (Opcional) helpers
#     @property
#     def tipos_lista(self) -> list[str]:
#         if not self.tipos_cadastro:
#             return []
#         return [v for v in self.tipos_cadastro.split(",") if v]

#     @tipos_lista.setter
#     def tipos_lista(self, values: list[str]):
#         self.tipos_cadastro = ",".join(sorted(set(values or [])))


# ---------------------------

class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Status(TimestampMixin, db.Model):
    __tablename__ = 'statuses'  # ajuste se for 'status'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(180), nullable=False)
    codigo = db.Column(db.String(180), nullable=False, unique=True)
    cor = db.Column(db.String(7), nullable=True)  # ex.: '#RRGGBB'
    descricao = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    # pode ser TEXT (csv) ou JSON/ARRAY dependendo do seu schema:
    tipos_cadastro = db.Column(db.String(255), nullable=True)  # ajuste conforme seu design


# ---------------------------
# Equipment
# ---------------------------
class Equipment(TimestampMixin, db.Model):
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)

    # Colunas mapeadas da planilha
    name = db.Column(db.String(180), nullable=False)  # Item
    pn = db.Column(db.String(80))                     # PN
    model_number = db.Column(db.String(120))          # Model Number / Model
    serial_number = db.Column(db.String(120))         # SN / Serial Number
    machine_installed = db.Column(db.String(180))     # Machine Installed
    image_ref = db.Column(db.String(255))             # Imagem de Referência

    # Extras úteis
    asset_tag = db.Column(db.String(80))              # espelha PN se desejar
    category = db.Column(db.String(120))              # opcional
    brand = db.Column(db.String(120))                 # opcional
    notes = db.Column(db.Text)                        # Obs

    # Associações
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    current_responsible_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id", ondelete="SET NULL"), nullable=True)  # <- corrigido

    owner = db.relationship("User", foreign_keys=[owner_id], lazy="selectin", passive_deletes=True)
    current_responsible = db.relationship("User", foreign_keys=[current_responsible_id], lazy="selectin", passive_deletes=True)
    location = db.relationship("Client", lazy="selectin", passive_deletes=True)
    project = db.relationship("Project", lazy="selectin", passive_deletes=True)
    status = db.relationship("Status", lazy="selectin", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<Equipment id={self.id} name={self.name!r} status_id={self.status_id}>"


# ============================
# Functional Areas
# ============================
class FunctionalArea(db.Model):
    __tablename__ = 'functional_areas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    positions = db.relationship(
        'Position',
        back_populates='functional_area',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<FunctionalArea {self.name}>'


# ============================
# Positions and Stakeholders
# ============================
class Position(db.Model):
    __tablename__ = 'positions'
    __table_args__ = (
        UniqueConstraint('name', 'functional_area_id', name='uq_positions_name_area'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    functional_area_id = db.Column(
        db.Integer,
        db.ForeignKey('functional_areas.id', ondelete='CASCADE'),
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    functional_area = db.relationship('FunctionalArea', back_populates='positions')
    stakeholders = db.relationship('Stakeholder', back_populates='position')

    def __repr__(self):
        return f'<Position {self.name}>'


# ============================
# Stakeholders
# ============================
class Stakeholder(db.Model):
    __tablename__ = 'stakeholders'
    __table_args__ = (
        CheckConstraint(
            "(tipo = 'INTERNO' AND position_id IS NOT NULL AND client_id IS NULL) "
            "OR (tipo = 'EXTERNO' AND client_id IS NOT NULL AND position_id IS NULL)",
            name='ck_stakeholders_tipo_rel'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.Enum('INTERNO', 'EXTERNO', name='tipo_stakeholder'), nullable=False)

    # Se EXTERNO -> client_id obrigatório; Se INTERNO -> position_id obrigatório
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='SET NULL'), nullable=True)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id', ondelete='SET NULL'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    client = db.relationship('Client', backref=db.backref('stakeholders', lazy='dynamic'))
    position = db.relationship('Position', back_populates='stakeholders')

    def __repr__(self):
        return f'<Stakeholder {self.name} ({self.tipo})>'

    @validates('tipo', 'client_id', 'position_id')
    def validate_tipo_rel(self, key, value):
        # Validação de coerência na camada de aplicação
        tipo = value if key == 'tipo' else self.tipo
        client_id = value if key == 'client_id' else self.client_id
        position_id = value if key == 'position_id' else self.position_id

        if tipo == 'INTERNO':
            if position_id is None:
                raise ValueError("Stakeholder INTERNO requer uma Posição.")
            if client_id is not None:
                raise ValueError("Stakeholder INTERNO não deve referenciar Cliente.")
        elif tipo == 'EXTERNO':
            if client_id is None:
                raise ValueError("Stakeholder EXTERNO requer um Cliente.")
            if position_id is not None:
                raise ValueError("Stakeholder EXTERNO não deve referenciar Posição.")
        return value


# ============================
# Activities
# ============================

activity_equipment = db.Table(
    'activity_equipment',
    db.Column('activity_id', db.Integer, db.ForeignKey('activities.id', ondelete='CASCADE'), primary_key=True),
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'), primary_key=True),
    UniqueConstraint('activity_id', 'equipment_id', name='uq_activity_equipment')
)

class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(400), nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='SET NULL'), nullable=False)
    project = db.relationship('Project', lazy='selectin')

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    duration_hours = db.Column(db.Float, nullable=True)

    owner_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=False)
    owner_user = db.relationship('User', foreign_keys=[owner_user_id], lazy='selectin')

    executor_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=False)
    executor_user = db.relationship('User', foreign_keys=[executor_user_id], lazy='selectin')

    environment = db.Column(
        db.Enum('SIMULADO', 'CONTROLADO', 'REAL', name='tipo_ambiente'),
        nullable=False
    )

    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='SET NULL'), nullable=True)
    client = db.relationship('Client', lazy='selectin')

    dealer_id = db.Column(db.Integer, db.ForeignKey('dealers.id', ondelete='SET NULL'), nullable=True)
    dealer = db.relationship('Dealer', lazy='selectin')

    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id', ondelete='SET NULL'), nullable=False)
    status = db.relationship('Status', lazy='selectin')

    # Máquinas envolvidas (CSV de VIN/Chassi)
    machines_text = db.Column(db.Text, nullable=True)

    # Equipamentos ligados à atividade
    equipments = db.relationship(
        'Equipment',
        secondary=activity_equipment,
        lazy='selectin',
        backref=db.backref('activities', lazy='selectin')
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(environment IN ('SIMULADO','CONTROLADO','REAL'))",
            name='ck_activities_environment'
        ),
    )

    def __repr__(self) -> str:
        return f"<Activity id={self.id} project_id={self.project_id} owner={self.owner_user_id} executor={self.executor_user_id}>"

    @property
    def machines_list(self) -> list[str]:
        if not self.machines_text:
            return []
        return [v.strip() for v in self.machines_text.split(',') if v.strip()]
