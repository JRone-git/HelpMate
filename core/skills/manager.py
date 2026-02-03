import asyncio
import logging
import os
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)


@dataclass
class SkillInfo:
    """Information about a loaded skill"""
    name: str
    version: str
    description: str
    author: Optional[str]
    tools: List[str]
    entrypoint: str
    manifest_path: str


class SkillManager:
    """Manages loading and execution of skills"""
    
    def __init__(self):
        self.skills: Dict[str, SkillInfo] = {}
        self.tool_registry: Dict[str, Callable] = {}
        
    async def load_skills(self):
        """Load all available skills from the skills directory"""
        logger.info("Loading skills...")
        
        skills_dir = settings.skills_dir
        if not skills_dir.exists():
            logger.warning(f"Skills directory {skills_dir} does not exist")
            return
        
        for skill_name in os.listdir(skills_dir):
            skill_path = skills_dir / skill_name
            if skill_path.is_dir():
                await self._load_skill(skill_name, skill_path)
        
        logger.info(f"Loaded {len(self.skills)} skills")
    
    async def _load_skill(self, skill_name: str, skill_path: Path):
        """Load a single skill"""
        try:
            manifest_path = skill_path / "manifest.json"
            if not manifest_path.exists():
                logger.warning(f"Skill {skill_name} missing manifest.json")
                return
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            skill_info = SkillInfo(
                name=manifest.get("name", skill_name),
                version=manifest.get("version", "1.0.0"),
                description=manifest.get("description", ""),
                author=manifest.get("author"),
                tools=manifest.get("tools", []),
                entrypoint=manifest.get("entrypoint", ""),
                manifest_path=str(manifest_path)
            )
            
            self.skills[skill_name] = skill_info
            logger.info(f"Loaded skill: {skill_name} v{skill_info.version}")
            
        except Exception as e:
            logger.error(f"Failed to load skill {skill_name}: {e}")
    
    def get_skill(self, skill_name: str) -> Optional[SkillInfo]:
        """Get information about a specific skill"""
        return self.skills.get(skill_name)
    
    def list_skills(self) -> List[SkillInfo]:
        """List all loaded skills"""
        return list(self.skills.values())
    
    def has_skill(self, skill_name: str) -> bool:
        """Check if a skill is loaded"""
        return skill_name in self.skills
    
    def get_tools(self) -> List[str]:
        """Get list of all available tools"""
        tools = set()
        for skill in self.skills.values():
            tools.update(skill.tools)
        return list(tools)
    
    def get_skill_by_tool(self, tool_name: str) -> Optional[SkillInfo]:
        """Find which skill provides a specific tool"""
        for skill in self.skills.values():
            if tool_name in skill.tools:
                return skill
        return None
    
    async def execute_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """Execute a tool from the appropriate skill"""
        skill = self.get_skill_by_tool(tool_name)
        if not skill:
            raise ValueError(f"Tool {tool_name} not found in any skill")
        
        # This is a simplified implementation
        # In a real system, you would load and execute the skill's code
        logger.info(f"Executing tool {tool_name} from skill {skill.name}")
        
        # Placeholder implementation
        return {
            "tool": tool_name,
            "skill": skill.name,
            "args": args,
            "kwargs": kwargs,
            "result": f"Tool {tool_name} executed successfully"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the skill manager"""
        return {
            "loaded_skills": len(self.skills),
            "available_tools": len(self.get_tools()),
            "skills": {name: {
                "version": info.version,
                "tools": info.tools,
                "description": info.description
            } for name, info in self.skills.items()}
        }