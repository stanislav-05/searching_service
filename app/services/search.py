from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.documents import DocumentResponse
from app.services.documents import DocumentService
from app.services.elasticsearch import ElasticsearchService, get_elasticsearch_service


class SearchService:
    def __init__(
        self,
        db: AsyncSession,
        es_service: ElasticsearchService | None = None,
    ):
        self.db = db
        self.es_service = es_service or get_elasticsearch_service()

    async def search(self, query: str, limit: int = 20) -> list[DocumentResponse]:
        doc_ids = await self.es_service.search_ids(query)
        if not doc_ids:
            return []
        documents = await DocumentService.get_by_ids_sorted(self.db, doc_ids, limit=limit)
        return [DocumentResponse.model_validate(doc) for doc in documents]
