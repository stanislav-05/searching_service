from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.documents import DocumentResponse
from app.services.documents import DocumentService
from app.services.search import SearchService

router = APIRouter(prefix='/documents', tags=['documents'])


@router.get(
    '/search',
    response_model=list[DocumentResponse],
    summary='Поиск документов по тексту',
)
async def search_documents(
    q: str = Query(..., min_length=1, description='Поисковый запрос'),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentResponse]:
    service = SearchService(db=db)
    return await service.search(query=q, limit=20)


@router.delete(
    '/{document_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить документ по id',
)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    document = await DocumentService.delete(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Document with id={document_id} not found',
        )
