import asyncio
import logging
import os
import platform
import shlex
import subprocess
import sys
from asyncio import create_subprocess_exec, subprocess as async_subprocess
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Union

import psutil
from pydantic import BaseModel

from .config import settings

logger = logging.getLogger(__name__)


class ExecutionResult(BaseModel):
    """Command execution result"""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    pid: Optional[int] = None


class ExecutionRequest(BaseModel):
    """Command execution request"""
    command: str
    args: List[str] = []
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    pty: bool = False
    elevated: bool = False
    sandbox: bool = False


class ShellExecutor:
    """Cross-platform shell command executor"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.shell = self._get_shell()
        
    def _get_shell(self) -> str:
        """Get appropriate shell for platform"""
        if self.platform == "windows":
            return "powershell.exe"
        else:
            return "/bin/bash"
    
    def _build_command(self, request: ExecutionRequest) -> List[str]:
        """Build command for execution"""
        if self.platform == "windows":
            if request.pty:
                # Use ConPTY for Windows
                cmd = ["powershell.exe", "-NoProfile", "-Command", request.command]
            else:
                cmd = ["powershell.exe", "-NoProfile", "-Command", request.command]
        else:
            if request.pty:
                # Use script command for PTY
                cmd = ["script", "-qec", request.command, "/dev/null"]
            else:
                cmd = [self.shell, "-c", request.command]
        
        return cmd
    
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute command with timeout and proper cleanup"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Build environment
            env = os.environ.copy()
            if request.env:
                env.update(request.env)
            
            # Build command
            cmd = self._build_command(request)
            
            # Handle sandboxing
            if request.sandbox and settings.use_containers:
                return await self._execute_in_container(request, env)
            
            # Execute command
            process = await create_subprocess_exec(
                *cmd,
                stdout=async_subprocess.PIPE,
                stderr=async_subprocess.PIPE,
                stdin=async_subprocess.PIPE if request.pty else None,
                cwd=request.cwd,
                env=env,
                shell=False
            )
            
            # Set timeout
            timeout = request.timeout or settings.ollama_timeout
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                # Kill process on timeout
                process.kill()
                await process.wait()
                raise TimeoutError(f"Command timed out after {timeout} seconds")
            
            duration = asyncio.get_event_loop().time() - start_time
            
            return ExecutionResult(
                command=request.command,
                exit_code=process.returncode,
                stdout=stdout.decode('utf-8', errors='replace'),
                stderr=stderr.decode('utf-8', errors='replace'),
                duration=duration,
                pid=process.pid
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            logger.error(f"Command execution failed: {e}")
            
            return ExecutionResult(
                command=request.command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration=duration
            )
    
    async def _execute_in_container(self, request: ExecutionRequest, env: Dict) -> ExecutionResult:
        """Execute command in Docker container"""
        try:
            import docker
            
            client = docker.from_env()
            
            # Create container
            container = client.containers.run(
                image="ubuntu:latest",  # Base image
                command=request.command,
                environment=env,
                working_dir=request.cwd,
                detach=True,
                remove=True,
                stdout=True,
                stderr=True
            )
            
            # Wait for completion
            result = container.wait()
            logs = container.logs().decode('utf-8')
            
            return ExecutionResult(
                command=request.command,
                exit_code=result['StatusCode'],
                stdout=logs,
                stderr="",
                duration=0,  # Container timing is complex
                pid=None
            )
            
        except Exception as e:
            logger.error(f"Container execution failed: {e}")
            raise
    
    async def stream_output(self, request: ExecutionRequest) -> AsyncGenerator[str, None]:
        """Stream command output in real-time"""
        try:
            # Build environment
            env = os.environ.copy()
            if request.env:
                env.update(request.env)
            
            # Build command
            cmd = self._build_command(request)
            
            # Execute with streaming
            process = await create_subprocess_exec(
                *cmd,
                stdout=async_subprocess.PIPE,
                stderr=async_subprocess.PIPE,
                stdin=async_subprocess.PIPE if request.pty else None,
                cwd=request.cwd,
                env=env,
                shell=False
            )
            
            # Stream output
            while True:
                if process.stdout:
                    line = await process.stdout.readline()
                    if line:
                        yield line.decode('utf-8', errors='replace')
                    elif process.returncode is not None:
                        break
                
                if process.stderr:
                    line = await process.stderr.readline()
                    if line:
                        yield line.decode('utf-8', errors='replace')
                    elif process.returncode is not None:
                        break
                
                await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Stream output failed: {e}")
            yield f"Error: {e}"
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        return {
            "platform": self.platform,
            "shell": self.shell,
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').total if self.platform != "windows" else psutil.disk_usage('C:').total
        }
    
    def is_command_available(self, command: str) -> bool:
        """Check if command is available"""
        try:
            if self.platform == "windows":
                result = subprocess.run(
                    ["where", command],
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    ["which", command],
                    capture_output=True,
                    text=True
                )
            return result.returncode == 0
        except Exception:
            return False