# ClawMate Makefile

.PHONY: help install start stop clean build docker-build docker-start docker-stop docker-clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install Python and Node.js dependencies"
	@echo "  start       - Start the application (backend + frontend)"
	@echo "  stop        - Stop the application"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build the application"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-start - Start Docker containers"
	@echo "  docker-stop  - Stop Docker containers"
	@echo "  docker-clean - Clean Docker containers and images"

# Install dependencies
install:
	@echo "📦 Installing Python dependencies..."
	cd core && pip install -r requirements.txt
	@echo "📦 Installing Node.js dependencies..."
	cd web && npm install

# Start application
start:
	@echo "🐍 Starting backend server..."
	cd core && python main.py &
	@echo "🌐 Starting frontend server..."
	sleep 3
	cd web && npm run dev &

# Stop application
stop:
	@echo "🛑 Stopping application..."
	pkill -f "python main.py" || true
	pkill -f "npm run dev" || true

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf core/__pycache__/
	rm -rf web/node_modules/
	rm -rf web/dist/
	rm -rf web/.svelte-kit/

# Build application
build:
	@echo "🔨 Building application..."
	cd web && npm run build

# Docker commands
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-start:
	@echo "🚀 Starting Docker containers..."
	docker-compose up -d

docker-stop:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down

docker-clean:
	@echo "🧹 Cleaning Docker containers and images..."
	docker-compose down -v --remove-orphans
	docker system prune -f