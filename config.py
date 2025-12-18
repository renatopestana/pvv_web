import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE = f"sqlite:///{(BASE_DIR / 'app' / 'app.db').as_posix()}"

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = None

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False
