# ClawMate Development Guide

This guide provides comprehensive information for developers working on ClawMate.

## Table of Contents

- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Backend Development](#backend-development)
- [Frontend Development](#frontend-development)
- [Skill Development](#skill-development)
- [Testing](#testing)
- [Docker Development](#docker-development)
- [Code Style](#code-style)
- [Debugging](#debugging)
- [Contributing](#contributing)

## Project Structure

```
clawmate/
├── core/                    # Backend Python application
│   ├── api/                # FastAPI endpoints
│   ├── agents/             # AI agent management
│   ├── executor.py         # Command execution engine
│   ├── ollama.py          # Ollama integration
│   └── main.py            # Application entry point
├── web/                    # Frontend Svelte application
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   └── package.json       # Dependencies
├── skills/                # External skills directory
│   └── example-skill/     # Example skill implementation
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Backend Dockerfile
├── nginx.conf            # Nginx reverse proxy config
├── Makefile              # Development commands
├── start.sh              # Development startup script
└── README.md             # Main documentation
```

## Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Docker (optional)
- Ollama (for AI features)

### Quick Start

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd clawmate
   make install
   ```

2. **Start development servers:**
   ```bash
   make start
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

### Manual Setup

#### Backend Setup

1. **Create virtual environment:**
   ```bash
   cd core
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start backend:**
   ```bash
   python main.py
   ```

#### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd web
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

## Backend Development

### Architecture

The backend follows a modular architecture with the following key components:

- **FastAPI**: Web framework for API endpoints
- **Ollama**: AI model integration
- **Executor**: Command execution engine
- **Agents**: AI agent management system

### Adding New API Endpoints

1. **Create endpoint in appropriate module:**
   ```python
   # core/api/new_endpoint.py
   from fastapi import APIRouter, HTTPException
   from pydantic import BaseModel
   
   router = APIRouter()
   
   class RequestModel(BaseModel):
       data: str
   
   @router.post("/new-endpoint")
   async def handle_new_endpoint(request: RequestModel):
       # Your logic here
       return {"message": "Success"}
   ```

2. **Register endpoint in main.py:**
   ```python
   from core.api.new_endpoint import router as new_endpoint_router
   
   app.include_router(new_endpoint_router, prefix="/api")
   ```

### Error Handling

Use FastAPI's HTTPException for proper error handling:

```python
from fastapi import HTTPException

@router.get("/example")
async def example_endpoint():
    if not condition:
        raise HTTPException(status_code=400, detail="Bad request")
    return {"data": "success"}
```

### Validation

Use Pydantic models for request/response validation:

```python
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
```

## Frontend Development

### Architecture

The frontend uses Svelte with the following structure:

- **Svelte Components**: Reusable UI components
- **Stores**: State management
- **Routes**: Page components
- **Utilities**: Shared functions and constants

### Component Development

1. **Create new component:**
   ```svelte
   <!-- src/components/NewComponent.svelte -->
   <script>
     import { createEventDispatcher } from 'svelte';
     
     const dispatch = createEventDispatcher();
     
     export let data;
     
     function handleClick() {
       dispatch('click', data);
     }
   </script>
   
   <div on:click={handleClick}>
     {data}
   </div>
   ```

2. **Use component:**
   ```svelte
   <!-- src/App.svelte -->
   <script>
     import NewComponent from './components/NewComponent.svelte';
     
     let items = ['item1', 'item2'];
   </script>
   
   {#each items as item}
     <NewComponent {item} on:click={(e) => console.log(e.detail)} />
   {/each}
   ```

### State Management

Use Svelte stores for state management:

```javascript
// src/stores/state.js
import { writable } from 'svelte/store';

export const userState = writable({
  name: '',
  isAuthenticated: false
});

export const updateUserName = (name) => {
  userState.update(state => ({ ...state, name }));
};
```

### Styling

Use Tailwind CSS for styling:

```svelte
<div class="bg-white rounded-lg shadow-md p-6">
  <h2 class="text-xl font-semibold text-gray-800 mb-4">
    Component Title
  </h2>
  <button class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
    Click me
  </button>
</div>
```

## Skill Development

### Skill Structure

Each skill should have the following structure:

```
skills/
└── my-skill/
    ├── manifest.json      # Skill metadata
    ├── scripts/
    │   ├── main.py       # Python implementation
    │   └── main.ps1      # PowerShell implementation
    └── README.md         # Documentation
```

### Manifest.json

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "A description of your skill",
  "tools": ["tool1", "tool2"],
  "entrypoint": "scripts/main.py",
  "windows": {
    "entrypoint": "scripts/main.ps1"
  }
}
```

### Python Implementation

```python
#!/usr/bin/env python3
"""
My custom skill for ClawMate.
"""

def tool1(param1: str, param2: int = 10) -> str:
    """
    Description of tool1.
    
    Args:
        param1 (str): First parameter
        param2 (int): Second parameter (optional)
        
    Returns:
        str: Result of the tool
    """
    return f"Tool1 result with {param1} and {param2}"

def tool2(data: list) -> dict:
    """
    Description of tool2.
    
    Args:
        data (list): Input data
        
    Returns:
        dict: Processed data
    """
    return {"processed": len(data), "items": data}

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <tool_name> [args...]")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    
    if tool_name == "tool1":
        param1 = sys.argv[2] if len(sys.argv) > 2 else "default"
        param2 = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        print(tool1(param1, param2))
    elif tool_name == "tool2":
        # Handle list parameters
        data = sys.argv[2:] if len(sys.argv) > 2 else []
        print(tool2(data))
    else:
        print(f"Unknown tool: {tool_name}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### PowerShell Implementation

```powershell
#!/usr/bin/env pwsh
<# 
.SYNOPSIS
My custom skill for ClawMate.

.PARAMETER ToolName
The name of the tool to execute

.PARAMETER Param1
First parameter for the tool
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("tool1", "tool2")]
    [string]$ToolName,
    
    [Parameter(Mandatory=$false)]
    [string]$Param1 = "default",
    
    [Parameter(Mandatory=$false)]
    [int]$Param2 = 10
)

function Invoke-Tool1 {
    param(
        [string]$Param1 = "default",
        [int]$Param2 = 10
    )
    return "Tool1 result with $Param1 and $Param2"
}

function Invoke-Tool2 {
    param(
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Data = @()
    )
    $result = [PSCustomObject]@{
        processed = $Data.Count
        items = $Data
    }
    return $result | ConvertTo-Json
}

switch ($ToolName) {
    "tool1" {
        Write-Output (Invoke-Tool1 -Param1 $Param1 -Param2 $Param2)
    }
    "tool2" {
        Write-Output (Invoke-Tool2 -Data $args)
    }
    default {
        Write-Error "Unknown tool: $ToolName"
        exit 1
    }
}
```

## Testing

### Backend Testing

Use pytest for backend testing:

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from core.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint():
    response = client.post("/api/chat", json={
        "message": "Hello",
        "context": []
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

Run tests:
```bash
cd core
pytest tests/
```

### Frontend Testing

Use Vitest for frontend testing:

```javascript
// src/tests/Component.test.js
import { render } from '@testing-library/svelte';
import Component from '../components/Component.svelte';

test('renders correctly', () => {
  const { getByText } = render(Component, { props: { message: 'Hello' } });
  expect(getByText('Hello')).toBeInTheDocument();
});
```

Run tests:
```bash
cd web
npm test
```

## Docker Development

### Development with Docker

1. **Build and start containers:**
   ```bash
   make docker-build
   make docker-start
   ```

2. **Access services:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop containers:**
   ```bash
   make docker-stop
   ```

### Customizing Docker

Edit `docker-compose.yml` to customize services:

```yaml
services:
  backend:
    build:
      context: ./core
      dockerfile: Dockerfile
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
    volumes:
      - ./core:/app
    ports:
      - "8000:8000"
```

## Code Style

### Python

- Use Black for code formatting
- Use isort for import sorting
- Follow PEP 8 guidelines
- Use type hints

```bash
cd core
black .
isort .
```

### JavaScript/TypeScript

- Use Prettier for code formatting
- Follow ESLint rules
- Use consistent naming conventions

```bash
cd web
npm run format
npm run lint
```

### Git Commit Messages

Use conventional commit format:

```
feat: add new authentication system
fix: resolve login timeout issue
docs: update API documentation
refactor: simplify component structure
test: add unit tests for API endpoints
```

## Debugging

### Backend Debugging

1. **Enable debug mode:**
   ```python
   # core/main.py
   if __name__ == "__main__":
       import uvicorn
       uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, debug=True)
   ```

2. **Add logging:**
   ```python
   import logging
   
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger(__name__)
   
   logger.debug("Debug message")
   logger.info("Info message")
   logger.error("Error message")
   ```

3. **Use breakpoints:**
   ```python
   import pdb; pdb.set_trace()  # Python debugger
   ```

### Frontend Debugging

1. **Browser Developer Tools:**
   - Use console for logging
   - Inspect network requests
   - Check component state

2. **Svelte DevTools:**
   - Install browser extension
   - Inspect component hierarchy
   - Monitor state changes

3. **Add debugging:**
   ```svelte
   <script>
     console.log('Component props:', { ...$$props });
   </script>
   ```

### Docker Debugging

1. **View container logs:**
   ```bash
   docker-compose logs [service-name]
   ```

2. **Execute commands in container:**
   ```bash
   docker-compose exec [service-name] bash
   ```

3. **Check container status:**
   ```bash
   docker-compose ps
   ```

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```
4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a pull request**

### Code Review Guidelines

- Ensure all tests pass
- Follow code style guidelines
- Add appropriate documentation
- Test changes locally
- Update relevant documentation

### Issue Reporting

When reporting issues, include:

- **Environment details** (OS, Python/Node.js version)
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Error messages and stack traces**
- **Screenshots** (if applicable)

### Feature Requests

When requesting features:

- **Describe the problem** you're trying to solve
- **Explain the proposed solution**
- **Include use cases and examples**
- **Consider backward compatibility**

## Performance Optimization

### Backend

- Use async/await for I/O operations
- Implement caching for expensive operations
- Optimize database queries
- Use connection pooling

### Frontend

- Implement lazy loading for components
- Use memoization for expensive calculations
- Optimize image loading
- Minimize bundle size

### Docker

- Use multi-stage builds
- Minimize image layers
- Use appropriate base images
- Implement health checks

## Security

### Best Practices

- Validate all user inputs
- Use environment variables for secrets
- Implement proper authentication
- Use HTTPS in production
- Regularly update dependencies

### Environment Variables

Use `.env` files for development:

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost/db
SECRET_KEY=your-secret-key
DEBUG=true
```

### Dependency Security

Regularly check for vulnerabilities:

```bash
# Python
pip-audit

# Node.js
npm audit
```

This guide provides a comprehensive overview of ClawMate development. For specific questions or issues, refer to the relevant section or create an issue in the repository.