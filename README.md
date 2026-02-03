# ClawMate - Cross-Platform Personal Assistant

A powerful, local-first AI personal assistant built with Python and Node.js, designed for Windows 11 and Linux. Features agentic capabilities, containerized swarm processing, and seamless Ollama integration.

## 🚀 Features

### Core Capabilities
- **Cross-Platform**: Works on Windows 11 and Linux with unified interface
- **Local AI**: Powered by Ollama for privacy-focused, offline operation
- **Agentic Swarm**: Multi-agent orchestration with container support
- **Terminal Integration**: Native shell access with PTY support
- **Web Interface**: Modern, responsive web dashboard
- **Skill System**: Extensible plugin architecture

### AI Modes
- **Assist**: Answer questions and analyze files
- **Guided**: Propose actions with user approval
- **Autonomous**: Execute multi-step workflows
- **Swarm**: Parallel agent execution with containerization

### Security & Control
- **3-Tier Approval**: Auto, prompt, or defer approval modes
- **Sandboxing**: Containerized execution for untrusted operations
- **User Control**: Full control over agent actions and permissions

## 🛠️ Architecture

```
clawmate/
├── core/                    # Python backend (FastAPI)
│   ├── api/                 # REST/WebSocket APIs
│   ├── ollama/              # Ollama integration
│   ├── executor/            # Cross-platform shell
│   ├── agents/              # Agent orchestration
│   ├── skills/              # Skill system
│   └── swarm/               # Container orchestration
├── web/                     # Node.js frontend
│   ├── src/
│   │   ├── components/      # Svelte components
│   │   ├── lib/terminal/    # Terminal interface
│   │   └── routes/          # Pages
├── skills/                  # User skills directory
└── containers/              # Docker configurations
```

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (for local AI)
- Docker (optional, for containerized swarm)

### Quick Start

#### Option 1: Automatic Setup (Recommended)
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

#### Option 2: Manual Setup

1. **Clone and setup**
```bash
git clone <repository-url>
cd clawmate
```

2. **Install Python dependencies**
```bash
cd core
pip install -r requirements.txt
```

3. **Install web dependencies**
```bash
cd ../web
npm install
```

4. **Start Ollama and pull a model**
```bash
ollama serve  # In a separate terminal
ollama pull qwen3-coder:latest
```

5. **Run the application**
```bash
# Terminal 1: Start backend
cd core
python main.py

# Terminal 2: Start frontend
cd ../web
npm run dev
```

6. **Access the interface**
- Web UI: http://localhost:3000
- API: http://localhost:8000

## 🎯 Usage

### Web Interface
The web interface provides a modern dashboard with:
- **Chat Interface**: Natural language interaction
- **Terminal**: Full shell access with streaming output
- **Skills Management**: Install and manage custom skills
- **System Monitoring**: Real-time system information

### Command Line
```bash
# Start the backend server
python core/main.py

# Start the frontend development server
cd web && npm run dev

# Build production frontend
cd web && npm run build
```

### API Usage
```bash
# Health check
curl http://localhost:8000/health

# Chat with AI
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'

# Execute commands
curl -X POST http://localhost:8000/api/v1/commands/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "ls", "args": [], "pty": true}'
```

## 🔧 Configuration

### Environment Variables
```bash
# Server settings
CLAWMATE_HOST=127.0.0.1
CLAWMATE_PORT=8000

# Ollama settings
CLAWMATE_OLLAMA_HOST=http://127.0.0.1:11434
CLAWMATE_OLLAMA_MODEL=qwen3-coder:latest

# Agent settings
CLAWMATE_MAX_CONCURRENT_AGENTS=4
CLAWMATE_AGENT_TIMEOUT=600

# Security settings
CLAWMATE_APPROVAL_REQUIRED=true
CLAWMATE_SANDBOX_MODE=true
```

### Configuration File
Create `.env` file in the project root:
```env
CLAWMATE_HOST=127.0.0.1
CLAWMATE_PORT=8000
CLAWMATE_OLLAMA_MODEL=qwen3-coder:latest
CLAWMATE_MAX_CONCURRENT_AGENTS=4
CLAWMATE_APPROVAL_REQUIRED=true
```

## 🧠 Skills System

### Built-in Skills
- **Service Desk**: Help desk automation and support
- **Dev Helper**: Development assistance and code analysis
- **SysAdmin**: System administration and monitoring

