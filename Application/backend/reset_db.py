from extension import db
from app import app  # Import Flask app instance
from seed_data import main as seed_data

def reset_database():
    """Drops and recreates all tables, then seeds the database."""
    with app.app_context():
        print("Resetting database...")
        
        db.drop_all()  # Drop existing tables
        db.create_all()  # Recreate tables
        
        print("Database reset successfully!")
        
        seed_data()  # Call seed function to populate tables

if __name__ == '__main__':
    reset_database()