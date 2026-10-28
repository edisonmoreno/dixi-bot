"""In-memory tenant repository."""
from psycopg_pool import ConnectionPool


class TenantRepositoryAdapter:
    """Concrete implementation of TenantRepository."""

    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    def find_by_id(self, tenant_id: str):
        """Find a tenant by its identifier."""
        with self.pool.connection() as conn:
            row = conn.execute(
                "SELECT id, code, name, status FROM tenants WHERE code = %s",
                (tenant_id,),
            ).fetchone()
        return row
