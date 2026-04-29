"""
Pytest configuration and fixtures for the Mergington High School Activities API tests.
"""

import pytest
from fastapi.testclient import TestClient
import app as app_module


@pytest.fixture
def test_activities():
    """
    Provides test data for activities that can be used across tests.
    This fixture returns a dictionary of test activities with isolated test data.
    """
    return {
        "Test Activity 1": {
            "description": "A test activity for unit tests",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 2,
            "participants": ["alice@test.edu", "bob@test.edu"]
        },
        "Test Activity 2": {
            "description": "Another test activity",
            "schedule": "Wednesdays, 2:00 PM - 3:00 PM",
            "max_participants": 3,
            "participants": ["charlie@test.edu"]
        },
        "Test Activity 3": {
            "description": "A third test activity with no participants",
            "schedule": "Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 5,
            "participants": []
        }
    }


@pytest.fixture
def client_with_test_data(monkeypatch, test_activities):
    """
    Provides a TestClient with test data pre-loaded into the app.
    Uses monkeypatch to replace the module-level activities dictionary.
    Each test gets fresh test data for isolation.
    """
    # Store original activities
    original_activities = app_module.activities.copy()
    
    # Replace with test activities
    monkeypatch.setattr(app_module, "activities", test_activities.copy())
    
    # Create and return the test client
    client = TestClient(app_module.app)
    
    yield client
    
    # Cleanup is automatic with monkeypatch


@pytest.fixture
def client():
    """
    Provides a TestClient for making requests to the FastAPI application.
    This fixture uses the actual app data (not test data).
    """
    return TestClient(app_module.app)
