from elasticsearch import AsyncElasticsearch, NotFoundError

from app.core.elasticsearch import INDEX_NAME, elasticsearch_client


class ElasticsearchService:
    def __init__(self, client: AsyncElasticsearch, index_name: str):
        self.client = client
        self.index_name = index_name

    async def search_ids(self, query: str) -> list[int]:
        if not query.strip():
            return []
        response = await self.client.search(
            index=self.index_name,
            query={'match': {'text': query}},
            size=1000,
        )
        hits = response['hits']['hits']
        return [int(hit['_id']) for hit in hits]

    async def index_document(self, doc_id: int, text: str) -> None:
        await self.client.index(
            index=self.index_name,
            id=str(doc_id),
            document={
                'id': doc_id,
                'text': text,
            },
        )

    async def delete_document(self, doc_id: int) -> None:
        try:
            await self.client.delete(
                index=self.index_name,
                id=str(doc_id),
            )
        except NotFoundError:
            pass


def get_elasticsearch_service() -> ElasticsearchService:
    return ElasticsearchService(
        client=elasticsearch_client,
        index_name=INDEX_NAME,
    )
