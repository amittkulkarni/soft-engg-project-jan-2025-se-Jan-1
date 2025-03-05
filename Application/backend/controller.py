from flask import Blueprint, request, jsonify, render_template, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Week, Lecture, Assignment, AssignmentQuestion, QuestionOption,ProgrammingAssignment,ChatHistory
from extension import db 
from sqlalchemy.sql import text
import os
from token_validation import generate_token
from datetime import datetime
import pdfkit
import platform


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

    # Validate required fields
    if not username or not email or not password:
        return jsonify({"message": "Username, email, and password are required"}), 400

    # Check if the email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    # Hash the password and save the new user
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        role=role,
        google_id=google_id
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


# Login Route - Authenticates a user and returns an access token
@user_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Email must be provided
    if not email:
        return jsonify({"message": "Email is required"}), 400

     # Find user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    # If user has Google ID, they should not log in with a password
    if user.google_id:
        return jsonify({"message": "Please use Google Sign-In"}), 403

    # Password must be provided for normal login
    if not password:
        return jsonify({"message": "Password is required"}), 400

    # Check if the password is correct
    if not check_password_hash(user.password, password):
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
    
    # Validate required fields with proper type checking
    if not isinstance(week_number, int) or week_number <= 0:
        return jsonify({"success": False, "message": "Invalid week number. It must be a positive integer"}), 400
    
    if not title or not isinstance(title, str):
        return jsonify({"success": False, "message": "Title is required and must be a string"}), 400

    # Check if the week already exists
    existing_week = Week.query.filter_by(week_number=week_number).first()
    if existing_week:
        return jsonify({"success": False, "message": "Week already exists"}), 409
    
    try:
        # Create and save a new week
        new_week = Week(week_number=week_number, title=title)
        db.session.add(new_week)
        db.session.commit()

        return jsonify({"success": True, "message": "New week added successfully", "week_id": new_week.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500
    
    
# Get All Weeks - Retrieves a list of all weeks
@user_routes.route('/weeks', methods=['GET'])
def get_weeks():
    try:
        # Fetch all weeks from the database
        weeks = Week.query.all()

        # If no weeks exist, return an empty list with a success message
        if not weeks:
            return jsonify({"success": True, "message": "No weeks found", "weeks": []}), 200

        # Return the list of weeks with a success message
        return jsonify({
            "success": True,
            "message": "Weeks retrieved successfully",
            "weeks": [{
                "id": week.id,
                "week_number": week.week_number,
                "title": week.title
            } for week in weeks]
        }), 200

    except Exception as e:
        # Handle any database-related errors
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Get Week Details - Retrieves details of a specific week by ID
@user_routes.route('/weeks/<int:week_id>', methods=['GET'])
def get_week_details(week_id):
    try:
        # Fetch the week from the database by ID
        week = Week.query.get(week_id)

        # If the week does not exist, return a 404 error
        if not week:
            return jsonify({"success": False, "message": "Week not found"}), 404

        # Return response with week details, including lectures and assignments
        return jsonify({
            "success": True,
            "message": "Week details retrieved successfully",
            "week": {
                "id": week.id,
                "week_number": week.week_number,
                "title": week.title,
                "lectures": [{"id": lec.id, "title": lec.title, "video_id": lec.video_id} for lec in week.lectures],
                "assignments": [{"id": assgn.id, "title": assgn.title, "assignment_type": assgn.assignment_type} for assgn in week.assignments]
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Update Week - Updates the details of a specific week
@user_routes.route('/weeks/<int:week_id>', methods=['PUT'])
def update_week(week_id):
    # Fetch the week from the database
    week = Week.query.get(week_id)
    
    #If the specified week does not exist, return a 404 error
    if not week:
        return jsonify({"success": False, "message": "Week not found"}), 404
    
    # Get request data
    data = request.get_json()

    # Validate and update the week_number (if provided)
    if "week_number" in data:
        if not isinstance(data["week_number"], int) or data["week_number"] <= 0:
            return jsonify({"success": False, "message": "Invalid week number. Must be a positive integer"}), 400
        week.week_number = data["week_number"] # Assign the new value

    # Validate and update the title (if provided)
    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify({"success": False, "message": "Title must be a non-empty string"}), 400
        week.title = data["title"] 

    try:
        # Commit changes to the database
        db.session.commit()
        return jsonify({"success": True, "message": "Week updated successfully"}), 200
    except Exception as e:
        # Rollback in case of an error
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Delete Week - Deletes a specific week from the database
@user_routes.route('/weeks/<int:week_id>', methods=['DELETE'])
def delete_week(week_id):
    try:
        # Fetch the week from the database by ID
        week = Week.query.get(week_id)

        # If the week does not exist, return a 404 error
        if not week:
            return jsonify({"success": False, "message": "Week not found"}), 404

        # Delete the week from the database
        db.session.delete(week)
        db.session.commit()

        return jsonify({"success": True, "message": "Week deleted successfully"}), 200

    except Exception as e:
        # Rollback in case of an error
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


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

#--------------------------------------------- AI APIs -----------------------------------------------------------------

# Generate Topic-Specific Questions
@user_routes.route('/generate_topic_specific_questions', methods=['POST'])
def generate_topic_specific_questions():
    try:
        # Parse request data
        data = request.get_json()
        topic = data.get('topic')
        num_questions = data.get('num_questions', 5)

        # Validate input
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400

        # Placeholder response with mock questions
        mock_response = {
            "questions": [
                {
                    "question": f"Sample question 1 about {topic}?",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "answer": "Option 1"
                },
                {
                    "question": f"Sample question 2 about {topic}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option B"
                }
            ][:num_questions]
        }

        return jsonify(mock_response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Video Summarizer API 
@user_routes.route('/video_summarizer', methods=['POST'])
def video_summarizer():
    data = request.get_json()
    lecture_id = data.get('lecture_id')

    # Validation
    if not lecture_id:
        return jsonify({"error": "lecture_id is required"}), 400

    summary = f"Summary of lecture {lecture_id}: This lecture provides a detailed explanation of the topic,covering key concepts and important points in a clear and concise manner."

    return jsonify({"summary": summary}), 200



# Kia Chatbot API

# Ensure chat_logs directory exists
os.makedirs("chat_logs", exist_ok=True)

# ---------------------------- Store Chat Interaction ----------------------------

@user_routes.route('/chat_history', methods=['POST'])
def save_chat_history():
    """API to save user chat interactions as an SQL file and store file path in DB"""
    data = request.get_json()
    user_id = data.get("user_id")
    query = data.get("query")
    response = data.get("response")

    if not all([user_id, query, response]):
        return jsonify({"message": "Missing required fields"}), 400
    
    # Check if the user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User ID not found"}), 404
    
    file_path = f"chat_logs/user_{user_id}_chat.sql"

    # Generate SQL entry 
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    sql_entry = (
        "INSERT INTO chat_logs (user_id, query, response, created_at) VALUES "
        "({}, '{}', '{}', '{}');\n"
    ).format(user_id, query.replace("'", "''"), response.replace("'", "''"), timestamp)

    try:
        # Append to the SQL file
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(sql_entry)

        # Store file path in the database if not already stored
        sql_store_path = text(
            "INSERT INTO chat_history (user_id, file_path) VALUES (:user_id, :file_path) "
            "ON CONFLICT (user_id) DO NOTHING;"
        )

        db.session.execute(sql_store_path, {"user_id": user_id, "file_path": file_path})
        db.session.commit()

        return jsonify({"message": "Chat history saved successfully", "file_path": file_path}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save chat history: {str(e)}"}), 500 


# ---------------------------- Get Chat History ----------------------------
@user_routes.route('/chat_history/<int:user_id>', methods=['GET'])
def get_chat_history(user_id):
    """API to retrieve chat history file path for a user"""
    chat_record = ChatHistory.query.filter_by(user_id=user_id).first()
    if not chat_record:
        return jsonify({"message": "No chat history found"}), 404

    return jsonify({"user_id": user_id, "file_path": chat_record.file_path}), 200
    
# Explain Error API
@user_routes.route('/explain_error', methods=['POST'])
def explain_error():
    data = request.get_json()
    code_snippet = data.get('code_snippet')

    # Validation
    if not code_snippet:
        return jsonify({"error": "Code snippet is required"}), 400

    response = {
        "explanation": "SyntaxError: Unexpected indent. This error occurs when there is an unexpected indentation "
                       "in the code. Python relies on indentation to define code blocks, and inconsistent indentation "
                       "can lead to this error. To fix this, check the indentation of your code. Ensure you use consistent "
                       "spaces or tabs and avoid mixing both."
    }
    
    return jsonify(response), 200


# Generate Week Summary
@user_routes.route('/generate_week_summary', methods=['POST'])
def generate_week_summary():
    data = request.get_json()
    week_id = data.get('week_id')

    if not week_id:
        return jsonify({'error': 'week_id is required'}), 400
    
    # Check if the week exists
    week = Week.query.get(week_id)
    if not week:
        return jsonify({"message": "Week not found"}), 404
    
    return jsonify({'summary': f'Summary for week {week_id} is being generated.'}), 200


# Generate Mock
@user_routes.route('/generate_mock', methods=['POST'])
def generate_mock():
    data = request.get_json()
    topic = data.get('topic')
    num_questions = data.get('num_questions', 10)

    if not topic:
        return jsonify({'error': 'topic is required'}), 400
    
    return jsonify({'mock': f'Mock test for topic {topic} with {num_questions} questions is being generated.'}), 200

# Generate Notes
@user_routes.route('/generate_notes', methods=['POST'])
def generate_notes():
    data = request.get_json()
    topic = data.get('topic')

    if not topic:
        return jsonify({'error': 'topic is required'}), 400
    
    return jsonify({'notes': f'Notes for topic {topic} are being generated.'}), 200


# Get Topic Recommendation

# Helper Function: Map Questions to Topics
def map_question_to_topic(question_text):
    """Maps questions to relevant topics based on keywords."""
    topic_keywords = {
        "Data Visualization Libraries": ["Matplotlib", "Seaborn", "data visualization"],
        "Histogram & Distribution Plots": ["histogram", "distribution", "continuous variable"],
        "Scatter Plot & Relationships": ["scatter plot", "relationship", "two continuous variables"],
        "Categorical Data Visualization": ["bar chart", "pie chart", "categorical data"],
        "Advantages of Seaborn": ["Seaborn", "themes", "aesthetics", "syntax", "Pandas DataFrames"]
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in question_text.lower() for keyword in keywords):
            return topic

    return "General Data Visualization Concepts"  # Default topic if no match found

# Topic Recommendation
@user_routes.route('/topic_recommendation', methods=['POST'])
def topic_recommendation():
    """Identifies incorrectly answered questions and recommends topics."""
    data = request.get_json()

    submitted_answers = data.get("answers", [])  # List of {"question_id": X, "selected_option_id": Y}

    if not submitted_answers:
        return jsonify({"message": "answers are required"}), 400

    topic_recommendation = []

    for answer in submitted_answers:
        question_id = answer.get("question_id")
        selected_option_id = answer.get("selected_option_id")

        # Get correct option for the question
        correct_option = QuestionOption.query.filter_by(question_id=question_id, is_correct=True).first()

        if correct_option and correct_option.id != selected_option_id:
            question = AssignmentQuestion.query.get(question_id)
            topic = map_question_to_topic(question.question_text)  # Function to get topic
            
            topic_recommendation.append(topic)

    return jsonify({"topic_recommendation": topic_recommendation}), 200



# ---------------------------------- PDF Generation (wkhtmltopdf Setup) ----------------------------------

# Automatically detect OS and set the wkhtmltopdf path
if platform.system() == "Windows":
    WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
elif platform.system() == "Darwin":  # macOS
    WKHTMLTOPDF_PATH = "/usr/local/bin/wkhtmltopdf"
else:  # Linux
    WKHTMLTOPDF_PATH = "/usr/bin/wkhtmltopdf"

# Ensure wkhtmltopdf exists
if not os.path.exists(WKHTMLTOPDF_PATH):
    raise FileNotFoundError(f"wkhtmltopdf not found at {WKHTMLTOPDF_PATH}")

# Explicitly configure pdfkit
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# Ensure reports directory exists
BASE_DIR = os.path.abspath(os.path.dirname(__file__)) # Get current directory
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)  


# ---------------------------------- Download Report (PDF) ----------------------------------
@user_routes.route('/download_report', methods=['POST'])
def download_report():
    """Generates and downloads a report as a PDF file."""
    data = request.json
    username = data.get("username")
    score = data.get("score")
    total = data.get("total")
    suggestions = data.get("suggestions", [])
    questions = data.get("questions", [])  # List of questions

    # Render the HTML template with data
    html_content = render_template("report.html", username=username, score=score, total=total, suggestions=suggestions, questions=questions)
    
    # Define file path inside reports folder
    pdf_file = os.path.join(REPORTS_DIR, f"MockTest_{username}.pdf")

    # Generate PDF
    try:
        pdfkit.from_string(html_content, pdf_file, configuration=config)
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

    # Send generated file as download
    try:
        return send_file(pdf_file, as_attachment=True, download_name=f"MockTest_{username}.pdf")
    except Exception as e:
        return jsonify({"error": f"File sending failed: {str(e)}"}), 500