### Creating Custom Skills

1. **Create skill directory**
```bash
mkdir skills/my-custom-skill
```

2. **Create skill manifest**
```json
{
  "name": "my-custom-skill",
  "version": "1.0.0",
  "description": "A custom skill for ClawMate",
  "tools": ["bash", "git", "file"],
  "entrypoint": "scripts/main.py",
  "windows": {
    "entrypoint": "scripts/main.ps1"
  }
}
```

3. **Implement skill logic**
```python
# skills/my-custom-skill/scripts/main.py
from clawmate.skills import skill, tool

@skill(name="my-custom-skill", version="1.0.0")
class MyCustomSkill:
    @tool("analyze_code")
    async def analyze_code(self, path: str) -> str:
        # Your skill implementation
        return f"Analyzed code at {path}"
```

4. **Install skill**
```bash
# Via API
curl -X POST http://localhost:8000/api/v1/skills/install/my-custom-skill

# Via web interface
# Navigate to Skills page and click "Install"
```

## 🐳 Container Support

### Swarm Mode
For heavy workloads, agents can run in isolated containers:

```bash
# Enable container mode
export CLAWMATE_USE_CONTAINERS=true

# Start with Docker
docker-compose up -d
```

### Docker Compose
```yaml
version: '3.8'
services:
  clawmate-core:
    build: ./core
    ports:
      - "8000:8000"
    environment:
      - CLAWMATE_USE_CONTAINERS=true
    volumes:
      - ./skills:/app/skills
      - /var/run/docker.sock:/var/run/docker.sock

  clawmate-web:
    build: ./web
    ports:
      - "3000:3000"
    depends_on:
      - clawmate-core
```

## 🔒 Security

### Approval Modes
- **Auto**: Safe read-only operations execute immediately
- **Prompt**: User approval required before execution
- **Defer**: Batch approval for multiple operations

### Sandboxing
- **Containerized**: Untrusted code runs in isolated containers
- **Elevated**: User permissions for system operations
- **Admin**: Explicit sudo/admin access (requires confirmation)

### Best Practices
1. Use sandbox mode for untrusted operations
2. Review agent actions before approval
3. Limit container resource usage
4. Regularly update Ollama models

## 🚀 Deployment

### Production Setup
1. **Build frontend**
```bash
cd web
npm run build
```

2. **Configure reverse proxy**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Run with systemd**
```bash
# Create service files for core and web
sudo systemctl enable clawmate-core
sudo systemctl enable clawmate-web
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: [API Reference](docs/api.md)
- **Examples**: [Example Skills](examples/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/clawmate/issues)

## 🙏 Acknowledgments

- Built on [Ollama](https://ollama.ai) for local AI
- Uses [FastAPI](https://fastapi.tiangolo.com) for backend
- Frontend powered by [Svelte](https://svelte.dev)
- Terminal interface with [xterm.js](https://xtermjs.org)
# HelpMate
# ClawMate - Cross-Platform Personal Assistant

A powerful, local-first AI personal assistant built with Python and Node.js, designed for Windows 11 and Linux. Features agentic capabilities, containerized swarm processing, and seamless Ollama integration.

## 🚀 Features

### Core Capabilities
- **Cross-Platform**: Works on Windows 11 and Linux with unified interface
- **Local AI**: Powered by Ollama for privacy-focused, offline operation
- **Agentic Swarm**: Multi-agent orchestration with container support
- **Terminal Integration**: Native shell access with PTY support
- **Web Interface**: Modern, responsive web dashboard
- **Skill System**: Extensible plugin architecture

### AI Modes
- **Assist**: Answer questions and analyze files
- **Guided**: Propose actions with user approval
- **Autonomous**: Execute multi-step workflows
- **Swarm**: Parallel agent execution with containerization

### Security & Control
- **3-Tier Approval**: Auto, prompt, or defer approval modes
- **Sandboxing**: Containerized execution for untrusted operations
- **User Control**: Full control over agent actions and permissions

## 🛠️ Architecture

```
clawmate/
├── core/                    # Python backend (FastAPI)
│   ├── api/                 # REST/WebSocket APIs
│   ├── ollama/              # Ollama integration
│   ├── executor/            # Cross-platform shell
│   ├── agents/              # Agent orchestration
│   ├── skills/              # Skill system
│   └── swarm/               # Container orchestration
├── web/                     # Node.js frontend
│   ├── src/
│   │   ├── components/      # Svelte components
│   │   ├── lib/terminal/    # Terminal interface
│   │   └── routes/          # Pages
├── skills/                  # User skills directory
└── containers/              # Docker configurations
```

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (for local AI)
- Docker (optional, for containerized swarm)

### Quick Start

1. **Clone and setup**
```bash
git clone <repository-url>
cd clawmate
```

2. **Install Python dependencies**
```bash
cd core
pip install -r requirements.txt
```

3. **Install web dependencies**
```bash
cd ../web
npm install
```

4. **Start Ollama and pull a model**
```bash
ollama pull qwen3-coder:latest
```

5. **Run the application**
```bash
# Terminal 1: Start backend
cd core
python main.py

