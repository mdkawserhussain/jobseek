import pytest
from app import app, db
from models import User

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory database for tests
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client  # Run the test
        with app.app_context():
            db.drop_all()

def test_register(client):
    response = client.post("/register", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 302  # Redirect to login page

def test_login(client):
    client.post("/register", json={"email": "test@example.com", "password": "password123"})
    response = client.post("/login", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 302  # Redirect to dashboard

def test_dashboard_access(client):
    client.post("/register", json={"email": "test@example.com", "password": "password123"})
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get("/dashboard")
    assert b"Please log in first" not in response.data  # User should be logged in
