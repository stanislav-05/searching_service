import pytest


@pytest.mark.asyncio(loop_scope='session')
async def test_search_success(api_client, indexed_documents):
    response = await api_client.get(
        '/api/v1/documents/search',
        params={'q': 'Python'},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert len(data) <= 20
    item = data[0]
    assert 'id' in item
    assert 'rubrics' in item
    assert 'text' in item
    assert 'created_date' in item
    assert any('Python' in doc['text'] for doc in data)


@pytest.mark.asyncio(loop_scope='session')
async def test_search_sorted_by_date(api_client, indexed_documents):
    response = await api_client.get(
        '/api/v1/documents/search',
        params={'q': 'a'},
    )
    assert response.status_code == 200
    data = response.json()
    if len(data) >= 2:
        dates = [item['created_date'] for item in data]
        assert dates == sorted(dates, reverse=True)


@pytest.mark.asyncio(loop_scope='session')
async def test_search_limit(api_client, indexed_documents):
    response = await api_client.get(
        '/api/v1/documents/search',
        params={'q': 'a'},
    )
    assert response.status_code == 200
    assert len(response.json()) <= 20


@pytest.mark.asyncio(loop_scope='session')
async def test_search_empty_query(api_client):
    response = await api_client.get(
        '/api/v1/documents/search',
        params={'q': ''},
    )
    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope='session')
async def test_search_no_results(api_client, indexed_documents):
    response = await api_client.get(
        '/api/v1/documents/search',
        params={'q': 'qwsedrftgfdfghjuuhgfdfg'},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope='session')
async def test_delete_success(api_client, indexed_documents):
    doc_id = indexed_documents[0].id
    response = await api_client.delete(f'/api/v1/documents/{doc_id}')
    assert response.status_code == 204
    response = await api_client.delete(f'/api/v1/documents/{doc_id}')
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope='session')
async def test_delete_not_found(api_client):
    response = await api_client.delete('/api/v1/documents/999999')
    assert response.status_code == 404
