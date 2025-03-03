from extension import db
from models import User, Week, Lecture, Assignment, AssignmentQuestion, QuestionOption
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def seed_data():
   print("Seeding data...")

   # Seed Users
   users = [
       User(username="admin_user", email="admin@test.com", password=generate_password_hash("adminpass"), role="admin"),
   ]
   db.session.add_all(users)
   db.session.commit()

   # Seed Weeks
   weeks = [
       Week(week_number=1, title="Week 1"),
       Week(week_number=2, title="Week 2"),
       Week(week_number=3, title="Week 3"),
       Week(week_number=4, title="Week 4"),
       Week(week_number=5, title="Week 5"),
       Week(week_number=6, title="Week 6"),
       Week(week_number=7, title="Week 7"),
       Week(week_number=8, title="Week 8"),
       Week(week_number=9, title="Week 9"),
       Week(week_number=10, title="Week 10"),
       Week(week_number=11, title="Week 11"),
       Week(week_number=12, title="Week 12")
   ]
   db.session.add_all(weeks)
   db.session.commit()

   # Seed Lectures
   lectures = [
       Lecture(week_id=weeks[0].id, title="Data Visualisation", video_id="kIyxumBVo6o"),
       Lecture(week_id=weeks[1].id, title="Data Preprocessing", video_id="_PcVkfVsjuo"),
       Lecture(week_id=weeks[2].id, title="Linear Regression", video_id="SFYn4UnZaSQ"),
       Lecture(week_id=weeks[3].id, title="Polynomial Regression", video_id="dMHECW-BkIM"),
       Lecture(week_id=weeks[4].id, title="Classification Functions in Scikit Learn", video_id="dhYydFzxfes"),
       Lecture(week_id=weeks[5].id, title="Naive Bayes Classifier", video_id="uM-MNko46Zo"),
       Lecture(week_id=weeks[6].id, title="K-Nearest Neighbors", video_id="gKiFTMLgZy4"),
       Lecture(week_id=weeks[7].id, title="Decision Trees", video_id="5OZc2zWS2cY"),
       Lecture(week_id=weeks[8].id, title="Bagging and Random Forest", video_id="EZ5szvjQgWw"),
       Lecture(week_id=weeks[9].id, title="K-means Clustering on Digit Dataset", video_id="-tPSKI9nUf0"),
       Lecture(week_id=weeks[10].id, title="Neural Networks:Multilayer Perceptron", video_id="wphku4k1e90"),
       Lecture(week_id=weeks[11].id, title="SVM", video_id="5erlKOqL8Xk"),
   ]
   db.session.add_all(lectures)
   db.session.commit()


   # Seed Assignments
   assignments = [
       Assignment(week_id=weeks[0].id, title="Assignment 1", assignment_type="graded", due_date=datetime.now() + timedelta(days=7), total_points=25),
   ]
   db.session.add_all(assignments)
   db.session.commit()

   # Seed Questions and Options for the first assignment (Assignment 1)
   questions = [
       AssignmentQuestion(
           assignment_id=assignments[0].id,
           question_text="Which of the following libraries is commonly used for data visualization in Python?",
           question_type="single_choice",
           points=5,
       ),
       AssignmentQuestion(
           assignment_id=assignments[0].id,
           question_text="What type of chart is best suited for showing the distribution of a single continuous variable?",
           question_type="single_choice",
           points=5,
       ),
       AssignmentQuestion(
           assignment_id=assignments[0].id,
           question_text=" Which plot is most appropriate for displaying the relationship between two continuous variables?",
           question_type="single_choice",
           points=5,
       ),
       AssignmentQuestion(
           assignment_id=assignments[0].id,
           question_text="Which of the following are advantages of using Seaborn over Matplotlib for data visualization?",
           question_type="multiple_choice",
           points=5,
       ),
       AssignmentQuestion(
           assignment_id=assignments[0].id,
           question_text="Which of the following charts are useful for visualizing categorical data?",
           question_type="multiple_choice",
           points=5,
       )
   ]
   db.session.add_all(questions)
   db.session.commit()


   # Add Options for Each Question
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
   print("Database seeded successfully!")


if __name__ == '__main__':
   from app import app  # Import the Flask app instance
   with app.app_context():
       seed_data()
