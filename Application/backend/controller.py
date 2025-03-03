from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Week, Lecture, Assignment, AssignmentQuestion, QuestionOption,ProgrammingAssignment,ChatHistory
from extension import db 
import os
import json

from token_validation import generate_token
from datetime import datetime

from config import Config
from mcq_generator import initialize_rag_pipeline, generate_mcqs
from pydantic import SecretStr




# Comment from Amit , Do use the prefix "/api/" for all APIs . For e.g http://localhost:3000/api/google_auth 


user_routes = Blueprint('user_routes', __name__)

# ------------------------- User Authentication Routes -------------------------

# Signup Route - Registers a new user
@user_routes.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')  # Default to 'student' if not provided
    google_id = data.get('google_id')
    # Check if the email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    # Hash the password and save the new user
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        role=role,
        google_id=google_id
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Login Route - Authenticates a user and returns an access token
@user_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validate user credentials
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Generate authentication token
    token = generate_token(user.id)
    return jsonify({"access_token": token, "message": "Login successful"}), 200




#-----------------------------------------CRUD Operations for Weeks--------------------------------------------------------------

# Create Week - Adds a new week to the database
@user_routes.route('/weeks', methods=['POST'])
def create_week():
    data = request.get_json()
    week_number = data.get('week_number')
    title = data.get('title')

    # Check if the week already exists
    existing_week = Week.query.filter_by(week_number=week_number).first()
    if existing_week:
        return jsonify({"message":"week already exists."}),409
    
    # Create and save a new week
    new_week =  Week(week_number=week_number, title=title)
    db.session.add(new_week)
    db.session.commit()

    return jsonify({"message": "new week added successfully"}), 201

# Get All Weeks - Retrieves a list of all weeks
@user_routes.route('/weeks', methods=['GET'])
def get_weeks():
    weeks = Week.query.all()
    return jsonify([{
        "id": week.id,
        "week_number": week.week_number,
        "title": week.title
    } for week in weeks]), 200

# Get Week Details - Retrieves details of a specific week by ID
@user_routes.route('/weeks/<int:week_id>', methods=['GET'])
def get_week_details(week_id):
    week = Week.query.get(week_id)
    if not week:
        return jsonify({"message": "Week not found"}), 404

    return jsonify({
        "id": week.id,
        "week_number": week.week_number,
        "title": week.title,
        "lectures": [{"id": lec.id, "title": lec.title, "video_url": lec.video_url} for lec in week.lectures],
        "assignments": [{"id": assgn.id, "title": assgn.title, "type": assgn.type} for assgn in week.assignments]
    }), 200

# Update Week - Updates the details of a specific week
@user_routes.route('/weeks/<int:week_id>', methods=['PUT'])
def update_week(week_id):
    week = Week.query.get(week_id)
    if not week:
        return jsonify({"message": "Week not found"}), 404
    
    data = request.get_json()

    # Update week properties if provided
    if "week_number" in data:
        week.week_number=data["week_number"]
    if "title" in data:
        week.title=data["title"]

    db.session.commit()

    return jsonify({"message": "week updated successfully"}), 200

# Delete Week - Deletes a specific week from the database
@user_routes.route('/weeks/<int:week_id>', methods=['DELETE'])
def delete_week(week_id):
    week = Week.query.get(week_id)
    if not week:
        return jsonify({"message": "Week not found"}), 404
    
    db.session.delete(week)
    db.session.commit()

    return jsonify({"message": "week delete successfully"}), 200


#-----------------------------------------------------CRUD Operations for Lectures -----------------------------------------------------

# Create Lecture - Adds a new lecture to a specific week
@user_routes.route('/lectures', methods=['POST'])
def create_lecture():
    data = request.get_json()
    week_id = data.get('week_id')
    title = data.get('title')
    video_id = data.get("video_id")

    # Validate input fields
    if "week_id" not in data or "title" not in data or "video_id" not in data:
        return jsonify({"message" : "All fields are required"}),400
    
    # Check if the associated week exists
    week = Week.query.get(week_id)
    if not week:
        return jsonify({"message": "Week not found"}), 404
    
    # Check if the lecture title already exists
    existing_lecture = Lecture.query.filter_by(title = title).first()
    if existing_lecture:
        return jsonify({"message":"lecture already exists."}),409
    
    # Create and save the new lecture
    new_lecture =  Lecture(week_id=week_id, title=title, video_id = video_id)
    db.session.add(new_lecture)
    db.session.commit()

    return jsonify({"message": "new lecture added successfully"}), 201

