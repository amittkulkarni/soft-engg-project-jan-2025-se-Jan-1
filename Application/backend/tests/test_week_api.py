# test_week_api.py
# 🚦 Test Case for the `POST /weeks` API
from models import User, Week
from conftest import db
def test_create_week(client):
    """Test the API endpoint to create a new week."""
    # ✅ Valid input data
    input_data = {
        "week_number": 13,
        "title": "Week 13 - Introduction"
    }
    response = client.post('/weeks', json=input_data)
    
    assert response.status_code == 201
    assert response.json["success"] is True
    assert response.json["message"] == "New week added successfully"
    
    # Check if the week was actually added to the database
    new_week = Week.query.filter_by(week_number=13).first()
    assert new_week is not None
    assert new_week.title == input_data["title"]

# 🚦 Test Case for Invalid Week Number
def test_create_week_invalid_week_number(client):
    """Test creating a week with an invalid week number."""
    input_data = {
        "week_number": -1,  # Invalid week number
        "title": "Week -1"
    }
    response = client.post('/weeks', json=input_data)
    
    assert response.status_code == 400
    assert response.json["success"] is False
    assert "Invalid week number" in response.json["message"]

# 🚦 Test Case for Missing Title
def test_create_week_missing_title(client):
    """Test creating a week with a missing title."""
    input_data = {
        "week_number": 2
    }
    response = client.post('/weeks', json=input_data)
    
    assert response.status_code == 400
    assert response.json["success"] is False
    assert "Title is required" in response.json["message"]

# 🚦 Test Case for Duplicate Week Number
def test_duplicate_week(client):

    # Attempt to create a duplicate week
    response = client.post('/weeks', json={
        'week_number': 1,
        'title': 'Duplicate Week 1'
    })

    # Check response status and message
    assert response.status_code == 409
    data = response.get_json()
    assert data['success'] is False
    assert data['message'] == 'Week already exists'
