from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration"""
    
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Ollama settings
    ollama_host: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3-coder:latest"
    ollama_timeout: int = 300
    
    # Agent settings
    max_concurrent_agents: int = 4
    agent_timeout: int = 600
    
    # Security settings
    approval_required: bool = True
    sandbox_mode: bool = True
    
    # Paths
    skills_dir: Path = Path(__file__).parent.parent / "skills"
    data_dir: Path = Path.home() / ".clawmate"
    
    # Container settings
    use_containers: bool = True
    docker_timeout: int = 300
    
    class Config:
        env_file = ".env"
        env_prefix = "CLAWMATE_"


settings = Settings()