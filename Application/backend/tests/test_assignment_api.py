import pytest
from conftest import db
from models import Assignment
from datetime import datetime

# Helper function to create an assignment payload
def assignment_payload(week_id=1, title="Assignment 2", assignment_type="graded", due_date="2024-12-31"):
    return {
        "week_id": week_id,
        "title": title,
        "assignment_type": assignment_type,
        "due_date": due_date
    }

def test_create_assignment_success(client):
    """Test successful creation of an assignment."""
    response = client.post('/assignments', json=assignment_payload())
    assert response.status_code == 201
    assert response.get_json()['success'] is True
    assert response.get_json()['message'] == 'New assignment added successfully'

def test_create_assignment_missing_fields(client):
    """Test creation with missing fields."""
    response = client.post('/assignments', json={})
    assert response.status_code == 400
    assert response.get_json()['message'] == 'All fields are required'

def test_create_assignment_invalid_date_format(client):
    """Test creation with an invalid date format."""
    invalid_payload = assignment_payload(due_date="12-31-2024")
    response = client.post('/assignments', json=invalid_payload)
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Invalid date format. Use YYYY-MM-DD'

def test_create_assignment_week_not_found(client):
    """Test creation with a non-existent week."""
    invalid_payload = assignment_payload(week_id=999)
    response = client.post('/assignments', json=invalid_payload)
    assert response.status_code == 404
    assert response.get_json()['message'] == 'Week not found'

def test_create_assignment_duplicate_title(client):
    """Test creation of a duplicate assignment in the same week."""
    
    # creation with the same title in the same week should fail
    response = client.post('/assignments', json=assignment_payload())
    assert response.status_code == 409
    assert response.get_json()['message'] == 'Assignment already exists in this week'

def test_create_assignment_empty_title(client):
    """Test creation with an empty title."""
    invalid_payload = assignment_payload(title="")
    response = client.post('/assignments', json=invalid_payload)
    assert response.status_code == 400
    assert response.get_json()['message'] == 'All fields are required'

#-----------------------------------------------------------------------------------------------------------------------------------------



# 1. Test when assignments exist
def test_get_assignments_with_data(client):
    """
    Test case for GET /assignments when assignments are present in the database.
    Expects a 200 status code with a list containing assignment data.
    """
    
    response = client.get('/assignments')  # Make the GET request
    assert response.status_code == 200  # Check for success status code
    
    json_data = response.get_json()  # Parse the response as JSON
    assert json_data['success'] is True  # Ensure the success flag is True
    assert json_data['message'] == 'Assignments retrieved successfully'  # Validate the response message
    assert len(json_data['assignments']) > 0  # Confirm at least one assignment is returned
    

#------------------------------------------------------------------------------------------------------------------------------------


# 1. Test when the assignment exists
def test_get_assignment_success(client):
    """
    Test case for GET /assignments/<assignment_id> when the assignment exists.
    Expects a 200 status code with the assignment details.
    """

    
    # Make a GET request to retrieve the assignment by ID
    response = client.get(f'/assignments/1')
    assert response.status_code == 200  # Check for success status code

    json_data = response.get_json()  # Parse the response as JSON
    assert json_data['success'] is True  # Ensure the success flag is True
    assert json_data['message'] == 'Assignment retrieved successfully'  # Validate the success message
    

# 2. Test when the assignment does not exist
def test_get_assignment_not_found(client):
    """
    Test case for GET /assignments/<assignment_id> when the assignment ID does not exist.
    Expects a 404 status code with an 'Assignment not found' message.
    """
    response = client.get('/assignments/999')  # Using a non-existent assignment ID
    assert response.status_code == 404  # Check for not found status code

    json_data = response.get_json()  # Parse the response as JSON
    assert json_data['success'] is False  # Ensure the success flag is False
    assert json_data['message'] == 'Assignment not found'  # Validate the not found message


#-----------------------------------------------------------------------------------------------------------------


