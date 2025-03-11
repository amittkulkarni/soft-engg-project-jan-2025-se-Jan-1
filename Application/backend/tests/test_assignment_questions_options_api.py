import pytest
from conftest import db
from models import QuestionOption
from datetime import datetime
import json

# -------------------------- CREATE OPTION TEST CASES --------------------------

TEST_QUESTION_ID = 1  # Assuming question ID 1 exists
NEW_OPTION_TEXT = "Heatmap"  # A new option not present in the seed data
def test_create_option_success(client):
    """Test creating a new option successfully."""
    response = client.post('/options', json={
        'question_id': TEST_QUESTION_ID,
        'option_text': NEW_OPTION_TEXT,
        'is_correct': True
    })
    assert response.status_code == 201
    assert response.json['success'] is True
    assert response.json['message'] == 'New option added successfully'


def test_create_option_missing_fields(client):
    """Test creating an option with missing fields."""
    response = client.post('/options', json={
        'question_id': TEST_QUESTION_ID
    })
    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'All fields are required'


def test_create_option_invalid_question(client):
    """Test creating an option for a non-existing question."""
    response = client.post('/options', json={
        'question_id': 999,
        'option_text': NEW_OPTION_TEXT,
        'is_correct': False
    })
    assert response.status_code == 404
    assert response.json['success'] is False
    assert response.json['message'] == 'Assignment question not found'


def test_create_option_duplicate(client):
    """Test creating a duplicate option for the same question."""
    # First creation
    client.post('/options', json={
        'question_id': TEST_QUESTION_ID,
        'option_text': NEW_OPTION_TEXT,
        'is_correct': False
    })
    # Duplicate creation
    response = client.post('/options', json={
        'question_id': TEST_QUESTION_ID,
        'option_text': NEW_OPTION_TEXT,
        'is_correct': False
    })
    assert response.status_code == 409
    assert response.json['success'] is False
    assert response.json['message'] == 'Option already exists for this question'


# -------------------------- GET OPTIONS TEST CASES --------------------------


def test_get_all_options(client):
    """Test retrieving all options."""
    response = client.get('/options')
    assert response.status_code == 200
    assert response.json['success'] is True


def test_get_option_by_id(client):
    """Test retrieving a specific option by ID."""
    option = QuestionOption.query.filter_by(question_id=TEST_QUESTION_ID, option_text=NEW_OPTION_TEXT, is_correct=True).first()
   
    response = client.get(f'/options/{option.id}')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['option']['option_text'] == NEW_OPTION_TEXT


def test_get_option_not_found(client):
    """Test retrieving a non-existent option by ID."""
    response = client.get('/options/999')
    assert response.status_code == 404
    assert response.json['success'] is False
    assert response.json['message'] == 'Option not found'


# -------------------------- UPDATE OPTION TEST CASES --------------------------


def test_update_option_success(client):
    """Test updating an existing option."""
   
    option = QuestionOption.query.filter_by(question_id=TEST_QUESTION_ID, option_text=NEW_OPTION_TEXT, is_correct=True).first()
    

    response = client.put(f'/options/{option.id}', json={
        'option_text': NEW_OPTION_TEXT,
        'is_correct': False
    })
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['message'] == 'Option updated successfully'


def test_update_option_not_found(client):
    """Test updating a non-existent option."""
    response = client.put('/options/999', json={
        'option_text': NEW_OPTION_TEXT,
        'is_correct': True
    })
    assert response.status_code == 404
    assert response.json['success'] is False
    assert response.json['message'] == 'Option not found'


# -------------------------- DELETE OPTION TEST CASES --------------------------


def test_delete_option_success(client):
    """Test deleting an option successfully."""
    # Create a test option
    option = QuestionOption.query.filter_by(question_id=TEST_QUESTION_ID, option_text=NEW_OPTION_TEXT, is_correct=False).first()
    
    response = client.delete(f'/options/{option.id}')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['message'] == 'Option deleted successfully'


def test_delete_option_not_found(client):
    """Test deleting a non-existent option."""
    response = client.delete('/options/999')
    assert response.status_code == 404
    assert response.json['success'] is False
    assert response.json['message'] == 'Option not found'

