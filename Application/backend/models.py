from extension import db
from datetime import datetime
import json

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(72), nullable=True)
    role = db.Column(db.Enum('student', 'admin', name='user_roles'), nullable=False)
    google_id = db.Column(db.String(80), nullable=True)
    chat_history = db.relationship('ChatHistory', back_populates='user', cascade='all, delete-orphan')

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    file_path = db.Column(db.String(255), nullable=False)  # Stores SQL file path
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
    video_id = db.Column(db.String(50))
    week = db.relationship('Week', back_populates='lectures')

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True) 
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    assignment_type = db.Column(db.Enum('graded', 'practice', 'programming',  name='assignment_types'), nullable=False)
    due_date = db.Column(db.DateTime)
    total_points = db.Column(db.Integer, default=0)
    week = db.relationship('Week', back_populates='assignments')
    questions = db.relationship('AssignmentQuestion', back_populates='assignment', cascade='all, delete-orphan')
    programming_assignment = db.relationship('ProgrammingAssignment', back_populates='assignment', uselist=False, cascade='all, delete-orphan')

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

class ProgrammingAssignment(db.Model):
    __tablename__ = 'programming_assignments'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    problem_statement = db.Column(db.Text, nullable=False)  
    input_format = db.Column(db.Text, nullable=False)       
    output_format = db.Column(db.Text, nullable=False)      
    constraints = db.Column(db.Text, nullable=True)         
    sample_input = db.Column(db.Text, nullable=False)  
    sample_output = db.Column(db.Text, nullable=False)  
    test_cases = db.Column(db.Text, nullable=False, default='[]') 
    assignment = db.relationship('Assignment', back_populates='programming_assignment', uselist=False)

    def set_test_cases(self, test_cases_list):
        """Stores test cases as a JSON string"""
        self.test_cases = json.dumps(test_cases_list)

    def get_test_cases(self):
        """Retrieves test cases as a Python list"""
        return json.loads(self.test_cases) if self.test_cases else []