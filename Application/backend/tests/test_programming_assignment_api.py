from conftest import db
from models import ProgrammingAssignment



# Test case for adding a new programming assignment (Happy Path)
def test_add_programming_assignment(client):
    response = client.post('/programming_assignments', json={
        "assignment_id": 101,
        "problem_statement": "Sum of Two Numbers",
        "input_format": "Two integers a, b",
        "output_format": "An integer which is the sum of a and b",
        "constraints": "1 <= a, b <= 1000",
        "sample_input": "5 10",
        "sample_output": "15",
        "test_cases": [
            {"input": "2 3", "expected_output": "5"},
            {"input": "0 0", "expected_output": "0"}
        ]
    })
    assert response.status_code == 201
    assert response.json['success'] == True
    assert response.json['message'] == "Programming assignment added successfully"

# Test case for missing required fields
def test_add_programming_assignment_missing_fields(client):
    response = client.post('/programming_assignments', json={
        "assignment_id": 102,
        "problem_statement": "Missing Input Format",
        "output_format": "Some output",
        "sample_input": "5",
        "sample_output": "10"
    })
    assert response.status_code == 400
    assert response.json['success'] == False
    assert "All required fields must be filled" in response.json['message']

# Test case for duplicate assignment ID
def test_add_duplicate_programming_assignment(client):
    response = client.post('/programming_assignments', json={
        "assignment_id": 101,
        "problem_statement": "Duplicate ID",
        "input_format": "Some input",
        "output_format": "Some output",
        "sample_input": "5",
        "sample_output": "10"
    })
    assert response.status_code == 409
    assert response.json['success'] == False
    assert "Assignment ID already exists" in response.json['message']

# Test case for retrieving a programming assignment
def test_get_programming_assignment(client):

    question = ProgrammingAssignment.query.filter_by(id = 1).first()
    response = client.get(f'/programming_assignments/{question.id}')
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['data']['assignment_id'] == 101

# Test case for non-existent assignment retrieval
def test_get_non_existent_assignment(client):
    response = client.get('/programming_assignments/999')
    assert response.status_code == 404
    assert response.json['success'] == False
    assert "Programming assignment not found" in response.json['message']

# Test case for updating a programming assignment
def test_update_programming_assignment(client):
    question = ProgrammingAssignment.query.filter_by(id = 1).first()
   
    response = client.put(f'/programming_assignments/{question.id}', json={
        "problem_statement": "Updated Problem Statement"
    })
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['message'] == "Programming assignment updated successfully"

# Test case for deleting a programming assignment
def test_delete_programming_assignment(client):
    response = client.delete('/programming_assignments/1')
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['message'] == "Programming assignment deleted successfully"

# Test case for deleting a non-existent assignment
def test_delete_non_existent_assignment(client):
    response = client.delete('/programming_assignments/999')
    assert response.status_code == 404
    assert response.json['success'] == False
    assert "Programming assignment not found" in response.json['message']

