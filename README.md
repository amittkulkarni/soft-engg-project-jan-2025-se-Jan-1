# AI Academic Guidance Portal

## Project Overview
A comprehensive AI agent-powered academic guidance system built with a Flask backend and Vue.js frontend. The system features lecture summarization, mock quiz generation, error explanation, topic-specific notes, and an AI chatbot assistant named Kia.

## Project Team
- Amit Kulkarni
- Anjali Galav
- Jyotiraditya Saha
- Kajol Singh
- Saima Zainab Shroff
- Sandeep Kumar
- Siddharth Umathe

## Project Structure
```
kia/
├── backend/
│   ├── chat_logs/         # Storage for chat conversations
│   ├── instance/          # Flask instance folder
│   ├── migrations/        # Database migrations
│   ├── templates/         # Flask templates
│   ├── tests/             # Test files
│   ├── vector_store/      # Vector embeddings for AI features
│   ├── .env.example       # Environment variables template
│   ├── .gitignore         # Git ignore rules
│   ├── app.py             # Main Flask application
│   ├── config.py          # Configuration settings
│   ├── controller.py      # API controllers
│   ├── error_explainer.py # Code error explanation module
│   ├── extension.py       # Flask extensions
│   ├── kia_chatbot.py     # Chatbot implementation
│   ├── lecture_summarizer.py # Lecture summary generator
│   ├── models.py          # Database models
│   ├── notes_generator.py # Study notes generator
│   ├── quiz_mock.py       # Quiz generation module
│   ├── requirements.txt   # Python dependencies
│   ├── reset_db.py        # Database reset utility
│   ├── seed_data.py       # Initial data generator
│   ├── token_validation.py # Authentication module
│   ├── topic_specific_mock.py # Topic-focused quiz generator
│   ├── topic_suggestions.py # Learning recommendation engine
│   └── week_summarizer.py  # Weekly content summarizer
│
├── frontend/
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── assets/        # Images/Icons
│   │   ├── components/    # Reusable Vue components
│   │   ├── router/        # Vue Router config
│   │   ├── App.vue        # Root component
│   │   └── main.js        # Entry point
│   ├── package-lock.json  # Dependency manifest
│   └── package.json       # Dependency manifest
```

## Prerequisites

### Backend
1. Python 3.8+
2. Virtual environment tool (virtualenv, pipenv, or conda)

### Frontend
1. Node.js v18.16.0+
2. npm v9.5.0+
3. Modern Browser (Chrome/Firefox/Edge)
4. Active Internet Connection (for YouTube Embed)

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   ```
   or
   ```
   copy .env.example .env
   ```

5. Generate and add keys to your .env file:
   - Visit https://jwtsecret.com/generate and set length to 128
   - Copy the generated key for both SECRET_KEY and JWT_SECRET_KEY
   - Obtain a Google API key (see API Keys section below)

6. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. Seed the database with initial data:
   ```
   python seed_data.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

## Quickstart

### Start Backend Server
1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Activate the virtual environment(if not activated):
   ```
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Start the Flask development server:
   ```
   python app.py
   ```
   The backend will be running at http://localhost:5000/

### Start Frontend Server
1. Open a new terminal/Command Prompt
2. Navigate to the frontend directory:
   ```
   cd frontend
   ```

3. Start the Vue development server:
   ```
   npm run serve
   ```
   The frontend will be accessible at http://localhost:8080/

## API Keys Setup

### JWT Secret Keys
1. Visit https://jwtsecret.com/generate
2. Set the length parameter to 128
3. Click "Generate Secret Key"
4. Copy the generated key and add it to your .env file for both:
   - SECRET_KEY
   - JWT_SECRET_KEY

### Google API Key
1. Go to the Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Dashboard"
4. Click "+ ENABLE APIS AND SERVICES"
5. Navigate to "APIs & Services" > "Credentials"
6. Click "Create Credentials" > "API key"
7. Copy the generated API key
8. Add the API key to your .env file as GOOGLE_API_KEY

## Feature Walkthrough

1. **Authentication**
   - Navigate to http://localhost:8080/
   - Login with "student1@test.com" and "studentpass1" as email and password respectively.
   - Register with new credentials or use Google OAuth SignIn. (GoogleOAuth might not render the first time correctly, so try refreshing if it doesn't work)

2. **Course Navigation**
   - After login, you'll be directed to the Course Page
   - Browse through weekly content organized by topics

3. **Lecture Summarization**
   - Open any Week (e.g., Week 5) and select a lecture (e.g., 5.1 Polynomial Regression)
   - View the lecture video
   - Click "Summarize" to have Kia generate a lecture summary
   - Use the 'Download PDF' button to download the summary as a PDF document

4. **Mock Quizzes**
   - Open "Generate Mock Quiz 1" to access AI-generated questions
   - Select your answers and click "Check Score" to evaluate performance
   - View topic suggestions based on your score
   - Download your performance report

5. **Programming Assignments**
   - Navigate to "Programming Assignment 1" in Week 2
   - View the problem statement and use the integrated code editor
   - Submit your solution for evaluation, once the correct code and once the erroneous code (Dummy submission code is given at the bottom of the README)
   - Click "Explain Error" to receive a simplified explanation of any errors

6. **Topic-Specific Mock Tests**
   - Go to "Generate Topic Specific Mock"
   - Enter a topic like "Regression" using the autocomplete
   - Click "Generate" to create a focused mock test

7. **Kia Chatbot**
   - Click the "Ask Kia" button in the bottom right corner
   - Interact with the AI assistant for course-related queries
   - Chat history persists across pages until manually reset

8. **Notes Generation**
   - Click "Generate Short Notes"
   - Choose between "Generate Topic Notes" or "Generate Week Summary"
   - Select a topic or week and click "Generate"
   - Download generated content as PDF

9. **Logout**
   - Use the logout button in the top left to securely end your session

Dummy Code: 
    1. Correct Code
    
    ```python
    def sum_of_array():
        n = int(input())
        
        arr = list(map(int, input().split()))

        total = sum(arr)

        print(total)

    sum_of_array()
    ```
    2. Erroneous Code
    
    ```python
    def sum_of_array():
        class CustomArray:
            def __init__(self, elements):
                self.elements = elements
                
            def calculate_sum(self, index=0, accumulator=None):
                if accumulator is None:
                    accumulator = []
                
                if index >= len(self.elements):
                    return sum(x for x in accumulator)

                try:
                    if index % 3 == 0:
                        value = int(self.elements[index])
                    elif index % 3 == 1:
                        value = float(self.elements[index])
                    else:
                        value = complex(self.elements[index])
                        
                    accumulator.append(value)
                    
                    return self.calculate_sum(index + 1, accumulator) + (0 if index % 5 != 0 else 1/len(accumulator))
                
                except Exception as e:
                    # Create nested exception
                    try:
                        # Intentional error: dict access with wrong key type
                        error_dict = {1: "Error", 2: "Another error"}
                        return error_dict[self.elements[index]]
                    except:
                        # Intentionally access beyond list bounds
                        return self.elements[len(self.elements) + 1]
    
    n = input()  # Not converting to int

    if not n.isdigit():
    	raise ValueError("Input must be a digit")
    
    arr = input().split()
    
    sum = 0 
    custom_arr
    ```

    

    
