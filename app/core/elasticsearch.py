from elasticsearch import AsyncElasticsearch

from app.core.config import settings


INDEX_NAME = 'documents'

elasticsearch_client = AsyncElasticsearch(
    settings.elasticsearch_url,
)

INDEX_MAPPING = {
    'properties': {
        'id': {
            'type': 'integer',
        },
        'text': {
            'type': 'text',
        },
    },
}


async def create_index() -> None:
    if await elasticsearch_client.indices.exists(index=INDEX_NAME):
        return
    await elasticsearch_client.indices.create(
        index=INDEX_NAME,
        mappings=INDEX_MAPPING,
    )
