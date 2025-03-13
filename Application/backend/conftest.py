import pytest
from app import app,db
# from extension import db
@pytest.fixture
def client():
    """Set up the Flask test client and initialize the test database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

        # Clean up after tests
        with app.app_context():
            db.session.remove()


@pytest.fixture(autouse=True)
def session_setup_and_teardown():
    """Automatically roll back database changes after each test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        # Bind the session to the connection
        db.session.bind = connection

        yield db.session

        # Properly roll back and close
        db.session.remove()  # Remove the session first
        transaction.rollback()  # Then rollback the transaction
        connection.close()  # Finally, close the connection