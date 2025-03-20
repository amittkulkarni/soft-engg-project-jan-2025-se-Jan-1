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


#----------------------------------- Test Case for Code Execution API --------------------------------

# Test case for successful code execution with all test cases passing
def test_execute_solution_success(client):
    response = client.post('/programming_assignments/1/execute',
                           json={
                               "code": '''
                               def is_prime(N):
                                   if N <= 1:
                                   return 'NO'
                                   for i in range(2, int(N**0.5) + 1):
                                       if N % i == 0:
                                           return 'NO'
                                   return 'YES'
                                N = int(input())
                                print(is_prime(N))
                           '''})

    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['score'] == 100
    assert response.json['passed_count'] == 4
    assert response.json['total_cases'] == 4

# Test case when no code is submitted
def test_execute_solution_no_code(client):
    response = client.post('/programming_assignments/1/execute', json={"code": ""})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'No code submitted'

# Test case for non-existent assignment
def test_execute_solution_nonexistent_assignment(client):
    response = client.post('/programming_assignments/999/execute',
                           json={"code": "print('hello')"})

    assert response.status_code == 404
    assert response.json['success'] is False
    assert response.json['message'] == 'Programming assignment not found'


#----------------------------------- Test Case for Check Score API --------------------------------

# Test case for successful score calculation with valid option IDs
def test_check_score_success(client):
    response = client.post('/assignments/check_score', json={"option_ids": [1, 2, 3]})

    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['total_score'] == 2
    assert response.json['message'] == 'Score calculated successfully'

# Test case for invalid input (empty list or non-list)
def test_check_score_invalid_input(client):
    # Test with empty list
    response = client.post('/assignments/check_score', json={"option_ids": []})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'Invalid input. Provide a list of option IDs.'

    # Test with non-list input
    response = client.post('/assignments/check_score', json={"option_ids": "not_a_list"})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'Invalid input. Provide a list of option IDs.'

# Test case for when no valid options are found in the database
def test_check_score_no_valid_options(client):
    response = client.post('/assignments/check_score', json={"option_ids": [999, 1000]})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'No valid option IDs found.'


#----------------------------------- Test Case for Download PDF API --------------------------------

# Test case for successful report generation and download
def test_download_report_success(client):
    # Test data with all required fields
    test_data = {
        "username": "testuser",
        "score": 85,
        "total": 100,
        "suggestions": ["Study more", "Practice regularly"],
        "questions": [{"question": "What is 2+2?", "answer": "4"}]
    }

    response = client.post('/download_report', json=test_data)

    assert response.status_code == 200
    # send_file was successfully called and returned our mock response

# Test case for missing required fields
def test_download_report_missing_fields(client):
    # Test with missing username
    response = client.post('/download_report', json={"score": 85, "total": 100})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == "Invalid input: 'username', 'score', and 'total' are required fields."

    # Test with missing score
    response = client.post('/download_report', json={"username": "testuser", "total": 100})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert "required fields" in response.json['message']


#----------------------------------- Test Case for KIA Chat API --------------------------------

# Test case for successful chat query processing
def test_chat_with_kia_success(client):
    # Test data with all required fields
    test_data = {
        "user_id": "1",
        "query": "What is the meaning of life?"
    }

    response = client.post('/kia_chat', json=test_data)

    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['response'] == 'This is the answer to your question'

# Test case for missing required fields
def test_chat_with_kia_missing_fields(client):
    # Test with missing user_id
    response = client.post('/kia_chat', json={"query": "What is the meaning of life?"})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'Missing required fields'

    # Test with missing query
    response = client.post('/kia_chat', json={"user_id": "user123"})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'Missing required fields'

    # Test with empty request
    response = client.post('/kia_chat', json={})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'Missing required fields'


#----------------------------------- Test Case for KIA Reset Chat API --------------------------------

# Test case for successful chat history reset
def test_reset_chat_history_success(client):
    # Test data with user_id
    test_data = {"user_id": "1"}

    response = client.post('/reset_chat_history', json=test_data)

    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['message'] == 'Chat history cleared successfully'

# Test case for missing user_id
def test_reset_chat_history_missing_user_id(client):
    # Test with empty request
    response = client.post('/reset_chat_history', json={})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'User ID is required'

    # Test with null user_id
    response = client.post('/reset_chat_history', json={"user_id": None})

    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'User ID is required'


#----------------------------------- Test Case for KIA Chat History for User API --------------------------------

    # Test case for successful retrieval of chat history
def test_get_chat_history_success(client):
    # Make the request
    response = client.get('/chat_history/3')

    # Assertions
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['user_id'] == 3
    assert response.json['message'] == 'Chat history retrieved successfully'

# Test case for when no chat history exists
def test_get_chat_history_empty(client):
    # Make the request
    response = client.get('/chat_history/5')

    # Assertions
    assert response.status_code == 404
    assert response.json['success'] is False
    assert response.json['user_id'] == 5
    assert response.json['message'] == 'No chat history found for the given user ID'


#----------------------------------- Test Case for Topic Recommendation API --------------------------------

# Test case for successful recommendation generation based on incorrect answers
def test_topic_recommendation_success(client):
    # Mock data for incorrect answers
    submitted_answers = [
        {"question_id": 1, "selected_option_id": 2},
        {"question_id": 2, "selected_option_id": 5}
    ]

    # Make the request
    response = client.post('/topic_recommendation',
                           json={"answers": submitted_answers})

    # Assertions
    assert response.status_code == 200
    assert response.json['success'] is True

    # Check structure exists
    assert 'message' in response.json
    assert 'suggestions' in response.json

    # Check suggestions has expected structure
    assert 'overall_assessment' in response.json['suggestions']
    assert 'topic_suggestions' in response.json['suggestions']
    assert 'general_tips' in response.json['suggestions']

    # Check content presence rather than exact equality
    assert len(response.json['suggestions']['topic_suggestions']) > 0
    assert len(response.json['suggestions']['general_tips']) > 0

    # For text fields, check that key phrases are present
    assert 'programming' in response.json['suggestions']['overall_assessment'].lower()

# Test case for when all answers are correct
def test_topic_recommendation_all_correct(client):
    # Mock data for correct answers
    submitted_answers = [
        {"question_id": 1, "selected_option_id": 3},
        {"question_id": 2, "selected_option_id": 6}
    ]

    # Make the request
    response = client.post('/topic_recommendation',
                           json={"answers": submitted_answers})

    # Assertions
    assert response.status_code == 200
    assert response.json['success'] is True
    assert "All answers are correct! Great job!" in response.json['message']
    assert response.json['suggestions']['overall_assessment'] == "All questions were answered correctly. Excellent performance!"
    assert len(response.json['suggestions']['topic_suggestions']) == 0

# Test case for missing answers
def test_topic_recommendation_missing_answers(client):
    # Request with empty answers array
    response = client.post('/topic_recommendation', json={"answers": []})

    # Assertions
    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'Answers are required'

    # Request with missing answers field
    response = client.post('/topic_recommendation', json={})

    # Assertions
    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'Answers are required'
