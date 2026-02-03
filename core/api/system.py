from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import platform
import psutil
import os

from executor import ShellExecutor
from ollama import OllamaClient

logger = logging.getLogger(__name__)

router = APIRouter()


class SystemInfo(BaseModel):
    platform: str
    shell: str
    python_version: str
    cpu_count: int
    memory_total: int
    memory_available: int
    disk_usage: int


class OllamaStatus(BaseModel):
    connected: bool
    models: List[Dict]
    current_model: str


class HealthCheck(BaseModel):
    status: str
    version: str
    ollama_connected: bool
    skills_loaded: int
    system_info: SystemInfo


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        # Check Ollama connection
        ollama = OllamaClient()
        ollama_connected = await ollama.is_connected()
        
        # Get system info
        executor = ShellExecutor()
        system_info = executor.get_system_info()
        
        # Count loaded skills (placeholder for now)
        skills_loaded = 0
        
        return HealthCheck(
            status="healthy",
            version="0.1.0",
            ollama_connected=ollama_connected,
            skills_loaded=skills_loaded,
            system_info=SystemInfo(**system_info)
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system", response_model=SystemInfo)
async def get_system_info():
    """Get detailed system information"""
    try:
        executor = ShellExecutor()
        system_info = executor.get_system_info()
        return SystemInfo(**system_info)
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ollama/status", response_model=OllamaStatus)
async def get_ollama_status():
    """Get Ollama status and available models"""
    try:
        ollama = OllamaClient()
        
        # Check connection
        connected = await ollama.is_connected()
        
        # Get models if connected
        models = []
        if connected:
            models = await ollama.list_models()
        
        return OllamaStatus(
            connected=connected,
            models=models,
            current_model=ollama.model
        )
        
    except Exception as e:
        logger.error(f"Failed to get Ollama status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes")
async def get_processes():
    """Get running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {"processes": processes}
    except Exception as e:
        logger.error(f"Failed to get processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory")
async def get_memory_info():
    """Get memory usage information"""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "virtual": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
                "free": memory.free
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            }
        }
    except Exception as e:
        logger.error(f"Failed to get memory info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/disk")
async def get_disk_info():
    """Get disk usage information"""
    try:
        if platform.system() == "Windows":
            disk = psutil.disk_usage('C:')
        else:
            disk = psutil.disk_usage('/')
        
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": (disk.used / disk.total) * 100
        }
    except Exception as e:
        logger.error(f"Failed to get disk info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network")
async def get_network_info():
    """Get network interface information"""
    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        network_info = {}
        for interface, addrs in interfaces.items():
            network_info[interface] = {
                "addresses": [
                    {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    }
                    for addr in addrs
                ],
                "stats": {
                    "isup": stats[interface].isup,
                    "duplex": str(stats[interface].duplex),
                    "speed": stats[interface].speed,
                    "mtu": stats[interface].mtu
                } if interface in stats else {}
            }
        
        return {"interfaces": network_info}
    except Exception as e:
        logger.error(f"Failed to get network info: {e}")
        raise HTTPException(status_code=500, detail=str(e))