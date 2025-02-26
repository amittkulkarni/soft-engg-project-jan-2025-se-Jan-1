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



#-----------------------------------------CRUD - WEEK--------------------------------------------------------------

@user_routes.route('/weeks', methods=['POST'])
def create_week():
    data = request.get_json()
    week_number = data.get('week_number')
    title = data.get('title')

    existing_week = Week.query.filter_by(week_number=week_number).first()
    if existing_week:
        return jsonify({"message":"week already exists."}),409
    
    new_week =  Week(week_number=week_number, title=title)
    db.session.add(new_week)
    db.session.commit()

    return jsonify({"message": "new week added successfully"}), 201


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

@user_routes.route('/weeks/<int:week_id>', methods=['PUT'])
def update_week(week_id):
    week = Week.query.get(week_id)
    if not week:
        return jsonify({"message": "Week not found"}), 404
    
    data = request.get_json()

    if "week_number" in data:
        week.week_number=data["week_number"]
    if "title" in data:
        week.title=data["title"]

    db.session.commit()

    return jsonify({"message": "week updated successfully"}), 200

@user_routes.route('/weeks/<int:week_id>', methods=['DELETE'])
def delete_week(week_id):
    week = Week.query.get(week_id)
    if not week:
        return jsonify({"message": "Week not found"}), 404
    
    db.session.delete(week)
    db.session.commit()

    return jsonify({"message": "week delete successfully"}), 200

@user_routes.route('/lectures', methods=['POST'])
def create_lecture():
    data = request.get_json()
    week_id = data.get('week_id')
    title = data.get('title')
    video_id = data.get("video_id")

    print("week_id",week_id)
    print("title",title)
    print("video_id",video_id)
    if "week_id" not in data or "title" not in data or "video_id" not in data:
        return jsonify({"message" : "All fields are required"}),400
    
    week = Week.query.get(week_id)
    if not week:
        return jsonify({"message": "Week not found"}), 404
    

    existing_lecture = Lecture.query.filter_by(title = title).first()
    if existing_lecture:
        return jsonify({"message":"lecture already exists."}),409
    
    new_lecture =  Lecture(week_id=week_id, title=title, video_id = video_id)
    db.session.add(new_lecture)
    db.session.commit()

    return jsonify({"message": "new lecture added successfully"}), 201

@user_routes.route('/lectures', methods=['GET'])
def get_lectures():
    lectures = Lecture.query.all()
    return jsonify([{
        "id": lecture.id,
        "week_id": lecture.week_id,
        "title": lecture.title,
        "video_id":lecture.video_id,
    } for lecture in lectures]), 200

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

@user_routes.route('/lectures/<int:lecture_id>', methods=['PUT'])
def update_lecture(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    if not lecture:
        return jsonify({"message": "lecture not found"}), 404
    
    data = request.get_json()

    if "week_id" in data:
        lecture.week_id=data["week_id"]
    if "title" in data:
        lecture.title=data["title"]
    if "video_id" in data:
        lecture.video_id=data["video_id"]

    db.session.commit()

    return jsonify({"message": "Lecture updated successfully"}), 200

@user_routes.route('/lectures/<int:lecture_id>', methods=['DELETE'])
def delete_lecture(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    if not lecture:
        return jsonify({"message": "Lecture not found"}), 404
    
    db.session.delete(lecture)
    db.session.commit()

    return jsonify({"message": "Lecture delete successfully"}), 200




