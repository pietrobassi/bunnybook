import os
import shutil
from pathlib import Path

from config import cfg
from database.core import db

# override services URIs to prevent port collisions between dev and test
# docker-compose configurations
if "DEV" not in os.environ:
    cfg.postgres_uri = "bunny:bunny@localhost:5433/bunnybook"
    cfg.cache_uri = "redis://127.0.0.1:6381"
    cfg.pubsub_uri = "redis://127.0.0.1:6382"
    cfg.neo4j_uri = "neo4j://localhost:7688"
    cfg.avatar_data_folder = "_data-test/avatar-data"
    db.__init__(
        f"postgresql://{cfg.postgres_uri}",
        min_size=cfg.postgres_min_pool_size,
        max_size=cfg.postgres_max_pool_size)

from asyncio import get_event_loop
from dataclasses import dataclass
from typing import Generator
from uuid import uuid4

import pytest
from httpx import AsyncClient

from init_db import init_rdbms, init_graph
from main import app, startup
from wait_for import wait_for_external_services

app_base_url = "http://bunnybook/web"


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir),
                        "docker-compose-test.yml")


@pytest.fixture(scope="session", autouse=True)
async def create_test_dir(request):
    test_dir = Path("_data-test")
    test_dir.mkdir(exist_ok=True, parents=True)
    yield
    shutil.rmtree(test_dir)


if "DEV" in os.environ:
    @pytest.fixture(scope="session", autouse=True)
    async def before_all_tests(request):
        await startup()
else:
    @pytest.fixture(scope="session", autouse=True)
    async def before_all_tests(request, docker_services):
        # wait until all containers are responsive
        docker_services.wait_until_responsive(
            timeout=60.0, pause=1, check=lambda: wait_for_external_services())
        # init databases
        init_rdbms()
        init_graph()
        # FastAPI startup event must be called manually
        await startup()


@dataclass
class TestUser:
    id: str
    username: str
    email: str
    password: str
    conn: AsyncClient


@pytest.fixture(scope="function")
async def new_profile() -> TestUser:
    """Return a new registered user."""
    uid = str(uuid4())[:32]
    username, email, password = uid, f"{uid}@bunnybook.com", uid
    async with AsyncClient(app=app,
                           base_url=app_base_url) as conn:
        register_response = await conn.post("/register", json=dict(
            username=uid,
            email=email,
            password=password))
        new_user_id = register_response.json()["id"]
        login_response = await conn.post("/login", json=dict(
            email=email,
            password=password))
    headers = {"Authorization": f"Bearer "
                                f"{login_response.json()['accessToken']}"}

    async with AsyncClient(app=app,
                           base_url=app_base_url,
                           headers=headers) as new_user_conn:
        yield TestUser(id=new_user_id,
                       username=username,
                       email=email,
                       password=password,
                       conn=new_user_conn)


# Named registered users used for clean testing (function scoped)
ben = daisy = sumba = pumba = exempel = bigcocoapuff = new_profile


@pytest.fixture(scope="function")
async def conn() -> Generator:
    async with AsyncClient(app=app,
                           base_url=app_base_url) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    loop = get_event_loop()
    yield loop