# Get All Lectures - Retrieves a list of all lectures
@user_routes.route('/lectures', methods=['GET'])
def get_lectures():
    lectures = Lecture.query.all()
    return jsonify([{
        "id": lecture.id,
        "week_id": lecture.week_id,
        "title": lecture.title,
        "video_id":lecture.video_id,
    } for lecture in lectures]), 200


# Get Lecture Details - Retrieves details of a specific lecture by ID
@user_routes.route('/lectures/<int:lecture_id>', methods=['GET'])
def get_lecture_details(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    if not lecture:
        return jsonify({"message": "lecture not found"}), 404

    return jsonify({
        "id": lecture.id,
        "week_id": lecture.week_id,
        "title": lecture.title,
        "video_id": lecture.video_id,
    }), 200

# Update Lecture - Updates the details of a specific lecture
@user_routes.route('/lectures/<int:lecture_id>', methods=['PUT'])
def update_lecture(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    if not lecture:
        return jsonify({"message": "lecture not found"}), 404
    
    data = request.get_json()

    # Update lecture properties if provided
    if "week_id" in data:
        lecture.week_id=data["week_id"]
    if "title" in data:
        lecture.title=data["title"]
    if "video_id" in data:
        lecture.video_id=data["video_id"]

    db.session.commit()

    return jsonify({"message": "Lecture updated successfully"}), 200

# Delete Lecture - Deletes a specific lecture from the database
@user_routes.route('/lectures/<int:lecture_id>', methods=['DELETE'])
def delete_lecture(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    if not lecture:
        return jsonify({"message": "Lecture not found"}), 404
    
    db.session.delete(lecture)
    db.session.commit()

    return jsonify({"message": "Lecture delete successfully"}), 200

#-----------------------------------------------------CRUD - ASSIGNMENT-----------------------------------------------------

# Create a new assignment
@user_routes.route('/assignments', methods=['POST'])
def create_assignment():
    data = request.get_json()
    week_id = data.get('week_id')
    title = data.get('title')
    assignment_type = data.get('assignment_type')
    due_date = data.get('due_date')
    
    # Validate required fields
    if not week_id or not title or not assignment_type or not due_date:
        return jsonify({"message" : "All fields are required"}), 400
    
    due_date = datetime.strptime(due_date, "%Y-%m-%d")
    
    # Check if the week exists
    week = Week.query.get(week_id)
    if not week:
        return jsonify({"message": "Week not found"}), 404
    
    # Check if assignment with the same title already exists in this week
    existing_assignment = Assignment.query.filter_by(title=title, week_id=week_id).first()
    if existing_assignment:
        return jsonify({"message": "Assignment already exists in this week."}), 409
    
    # Create and save a new assignment
    new_assignment =  Assignment(week_id=week_id, title=title, assignment_type = assignment_type, due_date=due_date)
    
    db.session.add(new_assignment)
    db.session.commit()
    
    return jsonify({"message": "New assignment added successfully"}), 201

# Get all assignments
@user_routes.route('/assignments', methods=['GET'])
def get_assignments():
    assignments = Assignment.query.all()
    return jsonify([{
        "id": assignment.id,
        "week_id": assignment.week_id,
        "title": assignment.title,
        "assignment_type": assignment.assignment_type,
        "due_date": assignment.due_date,
        "total_points": assignment.total_points
    } for assignment in assignments]), 200

# Get a specific assignment by ID
@user_routes.route('/assignments/<int:assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"message": "Assignment not found"}), 404

    return jsonify({
        "id": assignment.id,
        "week_id": assignment.week_id,
        "title": assignment.title,
        "assignment_type": assignment.assignment_type,
        "due_date": assignment.due_date,
        "total_points": assignment.total_points,
        "questions": [
            {
                "id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "points": question.points,
                "options": [
                    {
                        "id": option.id,
                        "option_text": option.option_text,
                        "is_correct": option.is_correct
                    } for option in question.options
                ]
            } for question in assignment.questions
        ]
    }), 200

# Update an existing assignment
@user_routes.route('/assignments/<int:assignment_id>', methods=['PUT'])
def update_assignment(assignment_id):
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"message": "Assignment not found"}), 404
    
    data = request.get_json()

    # Update fields if provided in the request
    if "title" in data:
        assignment.title = data["title"]
    if "assignment_type" in data:
        assignment.assignment_type = data["assignment_type"]
    if "due_date" in data:
        due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")
        assignment.due_date = due_date
    if "total_points" in data:
        assignment.total_points = data["total_points"]

    db.session.commit()

    return jsonify({"message": "Assignment updated successfully"}), 200

# Delete an assignment
@user_routes.route('/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"message": "Assignment not found"}), 404
    
    db.session.delete(assignment)
    db.session.commit()

    return jsonify({"message": "Assignment deleted successfully"}), 200

#-----------------------------------------------------CRUD - ASSIGNMENT QUESTION-----------------------------------------------------

# Create a new assignment question
@user_routes.route('/assignment_questions', methods=['POST'])
def create_assignment_question():
    data = request.get_json()
    assignment_id = data.get('assignment_id')
    question_text = data.get('question_text')
    question_type = data.get('question_type')
    points = data.get('points')

     # Validate required fields
    if not assignment_id or not question_text or not question_type or not points:
        return jsonify({"message": "All fields are required"}), 400

    # Check if the assignment exists
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"message": "Assignment not found"}), 404

    # Create a new question for the assignment
    new_question = AssignmentQuestion(
        assignment_id=assignment_id,
        question_text=question_text,
        question_type=question_type,
        points=points
    )

    db.session.add(new_question)
    
    # Update total points for the assignment
    assignment.total_points += points
    
    db.session.commit()

    return jsonify({"message": "New assignment question added successfully"}), 201

# Retrieve all assignment questions
@user_routes.route('/assignment_questions', methods=['GET'])
def get_assignment_questions():
    questions = AssignmentQuestion.query.all()
    return jsonify([{
        "id": question.id,
        "assignment_id": question.assignment_id,
        "question_text": question.question_text,
        "question_type": question.question_type,
        "points": question.points
    } for question in questions]), 200

# Retrieve a specific assignment question by ID
@user_routes.route('/assignment_questions/<int:question_id>', methods=['GET'])
def get_assignment_question(question_id):
    question = AssignmentQuestion.query.get(question_id)
    if not question:
        return jsonify({"message": "Assignment question not found"}), 404

    return jsonify({
        "id": question.id,
        "assignment_id": question.assignment_id,
        "question_text": question.question_text,
        "question_type": question.question_type,
        "points": question.points,
        "options": [
            {
                "id": option.id, 
                "option_text": option.option_text, 
                "is_correct": option.is_correct
            } for option in question.options
        ]
    }), 200

# Update an existing assignment question
@user_routes.route('/assignment_questions/<int:question_id>', methods=['PUT'])
def update_assignment_question(question_id):
    question = AssignmentQuestion.query.get(question_id)
    if not question:
        return jsonify({"message": "Assignment question not found"}), 404

    data = request.get_json()

    if "question_text" in data:
        question.question_text = data["question_text"]
    if "question_type" in data:
        question.question_type = data["question_type"]
    if "points" in data:
        previous_points = question.points  
        updated_points = data["points"]   
        question.points = updated_points
        
        # Update the total points of the associated assignment
        assignment = question.assignment
        assignment.total_points += (updated_points - previous_points)
        
    db.session.commit()

    return jsonify({"message": "Assignment question updated successfully"}), 200

 # Delete an assignment question
@user_routes.route('/assignment_questions/<int:question_id>', methods=['DELETE'])
def delete_assignment_question(question_id):
    question = AssignmentQuestion.query.get(question_id)
    if not question:
        return jsonify({"message": "Assignment question not found"}), 404

    assignment = question.assignment
    # Adjust total points for the assignment
    assignment.total_points -= question.points
    
    db.session.delete(question)
    db.session.commit()

    return jsonify({"message": "Assignment question deleted successfully"}), 200

#-----------------------------------------------------CRUD - ASSIGNMENT QUESTION OPTION-----------------------------------------------------

# API to create a new option for an assignment question
@user_routes.route('/options', methods=['POST'])
def create_option():
    data = request.get_json()
    question_id = data.get('question_id')
    option_text = data.get('option_text')
    is_correct = data.get('is_correct')

    # Validate required fields
    if question_id is None or not option_text or is_correct is None:
        return jsonify({"message": "All fields are required"}), 400

    # Check if the related assignment question exists
    question = AssignmentQuestion.query.get(question_id)
    if not question:
        return jsonify({"message": "Assignment question not found"}), 404
    
    # Prevent duplicate options for the same question
    existing_option = QuestionOption.query.filter_by(option_text=option_text, question_id=question_id).first()
    if existing_option:
        return jsonify({"message": "Option already exists for this question"}), 409
    
    # Create and save the new option
    new_option = QuestionOption(
        question_id=question_id,
        option_text=option_text,
        is_correct=is_correct
    )

    db.session.add(new_option)
    db.session.commit()

    return jsonify({"message": "New option added successfully"}), 201

# Retrieve all options for assignment questions
@user_routes.route('/options', methods=['GET'])
def get_options():
    options = QuestionOption.query.all()
    return jsonify([{
        "id": option.id,
        "question_id": option.question_id,
        "option_text": option.option_text,
        "is_correct": option.is_correct
    } for option in options]), 200

# Retrieve a specific option by its ID
@user_routes.route('/options/<int:option_id>', methods=['GET'])
def get_option(option_id):
    option = QuestionOption.query.get(option_id)
    if not option:
        return jsonify({"message": "Option not found"}), 404

    return jsonify({
        "id": option.id,
        "question_id": option.question_id,
        "option_text": option.option_text,
        "is_correct": option.is_correct
    }), 200

# Update an existing option by its ID
@user_routes.route('/options/<int:option_id>', methods=['PUT'])
def update_option(option_id):
    option = QuestionOption.query.get(option_id)
    if not option:
        return jsonify({"message": "Option not found"}), 404

    data = request.get_json()

    # Update option fields if provided
    if "option_text" in data:
        option.option_text = data["option_text"]
    if "is_correct" in data:
        option.is_correct = data["is_correct"]

    db.session.commit()

    return jsonify({"message": "Option updated successfully"}), 200

# Delete an option by its ID
@user_routes.route('/options/<int:option_id>', methods=['DELETE'])
def delete_option(option_id):
    option = QuestionOption.query.get(option_id)
    if not option:
        return jsonify({"message": "Option not found"}), 404

    db.session.delete(option)
    db.session.commit()

    return jsonify({"message": "Option deleted successfully"}), 200


# ---------------------------------------CRUD - ProgrammingAssignment-----------------------------------------------
# Add a new programming assignment
@user_routes.route('/programming_assignments', methods=['POST'])
def add_ProgrammingAssignment():
    # Parse JSON data from the request
    data = request.get_json()
    assignment_id = data.get('assignment_id')
    problem_statement = data.get('problem_statement')
    input_format = data.get('input_format')
    output_format = data.get('output_format')
    constraints = data.get('constraints')
    sample_input = data.get('sample_input')
    sample_output = data.get('sample_output')
    test_cases = data.get('test_cases', [])
    
    # Validate required fields
    if not assignment_id or not problem_statement or not input_format or not output_format or not sample_input or not sample_output:
        return jsonify({"message": "All required fields must be filled"}), 400
    
    # Create a new ProgrammingAssignment object
    new_programming_assignment = ProgrammingAssignment(
        assignment_id=assignment_id,
        problem_statement=problem_statement,
        input_format=input_format,
        output_format=output_format,
        constraints=constraints,
        sample_input=sample_input,
        sample_output=sample_output
    )
    # Set test cases and save to the database
    new_programming_assignment.set_test_cases(test_cases)
    db.session.add(new_programming_assignment)
    db.session.commit()
    
    return jsonify({"message": "Programming assignment added successfully"}), 201

# Retrieve a specific programming assignment by ID
@user_routes.route('/programming_assignments/<int:assignment_id>', methods=['GET'])
def get_ProgrammingAssignment(assignment_id):
    # Fetch the assignment from the database
    assignment = ProgrammingAssignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"message": "Programming assignment not found"}), 404
    
    # Return the assignment details as JSON
    return jsonify({
        "id": assignment.id,
        "assignment_id": assignment.assignment_id,
        "problem_statement": assignment.problem_statement,
        "input_format": assignment.input_format,
        "output_format": assignment.output_format,
        "constraints": assignment.constraints,
        "sample_input": assignment.sample_input,
        "sample_output": assignment.sample_output,
        "test_cases": assignment.get_test_cases()
    }), 200

