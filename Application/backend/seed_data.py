from extension import db
from models import User, Week, Lecture, Assignment, AssignmentQuestion, QuestionOption, ProgrammingAssignment, ChatHistory
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from sqlalchemy.sql import text
from app import app  # Import Flask app instance
import json

def seed_users():
    """Seed users into the database."""
    users = [
        User(username="admin_user", email="admin@test.com",
             password=generate_password_hash("adminpass"), role="admin"),
        User(username="student1", email="student1@test.com",
             password=generate_password_hash("studentpass1"), role="student"),
        User(username="student2", email="student2@test.com",
             password=generate_password_hash("studentpass2"), role="student"),
    ]
    db.session.add_all(users)
    db.session.commit()
    return users

def seed_weeks():
    """Seed weeks into the database."""
    weeks = [Week(week_number=i, title=f"Week {i}") for i in range(1, 13)]
    db.session.add_all(weeks)
    db.session.commit()
    return weeks  # Return for reference in other seed functions

def seed_lectures(weeks):
    """Seed lectures for each week."""
    lecture_data = [
        ("Data Visualisation", "kIyxumBVo6o"),
        ("Introduction: Looking at the big picture", "c3fKU3H4VDM"),
        ("Data Preprocessing", "_PcVkfVsjuo"),
        ("Linear regression", "SFYn4UnZaSQ"),
        ("Polynomial Regression", "dMHECW-BkIM"),
        ("Classification Functions in Scikit learn", "dhYydFzxfes"),
        ("Naive Bayes Classifier", "uM-MNko46Zo"),
        ("Demonstration: Softmax Regression with MNIST", "_zWJhbFQBQI"),
        ("Decision Trees", "5OZc2zWS2cY"),
        ("Voting, Bagging and Random Forest", "EZ5szvjQgWw"),
        ("K-means clustering on digit dataset", "tPSKI9nUf0"),
    ]
    lectures = [Lecture(week_id=weeks[i].id, title=title, video_id=vid)
                for i, (title, vid) in enumerate(lecture_data)]
    db.session.add_all(lectures)
    db.session.commit()

def seed_assignments(weeks):
    """Seed assignments."""
    assignments = [
        Assignment(week_id=weeks[0].id, title="Graded Assignment 1", assignment_type="graded",
                   due_date=datetime.now() + timedelta(days=7), total_points=25),
        Assignment(week_id=weeks[1].id, title="Graded Assignment 2", assignment_type="graded",
                   due_date=datetime.now() + timedelta(days=7), total_points=25),
        Assignment(week_id=weeks[0].id, title="Programming Assignment 1", assignment_type="programming",
                   due_date=datetime.now() + timedelta(days=7), total_points=25),
        Assignment(week_id=weeks[1].id, title="Programming Assignment 2", assignment_type="programming",
                   due_date=datetime.now() + timedelta(days=7), total_points=25)
    ]
    db.session.add_all(assignments)
    db.session.commit()
    return assignments  # Return for further reference

def seed_questions(assignments):
    """Seed questions for the first assignment."""
    questions = [
        AssignmentQuestion(assignment_id=assignments[0].id,
                           question_text="Which of the following libraries is commonly used for data visualization in Python?",
                           question_type="single_choice", points=5),
        AssignmentQuestion(assignment_id=assignments[0].id,
                           question_text="What type of chart is best suited for showing the distribution of a single continuous variable?",
                           question_type="single_choice", points=5),
        AssignmentQuestion(assignment_id=assignments[0].id,
                           question_text="Which plot is most appropriate for displaying the relationship between two continuous variables?",
                           question_type="single_choice", points=5),
        AssignmentQuestion(assignment_id=assignments[0].id,
                           question_text="Which of the following are advantages of using Seaborn over Matplotlib for data visualization?",
                           question_type="multiple_choice", points=5),
        AssignmentQuestion(assignment_id=assignments[0].id,
                           question_text="Which of the following charts are useful for visualizing categorical data?",
                           question_type="multiple_choice", points=5)
    ]
    db.session.add_all(questions)
    db.session.commit()
    return questions  # Return for options

