import time

import psycopg2
from neo4j import GraphDatabase
from redis import Redis
from timeout_decorator import timeout

from common.log import logger
from config import cfg


def wait_for_external_services(
        wait_for_pg: bool = True,
        wait_for_neo4j: bool = True,
        wait_for_pubsub: bool = True,
        wait_for_cache: bool = True,
        interval: float = 5,
        max_retries: int = 60) -> bool:
    """Wait for external services to be responsive."""
    retry_count = 0
    everything_is_up = False
    while not everything_is_up:
        try:
            if wait_for_neo4j:
                logger.info("Waiting for Neo4j...")
                driver = GraphDatabase.driver(
                    cfg.neo4j_uri,
                    auth=(cfg.neo4j_user, cfg.neo4j_password))

                @timeout(3)
                def neo4j_healthcheck():
                    with driver.session() as session:
                        session.read_transaction(lambda tx: list(tx.run("""
                            MATCH (healthcheck:Profile {id: 'healthcheck'})
                            RETURN healthcheck""")))

                neo4j_healthcheck()
                logger.info("Neo4j is ready!")
            if wait_for_pg:
                logger.info("Waiting for PostgreSQL...")
                psycopg2.connect(f"postgresql://{cfg.postgres_uri}")
                logger.info("PostgreSQL is ready!")
            if wait_for_pubsub:
                logger.info("Waiting for PubSub...")
                Redis(
                    host=cfg.pubsub_uri.split("//")[1].split(":")[0],
                    port=cfg.pubsub_uri.split("//")[1].split(":")[1]) \
                    .get("healthcheck")
                logger.info("PubSub is ready!")
            if wait_for_cache:
                logger.info("Waiting for Cache...")
                Redis(
                    host=cfg.cache_uri.split("//")[1].split(":")[0],
                    port=cfg.cache_uri.split("//")[1].split(":")[1]) \
                    .get("healthcheck")
                logger.info("Cache is ready!")
            logger.info("All external services are ready.")
            everything_is_up = True
        except:
            retry_count += 1
            if retry_count > max_retries:
                raise TimeoutError()
            logger.info(f"Retry n. {retry_count}...")
            time.sleep(interval)
    return True


if __name__ == "__main__":
    wait_for_external_services(wait_for_cache=False)
