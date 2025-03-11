# Test Case for the `POST /weeks` API
from models import Week
from conftest import db

#Test the API endpoint to create a new week.
def test_create_week(client):
    # Valid input data
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

#  Test Case for Invalid Week Number
def test_create_week_invalid_week_number(client):
    #Test creating a week with an invalid week number.
    input_data = {
        "week_number": -1,  # Invalid week number
        "title": "Week -1"
    }
    response = client.post('/weeks', json=input_data)
    
    assert response.status_code == 400
    assert response.json["success"] is False
    assert "Invalid week number" in response.json["message"]

#  Test Case for Missing Title
def test_create_week_missing_title(client):
    #Test creating a week with a missing title.
    input_data = {
        "week_number": 2
    }
    response = client.post('/weeks', json=input_data)
    
    assert response.status_code == 400
    assert response.json["success"] is False
    assert "Title is required" in response.json["message"]

#  Test Case for Duplicate Week Number
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

# Test Case: When weeks exist in the database
def test_get_weeks_with_data(client):
    """Test GET /weeks when there are weeks in the database."""
    response = client.get('/weeks')
    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Weeks retrieved successfully"
    assert isinstance(data["weeks"], list)

# Test when a valid week ID is provided and data exists
def test_get_week_details_valid_id(client):
    #Test GET /weeks/<week_id> with a valid existing week ID.
    response = client.get('/weeks/1')

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Week details retrieved successfully"
    assert "week" in data
    assert data["week"]["id"] == 1
    assert "lectures" in data["week"]
    assert "assignments" in data["week"]

# Test when an invalid week ID is provided (Not Found)
def test_get_week_details_invalid_id(client):
    #Test GET /weeks/<week_id> with an ID that does not exist.
    response = client.get('/weeks/9999')

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Week not found"

# Test for non-integer week ID
def test_get_week_details_non_integer_id(client):
    #Test GET /weeks/<week_id> with a non-integer ID (invalid request).
    response = client.get('/weeks/abc') 

    assert response.status_code == 404
#------------------------------------------------UPDATE WEEK------------------------------------------
# 1. Test for a successful update with valid data
def test_update_week_valid_data(client):
    #Test updating a week with valid data
    input_data = {
        "week_number": 10,
        "title": "Updated Week 10"
    }
    
    response = client.put('/weeks/1', json=input_data)
    
    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Week updated successfully"

    # Check if the database is updated correctly
    updated_week = Week.query.get(1)
    assert updated_week.week_number == 10
    assert updated_week.title == "Updated Week 10"


# 2. Test for non-existent week ID
def test_update_week_non_existent_id(client):
    #Test updating a non-existent week ID
    input_data = {
        "week_number": 15,
        "title": "Non-existent Week"
    }
    response = client.put('/weeks/9999', json=input_data)

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Week not found"


# 3. Test for invalid week number
def test_update_week_invalid_week_number(client):
    #Test updating with an invalid week number.
    input_data = {
        "week_number": -5,  # Invalid week number
        "title": "Invalid Week Number"
    }
    response = client.put('/weeks/1', json=input_data)

    assert response.status_code == 400
    data = response.get_json()

    assert data["success"] is False
    assert "Invalid week number" in data["message"]


# 4. Test for invalid title
def test_update_week_invalid_title(client):
    #Test updating with an invalid title
    input_data = {
        "week_number": 5,
        "title": ""  # Invalid title (empty string)
    }
    response = client.put('/weeks/1', json=input_data)

    assert response.status_code == 400
    data = response.get_json()

    assert data["success"] is False
    assert "Title must be a non-empty string" in data["message"]

# 6. Test for partial update (only title)
def test_update_week_partial_title(client):
    #Test updating only the title of a week
    input_data = {
        "title": "Partial Update Week Title"
    }
    
    response = client.put('/weeks/1', json=input_data)

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Week updated successfully"

    # Check if only the title is updated
    updated_week = Week.query.get(1)
    assert updated_week.title == "Partial Update Week Title"


# 7. Test for partial update (only week number)
def test_update_week_partial_week_number(client):
    #Test updating only the week number of a week.
    input_data = {
        "week_number": 20
    }
    
    response = client.put('/weeks/1', json=input_data)

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Week updated successfully"

    # Check if only the week number is updated
    updated_week = Week.query.get(1)
    assert updated_week.week_number == 20


# 8. Test for empty request body
def test_update_week_empty_request(client):
    #Test updating a week with an empty request body
    response = client.put('/weeks/1', json={})

    assert response.status_code == 200  # No update, but valid request
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Week updated successfully"

# 10. Test for no changes provided in the request body
def test_update_week_no_changes(client):
    #Test updating a week with no actual changes in the input
    existing_week = Week.query.get(1)
    original_week_number = existing_week.week_number
    original_title = existing_week.title

    input_data = {
        "week_number": original_week_number,
        "title": original_title
    }

    response = client.put('/weeks/1', json=input_data)

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Week updated successfully"

    # Ensure data remains unchanged
    updated_week = Week.query.get(1)
    assert updated_week.week_number == original_week_number
    assert updated_week.title == original_title

# Test for a successful deletion
def test_delete_week_success(client):
    #Test deleting an existing week successfully.
    response = client.delete('/weeks/1')

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Week deleted successfully"

    # Verify that the week no longer exists in the database
    deleted_week = Week.query.get(1)
    assert deleted_week is None

#Test deleting a non-existent week
def test_delete_week_not_found(client):
    response = client.delete('/weeks/9999')

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Week not found"