#!/usr/bin/env python3
"""
Example skill for ClawMate demonstrating the skill system.
This skill provides simple tools for demonstration purposes.
"""

import platform
import os
import sys
from datetime import datetime


def hello(name: str = "World") -> str:
    """
    A simple hello world tool.
    
    Args:
        name (str): Name to greet
        
    Returns:
        str: Greeting message
    """
    return f"Hello, {name}! This is the example skill speaking."


def system_info() -> str:
    """
    Get basic system information.
    
    Returns:
        str: Formatted system information
    """
    info = {
        "Platform": platform.platform(),
        "Python Version": sys.version.split()[0],
        "Current Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Working Directory": os.getcwd(),
        "OS": platform.system(),
        "Architecture": platform.architecture()[0],
        "Processor": platform.processor()
    }
    
    result = "System Information:\n"
    for key, value in info.items():
        result += f"  {key}: {value}\n"
    
    return result


def main():
    """Main entry point for the example skill."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <tool_name> [args...]")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    
    if tool_name == "hello":
        name = sys.argv[2] if len(sys.argv) > 2 else "World"
        print(hello(name))
    elif tool_name == "system_info":
        print(system_info())
    else:
        print(f"Unknown tool: {tool_name}")
        print("Available tools: hello, system_info")
        sys.exit(1)


if __name__ == "__main__":
    main()