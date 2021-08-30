import alembic.config
from neo4j import GraphDatabase

from config import cfg


def init_rdbms():
    """Align database schema to latest version."""
    alembic.config.main(argv=["upgrade", "head"])


def init_graph():
    """Create graph db constraints."""
    driver = GraphDatabase.driver(
        cfg.neo4j_uri,
        auth=(cfg.neo4j_user, cfg.neo4j_password))
    with driver.session() as session:
        session.write_transaction(lambda tx: tx.run(
            "CREATE CONSTRAINT IF NOT EXISTS ON (p:Profile) "
            "ASSERT p.id IS UNIQUE"))
        session.write_transaction(lambda tx: tx.run(
            "CREATE CONSTRAINT IF NOT EXISTS ON (p:Profile) "
            "ASSERT p.username IS UNIQUE"))


if __name__ == "__main__":
    init_rdbms()
    init_graph()
