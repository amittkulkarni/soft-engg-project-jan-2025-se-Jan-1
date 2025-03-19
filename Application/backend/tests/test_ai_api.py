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