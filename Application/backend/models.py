from extension import db
from datetime import datetime
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(72), nullable=True)
    role = db.Column(db.Enum('student', 'admin', name='user_roles'), nullable=False)
    google_id = db.Column(db.String(80), nullable=True)
    chat_history = db.relationship('ChatHistory', back_populates='user', cascade='all, delete-orphan')

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='chat_history')

class Week(db.Model):
    __tablename__ = 'weeks'
    id = db.Column(db.Integer, primary_key=True)
    week_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    lectures = db.relationship('Lecture', back_populates='week', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', back_populates='week', cascade='all, delete-orphan')

class Lecture(db.Model):
    __tablename__ = 'lectures'
    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    video_url = db.Column(db.String(100))
    week = db.relationship('Week', back_populates='lectures')

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True) 
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    type = db.Column(db.Enum('graded', 'practice', 'programming',  name='assignment_types'), nullable=False)
    due_date = db.Column(db.DateTime)
    total_points = db.Column(db.Integer, default=1)
    week = db.relationship('Week', back_populates='assignments')
    questions = db.relationship('AssignmentQuestion', back_populates='assignment', cascade='all, delete-orphan')

class AssignmentQuestion(db.Model):
    __tablename__ = 'assignment_questions'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('single_choice', 'multiple_choice', name='question_types'), nullable=False)
    points = db.Column(db.Integer, default=1)
    assignment = db.relationship('Assignment', back_populates='questions')
    options = db.relationship('QuestionOption', back_populates='question', cascade='all, delete-orphan')

class QuestionOption(db.Model):
    __tablename__ = 'question_options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('assignment_questions.id'), nullable=False)
    option_text = db.Column(db.String(150), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    question = db.relationship('AssignmentQuestion', back_populates='options')
