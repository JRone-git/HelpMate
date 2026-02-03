import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from .config import settings

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """Chat message"""
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    """Ollama chat request"""
    model: str
    messages: List[Message]
    stream: bool = True
    options: Optional[Dict] = None


class ChatResponse(BaseModel):
    """Ollama chat response"""
    model: str
    message: Message
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None


class OllamaClient:
    """Ollama API client with streaming support"""
    
    def __init__(self):
        self.base_url = settings.ollama_host
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        
    async def is_connected(self) -> bool:
        """Check if Ollama is running"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(urljoin(self.base_url, "/api/tags"))
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection check failed: {e}")
            return False
    
    async def list_models(self) -> List[Dict]:
        """List available models"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(urljoin(self.base_url, "/api/tags"))
                response.raise_for_status()
                return response.json().get("models", [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    async def chat_stream(
        self, 
        messages: List[Message], 
        model: Optional[str] = None
    ) -> AsyncGenerator[ChatResponse, None]:
        """Stream chat completion"""
        model = model or self.model
        
        request = ChatRequest(
            model=model,
            messages=messages,
            stream=True,
            options={"temperature": 0.7}
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    urljoin(self.base_url, "/api/chat"),
                    json=request.dict(exclude_none=True)
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                yield ChatResponse(**data)
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON line: {line}")
        except Exception as e:
            logger.error(f"Chat stream failed: {e}")
            raise
    
    async def chat(
        self, 
        messages: List[Message], 
        model: Optional[str] = None
    ) -> ChatResponse:
        """Get complete chat completion"""
        model = model or self.model
        
        request = ChatRequest(
            model=model,
            messages=messages,
            stream=False,
            options={"temperature": 0.7}
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    urljoin(self.base_url, "/api/chat"),
                    json=request.dict(exclude_none=True)
                )
                response.raise_for_status()
                return ChatResponse(**response.json())
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> str:
        """Generate text from prompt"""
        messages = [Message(role="user", content=prompt)]
        response = await self.chat(messages, model)
        return response.message.content