# 1. Test for successful assignment update
def test_update_assignment_success(client):
    """
    Test case for PUT /assignments/<assignment_id> when the assignment exists.
    Expects a 200 status code with a success message.
    """
    

    # Prepare the update payload
    payload = {
        "title": "Updated Title",
        "assignment_type": "graded",
        "due_date": "2024-11-30",
        "total_points": 100
    }

    # Make a PUT request to update the assignment
    response = client.put(f'/assignments/2', json=payload)
    assert response.status_code == 200  # Check for success status code

    json_data = response.get_json()  # Parse the response as JSON
    assert json_data['success'] is True  # Ensure the success flag is True
    assert json_data['message'] == 'Assignment updated successfully'  # Validate the success message

    # Check if the assignment was updated in the database
    updated_assignment = Assignment.query.get(2)
    assert updated_assignment.title == "Updated Title"  # Verify the title was updated
    assert updated_assignment.assignment_type == "graded"  # Verify the assignment type
    assert updated_assignment.due_date == datetime.strptime("2024-11-30", "%Y-%m-%d")  # Verify the due date
    assert updated_assignment.total_points == 100  # Verify the total points

# 2. Test for assignment not found
def test_update_assignment_not_found(client):
    """
    Test case for PUT /assignments/<assignment_id> when the assignment ID does not exist.
    Expects a 404 status code with an 'Assignment not found' message.
    """
    payload = {
        "title": "Non-existent Assignment"
    }

    response = client.put('/assignments/999', json=payload)  # Using a non-existent ID
    assert response.status_code == 404  # Check for not found status code

    json_data = response.get_json()  # Parse the response as JSON
    assert json_data['success'] is False  # Ensure the success flag is False
    assert json_data['message'] == 'Assignment not found'  # Validate the not found message

# 3. Test for invalid date format
def test_update_assignment_invalid_date_format(client):
    """
    Test case for PUT /assignments/<assignment_id> with an invalid date format.
    Expects a 400 status code with a 'Invalid due_date format' message.
    """

    payload = {
        "due_date": "31-12-2024"  # Invalid date format
    }

    response = client.put(f'/assignments/2', json=payload)
    assert response.status_code == 400  # Check for bad request status code

    json_data = response.get_json()  # Parse the response as JSON
    assert json_data['success'] is False  # Ensure the success flag is False
    assert json_data['message'] == 'Invalid due_date format. Use YYYY-MM-DD.'  # Validate the error message

# 4. Test for partial update
def test_update_assignment_partial_update(client):
    """
    Test case for PUT /assignments/<assignment_id> with only one field to update.
    Expects a 200 status code and only updates the provided field.
    """

    payload = {
        "total_points": 75  # Only updating the total points
    }

    response = client.put(f'/assignments/2', json=payload)
    assert response.status_code == 200  # Check for success status code

    json_data = response.get_json()  # Parse the response as JSON
    assert json_data['success'] is True  # Ensure the success flag is True
    assert json_data['message'] == 'Assignment updated successfully'  # Validate the success message

    # Verify only the total_points field was updated
    updated_assignment = Assignment.query.get(2)
    assert updated_assignment.total_points == 75  # Check if total points updated
    



#--------------------------------------------------------------------------------------------------------------------------------------


# 1. Test for successful assignment deletion
def test_delete_assignment_success(client):
    """
    Test case for DELETE /assignments/<assignment_id> when the assignment exists.
    Expects a 200 status code with a success message.
    """
    # Send a DELETE request to remove the assignment
    response = client.delete('/assignments/2')
    assert response.status_code == 200  # Check for success status code

    json_data = response.get_json()  # Parse the response as JSON
    assert json_data['success'] is True  # Ensure the success flag is True
    assert json_data['message'] == 'Assignment deleted successfully'  # Validate the success message

# 2. Test for assignment not found
def test_delete_assignment_not_found(client):
    """
    Test case for DELETE /assignments/<assignment_id> when the assignment ID does not exist.
    Expects a 404 status code with an 'Assignment not found' message.
    """
    response = client.delete('/assignments/999')  # Using a non-existent ID
    assert response.status_code == 404  # Check for not found status code

    json_data = response.get_json()  # Parse the response as JSON
    assert json_data['success'] is False  # Ensure the success flag is False
    assert json_data['message'] == 'Assignment not found'  # Validate the not found message

