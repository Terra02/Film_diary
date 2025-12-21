from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List, Dict, Any
import logging
from app.models.content import Content
from app.schemas.content import ContentCreate
from app.services.worker_adapter import worker_adapter

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_content_by_id(self, content_id: int) -> Optional[Content]:
        result = await self.db.execute(
            select(Content).where(Content.id == content_id)
        )
        return result.scalar_one_or_none()

    async def get_content_by_imdb_id(self, imdb_id: str) -> Optional[Content]:
        result = await self.db.execute(
            select(Content).where(Content.imdb_id == imdb_id)
        )
        return result.scalar_one_or_none()

    async def create_content(self, content_data: ContentCreate) -> Content:
        if content_data.imdb_id:
            existing_content = await self.get_content_by_imdb_id(content_data.imdb_id)
            if existing_content:
                return existing_content

        data = content_data.model_dump()
        cast = data.pop("cast", None)
        content = Content(**data)
        if cast is not None:
            content.actors_cast = cast

        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)
        logger.info(f"Новый контент создан: {content.title}")
        return content

    async def search_omdb_direct( self, title: str, content_type: str = None) -> Optional[List[Dict[str, Any]]]:
            stmt = select(Content).where(Content.title.ilike(f"%{title}%"))
            result = await self.db.execute(stmt)
            content = result.scalars().first()

            db_item = None
            if content:
                db_item = {
                    **self._content_to_dict(content),
                    "source": "database",
                    "already_watched": False,
                }

            worker_result = await worker_adapter.search_omdb(title, content_type) or []
            omdb_items = []
            seen_imdb_ids = set()

            if db_item and db_item.get("imdb_id"):
                seen_imdb_ids.add(db_item["imdb_id"])

            max_omdb_items = 5 - (1 if db_item else 0)

            for item in worker_result:
                imdb_id = item.get("imdb_id")
                if imdb_id and imdb_id in seen_imdb_ids:
                    continue
                if imdb_id:
                    seen_imdb_ids.add(imdb_id)
                omdb_items.append({**item, "source": "omdb", "already_watched": False})

                if len(omdb_items) >= max_omdb_items:
                    break

            combined: list = []
            if db_item:
                combined.append(db_item)

            combined.extend(omdb_items)
            if combined:
                return {
                    "source": "mixed" if db_item and omdb_items else (db_item and "database") or "omdb",
                    "data": combined,
                    "message": "Найдены результаты поиска"
                }

            return {
                "source": "not_found",
                "data": None,
                "message": f"'{title}' не найден в OMDB"
            }

    def _content_to_dict(self, content: Content) -> Dict[str, Any]:
            """Конвертировать Content в словарь"""
            if not content:
                return {}
                
            return {
                "id": content.id,
                "title": content.title,
                "original_title": content.original_title,
                "description": content.description,
                "content_type": content.content_type,
                "release_year": content.release_year,
                "imdb_rating": content.imdb_rating,
                "imdb_id": content.imdb_id,
                "poster_url": content.poster_url,
                "genre": content.genre,
                "director": content.director,
                "cast": content.actors_cast,
            }

   