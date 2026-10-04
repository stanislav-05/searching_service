import ast
import asyncio
import csv
from datetime import datetime
from pathlib import Path

from elasticsearch.helpers import async_bulk
from sqlalchemy import insert

from app.core.elasticsearch import create_index
from app.db.models import Document
from app.db.session import AsyncSessionLocal
from app.services.elasticsearch import get_elasticsearch_service


BATCH_SIZE = 500
CSV_FILE_PATH = Path(__file__).parent.parent / 'data' / 'posts.csv'


def parse_rubrics(rubrics_str: str) -> list[str]:
    try:
        parsed = ast.literal_eval(rubrics_str)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (ValueError, SyntaxError):
        pass
    return []


def parse_datetime(dt_str: str) -> datetime | None:
    try:
        return datetime.strptime(
            dt_str.strip(),
            '%Y-%m-%d %H:%M:%S',
        )
    except (ValueError, AttributeError):
        return None


async def process_batch(session, es_service, batch: list[dict]) -> int:
    if not batch:
        return 0
    statement = (
        insert(Document).values(batch).returning(Document.id, Document.text)
    )
    result = await session.execute(statement)
    inserted_docs = result.all()
    await session.commit()
    actions = [
        {
            '_index': es_service.index_name,
            '_id': str(doc_id),
            '_source': {
                'id': doc_id,
                'text': text,
            },
        }
        for doc_id, text in inserted_docs
    ]
    success, _ = await async_bulk(
        es_service.client,
        actions,
        raise_on_error=True,
    )
    return success


async def import_csv_data() -> None:
    if not CSV_FILE_PATH.exists():
        print(
            f'File not found at '
            f'{CSV_FILE_PATH.resolve()}'
        )
        return
    await create_index()
    es_service = get_elasticsearch_service()
    total_loaded = 0
    try:
        async with AsyncSessionLocal() as session:
            with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                batch: list[dict] = []
                for row in reader:
                    created_date = parse_datetime(
                        row.get('created_date', ''),
                    )
                    if created_date is None:
                        print(
                            'Skipping row with invalid date: '
                            f'{row.get("created_date")}'
                        )
                        continue
                    doc_data = {
                        'text': row['text'],
                        'rubrics': parse_rubrics(
                            row.get('rubrics', '[]'),
                        ),
                        'created_date': created_date,
                    }
                    batch.append(doc_data)
                    if len(batch) >= BATCH_SIZE:
                        loaded = await process_batch(session, es_service, batch)
                        total_loaded += loaded
                        print(
                            f'Loaded batch: {loaded} records '
                            f'(total: {total_loaded})'
                        )
                        batch.clear()
                if batch:
                    loaded = await process_batch(session, es_service, batch)
                    total_loaded += loaded
                    print(f'Loaded final batch: {loaded} records')

        print(f'Total documents loaded: {total_loaded}')
    finally:
        await es_service.client.close()


if __name__ == '__main__':
    asyncio.run(import_csv_data())