def seed_options(questions):
    """Seed options for questions."""
    options = [
        # Question 1 Options
        QuestionOption(question_id=questions[0].id, option_text="NumPy", is_correct=False),
        QuestionOption(question_id=questions[0].id, option_text="Pandas", is_correct=False),
        QuestionOption(question_id=questions[0].id, option_text="Matplotlib", is_correct=True),
        QuestionOption(question_id=questions[0].id, option_text="Scikit-learn", is_correct=False),

        # Question 2 Options
        QuestionOption(question_id=questions[1].id, option_text="Pie Chart", is_correct=False),
        QuestionOption(question_id=questions[1].id, option_text="Histogram", is_correct=True),
        QuestionOption(question_id=questions[1].id, option_text="Line Chart", is_correct=False),
        QuestionOption(question_id=questions[1].id, option_text="Bar Chart", is_correct=False),

        # Question 3 Options
        QuestionOption(question_id=questions[2].id, option_text="Scatter Plot", is_correct=True),
        QuestionOption(question_id=questions[2].id, option_text="Bar Chart", is_correct=False),
        QuestionOption(question_id=questions[2].id, option_text="Pie Chart", is_correct=False),
        QuestionOption(question_id=questions[2].id, option_text="Box Plot", is_correct=False),

        # Question 4 Options
        QuestionOption(question_id=questions[3].id, option_text="Built-in themes for better aesthetics", is_correct=True),
        QuestionOption(question_id=questions[3].id, option_text="Simpler syntax for complex visualizations", is_correct=True),
        QuestionOption(question_id=questions[3].id, option_text="Faster performance than Matplotlib", is_correct=False),
        QuestionOption(question_id=questions[3].id, option_text="Integration with Pandas DataFrames", is_correct=True),

        # Question 5 Options
        QuestionOption(question_id=questions[4].id, option_text="Bar Chart", is_correct=True),
        QuestionOption(question_id=questions[4].id, option_text="Pie Chart", is_correct=True),
        QuestionOption(question_id=questions[4].id, option_text="Scatter Plot", is_correct=False),
        QuestionOption(question_id=questions[4].id, option_text="Box Plot", is_correct=True),
    ]
    db.session.add_all(options)
    db.session.commit()

def seed_programming_assignments(assignments):
    """Seed programming assignments linked to existing assignments."""
    programming_assignments = [
        ProgrammingAssignment(
            assignment_id=assignments[2].id,
            problem_statement="Write a Python function to check if a number is prime.",
            input_format="A single integer N (1 <= N <= 10^6).",
            output_format="Output 'YES' if N is prime, otherwise 'NO'.",
            constraints="1 <= N <= 10^6",
            sample_input="5",
            sample_output="YES",
            test_cases=json.dumps([
                {"input": "2", "output": "YES"},
                {"input": "4", "output": "NO"},
                {"input": "17", "output": "YES"},
                {"input": "100", "output": "NO"}
            ])
        ),
        ProgrammingAssignment(
            assignment_id=assignments[3].id,
            problem_statement="Write a function to return the sum of an array.",
            input_format="First line contains an integer N, followed by N space-separated integers.",
            output_format="Output a single integer, the sum of the array.",
            constraints="1 <= N <= 1000, -10^5 <= arr[i] <= 10^5",
            sample_input="5\n1 2 3 4 5",
            sample_output="15",
            test_cases=json.dumps([
                {"input": "3\n10 20 30", "output": "60"},
                {"input": "4\n-1 -2 -3 -4", "output": "-10"},
                {"input": "5\n0 0 0 0 0", "output": "0"}
            ])
        )
    ]

    db.session.add_all(programming_assignments)
    db.session.commit()


def seed_chat_history(users):
    """Seed chat history for users by storing file paths in the database."""
    
    sample_chat_history = [
        {"user_id": users[1].id, "file_path": f"chat_logs/user_{users[1].id}_chat.sql"},
        {"user_id": users[2].id, "file_path": f"chat_logs/user_{users[2].id}_chat.sql"}
    ]

    try:
        for chat in sample_chat_history:
            sql_store_path = text(
                "INSERT INTO chat_history (user_id, file_path) VALUES (:user_id, :file_path) "
                "ON CONFLICT (user_id) DO NOTHING;"
            )
            db.session.execute(sql_store_path, chat)

        db.session.commit()
        print("Chat history seeded successfully!")

    except Exception as e:
        db.session.rollback()
        print(f"Failed to seed chat history: {str(e)}")

    
def seed_data():
    """Main function to seed the database."""
    print("Seeding data...")

    users = seed_users()
    weeks = seed_weeks()
    seed_lectures(weeks)
    assignments = seed_assignments(weeks)
    questions = seed_questions(assignments)
    seed_options(questions)
    seed_programming_assignments(assignments)
    seed_chat_history(users)

    print("Database seeded successfully!")

def main():
    """Function to run when called from another script."""
    with app.app_context():
        seed_data()

if __name__ == '__main__':
    main()