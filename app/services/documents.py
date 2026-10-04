from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document
from app.schemas.documents import DocumentCreate
from app.services.elasticsearch import ElasticsearchService, get_elasticsearch_service


class DocumentService:

    @staticmethod
    async def get_by_id(db: AsyncSession, doc_id: int) -> Document | None:
        query = select(Document).where(
            Document.id == doc_id,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_ids_sorted(
        db: AsyncSession,
        doc_ids: list[int],
        limit: int = 20
    ) -> list[Document]:
        if not doc_ids:
            return []
        query = (
            select(Document).where(Document.id.in_(doc_ids)).order_by(
                Document.created_date.desc()
            ).limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession,
        schema: DocumentCreate,
        es_service: ElasticsearchService | None = None,
    ) -> Document:
        document = Document(
            rubrics=schema.rubrics,
            text=schema.text,
            created_date=schema.created_date,
        )
        db.add(document)
        await db.flush()
        await db.refresh(document)
        es = es_service or get_elasticsearch_service()
        await es.index_document(document.id, document.text)
        return document

    @staticmethod
    async def delete(
        db: AsyncSession,
        doc_id: int,
        es_service: ElasticsearchService | None = None,
    ) -> Document | None:
        document = await DocumentService.get_by_id(db, doc_id)
        if document is None:
            return None
        await db.delete(document)
        await db.flush()
        es = es_service or get_elasticsearch_service()
        await es.delete_document(doc_id)
        return document
