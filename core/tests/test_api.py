import pytest
from fastapi.testclient import TestClient
from main import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "ollama_connected" in data
    assert "skills_loaded" in data
    assert data["status"] == "healthy"


def test_chat_endpoint(client):
    """Test chat endpoint"""
    response = client.post("/api/v1/chat", json={
        "message": "Hello",
        "context": []
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "context" in data


def test_skills_endpoint(client):
    """Test skills endpoint"""
    response = client.get("/api/v1/skills")
    assert response.status_code == 200
    
    data = response.json()
    assert "skills" in data
    assert isinstance(data["skills"], list)


def test_execute_command_endpoint(client):
    """Test execute command endpoint"""
    response = client.post("/api/v1/execute", json={
        "command": "echo test",
        "timeout": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "output" in data
    assert "success" in data


def test_system_info_endpoint(client):
    """Test system info endpoint"""
    response = client.get("/api/v1/system")
    assert response.status_code == 200
    
    data = response.json()
    assert "platform" in data
    assert "python_version" in data
    assert "working_directory" in data