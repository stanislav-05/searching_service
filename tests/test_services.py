from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.schemas.documents import DocumentCreate
from app.services.documents import DocumentService


@pytest.mark.asyncio(loop_scope='session')
async def test_get_by_id(db_session, sample_documents):
    doc = sample_documents[0]
    result = await DocumentService.get_by_id(db_session, doc.id)
    assert result is not None
    assert result.id == doc.id
    assert result.text == doc.text
    assert result.rubrics == doc.rubrics


@pytest.mark.asyncio(loop_scope='session')
async def test_get_by_id_not_found(db_session):
    result = await DocumentService.get_by_id(db_session, 99999)
    assert result is None


@pytest.mark.asyncio(loop_scope='session')
async def test_get_by_ids_sorted(db_session, sample_documents):
    ids = [doc.id for doc in sample_documents]
    result = await DocumentService.get_by_ids_sorted(db_session, ids)
    assert len(result) == 3
    dates = [doc.created_date for doc in result]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.asyncio(loop_scope='session')
async def test_get_by_ids_empty(db_session):
    result = await DocumentService.get_by_ids_sorted(db_session, [])
    assert result == []


@pytest.mark.asyncio(loop_scope='session')
async def test_create(db_session):
    schema = DocumentCreate(
        text='New test document',
        rubrics=['Test'],
        created_date=datetime(2019, 5, 1, 10, 0, 0),
    )
    mock_es = AsyncMock()
    doc = await DocumentService.create(db_session, schema, es_service=mock_es)
    assert doc.id is not None
    assert doc.text == 'New test document'
    assert doc.rubrics == ['Test']
    assert doc.created_date == datetime(2019, 5, 1, 10, 0, 0)
    mock_es.index_document.assert_awaited_once_with(doc.id, doc.text)


@pytest.mark.asyncio(loop_scope='session')
async def test_delete(db_session, sample_documents):
    doc = sample_documents[0]
    mock_es = AsyncMock()
    deleted = await DocumentService.delete(db_session, doc.id, es_service=mock_es)
    assert deleted is not None
    assert deleted.id == doc.id
    mock_es.delete_document.assert_awaited_once_with(doc.id)
    result = await DocumentService.get_by_id(db_session, doc.id)
    assert result is None


@pytest.mark.asyncio(loop_scope='session')
async def test_delete_not_found(db_session):
    mock_es = AsyncMock()
    result = await DocumentService.delete(db_session, 99999, es_service=mock_es)
    assert result is None
    mock_es.delete_document.assert_not_awaited()
