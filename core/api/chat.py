from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, AsyncGenerator, Optional
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
    model: Optional[str] = None


class CommandRequest(BaseModel):
    command: str
    args: List[str] = []
    cwd: Optional[str] = None
    env: Optional[dict] = None
    timeout: Optional[int] = None
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
            try:
                request = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                continue
            
            # Process message
            if "messages" not in request:
                await websocket.send_text(json.dumps({"error": "No messages provided"}))
                continue
                
            messages = [Message(role=msg["role"], content=msg["content"]) for msg in request["messages"]]
            
            # Send to Ollama
            ollama = OllamaClient()
            try:
                async for response in ollama.chat_stream(messages, request.get("model")):
                    await websocket.send_text(response.json())
            except Exception as e:
                await websocket.send_text(json.dumps({"error": f"Ollama error: {str(e)}"}))
                
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
            env=request.env,
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
            try:
                request = CommandRequest.parse_raw(data)
            except Exception as e:
                await websocket.send_text(json.dumps({"error": f"Invalid request: {str(e)}"}))
                continue
            
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
            try:
                async for output in executor.stream_output(exec_request):
                    await websocket.send_text(output)
            except Exception as e:
                await websocket.send_text(json.dumps({"error": f"Execution error: {str(e)}"}))
                
    except WebSocketDisconnect:
        logger.info("Command client disconnected")
    except Exception as e:
        logger.error(f"Command WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))
