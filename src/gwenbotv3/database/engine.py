import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from gwenbotv3.config import DatabaseConfig

DATABASE_URL = (
    f"mysql+aiomysql://{DatabaseConfig.DB_USER}:{DatabaseConfig.DB_PASS}"
    f"@{DatabaseConfig.DB_HOST}:{DatabaseConfig.DB_PORT}/{DatabaseConfig.DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
logging.getLogger(__name__).info("Initialised engine.")
