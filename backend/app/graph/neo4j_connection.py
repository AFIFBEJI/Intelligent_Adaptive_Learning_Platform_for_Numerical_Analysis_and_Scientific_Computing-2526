import logging
from typing import Any

from neo4j import GraphDatabase

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Singleton for the Neo4j connection"""
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        if self._driver is None:
            settings = get_settings()
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info(f"✅ Connecté à Neo4j : {settings.NEO4J_URI}")
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    def get_session(self):
        return self.connect().session()

    def run_query(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a read query and return a list of dictionaries."""
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]

    def run_write_query(self, query: str, parameters: dict[str, Any] | None = None) -> None:
        """Execute a write query (CREATE, MERGE, DELETE)."""
        with self.get_session() as session:
            session.run(query, parameters or {})


# Global instance (Singleton)
neo4j_conn = Neo4jConnection()
