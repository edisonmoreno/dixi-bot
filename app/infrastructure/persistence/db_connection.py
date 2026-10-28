from functools import lru_cache
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config.config import settings


def _build_conn_info() -> str:
    return make_conninfo(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        sslmode=settings.db_ssl_mode,
        sslrootcert=settings.db_ssl_root_cert
    )


@lru_cache(maxsize=1)
def get_connection_pool() -> ConnectionPool:
    """Create and return a configured PostgreSQL connection pool."""
    pool = ConnectionPool(
        _build_conn_info(),
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
        timeout=settings.db_pool_timeout,
        open=False,
        kwargs={
            "row_factory": dict_row,
            "connect_timeout": settings.db_connect_timeout
        },
    )
    pool.open()
    pool.wait(timeout=settings.db_pool_wait_timeout)
    return pool


# Única instancia global para toda la app
connection_pool = get_connection_pool()
