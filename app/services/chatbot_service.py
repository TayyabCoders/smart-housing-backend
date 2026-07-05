"""
Chatbot (O.T.T.O) Service — proxies chat queries to the RAG microservice
"""
import httpx
from fastapi import HTTPException

from app.configs.app_config import settings


class ChatbotService:

    async def ask(self, query: str) -> dict:
        """Forward a query to the O.T.T.O RAG service and return its answer."""
        try:
            async with httpx.AsyncClient(timeout=settings.RAG_SERVICE_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.RAG_SERVICE_URL}/chat",
                    json={"query": query},
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="O.T.T.O took too long to respond")
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="O.T.T.O service is unavailable")
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=502, detail="O.T.T.O failed to generate a response")