# Terminal 2: Start frontend
cd ../web
npm run dev
```

6. **Access the interface**
- Web UI: http://localhost:3000
- API: http://localhost:8000

## 🎯 Usage

### Web Interface
The web interface provides a modern dashboard with:
- **Chat Interface**: Natural language interaction
- **Terminal**: Full shell access with streaming output
- **Skills Management**: Install and manage custom skills
- **System Monitoring**: Real-time system information

### Command Line
```bash
# Start the backend server
python core/main.py

# Start the frontend development server
cd web && npm run dev

# Build production frontend
cd web && npm run build
```

### API Usage
```bash
# Health check
curl http://localhost:8000/health

# Chat with AI
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'

# Execute commands
curl -X POST http://localhost:8000/api/v1/commands/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "ls", "args": [], "pty": true}'
```

## 🔧 Configuration

### Environment Variables
```bash
# Server settings
CLAWMATE_HOST=127.0.0.1
CLAWMATE_PORT=8000

# Ollama settings
CLAWMATE_OLLAMA_HOST=http://127.0.0.1:11434
CLAWMATE_OLLAMA_MODEL=qwen3-coder:latest

# Agent settings
CLAWMATE_MAX_CONCURRENT_AGENTS=4
CLAWMATE_AGENT_TIMEOUT=600

# Security settings
CLAWMATE_APPROVAL_REQUIRED=true
CLAWMATE_SANDBOX_MODE=true
```

### Configuration File
Create `.env` file in the project root:
```env
CLAWMATE_HOST=127.0.0.1
CLAWMATE_PORT=8000
CLAWMATE_OLLAMA_MODEL=qwen3-coder:latest
CLAWMATE_MAX_CONCURRENT_AGENTS=4
CLAWMATE_APPROVAL_REQUIRED=true
```

## 🧠 Skills System

### Built-in Skills
- **Service Desk**: Help desk automation and support
- **Dev Helper**: Development assistance and code analysis
- **SysAdmin**: System administration and monitoring

### Creating Custom Skills

1. **Create skill directory**
```bash
mkdir skills/my-custom-skill
```

2. **Create skill manifest**
```json
{
  "name": "my-custom-skill",
  "version": "1.0.0",
  "description": "A custom skill for ClawMate",
  "tools": ["bash", "git", "file"],
  "entrypoint": "scripts/main.py",
  "windows": {
    "entrypoint": "scripts/main.ps1"
  }
}
```

3. **Implement skill logic**
```python
# skills/my-custom-skill/scripts/main.py
from clawmate.skills import skill, tool

@skill(name="my-custom-skill", version="1.0.0")
class MyCustomSkill:
    @tool("analyze_code")
    async def analyze_code(self, path: str) -> str:
        # Your skill implementation
        return f"Analyzed code at {path}"
```

4. **Install skill**
```bash
# Via API
curl -X POST http://localhost:8000/api/v1/skills/install/my-custom-skill

# Via web interface
# Navigate to Skills page and click "Install"
```

## 🐳 Container Support

### Swarm Mode
For heavy workloads, agents can run in isolated containers:

```bash
# Enable container mode
export CLAWMATE_USE_CONTAINERS=true

# Start with Docker
docker-compose up -d
```

### Docker Compose
```yaml
version: '3.8'
services:
  clawmate-core:
    build: ./core
    ports:
      - "8000:8000"
    environment:
      - CLAWMATE_USE_CONTAINERS=true
    volumes:
      - ./skills:/app/skills
      - /var/run/docker.sock:/var/run/docker.sock

  clawmate-web:
    build: ./web
    ports:
      - "3000:3000"
    depends_on:
      - clawmate-core
