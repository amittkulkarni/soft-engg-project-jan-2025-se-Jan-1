from extension import db
from models import User, Week, Lecture, Assignment, AssignmentQuestion, QuestionOption
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from app import app  # Import Flask app instance

def seed_users():
    """Seed users into the database."""
    users = [
        User(username="admin_user", email="admin@test.com",
             password=generate_password_hash("adminpass"), role="admin"),
    ]
    db.session.add_all(users)
    db.session.commit()

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
        ("Data Preprocessing", "_PcVkfVsjuo"),
        ("Linear Regression", "SFYn4UnZaSQ"),
        ("Polynomial Regression", "dMHECW-BkIM"),
        ("Classification Functions in Scikit Learn", "dhYydFzxfes"),
        ("Naive Bayes Classifier", "uM-MNko46Zo"),
        ("K-Nearest Neighbors", "gKiFTMLgZy4"),
        ("Decision Trees", "5OZc2zWS2cY"),
        ("Bagging and Random Forest", "EZ5szvjQgWw"),
        ("K-means Clustering on Digit Dataset", "-tPSKI9nUf0"),
        ("Neural Networks: Multilayer Perceptron", "wphku4k1e90"),
        ("SVM", "5erlKOqL8Xk"),
    ]
    lectures = [Lecture(week_id=weeks[i].id, title=title, video_id=vid)
                for i, (title, vid) in enumerate(lecture_data)]
    db.session.add_all(lectures)
    db.session.commit()

def seed_assignments(weeks):
    """Seed assignments."""
    assignments = [
        Assignment(week_id=weeks[0].id, title="Assignment 1", assignment_type="graded",
                   due_date=datetime.now() + timedelta(days=7), total_points=25),
        Assignment(week_id=weeks[1].id, title="Assignment 3", assignment_type="graded",
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

def seed_data():
    """Main function to seed the database."""
    print("Seeding data...")

    seed_users()
    weeks = seed_weeks()
    seed_lectures(weeks)
    assignments = seed_assignments(weeks)
    questions = seed_questions(assignments)
    seed_options(questions)

    print("Database seeded successfully!")

def main():
    """Function to run when called from another script."""
    with app.app_context():
        seed_data()

if __name__ == '__main__':
    main()