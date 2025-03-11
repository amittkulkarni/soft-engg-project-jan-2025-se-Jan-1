from conftest import db
from models import Assignment, AssignmentQuestion

QUestion_id = 1
#Test Case for Creating an assignment question
def test_create_assignment_question_success(client):
    #Test successfully creating an assignment question.
    input_data = {
        "assignment_id": 3,
        "question_text": "What is 2 + 2?",
        "question_type": "single_choice",
        "points": 5
    }
    input_data2 = {
        "assignment_id": 3,
        "question_text": "What is 2 + 2?",
        "question_type": "single_choice",
        "points": 5
    }
    response = client.post('/assignment_questions', json=input_data)
    response2 = client.post('/assignment_questions', json=input_data2)
    assert response.status_code == 201
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "New assignment question added successfully"
    assert "question_id" in data
    QUestion_id = data["question_id"]
    print(QUestion_id)


def test_create_assignment_question_missing_fields(client):
    #Test creating an assignment question with missing fields.
    input_data = {
        "assignment_id": 1
    }
    response = client.post('/assignment_questions', json=input_data)

    assert response.status_code == 400
    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "All fields are required"


def test_create_assignment_question_invalid_points(client):
    #Test creating an assignment question with negative points.
    input_data = {
        "assignment_id": 1,
        "question_text": "What is 2 + 2?",
        "question_type": "MCQ",
        "points": -5
    }
    response = client.post('/assignment_questions', json=input_data)

    assert response.status_code == 400
    data = response.get_json()

    assert data["success"] is False
    assert "Points must be a non-negative integer" in data["message"]


def test_create_assignment_question_assignment_not_found(client):
    #Test creating an assignment question for a non-existent assignment.
    input_data = {
        "assignment_id": 9999,  # Non-existent assignment
        "question_text": "What is 2 + 2?",
        "question_type": "MCQ",
        "points": 5
    }
    response = client.post('/assignment_questions', json=input_data)

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Assignment not found"

#Test Case to retreive all assignment questions
def test_get_all_assignment_questions(client):
    #Test retrieving all assignment questions when data exists.
    response = client.get('/assignment_questions')

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert isinstance(data["questions"], list)

def test_get_assignment_question_by_id(client):
    #Test retrieving an assignment question by its ID
    response = client.get(f'/assignment_questions/{QUestion_id}')  

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert "question" in data


def test_get_assignment_question_not_found(client):
    #Test retrieving a non-existent assignment question
    response = client.get('/assignment_questions/9999')

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Assignment question not found"

#Test case to update an assignment question
def test_update_assignment_question_success(client):
    #Test successfully updating an assignment question.
    input_data = {
        "question_text": "Updated question text",
        "question_type": "single_choice",
        "points": 10
    }
    response = client.put(f'/assignment_questions/{QUestion_id}', json=input_data) 

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Assignment question updated successfully"


def test_update_assignment_question_not_found(client):
    #Test updating a non-existent assignment question.
    input_data = {
        "question_text": "Updated question text",
        "question_type": "single choice",
        "points": 10
    }
    response = client.put('/assignment_questions/9999', json=input_data)

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Assignment question not found"

#Test cases for deleting an assignment question
def test_delete_assignment_question_success(client):
    #Test successfully deleting an assignment question.
    response = client.delete(f'/assignment_questions/{QUestion_id}')  

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Assignment question deleted successfully"

    # Verify the question is actually deleted
    # deleted_question = AssignmentQuestion.query.get()
    # assert deleted_question is None


def test_delete_assignment_question_not_found(client):
    #Test deleting a non-existent assignment question.
    response = client.delete('/assignment_questions/9999')

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Assignment question not found"

