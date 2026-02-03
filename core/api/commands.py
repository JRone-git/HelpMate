from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from executor import ExecutionRequest, ShellExecutor

logger = logging.getLogger(__name__)

router = APIRouter()


class CommandRequest(BaseModel):
    command: str
    args: List[str] = []
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    pty: bool = False
    elevated: bool = False
    sandbox: bool = False


class CommandResponse(BaseModel):
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    pid: Optional[int] = None


@router.post("/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """Execute a shell command"""
    try:
        # Create execution request
        exec_request = ExecutionRequest(
            command=request.command,
            args=request.args,
            cwd=request.cwd,
            env=request.env,
            timeout=request.timeout,
            pty=request.pty,
            elevated=request.elevated,
            sandbox=request.sandbox
        )
        
        # Execute command
        executor = ShellExecutor()
        result = await executor.execute(exec_request)
        
        return CommandResponse(
            command=result.command,
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            duration=result.duration,
            pid=result.pid
        )
        
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-info")
async def get_system_info():
    """Get system information"""
    try:
        executor = ShellExecutor()
        return executor.get_system_info()
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-command/{command}")
async def check_command(command: str):
    """Check if a command is available"""
    try:
        executor = ShellExecutor()
        available = executor.is_command_available(command)
        return {"command": command, "available": available}
    except Exception as e:
        logger.error(f"Failed to check command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_command(request: CommandRequest):
    """Stream command output (returns WebSocket URL)"""
    # This endpoint would return a WebSocket URL for streaming
    # The actual streaming is handled by the WebSocket endpoint
    return {
        "message": "Use WebSocket endpoint /api/v1/commands/stream/ws for streaming",
        "websocket_url": "/api/v1/commands/stream/ws"
    }


@router.websocket("/stream/ws")
async def stream_command_ws(websocket):
    """WebSocket endpoint for streaming command output"""
    await websocket.accept()
    
    try:
        while True:
            # Receive command from client
            data = await websocket.receive_text()
            request = CommandRequest.parse_raw(data)
            
            # Create execution request
            exec_request = ExecutionRequest(
                command=request.command,
                args=request.args,
                cwd=request.cwd,
                env=request.env,
                timeout=request.timeout,
                pty=request.pty,
                elevated=request.elevated,
                sandbox=request.sandbox
            )
            
            # Execute with streaming
            executor = ShellExecutor()
            async for output in executor.stream_output(exec_request):
                await websocket.send_text(output)
                
    except Exception as e:
        logger.error(f"Command WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))