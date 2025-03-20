# ---------------------------- Test Cases for Google Signup API ----------------------------

# Test case for successful signup (new user)
def test_google_signup_success(client):
    response = client.post('/google_signup', json={"access_token": "valid_token"})

    assert response.status_code == 201
    assert response.json['Success'] is True
    assert response.json['access_token'] == 'mock_jwt_token'
    assert response.json['message'] == 'User registered successfully'

# Test case for missing access token
def test_google_signup_missing_token(client):
    response = client.post('/google_signup', json={})

    assert response.status_code == 400
    assert response.json['Success'] is False
    assert response.json['message'] == 'Google access token is required'


# ---------------------------- Test Cases for Google Login API ----------------------------

# Test case for successful login
def test_google_login_success(client):
    response = client.post('/google_login', json={"access_token": "valid_token"})

    assert response.status_code == 200
    assert response.json['Success'] is True
    assert response.json['access_token'] == 'mock_jwt_token'
    assert response.json['message'] == 'Login successful'

# Test case for missing access token
def test_google_login_missing_token(client):
    response = client.post('/google_login', json={})

    assert response.status_code == 400
    assert response.json['Success'] is False
    assert response.json['message'] == 'Google access token is required'


# ---------------------------- Test Cases for Signup API ----------------------------

# Test case for successful signup
def test_signup_success(client):
    # Test data
    test_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "secure123",
        "role": "student"
    }

    response = client.post('/signup', json=test_data)

    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

# Test case for username or email already exists
def test_signup_existing_user(client):
    # Test username already exists
    username_data = {
        "username": "existinguser",
        "email": "new@example.com",
        "password": "secure123"
    }

    response = client.post('/signup', json=username_data)

    assert response.status_code == 400
    assert response.json['message'] == 'Username already exists'

    # Test email already exists
    email_data = {
        "username": "newuser",
        "email": "existing@example.com",
        "password": "secure123"
    }

    response = client.post('/signup', json=email_data)

    assert response.status_code == 400
    assert response.json['message'] == 'Email already exists'

# Test case for missing required fields
def test_signup_missing_fields(client):
    # Test missing email
    missing_email_data = {
        "username": "newuser",
        "password": "secure123"
    }

    response = client.post('/signup', json=missing_email_data)

    assert response.status_code == 400
    assert response.json['message'] == 'Email is required'

    # Test missing password
    missing_password_data = {
        "username": "newuser",
        "email": "new@example.com"
    }

    response = client.post('/signup', json=missing_password_data)

    assert response.status_code == 400
    assert response.json['message'] == 'Password is required'



# ---------------------------- Test Cases for Login API ----------------------------

# Test case for successful login
def test_login_success(client):
    # Test data
    test_data = {
        "email": "user@example.com",
        "password": "correct_password"
    }

    response = client.post('/login', json=test_data)

    assert response.status_code == 200
    assert response.json['access_token'] == 'mock_access_token'
    assert response.json['message'] == 'Login successful'

# Test case for missing required fields
def test_login_missing_fields(client):
    # Test missing email
    missing_email_data = {
        "password": "password123"
    }

    response = client.post('/login', json=missing_email_data)

    assert response.status_code == 400
    assert response.json['message'] == 'Email and password are required'

    # Test missing password
    missing_password_data = {
        "email": "user@example.com"
    }

    response = client.post('/login', json=missing_password_data)

    assert response.status_code == 400
    assert response.json['message'] == 'Email and password are required'

    # Test empty request
    response = client.post('/login', json={})

    assert response.status_code == 400
    assert response.json['message'] == 'Email and password are required'

# Test case for invalid credentials
def test_login_invalid_credentials(client):
    # Test user not found
    not_found_data = {
        "email": "notfound@example.com",
        "password": "any_password"
    }

    response = client.post('/login', json=not_found_data)

    assert response.status_code == 401
    assert response.json['message'] == 'Invalid email or password'

    # Test incorrect password
    wrong_password_data = {
        "email": "user@example.com",
        "password": "wrong_password"
    }

    response = client.post('/login', json=wrong_password_data)

    assert response.status_code == 401
    assert response.json['message'] == 'Invalid email or password'