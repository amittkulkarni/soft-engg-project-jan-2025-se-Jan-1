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




