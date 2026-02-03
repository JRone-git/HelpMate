from fastapi import APIRouter

from .chat import router as chat_router
from .commands import router as commands_router
from .skills import router as skills_router
from .system import router as system_router

router = APIRouter()

# Include all sub-routers
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(commands_router, prefix="/commands", tags=["commands"])
router.include_router(skills_router, prefix="/skills", tags=["skills"])
router.include_router(system_router, prefix="/system", tags=["system"])