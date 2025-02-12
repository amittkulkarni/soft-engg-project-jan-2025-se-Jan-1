from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User,Week,Lecture,Assignment
from extension import db 

from token_validation import generate_token



# Comment from Amit , Do use the prefix "/api/" for all APIs . For e.g http://localhost:3000/api/google_auth 


user_routes = Blueprint('user_routes', __name__)

# Signup Route
@user_routes.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Login Route
@user_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    token = generate_token(user.id)
    return jsonify({"access_token": token, "message": "Login successful"}), 200


@user_routes.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logged out successfully"}), 200


@user_routes.route('/weeks', methods=['GET'])
def get_weeks():
    weeks = Week.query.all()
    return jsonify([{
        "id": week.id,
        "week_number": week.week_number,
        "title": week.title
    } for week in weeks]), 200


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

