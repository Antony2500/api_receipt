import pytest
import sys
import asyncio
from pathlib import Path
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
from contextlib import ExitStack
from fastapi.testclient import TestClient
from datetime import timedelta

from app.services.auth import new_token

sys.path.append(str(Path(__file__).resolve().parent.parent))


from app.models.base import Base
from app.schemas.auth import Signup, LoginArgs
from app.main import init_app
from app.database import sessionmanager, get_db_session
from app.models.user import User
from app.utils.auth import hash_password, utc_now


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield init_app(init_db=False)


# @pytest.fixture
# async def client(app):
#     async with TestClient(app) as client:
#         yield client

@pytest.fixture
async def client(app):
    return TestClient(app)

test_db = factories.postgresql_proc(
    port=None,
    dbname="test_fast_poetry",
)


@pytest.fixture(scope="session")
def event_loop(request):
    """
    Create an isolated event loop for the session scope.

    This fixture provides an isolated loop for test that require
    asynchronous execution. The loop is created once per test session to
    ensure test isolation and to prevent conflicts with the global event loop.

    :arg request: A pytest request object, not used in this func but
                    necessary for the fixture definition.

    :return:
        Yields:
            An instance of asyncio event loop
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def connection_test(test_db, event_loop):
    with DatabaseJanitor(
            host=test_db.host,
            port=test_db.port,
            user=test_db.user,
            dbname=test_db.dbname,
            password=test_db.password,
            version='16',
    ):
        connection_str = f"postgresql+psycopg://{test_db.user}:{test_db.password}@{test_db.host}:{test_db.port}/{test_db.dbname}"
        sessionmanager.init(connection_str)
        yield
        await sessionmanager.close()


@pytest.fixture(scope="function", autouse=True)
async def create_tables(connection_test):
    async with sessionmanager.connect() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function", autouse=True)
async def session_override(app, connection_test):
    async def get_db_override():
        async with sessionmanager.session() as session:
            yield session

    app.dependency_overrides[get_db_session] = get_db_override


@pytest.fixture
async def test_session():
    async with sessionmanager.session() as session:
        yield session


@pytest.fixture
async def admin_user(test_session):
    admin = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password=hash_password("password"),
        role="admin",
        created=utc_now(),
        activation_token=new_token(),
        activation_expire=utc_now() + timedelta(hours=3)
    )

    test_session.add(admin)
    await test_session.commit()
    await test_session.refresh(admin)
    return admin


@pytest.fixture
async def register_user(client):
    signup_data = Signup(
        email="testuser@example.com",
        password="testpassword",
        username="testuser"
    ).model_dump()

    response = client.post("/auth/registration", json=signup_data)
    assert response.status_code == 200


@pytest.fixture
async def register_current_user(
        client,
        email: str = "testadmin@example.com",
        password: str = "password",
        username: str = "testuser"
):
    signup_data = Signup(
        email=email,
        password=password,
        username=username
    ).dict()

    response = client.post("/auth/registration", json=signup_data)
    assert response.status_code == 200


@pytest.fixture
async def login_admin_user(client, admin_user):
    login_data = LoginArgs(
        password="password",
        email=admin_user.email
    ).model_dump()

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert "refresh_token" in json_response
    return json_response["access_token"]
