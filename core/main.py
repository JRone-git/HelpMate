#!/usr/bin/env python3
"""
ClawMate - Personal Assistant Core
Cross-platform AI assistant with agentic capabilities
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from api import router as api_router
from ollama import OllamaClient
from executor import ShellExecutor
from agents import AgentManager
from skills import SkillManager
from config import settings
from logging_config import get_logger

# Get logger instance
logger = get_logger(__name__)

# Global state
ollama_client: OllamaClient
shell_executor: ShellExecutor
agent_manager: AgentManager
skill_manager: SkillManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ollama_client, shell_executor, agent_manager, skill_manager
    
    logger.info("🚀 Starting ClawMate Core...")
    
    # Initialize components
    ollama_client = OllamaClient()
    shell_executor = ShellExecutor()
    agent_manager = AgentManager(ollama_client, shell_executor)
    skill_manager = SkillManager()
    
    # Load skills
    await skill_manager.load_skills()
    
    logger.info("✅ ClawMate Core initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down ClawMate Core...")
    await agent_manager.shutdown()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="ClawMate Core API",
        description="Cross-platform AI personal assistant",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Serve static files (web interface)
    web_dir = Path(__file__).parent.parent / "web" / "dist"
    if web_dir.exists():
        app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return HTMLResponse(content=(web_dir / "index.html").read_text())
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": "0.1.0",
            "ollama_connected": await ollama_client.is_connected(),
            "skills_loaded": len(skill_manager.skills)
        }
    
    return app


def main():
    """Main entry point"""
    app = create_app()
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info"
    )


if __name__ == "__main__":
    main()