# Update an existing programming assignment
@user_routes.route('/programming_assignments/<int:assignment_id>', methods=['PUT'])
def update_ProgrammingAssignment(assignment_id):
    assignment = ProgrammingAssignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"message": "Programming assignment not found"}), 404
    
    # Parse JSON data and update relevant fields
    data = request.get_json()
    if "problem_statement" in data:
        assignment.problem_statement = data["problem_statement"]
    if "input_format" in data:
        assignment.input_format = data["input_format"]
    if "output_format" in data:
        assignment.output_format = data["output_format"]
    if "constraints" in data:
        assignment.constraints = data["constraints"]
    if "sample_input" in data:
        assignment.sample_input = data["sample_input"]
    if "sample_output" in data:
        assignment.sample_output = data["sample_output"]
    if "test_cases" in data:
        assignment.set_test_cases(data["test_cases"])
    
    db.session.commit()
    return jsonify({"message": "Programming assignment updated successfully"}), 200

# Delete a specific programming assignment
@user_routes.route('/programming_assignments/<int:assignment_id>', methods=['DELETE'])
def delete_ProgrammingAssignment(assignment_id):
    assignment = ProgrammingAssignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"message": "Programming assignment not found"}), 404
    
    db.session.delete(assignment)
    db.session.commit()
    return jsonify({"message": "Programming assignment deleted successfully"}), 200


