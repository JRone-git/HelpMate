from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import os
import json

logger = logging.getLogger(__name__)

router = APIRouter()


class SkillInfo(BaseModel):
    id: str
    name: str
    version: str
    description: str
    author: Optional[str] = None
    tools: List[str] = []
    documentation: Optional[str] = None


class SkillListResponse(BaseModel):
    skills: List[SkillInfo]


@router.get("/list", response_model=SkillListResponse)
async def list_skills():
    """List all available skills"""
    try:
        skills_dir = os.path.join(os.path.dirname(__file__), "..", "..", "skills")
        skills = []
        
        if os.path.exists(skills_dir):
            for skill_name in os.listdir(skills_dir):
                skill_path = os.path.join(skills_dir, skill_name)
                if os.path.isdir(skill_path):
                    manifest_path = os.path.join(skill_path, "manifest.json")
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, 'r') as f:
                                manifest = json.load(f)
                            
                            skill_info = SkillInfo(
                                id=skill_name,
                                name=manifest.get("name", skill_name),
                                version=manifest.get("version", "1.0.0"),
                                description=manifest.get("description", ""),
                                author=manifest.get("author"),
                                tools=manifest.get("tools", []),
                                documentation=manifest.get("documentation")
                            )
                            skills.append(skill_info)
                        except Exception as e:
                            logger.error(f"Failed to load skill {skill_name}: {e}")
        
        return SkillListResponse(skills=skills)
        
    except Exception as e:
        logger.error(f"Failed to list skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/install/{skill_id}")
async def install_skill(skill_id: str):
    """Install a skill"""
    try:
        # This is a placeholder - in a real implementation, this would
        # download and install the skill from a repository
        return {"message": f"Skill {skill_id} installation initiated"}
    except Exception as e:
        logger.error(f"Failed to install skill {skill_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/uninstall/{skill_id}")
async def uninstall_skill(skill_id: str):
    """Uninstall a skill"""
    try:
        # This is a placeholder - in a real implementation, this would
        # remove the skill from the system
        return {"message": f"Skill {skill_id} uninstallation initiated"}
    except Exception as e:
        logger.error(f"Failed to uninstall skill {skill_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{skill_id}/info")
async def get_skill_info(skill_id: str):
    """Get detailed information about a skill"""
    try:
        skills_dir = os.path.join(os.path.dirname(__file__), "..", "..", "skills")
        skill_path = os.path.join(skills_dir, skill_id)
        
        if not os.path.exists(skill_path):
            raise HTTPException(status_code=404, detail="Skill not found")
        
        manifest_path = os.path.join(skill_path, "manifest.json")
        if not os.path.exists(manifest_path):
            raise HTTPException(status_code=404, detail="Skill manifest not found")
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        return manifest
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get skill info for {skill_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))