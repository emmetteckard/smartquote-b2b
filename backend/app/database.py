import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create database engine

# ... (中间可能还有其他代码) ...

# --- 开始替换 ---

# 1. 优先尝试获取 Vercel 提供的云数据库地址 (POSTGRES_URL)
#    如果获取不到（说明在本地），则回退使用 settings.DATABASE_URL
database_url = os.getenv("POSTGRES_URL", settings.DATABASE_URL)

# 2. 关键修复：SQLAlchemy 不认识 "postgres://"，必须改成 "postgresql://"
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# 3. 创建数据库引擎 (注意这里传的是处理过的 database_url)
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# --- 替换结束 ---

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