#-----------------------------------------Score Checking ----------------------------------------------------------------
# Calculate score based on selected option IDs
@user_routes.route('/assignments/check_score', methods=['POST'])
def check_score():
    data = request.get_json()
    option_ids = data.get("option_ids", [])

    # Validate the input option IDs
    if not option_ids or not isinstance(option_ids, list):
        return jsonify({"message": "Invalid input. Provide a list of option IDs."}), 400

    # Fetch all options in a single query
    options = QuestionOption.query.filter(QuestionOption.id.in_(option_ids)).all()

    if not options:
        return jsonify({"message": "No valid option IDs found."}), 400

    # Find correct answers 
    correct_options = [opt for opt in options if opt.is_correct]
   
    total_score = len(correct_options)

    return jsonify({"message": "Score calculated successfully", "total_score": total_score}), 200



google_api_key = SecretStr(Config.GEMINI_API_KEY)

# Initialize RAG pipeline only once
llm, vectorstore = initialize_rag_pipeline(google_api_key)

# Generating MCQs
@user_routes.route('/generate_mcq', methods=['POST'])
def generate_mcq_api():
    try:
        # Parse request data
        data = request.get_json()
        topic = data.get('topic')
        num_questions = data.get('num_questions', 5)

        # Validate input
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400

        # Generate MCQs
        mcq_response = generate_mcqs(llm, vectorstore, topic, num_questions)

        # Return the generated MCQs as a JSON response
        return jsonify(mcq_response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Video Summarizer API (Placeholder)
@user_routes.route('/video_summarizer', methods=['POST'])
def video_summarizer():
    data = request.get_json()
    lecture_id = data.get('lecture_id')
    summary_type = data.get('summary_type')

    # Validation
    if not lecture_id:
        return jsonify({"error": "lecture_id is required"}), 400
    if not summary_type:
        return jsonify({"error": "summary_type is required"}), 400

    # Mock response based on the requested summary type
    if summary_type.lower() == "paragraph":
        summary = f"Summary of lecture {lecture_id}: This lecture covers the basics of the topic, explaining key concepts in a simplified manner."
    elif summary_type.lower() == "numbered":
        summary = f"Summary of lecture {lecture_id}:\n1. Introduction to the topic\n2. Key concepts explained\n3. Summary of important points"
    elif summary_type.lower() == "bulleted":
        summary = f"Summary of lecture {lecture_id}:\n- Introduction to the topic\n- Explanation of key concepts\n- Important takeaways"
    else:
        return jsonify({"error": "Invalid summary_type. Choose from 'paragraph', 'numbered', 'bulleted'."}), 400

    return jsonify({"summary": summary}), 200

# Kia Chatbot API
@user_routes.route('/kia_chat', methods=['POST'])
def kia_chat():
    data = request.get_json()
    user_id = data.get('user_id')
    query = data.get('query')
    timestamp = data.get('timestamp')

    # Validation
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    if not query:
        return jsonify({"error": "query is required"}), 400
    if not timestamp:
        return jsonify({"error": "timestamp is required"}), 400

    # Mock chatbot response
    response_text = f"Kia says: I have received your question '{query}', let me think about it!"

    # Store the chat history as a JSON string in the file_path column
    try:
        chat_data = {
            "query": query,
            "response": response_text,
            "timestamp": timestamp
        }
        
        chat_history = ChatHistory(
            user_id=user_id,
            file_path=json.dumps(chat_data)  # Storing chat data as a JSON string
        )
        
        db.session.add(chat_history)
        db.session.commit()

        return jsonify({"response": response_text}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save chat history: {str(e)}"}), 500
    
# Explain Error API
@user_routes.route('/api/explain_error', methods=['POST'])
def explain_error():
    data = request.get_json()
    code_snippet = data.get('code_snippet')

    if not code_snippet:
        return jsonify({"error": "Code snippet is required"}), 400

    # response
    response = {
        "error_analysis": {
            "error": "SyntaxError: Unexpected indent",
            "explanation": "This error occurs when there is an unexpected indentation in the code. "
                           "Python relies on indentation to define code blocks, and inconsistent indentation "
                           "can lead to this error.",
            "fix_suggestion": "Check the indentation of your code. Make sure you use consistent spaces or tabs. "
                              "Avoid mixing both."
        }
    }
    
    return jsonify(response), 200

