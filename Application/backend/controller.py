from flask import Blueprint, request, jsonify, render_template, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Week, Lecture, Assignment, AssignmentQuestion, QuestionOption, ProgrammingAssignment, \
    ChatHistory
from extension import db
import os
from token_validation import generate_token
from datetime import datetime
import pdfkit
import platform
import subprocess
import tempfile
import requests
import logging

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.tables import TableExtension
import re

from quiz_mock import generate_mcqs
from week_summarizer import summarize_week_slides
from topic_specfic_mock import generate_topic_mcqs
from error_explainer import explain_error
from lecture_summarizer import summarize_lecture
from kia_chatbot import initialize_database, save_chat_turn_to_db, load_chat_history_from_db, get_answer, \
    clear_user_history
from notes_generator import generate_topic_notes
from topic_suggestions import generate_topic_suggestions

user_routes = Blueprint('user_routes', __name__)

# ------------------------- User Authentication Routes -------------------------

# Signup Route - Registers a new user
# Environment variables
GOOGLE_CLIENT_ID = "859846322076-3u1k9ter70q7b5jqaum8i7e5jc506mnh.apps.googleusercontent.com"  # Set your Google Client ID
GOOGLE_CLIENT_SECRET = "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"

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@user_routes.route('/google_signup', methods=['POST'])
def google_signup():
    data = request.get_json()
    access_token = data.get('access_token')

    if not access_token:
        return jsonify({"Success": False, "message": "Google access token is required"}), 400

    try:
        # Use the access token to get user info from Google
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # Fetch user information from Google's userinfo endpoint
        response = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers)

        if response.status_code != 200:
            return jsonify({"Success": False, "message": f"Failed to verify access token: {response.text}"}), 400

        user_info = response.json()

        # Extract user data from the response
        google_id = user_info.get('sub')
        email = user_info.get('email')
        username = user_info.get('name')
        email_verified = user_info.get('email_verified', False)

        # Check if email is verified
        if not email_verified:
            return jsonify({"Success": False, "message": "Email not verified with Google"}), 400

        # Check if user already exists - handle as login case
        user = User.query.filter_by(google_id=google_id).first()
        if user:
            token = generate_token(user.id)
            return jsonify({"Success": True, "access_token": token, "message": "Login successful"}), 200

        # Check if email is already in use
        if User.query.filter_by(email=email).first():
            return jsonify({"Success": False, "message": "Email already exists"}), 400

        # Create a new user with Google ID
        new_user = User(
            username=username,
            email=email,
            password=None,  # No password needed for Google Auth
            role='student',  # Default role
            google_id=google_id
        )

        db.session.add(new_user)
        db.session.commit()

        # Generate JWT token
        token = generate_token(new_user.id)
        return jsonify({"Success": True, "access_token": token, "message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"Success": False, "message": f"An error occurred: {str(e)}"}), 500


@user_routes.route('/google_login', methods=['POST'])
def google_login():
    data = request.get_json()
    access_token = data.get('access_token')

    if not access_token:
        return jsonify({"Success": False, "message": "Google access token is required"}), 400

    try:
        # Use the access token to get user info from Google
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # Fetch user information from Google's userinfo endpoint
        response = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers)

        if response.status_code != 200:
            return jsonify({"Success": False, "message": f"Failed to verify access token: {response.text}"}), 400

        user_info = response.json()

        # Extract user's Google ID
        google_id = user_info.get('sub')

        # Check if the user exists with the provided Google ID
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            return jsonify({"Success": False, "message": "User not registered"}), 404

        # Generate JWT token
        token = generate_token(user.id)
        return jsonify({"Success": True, "access_token": token, "message": "Login successful"}), 200

    except Exception as e:
        return jsonify({"Success": False, "message": f"An error occurred: {str(e)}"}), 500


# Signup Route - Registers a new user

@user_routes.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')  # Default to 'student' if not provided

    # Check if the username exists only if provided
    if username and User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    # Check if the email is provided
    if not email:
        return jsonify({"message": "Email is required"}), 400

    # Check if the email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    # Password validation (required if not signing up via Google)
    if not password:
        return jsonify({"message": "Password is required"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Create and save new user
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        role=role,
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

    # Validate required fields
    if not all([email, password]):
        return jsonify({"message": "Email and password are required"}), 400

    # Find user by email
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Generate authentication token
    token = generate_token(user.id)
    return jsonify({"access_token": token, "message": "Login successful"}), 200


# -----------------------------------------CRUD Operations for Weeks--------------------------------------------------------------

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
                "assignments": [{"id": assgn.id, "title": assgn.title, "assignment_type": assgn.assignment_type} for
                                assgn in week.assignments]
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

    # If the specified week does not exist, return a 404 error
    if not week:
        return jsonify({"success": False, "message": "Week not found"}), 404

    # Get request data
    data = request.get_json()

    # Validate and update the week_number (if provided)
    if "week_number" in data:
        if not isinstance(data["week_number"], int) or data["week_number"] <= 0:
            return jsonify({"success": False, "message": "Invalid week number. Must be a positive integer"}), 400
        week.week_number = data["week_number"]  # Assign the new value

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


# -----------------------------------------------------CRUD Operations for Lectures -----------------------------------------------------

# Create Lecture - Adds a new lecture to a specific week
@user_routes.route('/lectures', methods=['POST'])
def create_lecture():
    try:
        data = request.get_json()
        week_id = data.get('week_id')
        title = data.get('title')
        video_id = data.get('video_id')

        # Validate required fields with proper type checking
        if not isinstance(week_id, int) or week_id <= 0:
            return jsonify({"success": False, "message": "Invalid week ID. It must be a positive integer"}), 400

        if not title or not isinstance(title, str):
            return jsonify({"success": False, "message": "Title is required and must be a string"}), 400

        if not video_id or not isinstance(video_id, str):
            return jsonify({"success": False, "message": "Video ID is required and must be a string"}), 400

        # Check if the associated week exists
        week = Week.query.get(week_id)
        if not week:
            return jsonify({"success": False, "message": "Week not found"}), 404

        # Check if the lecture title already exists in the same week
        existing_lecture = Lecture.query.filter_by(week_id=week_id, title=title).first()
        if existing_lecture:
            return jsonify({"success": False, "message": "Lecture already exists in this week"}), 409

        # Create and save the new lecture
        new_lecture = Lecture(week_id=week_id, title=title, video_id=video_id)
        db.session.add(new_lecture)
        db.session.commit()

        return jsonify(
            {"success": True, "message": "New lecture added successfully", "lecture_id": new_lecture.id}), 201

    except Exception as e:
        # Rollback in case of an error
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Get All Lectures - Retrieves a list of all lectures
@user_routes.route('/lectures', methods=['GET'])
def get_lectures():
    try:
        # Fetch all lectures from the database
        lectures = Lecture.query.all()

        # If no lectures exist, return an empty list with a message
        if not lectures:
            return jsonify({"success": True, "message": "No lectures found", "lectures": []}), 200

        # Return the list of lectures with success message
        return jsonify({
            "success": True,
            "message": "Lectures retrieved successfully",
            "lectures": [{
                "id": lecture.id,
                "week_id": lecture.week_id,
                "title": lecture.title,
                "video_id": lecture.video_id
            } for lecture in lectures]
        }), 200

    except Exception as e:
        # Handle unexpected errors and return a database error message
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Get Lecture Details - Retrieves details of a specific lecture by ID
@user_routes.route('/lectures/<int:lecture_id>', methods=['GET'])
def get_lecture_details(lecture_id):
    try:
        # Fetch the lecture by ID from the database
        lecture = Lecture.query.get(lecture_id)

        # If the lecture does not exist, return a 404 error
        if not lecture:
            return jsonify({"success": False, "message": "Lecture not found"}), 404

        # Return the lecture details with a success message
        return jsonify({
            "success": True,
            "message": "Lecture retrieved successfully",
            "lecture": {
                "id": lecture.id,
                "week_id": lecture.week_id,
                "title": lecture.title,
                "video_id": lecture.video_id
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors and return a database error message
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Update Lecture - Updates the details of a specific lecture
@user_routes.route('/lectures/<int:lecture_id>', methods=['PUT'])
def update_lecture(lecture_id):
    try:
        # Fetch the lecture from the database
        lecture = Lecture.query.get(lecture_id)

        # If lecture does not exist, return a 404 error
        if not lecture:
            return jsonify({"success": False, "message": "Lecture not found"}), 404

        # Parse the JSON request body
        data = request.get_json()

        # Validate that data is provided
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        # Update lecture properties only if present in the request
        if "week_id" in data:
            if not isinstance(data["week_id"], int):
                return jsonify({"success": False, "message": "Invalid week_id format"}), 400
            lecture.week_id = data["week_id"]

        if "title" in data:
            if not isinstance(data["title"], str) or not data["title"].strip():
                return jsonify({"success": False, "message": "Invalid title format"}), 400
            lecture.title = data["title"]

        if "video_id" in data:
            if not isinstance(data["video_id"], str) or not data["video_id"].strip():
                return jsonify({"success": False, "message": "Invalid video_id format"}), 400
            lecture.video_id = data["video_id"]

        # Commit the changes to the database
        db.session.commit()

        return jsonify({"success": True, "message": "Lecture updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Delete Lecture - Deletes a specific lecture from the database
@user_routes.route('/lectures/<int:lecture_id>', methods=['DELETE'])
def delete_lecture(lecture_id):
    try:
        # Fetch the lecture from the database
        lecture = Lecture.query.get(lecture_id)

        # If lecture does not exist, return a 404 error
        if not lecture:
            return jsonify({"success": False, "message": "Lecture not found"}), 404

        # Delete the lecture
        db.session.delete(lecture)
        db.session.commit()

        return jsonify({"success": True, "message": "Lecture deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# -----------------------------------------------------CRUD - ASSIGNMENT-----------------------------------------------------

# Create a new assignment
@user_routes.route('/assignments', methods=['POST'])
def create_assignment():
    try:
        data = request.get_json()

        # Extract fields from the request body
        week_id = data.get('week_id')
        title = data.get('title')
        assignment_type = data.get('assignment_type')
        due_date = data.get('due_date')

        # Validate required fields
        if not all([week_id, title, assignment_type, due_date]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        # Validate due_date format
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Check if the associated week exists
        week = Week.query.get(week_id)
        if not week:
            return jsonify({'success': False, 'message': 'Week not found'}), 404

        # Check if an assignment with the same title exists in the same week
        existing_assignment = Assignment.query.filter_by(title=title, week_id=week_id).first()
        if existing_assignment:
            return jsonify({'success': False, 'message': 'Assignment already exists in this week'}), 409

        # Create a new assignment and save it to the database
        new_assignment = Assignment(
            week_id=week_id,
            title=title,
            assignment_type=assignment_type,
            due_date=due_date
        )
        db.session.add(new_assignment)
        db.session.commit()

        return jsonify(
            {'success': True, 'message': 'New assignment added successfully', 'assignment_id': new_assignment.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500


# Get All Assignments - Retrieves a list of all assignments
@user_routes.route('/assignments', methods=['GET'])
def get_assignments():
    try:
        assignments = Assignment.query.all()

        # If no assignments are found, return an empty list with a message
        if not assignments:
            return jsonify({"success": True, "message": "No assignments found", "assignments": []}), 200

        return jsonify({
            "success": True,
            "message": "Assignments retrieved successfully",
            "assignments": [{
                "id": assignment.id,
                "week_id": assignment.week_id,
                "title": assignment.title,
                "assignment_type": assignment.assignment_type,
                "due_date": assignment.due_date.strftime('%Y-%m-%d'),  # Convert date to string format
                "total_points": assignment.total_points
            } for assignment in assignments]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Get Assignment Details - Retrieves details of a specific assignment by ID
@user_routes.route('/assignments/<int:assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    try:
        assignment = Assignment.query.get(assignment_id)

        # Check if the assignment exists
        if not assignment:
            return jsonify({"success": False, "message": "Assignment not found"}), 404

        return jsonify({
            "success": True,
            "message": "Assignment retrieved successfully",
            "assignment": {
                "id": assignment.id,
                "week_id": assignment.week_id,
                "title": assignment.title,
                "assignment_type": assignment.assignment_type,
                "due_date": assignment.due_date.strftime('%Y-%m-%d'),  # Convert date to string format
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
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


## Update Assignment - Updates details of a specific assignment
@user_routes.route('/assignments/<int:assignment_id>', methods=['PUT'])
def update_assignment(assignment_id):
    try:
        assignment = Assignment.query.get(assignment_id)

        # Check if assignment exists
        if not assignment:
            return jsonify({"success": False, "message": "Assignment not found"}), 404

        data = request.get_json()

        # Update fields only if they are provided in the request
        if "title" in data:
            assignment.title = data["title"]
        if "assignment_type" in data:
            assignment.assignment_type = data["assignment_type"]
        if "due_date" in data:
            try:
                assignment.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")
            except ValueError:
                return jsonify({"success": False, "message": "Invalid due_date format. Use YYYY-MM-DD."}), 400
        if "total_points" in data:
            assignment.total_points = data["total_points"]

        db.session.commit()

        return jsonify({"success": True, "message": "Assignment updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Delete Assignment - Deletes a specific assignment from the database
@user_routes.route('/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    try:
        assignment = Assignment.query.get(assignment_id)

        # Check if assignment exists
        if not assignment:
            return jsonify({"success": False, "message": "Assignment not found"}), 404

        # Delete the assignment
        db.session.delete(assignment)
        db.session.commit()

        return jsonify({"success": True, "message": "Assignment deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# -----------------------------------------------------CRUD - ASSIGNMENT QUESTION-----------------------------------------------------

# Create Assignment Question - Adds a new question to a specific assignment
@user_routes.route('/assignment_questions', methods=['POST'])
def create_assignment_question():
    try:
        data = request.get_json()
        assignment_id = data.get('assignment_id')
        question_text = data.get('question_text')
        question_type = data.get('question_type')
        points = data.get('points')

        # Validate required fields
        if not assignment_id or not question_text or not question_type or points is None:
            return jsonify({"success": False, "message": "All fields are required"}), 400

        # Ensure points is a positive integer
        if not isinstance(points, int) or points < 0:
            return jsonify({"success": False, "message": "Points must be a non-negative integer"}), 400

        # Check if the assignment exists
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({"success": False, "message": "Assignment not found"}), 404

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

        return jsonify({"success": True, "message": "New assignment question added successfully",
                        "question_id": new_question.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Retrieve All Assignment Questions - Fetches all questions across assignments
@user_routes.route('/assignment_questions', methods=['GET'])
def get_assignment_questions():
    try:
        # Fetch all assignment questions from the database
        questions = AssignmentQuestion.query.all()

        # If no questions exist, return an empty list with a message
        if not questions:
            return jsonify({"success": True, "message": "No assignment questions found", "questions": []}), 200

        # Prepare response data
        question_list = [{
            "id": question.id,
            "assignment_id": question.assignment_id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "points": question.points
        } for question in questions]

        return jsonify({"success": True, "questions": question_list}), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Retrieve a specific assignment question by ID
@user_routes.route('/assignment_questions/<int:question_id>', methods=['GET'])
def get_assignment_question(question_id):
    try:
        question = AssignmentQuestion.query.get(question_id)
        if not question:
            return jsonify({'success': False, 'message': 'Assignment question not found'}), 404

        return jsonify({'success': True, 'question': {
            'id': question.id,
            'assignment_id': question.assignment_id,
            'question_text': question.question_text,
            'question_type': question.question_type,
            'points': question.points,
            'options': [{
                'id': option.id,
                'option_text': option.option_text,
                'is_correct': option.is_correct
            } for option in question.options]
        }}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred', 'error': str(e)}), 500


# Update an existing assignment question
@user_routes.route('/assignment_questions/<int:question_id>', methods=['PUT'])
def update_assignment_question(question_id):
    try:
        question = AssignmentQuestion.query.get(question_id)
        if not question:
            return jsonify({'success': False, 'message': 'Assignment question not found'}), 404

        data = request.get_json()

        if 'question_text' in data:
            question.question_text = data['question_text']
        if 'question_type' in data:
            question.question_type = data['question_type']
        if 'points' in data:
            previous_points = question.points
            updated_points = data['points']
            question.points = updated_points

            # Update the total points of the associated assignment
            assignment = question.assignment
            assignment.total_points = (assignment.total_points or 0) + (updated_points - previous_points)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Assignment question updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred', 'error': str(e)}), 500


# Delete an assignment question
@user_routes.route('/assignment_questions/<int:question_id>', methods=['DELETE'])
def delete_assignment_question(question_id):
    try:
        question = AssignmentQuestion.query.get(question_id)
        if not question:
            return jsonify({'success': False, 'message': 'Assignment question not found'}), 404

        assignment = question.assignment

        # Adjust total points for the assignment
        assignment.total_points = (assignment.total_points or 0) - question.points

        db.session.delete(question)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Assignment question deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred', 'error': str(e)}), 500


# -----------------------------------------------------CRUD - ASSIGNMENT QUESTION OPTION-----------------------------------------------------

# API to create a new option for an assignment question
@user_routes.route('/options', methods=['POST'])
def create_option():
    try:
        # Get the request data
        data = request.get_json()
        question_id = data.get('question_id')
        option_text = data.get('option_text')
        is_correct = data.get('is_correct')

        # Validate required fields
        if question_id is None or not option_text or is_correct is None:
            return jsonify({"success": False, "message": "All fields are required"}), 400

        # Check if the related assignment question exists
        question = AssignmentQuestion.query.get(question_id)
        if not question:
            return jsonify({"success": False, "message": "Assignment question not found"}), 404

        # Prevent duplicate options for the same question
        existing_option = QuestionOption.query.filter_by(option_text=option_text, question_id=question_id).first()
        if existing_option:
            return jsonify({"success": False, "message": "Option already exists for this question"}), 409

        # Create and save the new option
        new_option = QuestionOption(
            question_id=question_id,
            option_text=option_text,
            is_correct=is_correct
        )
        db.session.add(new_option)
        db.session.commit()

        return jsonify({"success": True, "message": "New option added successfully"}), 201

    except Exception as e:
        # Rollback in case of an error
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Retrieve all options for assignment questions
@user_routes.route('/options', methods=['GET'])
def get_options():
    try:
        # Fetch all options from the database
        options = QuestionOption.query.all()

        return jsonify({"success": True, "options": [{
            "id": option.id,
            "question_id": option.question_id,
            "option_text": option.option_text,
            "is_correct": option.is_correct
        } for option in options]}), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Retrieve a specific option by its ID
@user_routes.route('/options/<int:option_id>', methods=['GET'])
def get_option(option_id):
    try:
        # Fetch the option by ID
        option = QuestionOption.query.get(option_id)
        if not option:
            return jsonify({"success": False, "message": "Option not found"}), 404

        # Return the option details
        return jsonify({"success": True, "option": {
            "id": option.id,
            "question_id": option.question_id,
            "option_text": option.option_text,
            "is_correct": option.is_correct
        }}), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Update an existing option by its ID
@user_routes.route('/options/<int:option_id>', methods=['PUT'])
def update_option(option_id):
    try:
        # Fetch the option by ID
        option = QuestionOption.query.get(option_id)
        if not option:
            return jsonify({"success": False, "message": "Option not found"}), 404

        # Get the request data
        data = request.get_json()

        # Update option fields if provided
        if "option_text" in data:
            option.option_text = data["option_text"]
        if "is_correct" in data:
            option.is_correct = data["is_correct"]

        # Commit changes to the database
        db.session.commit()

        return jsonify({"success": True, "message": "Option updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Delete an option by its ID
@user_routes.route('/options/<int:option_id>', methods=['DELETE'])
def delete_option(option_id):
    try:
        # Fetch the option by ID
        option = QuestionOption.query.get(option_id)
        if not option:
            return jsonify({"success": False, "message": "Option not found"}), 404

        # Delete the option from the database
        db.session.delete(option)
        db.session.commit()

        return jsonify({"success": True, "message": "Option deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# ---------------------------------------CRUD - ProgrammingAssignment-----------------------------------------------

# Add a New Programming Assignment
@user_routes.route('/programming_assignments', methods=['POST'])
def add_ProgrammingAssignment():
    try:
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
        if not all([assignment_id, problem_statement, input_format, output_format, sample_input, sample_output]):
            return jsonify({"success": False, "message": "All required fields must be filled"}), 400

        # Prevent duplicate assignment IDs
        existing_assignment = ProgrammingAssignment.query.filter_by(assignment_id=assignment_id).first()
        if existing_assignment:
            return jsonify({"success": False, "message": "Assignment ID already exists"}), 409

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

        return jsonify({"success": True, "message": "Programming assignment added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


@user_routes.route('/programming_assignments/<int:assignment_id>', methods=['GET'])
def get_ProgrammingAssignment(assignment_id):
    try:
        # Explicitly set starting table to resolve join ambiguity
        assignment = db.session.query(
            ProgrammingAssignment, Week
        ).select_from(ProgrammingAssignment) \
            .join(Assignment, ProgrammingAssignment.assignment_id == Assignment.id) \
            .join(Week, Assignment.week_id == Week.id) \
            .filter(ProgrammingAssignment.assignment_id == assignment_id).first()  # <-- Changed here

        if not assignment:
            return jsonify({"success": False, "message": "Programming assignment not found"}), 404

        programming_assignment, week = assignment  # Extract details from the joined result

        # Return the assignment details along with the week number
        return jsonify({
            "success": True,
            "data": {
                "id": programming_assignment.id,
                "assignment_id": programming_assignment.assignment_id,
                "problem_statement": programming_assignment.problem_statement,
                "input_format": programming_assignment.input_format,
                "output_format": programming_assignment.output_format,
                "constraints": programming_assignment.constraints,
                "sample_input": programming_assignment.sample_input,
                "sample_output": programming_assignment.sample_output,
                "test_cases": programming_assignment.get_test_cases(),
                "week_number": week.week_number
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Error retrieving assignment", "error": str(e)}), 500


# Update an existing programming assignment
@user_routes.route('/programming_assignments/<int:assignment_id>', methods=['PUT'])
def update_ProgrammingAssignment(assignment_id):
    try:
        assignment = ProgrammingAssignment.query.get(assignment_id)
        if not assignment:
            return jsonify({"success": False, "message": "Programming assignment not found"}), 404

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
        return jsonify({"success": True, "message": "Programming assignment updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


# Delete a specific programming assignment
@user_routes.route('/programming_assignments/<int:assignment_id>', methods=['DELETE'])
def delete_ProgrammingAssignment(assignment_id):
    try:
        assignment = ProgrammingAssignment.query.get(assignment_id)
        if not assignment:
            return jsonify({"success": False, "message": "Programming assignment not found"}), 404

        db.session.delete(assignment)
        db.session.commit()
        return jsonify({"success": True, "message": "Programming assignment deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


@user_routes.route('/programming_assignments/<int:assignment_id>/execute', methods=['POST'])
def execute_solution(assignment_id):
    try:
        # Parse the request data
        data = request.get_json()
        code = data.get("code")

        if not code:
            return jsonify({"success": False, "message": "No code submitted"}), 400

        # Fetch the assignment to verify it exists
        assignment = ProgrammingAssignment.query.get(assignment_id)
        if not assignment:
            return jsonify({"success": False, "message": "Programming assignment not found"}), 404

        # Get test cases from the assignment
        test_cases = assignment.get_test_cases()

        # Execute the code against the test cases
        results = []
        passed_count = 0
        total_cases = len(test_cases)

        for i, test_case in enumerate(test_cases):
            try:
                # Get input for this test case
                input_data = test_case["input"]

                if "output" in test_case:
                    expected_output = test_case["output"]
                else:
                    raise KeyError(f"Test case {i + 1} is missing output field")

                # Execute the code with this input
                actual_output = execute_python_code(code, input_data)

                # Compare output with expected
                # is_correct = compare_ml_outputs(actual_output, expected_output)

                if actual_output.strip() == expected_output.strip():
                    status = "passed"
                    passed_count += 1
                else:
                    status = "failed"

                # Add result
                results.append({
                    "test_case_id": i + 1,
                    "status": status,
                    "input": input_data,
                    "expected_output": expected_output,
                    "actual_output": actual_output
                })

            except Exception as e:
                # Handle execution errors
                results.append({
                    "test_case_id": i + 1,
                    "status": "error",
                    "error_message": str(e)
                })

        # Calculate score
        score = (passed_count / total_cases) * 100 if total_cases > 0 else 0

        # Return results
        return jsonify({
            "success": True,
            "score": score,
            "passed_count": passed_count,
            "total_cases": total_cases,
            "results": results,
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()  # Print stacktrace for debugging
        return jsonify({"success": False, "message": f"Error executing code: {str(e)}", "error": str(e)}), 500


# Helper function to execute Python code
def execute_python_code(code, input_data):
    """
Execute python code with provided input and return the output
    """

    # Ensure input ends with newline
    if not input_data.endswith('\n'):
        input_data += '\n'

    # Create temporary files for code
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        f.write(code)
        code_file = f.name

    try:
        # Execute the code with the input
        result = subprocess.run(
            ['python', code_file],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )

        if result.returncode != 0:
            # If execution failed, return the error
            return f"Execution Error: {result.stderr}"

        return result.stdout

    finally:
        # Clean up temporary files
        os.unlink(code_file)


# Function to compare Machine Learning outputs with tolerance
# def compare_ml_outputs(actual_output, expected_output):
#     """
# Compare ML prediction outputs with a tolerance for floating-point differences
#     """
#     try:
#         # Parse outputs (assuming they're newline-separated numeric values)
#         actual_values = [float(line.strip()) for line in actual_output.strip().split('\n') if line.strip()]
#         expected_values = [float(line.strip()) for line in expected_output.strip().split('\n') if line.strip()]
#
#         # Check if number of predictions matches
#         if len(actual_values) != len(expected_values):
#             return False
#
#         # Check if each prediction is within acceptable error margin (5%)
#         for actual, expected in zip(actual_values, expected_values):
#             error_margin = abs(expected) * 0.05  # 5% tolerance
#             if abs(actual - expected) > error_margin:
#                 return False
#
#         return True
#
#     except Exception:
#         # If parsing fails, fall back to exact string comparison
#         return actual_output.strip() == expected_output.strip()


# -----------------------------------------Score Checking ----------------------------------------------------------------
# Calculate score based on selected option IDs
@user_routes.route('/assignments/check_score', methods=['POST'])
def check_score():
    # Parse the request data to get the list of selected option IDs
    data = request.get_json()
    option_ids = data.get("option_ids", [])

    # Validate the input option IDs
    if not option_ids or not isinstance(option_ids, list):
        return jsonify({"success": False, "message": "Invalid input. Provide a list of option IDs."}), 400

    # Fetch all options from the database based on provided option IDs
    options = QuestionOption.query.filter(QuestionOption.id.in_(option_ids)).all()

    # Check if any valid options were retrieved
    if not options:
        return jsonify({"success": False, "message": "No valid option IDs found."}), 400

    # Identify the correct options by checking the 'is_correct' attribute
    correct_options = [opt for opt in options if opt.is_correct]

    # Calculate the score as the count of correct options
    total_score = len(correct_options)

    # Return the score with a success message
    return jsonify({"success": True, "message": "Score calculated successfully", "total_score": total_score}), 200


# --------------------------------------------- AI APIs -----------------------------------------------------------------

# Generate Topic-Specific Questions
@user_routes.route('/generate_topic_specific_questions', methods=['POST'])
def generate_topic_specific_questions():
    try:
        # Parse request data
        data = request.get_json()
        topic = data.get('topic')
        num_questions = data.get('num_questions', 5)

        # Input Validations
        if not topic:
            return jsonify({'success': False, 'message': 'Topic is required'}), 400

        if not isinstance(num_questions, int):
            return jsonify({'success': False, 'message': 'Invalid data type for num_questions'}), 400

        if num_questions < 1:
            return jsonify({'success': False, 'message': 'Number of questions must be at least 1'}), 400

        if not isinstance(num_questions, int):
            return jsonify({'success': False, 'message': 'Invalid data type for num_questions'}), 400

        if num_questions < 1:
            return jsonify({'success': False, 'message': 'Number of questions must be at least 1'}), 400

        # Generate dynamic MCQs using the imported function
        try:
            mcq_set = generate_topic_mcqs(topic, num_questions)

            # Debug the returned data structure type
            print(f"MCQ Set type: {type(mcq_set)}")

            # Handle dictionary return case
            if isinstance(mcq_set, dict):
                if "questions" in mcq_set:
                    # Dictionary with questions key
                    questions_list = mcq_set["questions"]
                    response_data = {
                        'message': 'Questions generated successfully',
                        'success': True,
                        'questions': [
                            {
                                'question': q["question"],
                                'options': q["options"],
                                'correct_answer': q["correct_answer"],
                            } for q in questions_list
                        ]
                    }
                else:
                    # Flat dictionary of a single question
                    response_data = {
                        'message': 'Questions generated successfully',
                        'success': True,
                        'questions': [mcq_set]  # Just use the dict directly
                    }
            # Handle Pydantic model return case
            elif hasattr(mcq_set, "questions"):
                response_data = {
                    'message': 'Questions generated successfully',
                    'success': True,
                    'questions': [
                        {
                            'question': q.question,
                            'options': q.options,
                            'correct_answer': q.correct_answer,
                        } for q in mcq_set.questions
                    ]
                }
            # Handle list return case
            elif isinstance(mcq_set, list):
                response_data = {
                    'message': 'Questions generated successfully',
                    'success': True,
                    'questions': [
                        {
                            'question': q["question"] if isinstance(q, dict) else q.question,
                            'options': q["options"] if isinstance(q, dict) else q.options,
                            'correct_answer': q["correct_answer"] if isinstance(q, dict) else q.correct_answer,
                        } for q in mcq_set
                    ]
                }
            else:
                raise TypeError(f"Unexpected return type from generate_topic_mcqs: {type(mcq_set)}")

            return jsonify(response_data), 200

        except Exception as e:
            import traceback
            traceback.print_exc()  # Print full stack trace for debugging
            return jsonify({
                'success': False,
                'message': 'Failed to generate dynamic questions',
                'error': str(e)
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to generate questions',
            'error': str(e)
        }), 500


# Video Summarizer API 
@user_routes.route('/video_summarizer', methods=['POST'])
def video_summarizer():
    # Parse request data
    data = request.get_json()
    week_id = data.get('week_id')

    # Validate input
    if not week_id:
        return jsonify({'message': 'week_id is required', 'success': False}), 400

    # Generate summary using lecture_summarizer logic
    result = summarize_lecture(week_id, 1)

    return jsonify(result), 200 if result['success'] else 404


# Kia Chatbot API

# Ensure chat_logs directory exists
os.makedirs("chat_logs", exist_ok=True)


@user_routes.route('/kia_chat', methods=['POST'])
def chat_with_kia():
    """API to process user query and get response from Kia"""
    data = request.get_json()
    user_id = data.get('user_id')
    query = data.get('query')

    if not all([user_id, query]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        # Use the get_answer function from your existing code
        result = get_answer(user_id, query)

        return jsonify(result), 200 if result['success'] else 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to process query: {str(e)}',
            'response': 'I seem to be having a little brain freeze! Let\'s chat again in a moment? 😅'
        }), 500


@user_routes.route('/reset_chat_history', methods=['POST'])
def reset_chat_history():
    """API to clear chat history for a user"""
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'success': False, 'message': 'User ID is required'}), 400

    try:
        # Use the clear_user_history function from your existing code
        result = clear_user_history(user_id)
        return jsonify(result), 200 if result['success'] else 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to clear chat history: {str(e)}'
        }), 500


@user_routes.route('/chat_history', methods=['POST'])
def save_chat_history():
    """API to save user chat interactions in SQLite database"""
    data = request.get_json()
    user_id = data.get("user_id")
    query = data.get("query")
    response = data.get("response")

    # Validation for required fields
    if not all([user_id, query, response]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        # Initialize database if not present
        initialize_database()

        # Save chat interaction in the database
        save_chat_turn_to_db(user_id, query, response)

        return jsonify({
            "success": True,
            "message": "Chat history saved successfully",
            "user_id": user_id
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to save chat history: {str(e)}"
        }), 500


# ---------------------------- Get Chat History ----------------------------
@user_routes.route('/chat_history/<int:user_id>', methods=['GET'])
def get_chat_history(user_id):
    """API to retrieve chat history for a given user"""
    try:
        # Use the load_chat_history_from_db function to get the ChatMessageHistory object
        chat_history = load_chat_history_from_db(user_id)

        # If no messages found in the ChatMessageHistory
        if not chat_history.messages:
            return jsonify({
                'success': False,
                'message': 'No chat history found for the given user ID',
                'user_id': user_id
            }), 404

        # Convert ChatMessageHistory to the format expected by the frontend
        formatted_history = []
        messages = chat_history.messages

        # Format messages for frontend consumption
        for i in range(0, len(messages), 2):
            if i < len(messages):
                # Add user message
                formatted_history.append({
                    "sender": "user",
                    "text": messages[i].content,
                    "timestamp": None
                })

                # Add KIA response (if exists)
                if i+1 < len(messages):
                    formatted_history.append({
                        "sender": "kia",
                        "text": messages[i+1].content,
                        "timestamp": None
                    })

        return jsonify({
            'success': True,
            'message': 'Chat history retrieved successfully',
            'user_id': user_id,
            'chat_history': formatted_history
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve chat history: {str(e)}',
            'user_id': user_id
        }), 500


# Explain Error API
@user_routes.route('/explain_error', methods=['POST'])
def explain_error_route():
    '''API to explain errors in a provided code snippet'''
    data = request.get_json()
    code_snippet = data.get('code_snippet')

    # Validate if code snippet is provided
    if not code_snippet:
        return jsonify({'message': 'Code snippet is required', 'success': False}), 400

    # Attempt to analyze the error using error_explainer logic
    try:
        explanation = explain_error(code_snippet)
        return jsonify({
            'success': True,
            'message': 'Error explanation generated successfully',
            'explanation': explanation
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to generate error explanation',
            'error': str(e)
        }), 500


# Generate Week Summary
@user_routes.route('/generate_week_summary', methods=['POST'])
def generate_week_summary():
    '''API to generate a summary for a specific week'''
    data = request.get_json()
    week_id = data.get('week_id')

    # Validate if week_id is provided
    if not week_id:
        return jsonify({'message': 'week_id is required', 'success': False}), 400

    # Check if the week exists in the database
    week = Week.query.get(week_id)
    if not week:
        return jsonify({'message': 'Week not found', 'success': False}), 404

    # Generate summary using slides_summarizer logic
    result = summarize_week_slides(week.week_number)

    # Return result
    return jsonify(result), 200 if result['success'] else 404


# ---------------------------- Generate Mock Test ----------------------------
@user_routes.route('/generate_mock', methods=['POST'])
def generate_mock():
    '''API to generate a mock test based on a specific topic'''
    data = request.get_json()
    quiz_type = data.get('quiz_type')
    num_questions = data.get('num_questions', 10)  # Default to 10 questions if not provided

    # Validate required fields
    if not quiz_type:
        return jsonify({'message': 'quiz_type is required', 'success': False}), 400

    # Generate MCQs using the provided logic
    result = generate_mcqs(quiz_type, num_questions)

    # Return the generated mock test or error response
    if result['success']:
        return jsonify({
            'message': f'Mock test generated successfully for {quiz_type}',
            'success': True,
            'quiz_type': quiz_type,
            'num_questions': num_questions,
            'questions': result['questions']
        }), 200
    else:
        return jsonify({
            'message': result['message'],
            'success': False,
            'quiz_type': quiz_type
        }), 404


# ---------------------------- Generate Notes ----------------------------
@user_routes.route('/generate_notes', methods=['POST'])
def generate_notes():
    '''API to generate notes for a specific topic'''
    data = request.get_json()
    topic = data.get('topic')

    # Validate if topic is provided
    if not topic:
        return jsonify({'message': 'topic is required', 'success': False}), 400

    # Generate notes using the provided logic
    result = generate_topic_notes(topic)

    # Return the generated notes or error response
    if result['success']:
        return jsonify({
            'message': f'Notes generated successfully for topic "{topic}"',
            'success': True,
            'topic': topic,
            'notes': result['notes']
        }), 200
    else:
        return jsonify({
            'message': result['message'],
            'success': False,
            'topic': topic
        }), 404


# ---------------------------- Topic Recommendation ----------------------------
@user_routes.route('/topic_recommendation', methods=['POST'])
def topic_recommendation():
    """API endpoint to recommend study topics based on incorrect answers"""
    data = request.get_json()
    logger.info(f"Received topic recommendation request: {data.keys()}")

    wrong_questions = data.get('wrong_questions', [])
    logger.info(f"Extracted {len(wrong_questions)} wrong questions")

    # Validate if wrong_questions list is provided
    if not wrong_questions:
        return jsonify({
            'message': 'All answers are correct! Great job! 🎯',
            'success': True,
            'suggestions': {
                'overall_assessment': "All questions were answered correctly. Excellent performance!",
                'topic_suggestions': [],
                'general_tips': ["Continue practicing to maintain your knowledge. 🚀"]
            }
        }), 200

    try:
        # Generate suggestions
        suggestions = generate_topic_suggestions(wrong_questions)
        return jsonify(suggestions), 200
    except Exception as e:
        logger.error(f"Error in topic_recommendation endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'message': f'Error generating suggestions: {str(e)}',
            'success': False,
            'suggestions': {
                'overall_assessment': "We encountered an issue analyzing your answers.",
                'topic_suggestions': [],
                'general_tips': ["Review the course materials for the topics you missed."]
            }
        }), 200


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
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get current directory
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


# ---------------------------------- Download Report (PDF) ----------------------------------
@user_routes.route('/download_report', methods=['POST'])
# @jwt_required()
def download_report():
    """Generates and downloads a report as a PDF file."""
    data = request.json
    # user_id = get_current_user()
    # user = User.query.get(user_id)

    # username = user.username
    username = "Jyotiraditya Saha"
    score = data.get("score")  # Get the score from the request
    total = data.get("total")  # Get the total score from the request
    # Extract suggestions from potentially different formats
    suggestions = data.get("suggestions", [])
    if isinstance(suggestions, dict):
        # Extract from dictionary format if needed
        temp_suggestions = []
        if "overall_assessment" in suggestions:
            temp_suggestions.append(suggestions["overall_assessment"])
        if "topic_suggestions" in suggestions:
            for topic in suggestions["topic_suggestions"]:
                temp_suggestions.extend([f"{topic['topic']}: {s}" for s in topic["suggestions"]])
        if "general_tips" in suggestions:
            temp_suggestions.extend(suggestions["general_tips"])
        suggestions = temp_suggestions

    questions = data.get("questions", [])  # Get questions list (default to empty if not provided)

    # Validate required fields
    if not username or score is None or total is None:
        return jsonify({
            "message": "Invalid input: 'username', 'score', and 'total' are required fields.",
            "success": False
        }), 400

    # Render the HTML template with the provided data
    html_content = render_template(
        "report.html",
        username=username,
        score=score,
        total=total,
        suggestions=suggestions,
        questions=questions,
        current_time=datetime.now()
    )

    # Define the file path for the generated PDF inside the "reports" folder
    pdf_file = os.path.join(REPORTS_DIR, f"MockTest_{username}.pdf")

    # Attempt to generate the PDF from the rendered HTML content
    try:
        pdfkit.from_string(html_content, pdf_file, configuration=config)
    except Exception as e:
        # Return a failure response with an error message if PDF generation fails
        return jsonify({
            "message": "PDF generation failed",
            "success": False,
            "error": str(e)
        }), 500

    # Attempt to send the generated PDF file as a download
    try:
        response = send_file(
            pdf_file,
            as_attachment=True,
            download_name=f"MockTest_{username}.pdf"
        )
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response
    except Exception as e:
        # Return a failure response if file sending fails
        return jsonify({
            "message": "File sending failed",
            "success": False,
            "error": str(e)
        }), 500


@user_routes.route('/download_markdown_pdf', methods=['POST'])
def download_markdown_pdf():
    """Converts markdown content (with LaTeX) to PDF and returns it for download"""
    data = request.json
    markdown_content = data.get('content')
    title = data.get('title', 'Notes')
    filename = data.get('filename', f'{title.replace(" ", "_")}.pdf')

    if not markdown_content:
        return jsonify({
            "message": "No content provided",
            "success": False
        }), 400

    try:
        # Directory for saving files
        temp_dir = tempfile.mkdtemp() if 'REPORTS_DIR' not in globals() else REPORTS_DIR

        # Pre-process markdown to handle LaTeX expressions
        # Replace $$ ... $$ with HTML for display math
        markdown_content = re.sub(
            r'\$\$(.*?)\$\$',
            r'<div class="math-display">\1</div>',
            markdown_content,
            flags=re.DOTALL
        )

        # Replace $ ... $ with HTML for inline math
        markdown_content = re.sub(
            r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)',
            r'<span class="math-inline">\1</span>',
            markdown_content
        )

        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=[
                'fenced_code',
                'tables',
                CodeHiliteExtension(linenums=False, css_class='highlight'),
                TableExtension(),
                'nl2br'
            ]
        )

        # Create HTML template with CSS for math rendering
        html_template = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>${title}</title>
<style>
/* Variables for consistent theming */
            :root {{
            --primary-color: #3498db;
--primary-dark: #2980b9;
--secondary-color: #2c3e50;
--accent-color: #1E847F;
--text-color: #333333;
--light-gray: #f5f7fa;
--medium-gray: #ecf0f1;
--border-color: #dfe6e9;
--shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}

/* General document styling */
            body {{
            font-family: 'Segoe UI', Arial, sans-serif;
line-height: 1.6;
color: var(--text-color);
max-width: 900px;
margin: 0 auto;
padding: 25px;
background-color: #ffffff;
box-shadow: var(--shadow);
border-radius: 8px;
            }}

/* Header styling with gradient underline */
            h1 {{
            font-size: 28pt;
color: var(--secondary-color);
margin-top: 0.5em;
margin-bottom: 0.5em;
padding-bottom: 15px;
position: relative;
            }}

            h1::after {{
            content: "";
position: absolute;
bottom: 0;
left: 0;
height: 3px;
width: 100%;
background: linear-gradient(to right, var(--primary-color), var(--primary-dark));
border-radius: 3px;
            }}

            h2 {{
            font-size: 22pt;
color: var(--secondary-color);
margin-top: 1.5em;
margin-bottom: 0.7em;
border-bottom: 1px solid var(--border-color);
padding-bottom: 7px;
            }}

            h3 {{
            font-size: 18pt;
color: var(--secondary-color);
margin-top: 1.2em;
margin-bottom: 0.6em;
            }}

            p {{
            margin-bottom: 1.2em;
text-align: justify;
            }}

/* Code styling with enhanced visuals */
            pre {{
            background-color: var(--light-gray);
border: 1px solid var(--border-color);
border-radius: 6px;
padding: 16px;
margin: 20px 0;
overflow-x: auto;
box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
            }}
            code {{
            font-family: Consolas, Monaco, 'Andale Mono', monospace;
font-size: 0.9em;
color: var(--accent-color);
            }}

            p code {{
            background-color: var(--light-gray);
padding: 0.2em 0.4em;
border-radius: 4px;
border: 1px solid var(--border-color);
            }}

/* LaTeX Math Styling with improved visuals */
            .math-display {{
            display: block;
padding: 16px;
margin: 24px 0;
text-align: center;
font-family: 'Times New Roman', serif;
font-size: 1.1em;
background-color: var(--light-gray);
border-left: 4px solid var(--primary-color);
border-radius: 0 6px 6px 0;
box-shadow: var(--shadow);
            }}

            .math-inline {{
            font-family: 'Times New Roman', serif;
padding: 0 4px;
background-color: var(--light-gray);
border-radius: 3px;
            }}

/* Table styling with alternating rows */
            table {{
            border-collapse: collapse;
width: 100%;
margin: 20px 0;
border-radius: 6px;
overflow: hidden;
box-shadow: var(--shadow);
            }}

            th {{
            background-color: var(--primary-color);
color: #ffffff;
font-weight: 600;
text-align: left;
padding: 12px;
            }}

            td {{
            padding: 10px 12px;
border: 1px solid var(--border-color);
            }}

            tr:nth-child(even) {{
            background-color: var(--light-gray);
            }}

            tr:hover {{
            background-color: var(--medium-gray);
            }}

/* List styling */
            ul, ol {{
            padding-left: 25px;
margin: 16px 0;
            }}

            li {{
            margin-bottom: 8px;
position: relative;
            }}

            ul li::marker {{
            color: var(--primary-color);
            }}

/* Blockquote styling */
            blockquote {{
            border-left: 4px solid var(--primary-color);
background-color: var(--light-gray);
margin: 20px 0;
padding: 16px 20px;
border-radius: 0 6px 6px 0;
font-style: italic;
color: #555;
box-shadow: var(--shadow);
            }}
/* Link styling */
            a {{
            color: var(--primary-color);
text-decoration: none;
border-bottom: 1px solid transparent;
transition: border-color 0.2s;
            }}

            a:hover {{
            border-bottom-color: var(--primary-color);
            }}
/* Print-specific styles for PDF output */
            @media print {{
            body {{
                box-shadow: none;
                padding: 0;
                max-width: none;
            }}

            pre, code, blockquote, table {{
                page-break-inside: avoid;
        }}

        h1, h2, h3 {{
            page-break-after: avoid;
        }}

        img {{
            max-width: 100% !important;
        }}

        @page {{
            margin: 2cm;
        }}
        }}
        </style>
            </head>
            <body>
            <div class="content">
    {html_content}
    </div>
    </body>
    </html>
    """

        # Write HTML to a file
        html_file = os.path.join(temp_dir, "temp.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_template)

        # Prepare PDF file path
        pdf_file = os.path.join(temp_dir, filename)

        # Configure pdfkit options for best results
        options = {
            'enable-local-file-access': '',
            'quiet': '',
            'encoding': 'UTF-8',
            'print-media-type': '',
            'margin-top': '15mm',
            'margin-right': '15mm',
            'margin-bottom': '15mm',
            'margin-left': '15mm',
            'page-size': 'A4',
            'dpi': 300,
            'no-outline': None
        }

        # Generate PDF directly without JavaScript
        pdfkit.from_file(html_file, pdf_file, options=options)

        # Return the file for download
        response = send_file(
            pdf_file,
            as_attachment=True,
            download_name=filename
        )

        # Set appropriate headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF generation error: {str(e)}")
        print(error_details)
        return jsonify({
            "message": "Failed to generate PDF",
            "success": False,
            "error": str(e),
            "details": error_details
        }), 500