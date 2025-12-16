from fastapi import FastAPI
import httpx
import os
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

app = FastAPI(title="OMDB Worker")
logger = logging.getLogger(__name__)

class SearchRequest(BaseModel):
    title: str
    content_type: Optional[str] = None

class SearchResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class OMDBService:
    def __init__(self):
        self.api_key = os.getenv("OMDB_API_KEY")
        self.base_url = "http://www.omdbapi.com/"
        
        if not self.api_key:
            logger.error("OMDB_API_KEY not configured in worker")
    
    async def search(self, title: str, content_type: str = None) -> Optional[List[Dict[str, Any]]]:

        if not self.api_key:
            logger.error("OMDB API key not configured")
            return None

        try:
            search_params = {
                "apikey": self.api_key,
                "s": title,
                "plot": "short"
            }

            if content_type:
                search_params["type"] = content_type

            logger.info(f"Worker ищет в OMDB (list): {title}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                search_resp = await client.get(self.base_url, params=search_params)

                if search_resp.status_code != 200:
                    logger.error(f"OMDB API error: {search_resp.status_code}")
                    return None

                search_data = search_resp.json()
                if search_data.get("Response") != "True" or not search_data.get("Search"):
                    logger.warning(f"Не найдено в OMDB: {search_data.get('Error')}")
                    return None

                # Берем первые 5 результатов и запрашиваем подробности по imdbID
                parsed_results: List[Dict[str, Any]] = []
                for item in search_data.get("Search", [])[:5]:
                    imdb_id = item.get("imdbID")
                    if not imdb_id:
                        continue

                    details = await self._fetch_details(client, imdb_id)
                    if details:
                        parsed_results.append(details)

                return parsed_results if parsed_results else None

        except Exception as e:
            logger.error(f"Worker error: {e}")
            return None

    async def _fetch_details(self, client: httpx.AsyncClient, imdb_id: str) -> Optional[Dict[str, Any]]: #Детльная инфа по imbID

        try:
            params = {
                "apikey": self.api_key,
                "i": imdb_id,
                "plot": "short"
            }
            detail_resp = await client.get(self.base_url, params=params)
            if detail_resp.status_code != 200:
                logger.error(f"OMDB detail error for {imdb_id}: {detail_resp.status_code}")
                return None

            detail_data = detail_resp.json()
            if detail_data.get("Response") != "True":
                logger.warning(f"Не удалось получить детали для {imdb_id}: {detail_data.get('Error')}")
                return None

            logger.info(f"Детали OMDB: {detail_data.get('Title')}")
            return self._parse_response(detail_data)
        except Exception as e:
            logger.error(f"Ошибка при получении деталей OMDB {imdb_id}: {e}")
            return None
        
    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:         #Парсинг ответов
        content_type = "movie"
        if data.get("Type") == "series":
            content_type = "series"
        
        # Парсим год
        release_year = None
        if data.get("Year") and data.get("Year") != "N/A":
            try:
                year_str = data["Year"].split("–")[0]
                release_year = int(year_str)
            except ValueError:
                pass
        
        # Парсим рейтинг
        imdb_rating = None
        if data.get("imdbRating") and data.get("imdbRating") != "N/A":
            try:
                imdb_rating = float(data["imdbRating"])
            except ValueError:
                pass
        
        return {
            "title": data.get("Title"),
            "original_title": data.get("Title"),
            "description": data.get("Plot"),
            "content_type": content_type,
            "release_year": release_year,
            "imdb_rating": imdb_rating,
            "imdb_id": data.get("imdbID"),
            "poster_url": data.get("Poster") if data.get("Poster") != "N/A" else None,
            "genre": data.get("Genre"),
            "director": data.get("Director"),
            "cast": data.get("Actors"),
        }

# Инициализация сервиса
omdb_service = OMDBService()

@app.post("/search", response_model=SearchResponse)
async def search_omdb(request: SearchRequest):
    """Endpoint для поиска в OMDB"""
    if not omdb_service.api_key:
        return SearchResponse(
            success=False,
            error="OMDB API key not configured in worker"
        )
    
    result = await omdb_service.search(request.title, request.content_type)
    
    if result:
        return SearchResponse(success=True, data=result)
    else:
        return SearchResponse(
            success=False,
            error=f"Фильм '{request.title}' не найден в OMDB"
        )

@app.get("/health")
async def health_check():
    """Проверка здоровья worker"""
    return {"status": "healthy", "service": "omdb-worker"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)