```

## 🔒 Security

### Approval Modes
- **Auto**: Safe read-only operations execute immediately
- **Prompt**: User approval required before execution
- **Defer**: Batch approval for multiple operations

### Sandboxing
- **Containerized**: Untrusted code runs in isolated containers
- **Elevated**: User permissions for system operations
- **Admin**: Explicit sudo/admin access (requires confirmation)

### Best Practices
1. Use sandbox mode for untrusted operations
2. Review agent actions before approval
3. Limit container resource usage
4. Regularly update Ollama models

## 🚀 Deployment

### Production Setup
1. **Build frontend**
```bash
cd web
npm run build
```

2. **Configure reverse proxy**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Run with systemd**
```bash
# Create service files for core and web
sudo systemctl enable clawmate-core
sudo systemctl enable clawmate-web
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: [API Reference](docs/api.md)
- **Examples**: [Example Skills](examples/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/clawmate/issues)

## 🙏 Acknowledgments

- Built on [Ollama](https://ollama.ai) for local AI
- Uses [FastAPI](https://fastapi.tiangolo.com) for backend
- Frontend powered by [Svelte](https://svelte.dev)
- Terminal interface with [xterm.js](https://xtermjs.org)
>>>>>>> f2e6ad5 (Initial commit: Complete ClawMate AI assistant implementation with Python backend, Svelte frontend, Ollama integration, and skill system)
=======
# ClawMate - Cross-Platform Personal Assistant

A powerful, local-first AI personal assistant built with Python and Node.js, designed for Windows 11 and Linux. Features agentic capabilities, containerized swarm processing, and seamless Ollama integration.

## 🚀 Features

### Core Capabilities
- **Cross-Platform**: Works on Windows 11 and Linux with unified interface
- **Local AI**: Powered by Ollama for privacy-focused, offline operation
- **Agentic Swarm**: Multi-agent orchestration with container support
- **Terminal Integration**: Native shell access with PTY support
- **Web Interface**: Modern, responsive web dashboard
- **Skill System**: Extensible plugin architecture

### AI Modes
- **Assist**: Answer questions and analyze files
- **Guided**: Propose actions with user approval
- **Autonomous**: Execute multi-step workflows
- **Swarm**: Parallel agent execution with containerization

### Security & Control
- **3-Tier Approval**: Auto, prompt, or defer approval modes
- **Sandboxing**: Containerized execution for untrusted operations
- **User Control**: Full control over agent actions and permissions

## 🛠️ Architecture

```
clawmate/
├── core/                    # Python backend (FastAPI)
│   ├── api/                 # REST/WebSocket APIs
│   ├── ollama/              # Ollama integration
│   ├── executor/            # Cross-platform shell
│   ├── agents/              # Agent orchestration
│   ├── skills/              # Skill system
│   └── swarm/               # Container orchestration
├── web/                     # Node.js frontend
│   ├── src/
│   │   ├── components/      # Svelte components
│   │   ├── lib/terminal/    # Terminal interface
│   │   └── routes/          # Pages
├── skills/                  # User skills directory
└── containers/              # Docker configurations
```

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (for local AI)
- Docker (optional, for containerized swarm)

### Quick Start

1. **Clone and setup**
```bash
git clone <repository-url>
cd clawmate
```

2. **Install Python dependencies**
```bash
cd core
pip install -r requirements.txt
```

3. **Install web dependencies**
```bash
cd ../web
npm install
```

4. **Start Ollama and pull a model**
```bash
ollama pull qwen3-coder:latest
```

5. **Run the application**
```bash
# Terminal 1: Start backend
cd core
python main.py

# Terminal 2: Start frontend
cd ../web
npm run dev
```

6. **Access the interface**
- Web UI: http://localhost:3000
- API: http://localhost:8000

## 🎯 Usage

### Web Interface
The web interface provides a modern dashboard with:
- **Chat Interface**: Natural language interaction
- **Terminal**: Full shell access with streaming output
- **Skills Management**: Install and manage custom skills
- **System Monitoring**: Real-time system information

### Command Line
```bash
# Start the backend server
python core/main.py

# Start the frontend development server
cd web && npm run dev

# Build production frontend
cd web && npm run build
```

### API Usage
```bash
# Health check
curl http://localhost:8000/health

# Chat with AI
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'

# Execute commands
curl -X POST http://localhost:8000/api/v1/commands/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "ls", "args": [], "pty": true}'
```

## 🔧 Configuration

### Environment Variables
```bash
# Server settings
CLAWMATE_HOST=127.0.0.1
CLAWMATE_PORT=8000

# Ollama settings
CLAWMATE_OLLAMA_HOST=http://127.0.0.1:11434
CLAWMATE_OLLAMA_MODEL=qwen3-coder:latest

# Agent settings
CLAWMATE_MAX_CONCURRENT_AGENTS=4
CLAWMATE_AGENT_TIMEOUT=600

# Security settings
CLAWMATE_APPROVAL_REQUIRED=true
CLAWMATE_SANDBOX_MODE=true
```

### Configuration File
Create `.env` file in the project root:
```env
CLAWMATE_HOST=127.0.0.1
CLAWMATE_PORT=8000
CLAWMATE_OLLAMA_MODEL=qwen3-coder:latest
CLAWMATE_MAX_CONCURRENT_AGENTS=4
CLAWMATE_APPROVAL_REQUIRED=true
```

## 🧠 Skills System

### Built-in Skills
- **Service Desk**: Help desk automation and support
- **Dev Helper**: Development assistance and code analysis
- **SysAdmin**: System administration and monitoring

### Creating Custom Skills

1. **Create skill directory**
```bash
mkdir skills/my-custom-skill
```

2. **Create skill manifest**
```json
{
  "name": "my-custom-skill",
  "version": "1.0.0",
  "description": "A custom skill for ClawMate",
  "tools": ["bash", "git", "file"],
  "entrypoint": "scripts/main.py",
  "windows": {
    "entrypoint": "scripts/main.ps1"
  }
}
```

3. **Implement skill logic**
```python
# skills/my-custom-skill/scripts/main.py
from clawmate.skills import skill, tool

@skill(name="my-custom-skill", version="1.0.0")
class MyCustomSkill:
    @tool("analyze_code")
    async def analyze_code(self, path: str) -> str:
        # Your skill implementation
        return f"Analyzed code at {path}"
```

4. **Install skill**
```bash
# Via API
curl -X POST http://localhost:8000/api/v1/skills/install/my-custom-skill

# Via web interface
# Navigate to Skills page and click "Install"
```

## 🐳 Container Support

### Swarm Mode
For heavy workloads, agents can run in isolated containers:

```bash
# Enable container mode
export CLAWMATE_USE_CONTAINERS=true

# Start with Docker
docker-compose up -d
```

### Docker Compose
```yaml
version: '3.8'
services:
  clawmate-core:
    build: ./core
    ports:
      - "8000:8000"
    environment:
      - CLAWMATE_USE_CONTAINERS=true
    volumes:
      - ./skills:/app/skills
      - /var/run/docker.sock:/var/run/docker.sock

  clawmate-web:
    build: ./web
    ports:
      - "3000:3000"
    depends_on:
      - clawmate-core
```

## 🔒 Security

### Approval Modes
- **Auto**: Safe read-only operations execute immediately
- **Prompt**: User approval required before execution
- **Defer**: Batch approval for multiple operations

### Sandboxing
- **Containerized**: Untrusted code runs in isolated containers
- **Elevated**: User permissions for system operations
- **Admin**: Explicit sudo/admin access (requires confirmation)

### Best Practices
1. Use sandbox mode for untrusted operations
2. Review agent actions before approval
3. Limit container resource usage
4. Regularly update Ollama models

## 🚀 Deployment

### Production Setup
1. **Build frontend**
```bash
cd web
npm run build
```

2. **Configure reverse proxy**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Run with systemd**
```bash
# Create service files for core and web
sudo systemctl enable clawmate-core
sudo systemctl enable clawmate-web
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: [API Reference](docs/api.md)
- **Examples**: [Example Skills](examples/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/clawmate/issues)

## 🙏 Acknowledgments

- Built on [Ollama](https://ollama.ai) for local AI
- Uses [FastAPI](https://fastapi.tiangolo.com) for backend
- Frontend powered by [Svelte](https://svelte.dev)
- Terminal interface with [xterm.js](https://xtermjs.org)
>>>>>>> f2e6ad5 (Initial commit: Complete ClawMate AI assistant implementation with Python backend, Svelte frontend, Ollama integration, and skill system)
