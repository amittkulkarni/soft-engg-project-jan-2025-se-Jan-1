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
       Lecture(week_id=weeks[0].id, title="Pandas Series and Dataframe", video_url="https://www.youtube.com/watch?v=MdnmbjKM7a0"),
       Lecture(week_id=weeks[1].id, title="Data Visualisation", video_url="https://www.youtube.com/watch?v=kIyxumBVo6o"),
       Lecture(week_id=weeks[2].id, title="Data Preprocessing", video_url="https://www.youtube.com/watch?v=_PcVkfVsjuo"),
       Lecture(week_id=weeks[3].id, title="Linear Regression", video_url="https://www.youtube.com/watch?v=SFYn4UnZaSQ"),
       Lecture(week_id=weeks[4].id, title="Polynomial Regression", video_url="https://www.youtube.com/watch?v=dMHECW-BkIM"),
       Lecture(week_id=weeks[5].id, title="Classification Functions in Scikit Learn", video_url="https://www.youtube.com/watch?v=dhYydFzxfes"),
       Lecture(week_id=weeks[6].id, title="Naive Bayes Classifier", video_url="https://www.youtube.com/watch?v=uM-MNko46Zo"),
       Lecture(week_id=weeks[7].id, title="K-Nearest Neighbors", video_url="https://www.youtube.com/watch?v=gKiFTMLgZy4"),
       Lecture(week_id=weeks[8].id, title="Decision Trees", video_url="https://www.youtube.com/watch?v=5OZc2zWS2cY"),
       Lecture(week_id=weeks[9].id, title="Bagging and Random Forest", video_url="https://www.youtube.com/watch?v=EZ5szvjQgWw"),
       Lecture(week_id=weeks[10].id, title="K-means Clustering on Digit Dataset", video_url="https://www.youtube.com/watch?v=-tPSKI9nUf0"),
       Lecture(week_id=weeks[11].id, title="Case Study", video_url="https://www.youtube.com/watch?v=27G4drv3Nfk"),
   ]
   db.session.add_all(lectures)
   db.session.commit()


   # Seed Assignments
   assignments = [
       Assignment(week_id=weeks[0].id, title="Assignment 1", type="graded", due_date=datetime.now() + timedelta(days=7), total_points=25),
   ]
   db.session.add_all(assignments)
   db.session.commit()

   # Seed Questions and Options for the first assignment (Assignment 1)
   questions = [
       AssignmentQuestion(
           assignment_id=assignments[0].id,
           question_text="Which of the following is the primary data structure in pandas?",
           question_type="single_choice",
           points=5,
       ),
       AssignmentQuestion(
           assignment_id=assignments[0].id,
           question_text="What method is used to check for missing values in a pandas DataFrame?",
           question_type="single_choice",
           points=5,
       ),
       AssignmentQuestion(
           assignment_id=assignments[0].id,
           question_text="How do you select a column named 'Age' from a DataFrame df?",
           question_type="single_choice",
           points=5,
       ),
       AssignmentQuestion(
           assignment_id=assignments[0].id,
           question_text="Which of the following statements about pandas DataFrame are true? (Select all that apply)",
           question_type="multiple_choice",
           points=5,
       ),
       AssignmentQuestion(
           assignment_id=assignments[0].id,
           question_text="Which of the following methods can be used to filter rows in a DataFrame? (Select all that apply)",
           question_type="multiple_choice",
           points=5,
       )
   ]
   db.session.add_all(questions)
   db.session.commit()


   # Add Options for Each Question
   options = [
       # Question 1 Options
       QuestionOption(question_id=questions[0].id, option_text="Dictionary", is_correct=False),
       QuestionOption(question_id=questions[0].id, option_text="Dataframe", is_correct=True),
       QuestionOption(question_id=questions[0].id, option_text="Tuple", is_correct=False),
        QuestionOption(question_id=questions[0].id, option_text="List", is_correct=False),

       # Question 2 Options
       QuestionOption(question_id=questions[1].id, option_text="df.isnull()", is_correct=True),
       QuestionOption(question_id=questions[1].id, option_text="df.missing()", is_correct=False),
       QuestionOption(question_id=questions[1].id, option_text="df.checknull()", is_correct=False),
       QuestionOption(question_id=questions[1].id, option_text="df.hasnull()", is_correct=False),

       # Question 3 Options
       QuestionOption(question_id=questions[2].id, option_text="df['Age']", is_correct=False),
       QuestionOption(question_id=questions[2].id, option_text="df.Age", is_correct=False),
       QuestionOption(question_id=questions[2].id, option_text="df.loc[:,'Age']", is_correct=False),
       QuestionOption(question_id=questions[2].id, option_text="All of the Above", is_correct=True),
       
        # Question 4 Options
       QuestionOption(question_id=questions[3].id, option_text="A DataFrame is a 2D labeled data structure.", is_correct=True),
       QuestionOption(question_id=questions[3].id, option_text="Columns in a DataFrame can have different data types.", is_correct=True),
       QuestionOption(question_id=questions[3].id, option_text="You can create a DataFrame from a dictionary.", is_correct=True),
       QuestionOption(question_id=questions[3].id, option_text="A DataFrame must always have an integer index.", is_correct=False),
       
        # Question 5 Options
       QuestionOption(question_id=questions[4].id, option_text="df[df['column'] > 10]", is_correct=True),
       QuestionOption(question_id=questions[4].id, option_text="df.query('column > 10')", is_correct=True),
       QuestionOption(question_id=questions[4].id, option_text=" df.loc[df['column'] > 10]", is_correct=True),
       QuestionOption(question_id=questions[4].id, option_text="df.filter('column > 10')", is_correct=False),
   ]
   db.session.add_all(options)


   db.session.commit()
   print("Database seeded successfully!")


if __name__ == '__main__':
   from app import app  # Import the Flask app instance
   with app.app_context():
       seed_data()
