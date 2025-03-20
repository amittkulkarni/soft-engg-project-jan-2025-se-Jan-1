import pytest

# ---------------------------- Test Cases for Generate Topic-Specific Questions API ----------------------------

def test_generate_topic_specific_questions_success(client):
    """Test successful generation of topic-specific questions."""
    payload = {
        "topic": "Data Visualization Libraries",
        "num_questions": 3
    }
    response = client.post('/generate_topic_specific_questions', json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert 'questions' in data
    assert len(data['questions']) == 3
    assert 'question' in data['questions'][0]
    assert 'options' in data['questions'][0]
    assert 'answer' in data['questions'][0]
    assert 'explanation' in data['questions'][0]


def test_generate_topic_specific_questions_zero_questions(client):
    """Test API with zero questions requested."""
    payload = {"topic": "Artificial Intelligence", "num_questions": 0}
    response = client.post('/generate_topic_specific_questions', json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['success'] is False
    assert data['message'] == 'Number of questions must be at least 1'


def test_generate_topic_specific_questions_negative_questions(client):
    """Test API with negative value for `num_questions`."""
    payload = {"topic": "Cyber Security", "num_questions": -3}
    response = client.post('/generate_topic_specific_questions', json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['success'] is False
    assert data['message'] == 'Number of questions must be at least 1'


def test_generate_topic_specific_questions_missing_topic(client):
    """Test API when topic is missing in the payload."""
    payload = {"num_questions": 3}
    response = client.post('/generate_topic_specific_questions', json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['success'] is False
    assert data['message'] == 'Topic is required'



def test_generate_topic_specific_questions_invalid_data_type(client):
    """Test API with invalid data types in the payload."""
    payload = {"topic": 12345, "num_questions": "three"}
    response = client.post('/generate_topic_specific_questions', json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['success'] is False
    assert data['message'] == 'Invalid data type for num_questions'


# ---------------------------- Test Cases for Video Summarizer API ----------------------------

def test_video_summarizer_success(client):
    """Test successful video summarization with valid lecture_id."""

    payload = {"lecture_id": "2"}
    response = client.post('/video_summarizer', json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True


def test_video_summarizer_missing_lecture_id(client):
    """Test API when `lecture_id` is missing in the payload."""
    payload = {}
    response = client.post('/video_summarizer', json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['success'] is False
    assert data['message'] == 'lecture_id is required'


def test_video_summarizer_lecture_not_found(client):
    """Test API when the requested lecture_id is not found."""
   
    payload = {"lecture_id": "99_99"}
    response = client.post('/video_summarizer', json=payload)
    data = response.get_json()

    assert response.status_code == 404
    assert data['success'] is False
    assert data['message'] == 'Lecture not found'


#------------------------------Test Cases for Explain Error and Kia chatbot API ------------------

from conftest import client
from models import ChatHistory
from datetime import datetime

# Test Case: Successful Error Explanation
def test_explain_error_success(client):
    """Test API with a valid code snippet that contains an error."""
    input_data = {
        "code_snippet": "print(1/0)"  # Causes ZeroDivisionError
    }
    response = client.post('/explain_error', json=input_data)

    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Error explanation generated successfully"
    assert "explanation" in response.json
    assert "divide by zero" in response.json["explanation"]

# Test Case: Missing Code Snippet
def test_explain_error_missing_code_snippet(client):
    """Test API when the request body is missing the 'code_snippet' key."""
    input_data = {}
    response = client.post('/explain_error', json=input_data)

    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Code snippet is required"

# Test Case: Empty Code Snippet
def test_explain_error_empty_code_snippet(client):
    """Test API when an empty code snippet is provided."""
    input_data = {
        "code_snippet": ""
    }
    response = client.post('/explain_error', json=input_data)

    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Code snippet is required"

# Test Case: Successful Chatbot Response
def test_chatbot_response(client):
    """Test if chatbot returns a valid response"""
    input_data = {
        "user_id": 1,
        "query": "What is machine learning?",
        "response": "Machine learning is a subfield of artificial intelligence."
    }
    response = client.post('/chat_history', json=input_data)

    assert response.status_code == 201
    
    data = response.get_json() 
    
    assert data["success"] is True
    assert data["message"] == "Chat history saved successfully"
    assert data["user_id"] == 1

# Test Case: Missing Query
def test_chatbot_missing_query(client):
    """Test chatbot response when the query is missing"""
    input_data = {
        "user_id": 2  # No query provided
    }
    response = client.post('/chat_history', json=input_data)

    assert response.status_code == 400

    data = response.get_json()  

    assert data["success"] is False
    assert data["message"] == "Missing required fields"

#---------------------------------- Test Case for Generate Mock API---------------------------------

#Test case for successful generation of a mock test
def test_generate_mock_success(client):
    response = client.post('/generate_mock', json={'quiz_type': 'quiz1', 'num_questions': 10})

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'questions' in data

# Test case: Missing quiz_type field
def test_generate_mock_missing_quiz_type(client):
    response = client.post('/generate_mock', json={
        'num_questions': 5
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert data['message'] == 'quiz_type is required'

# Test case: Non-existent quiz_type
def test_generate_mock_non_existent_quiz_type(client):
    response = client.post('/generate_mock', json={
        'quiz_type': 'unknown_quiz',
        'num_questions': 5
    })
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'message' in data

#------------------------------------ Test Case for Generate Notes API ------------------------------

#Test Case: Generate Notes Successfully
def test_generate_notes_success(client):
    response = client.post('/generate_notes', json={"topic": "Reinforcement Learning"})

    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['message'] == 'Notes generated successfully for topic "Reinforcement Learning"'
    assert 'notes' in response.json

#Test Case: missing topic 
def test_generate_notes_missing_topic(client):
    response = client.post('/generate_notes', json={})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'topic is required'

#----------------------------------- Test Case for Week Summary API --------------------------------

#Test case for successful summary generation when the week exists.
def test_generate_week_summary_success(client):
    response = client.post('/generate_week_summary', json={"week_id": 2})
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'summary' in response.json

#Test case when `week_id` is missing in the request body.
def test_generate_week_summary_missing_week_id(client):
    response = client.post('/generate_week_summary', json={})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'week_id is required'

#Test case when `week_id` does not exist in the database.
def test_generate_week_summary_non_existent_week(client):
    response = client.post('/generate_week_summary', json={"week_id": 999})

    assert response.status_code == 404
    assert response.json['success'] is False
    assert response.json['message'] == 'Week not found'
