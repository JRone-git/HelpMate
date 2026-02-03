from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, AsyncGenerator
import json
import logging

from ollama import Message, OllamaClient
from executor import ExecutionRequest, ShellExecutor

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = False
    model: str = None


class CommandRequest(BaseModel):
    command: str
    args: List[str] = []
    cwd: str = None
    timeout: int = None
    pty: bool = False
    elevated: bool = False
    sandbox: bool = False


@router.post("/send")
async def send_message(request: ChatRequest):
    """Send a message to the AI assistant"""
    try:
        # Convert to internal Message format
        messages = [Message(role=msg.role, content=msg.content) for msg in request.messages]
        
        # Get Ollama client
        ollama = OllamaClient()
        
        if request.stream:
            # Return streaming response
            async def stream_response():
                async for response in ollama.chat_stream(messages, request.model):
                    yield f"data: {response.json()}\n\n"
            
            return StreamingResponse(stream_response(), media_type="text/event-stream")
        else:
            # Return complete response
            response = await ollama.chat(messages, request.model)
            return {
                "message": response.message.content,
                "model": response.model,
                "done": response.done
            }
            
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            request = json.loads(data)
            
            # Process message
            messages = [Message(role=msg["role"], content=msg["content"]) for msg in request["messages"]]
            
            # Send to Ollama
            ollama = OllamaClient()
            async for response in ollama.chat_stream(messages, request.get("model")):
                await websocket.send_text(response.json())
                
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))


@router.post("/command")
async def execute_command(request: CommandRequest):
    """Execute a shell command"""
    try:
        # Create execution request
        exec_request = ExecutionRequest(
            command=request.command,
            args=request.args,
            cwd=request.cwd,
            timeout=request.timeout,
            pty=request.pty,
            elevated=request.elevated,
            sandbox=request.sandbox
        )
        
        # Execute command
        executor = ShellExecutor()
        result = await executor.execute(exec_request)
        
        return {
            "command": result.command,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": result.duration,
            "pid": result.pid
        }
        
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/command/ws")
async def command_websocket(websocket: WebSocket):
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
                timeout=request.timeout,
                pty=request.pty,
                elevated=request.elevated,
                sandbox=request.sandbox
            )
            
            # Execute with streaming
            executor = ShellExecutor()
            async for output in executor.stream_output(exec_request):
                await websocket.send_text(output)
                
    except WebSocketDisconnect:
        logger.info("Command client disconnected")
    except Exception as e:
        logger.error(f"Command WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))