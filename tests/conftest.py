from datetime import datetime

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.db.models import Document
from app.db.session import Base, get_db
from app.services.elasticsearch import get_elasticsearch_service


TEST_DATABASE_URL = (
    'postgresql+asyncpg://postgres:postgres'
    '@postgres:5432/searching_service_test'
)

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

AsyncSessionTest = async_sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope='session', autouse=True, loop_scope='session')
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine_test.dispose()


@pytest_asyncio.fixture(loop_scope='session')
async def db_session():
    async with AsyncSessionTest() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(loop_scope='session')
async def sample_documents(db_session: AsyncSession):
    docs = [
        Document(
            text='Python',
            rubrics=['IT', 'Programming'],
            created_date=datetime(2019, 6, 1, 12, 0, 0),
        ),
        Document(
            text='FastAPI',
            rubrics=['IT', 'Python'],
            created_date=datetime(2019, 8, 15, 10, 30, 0),
        ),
        Document(
            text='Elasticsearch',
            rubrics=['Search', 'IT'],
            created_date=datetime(2019, 3, 20, 8, 0, 0),
        ),
    ]
    db_session.add_all(docs)
    await db_session.flush()
    return docs


@pytest_asyncio.fixture(loop_scope='session')
async def api_client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(loop_scope='session')
async def indexed_documents(db_session):
    es = get_elasticsearch_service()
    docs_data = [
        {
            'text': 'Python',
            'rubrics': ['IT', 'Programming'],
            'created_date': datetime(2019, 8, 15, 10, 0, 0),
        },
        {
            'text': 'FastAPI',
            'rubrics': ['IT', 'Web'],
            'created_date': datetime(2019, 12, 1, 12, 0, 0),
        },
        {
            'text': 'Elasticsearch',
            'rubrics': ['Search'],
            'created_date': datetime(2019, 3, 20, 8, 0, 0),
        },
    ]
    documents = []
    try:
        for data in docs_data:
            doc = Document(**data)
            db_session.add(doc)
            await db_session.flush()
            await db_session.refresh(doc)
            await es.index_document(doc.id, doc.text)
            documents.append(doc)
        await db_session.commit()
        await es.client.indices.refresh(index=es.index_name)
        yield documents
    finally:
        for doc in documents:
            try:
                await es.delete_document(doc.id)
            except Exception:
                pass
        await es.client.close()
