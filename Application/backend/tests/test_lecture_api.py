from models import Lecture
from conftest import db

# Test Case for Creating a New Lecture
def test_create_lecture(client):
    """Test the API endpoint to create a new lecture with valid data"""
    
    input_data = {
        "week_id": 1, 
        "title": "Introduction to Machine Learning",
        "video_id": "ml_intro_123"
    }
    
    response = client.post('/lectures', json=input_data)
    
    assert response.status_code == 201
    assert response.json["success"] is True
    assert response.json["message"] == "New lecture added successfully"

    new_lecture = Lecture.query.filter_by(title="Introduction to Machine Learning").first()
    assert new_lecture is not None
    assert new_lecture.week_id == 1
    assert new_lecture.video_id == "ml_intro_123"

# Test Case for Missing Title
def test_create_lecture_missing_fields(client):
    """Test creating a lecture with missing title"""
    
    input_data = {
        "week_id": 1,
        "video_id": "ml_video_456"
    }
    
    response = client.post('/lectures', json=input_data)
    
    assert response.status_code == 400
    assert response.json["success"] is False
    assert "Title is required" in response.json["message"]

# Test Case for Invalid Week ID (Non-existent)
def test_create_lecture_invalid_week(client):
    """Test creating a lecture for a non-existing week"""
    
    input_data = {
        "week_id": 99,  # Week ID that doesn't exist
        "title": "Supervised Learning Fundamentals",
        "video_id": "supervised_ml_789"
    }
    
    response = client.post('/lectures', json=input_data)
    
    assert response.status_code == 404
    assert response.json["success"] is False
    assert response.json["message"] == "Week not found"
    
# Test Case for Invalid Week ID (Negative)
def test_create_lecture_invalid_week_id_negative(client):
    """Test creating a lecture with a negative week ID"""
    
    input_data = {
        "week_id": -2,
        "title": "Regression Techniques",
        "video_id": "regression_890"
    }
    
    response = client.post('/lectures', json=input_data)
    
    assert response.status_code == 400
    assert response.json["success"] is False
    assert "Invalid week ID" in response.json["message"]


# Test Case for Duplicate Lecture in the Same Week
def test_create_lecture_duplicate(client):
    """Test creating a lecture with a duplicate title in the same week"""

    input_data = {
        "week_id": 1,
        "title": "Introduction to Machine Learning", 
        "video_id": "ml_intro_123"
    }
    
    response = client.post('/lectures', json=input_data)
    
    assert response.status_code == 409
    assert response.json["success"] is False
    assert response.json["message"] == "Lecture already exists in this week"

# Test Case for Non-String Title
def test_create_lecture_invalid_title_type(client):
    """Test creating a lecture with an invalid title type"""
    
    input_data = {
        "week_id": 1,
        "title": 12345,  # Invalid type
        "video_id": "ml_video_321"
    }
    
    response = client.post('/lectures', json=input_data)
    
    assert response.status_code == 400
    assert response.json["success"] is False
    assert "Title is required and must be a string" in response.json["message"]

# Test Case for Non-String Video ID
def test_create_lecture_invalid_video_id_type(client):
    """Test creating a lecture with an invalid video ID type"""
    
    input_data = {
        "week_id": 1,
        "title": "Unsupervised Learning",
        "video_id": 98765  # Invalid type
    }
    
    response = client.post('/lectures', json=input_data)
    
    assert response.status_code == 400
    assert response.json["success"] is False
    assert "Video ID is required and must be a string" in response.json["message"]


# Test Case for Retrieving All Lectures 
def test_get_lectures(client):
    """Test the API endpoint to retrieve all lectures"""
    
    response = client.get('/lectures')
    
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Lectures retrieved successfully"
    assert isinstance(response.json["lectures"], list)
    assert len(response.json["lectures"]) > 0  # Lectures should exist

    # Check lecture structure
    for lecture in response.json["lectures"]:
        assert "id" in lecture
        assert "week_id" in lecture
        assert "title" in lecture
        assert "video_id" in lecture


# Test Case for Retrieving a Specific Lecture by ID
def test_get_lecture_details(client):
    """Test retrieving details of a specific lecture by ID"""

    lecture_id = 1  
    response = client.get(f'/lectures/{lecture_id}')

    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Lecture retrieved successfully"
    
    lecture_data = response.json["lecture"]
    assert "id" in lecture_data
    assert "week_id" in lecture_data
    assert "title" in lecture_data
    assert "video_id" in lecture_data

    assert lecture_data["id"] == lecture_id  # Ensure it matches the requested ID

# Test Case for Retrieving a Non-Existent Lecture
def test_get_lecture_details_not_found(client):
    """Test retrieving a lecture that does not exist"""
    
    invalid_lecture_id = 99
    response = client.get(f'/lectures/{invalid_lecture_id}')
    
    assert response.status_code == 404
    assert response.json["success"] is False
    assert response.json["message"] == "Lecture not found"
    

# Test Case for Successfully Updating a Lecture
def test_update_lecture(client):
    """Test the API endpoint to update an existing lecture with valid data"""
    
    lecture_id = 1 
    input_data = {
        "title": "Updated Machine Learning Concepts",
        "video_id": "updated_ml_456"
    }
    
    response = client.put(f'/lectures/{lecture_id}', json=input_data)
    
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Lecture updated successfully"

    updated_lecture = Lecture.query.get(lecture_id)
    assert updated_lecture is not None
    assert updated_lecture.title == "Updated Machine Learning Concepts"
    assert updated_lecture.video_id == "updated_ml_456"

# Test Case for Updating a Non-Existent Lecture
def test_update_lecture_not_found(client):
    """Test updating a lecture that does not exist"""
    
    invalid_lecture_id = 99  
    input_data = {
        "title": "Non-Existent Lecture",
        "video_id": "no_video"
    }
    
    response = client.put(f'/lectures/{invalid_lecture_id}', json=input_data)
    
    assert response.status_code == 404
    assert response.json["success"] is False
    assert response.json["message"] == "Lecture not found"

# Test Case for Non-String Title
def test_update_lecture_invalid_title_type(client):
    """Test updating a lecture with an invalid title type"""
    
    lecture_id = 1
    input_data = {
        "title": 12345,  # Invalid type
        "video_id": "valid_video_id"
    }
    
    response = client.put(f'/lectures/{lecture_id}', json=input_data)
    
    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Invalid title format"

# Test Case for Non-String Video ID
def test_update_lecture_invalid_video_id_type(client):
    """Test updating a lecture with an invalid video ID type"""
    
    lecture_id = 1
    input_data = {
        "title": "Valid Title",
        "video_id": 98765  # Invalid type
    }
    
    response = client.put(f'/lectures/{lecture_id}', json=input_data)
    
    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Invalid video_id format"


# Test Case for Successfully Deleting an Existing Lecture
def test_delete_existing_lecture(client):
    """Test deleting an existing lecture"""

    lecture_id = 1  

    response = client.delete(f'/lectures/{lecture_id}')

    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Lecture deleted successfully"

    # Ensure the lecture is actually deleted
    deleted_lecture = Lecture.query.get(lecture_id)
    assert deleted_lecture is None

# Test Case for Deleting a Non-Existent Lecture
def test_delete_non_existent_lecture(client):
    """Test deleting a lecture that does not exist"""

    invalid_lecture_id = 999  

    response = client.delete(f'/lectures/{invalid_lecture_id}')

    assert response.status_code == 404
    assert response.json["success"] is False
    assert response.json["message"] == "Lecture not found"
