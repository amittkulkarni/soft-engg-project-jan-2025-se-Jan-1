# README

## File Structure and Description

### **1. `app.py`**
- The main entry point of the application.
- Initializes the Flask app and registers blueprints for routes.
- Integrates extensions like SQLAlchemy, Flask-Migrate, and JWT.
- If you add a new route (e.g., admin routes), register its blueprint here.

### **2. `controllers.py`**
- Contains all the routes for user and admin functionalities.
- Uses **Blueprints** to organize routes.
- Includes routes for signup, login, and logout.
- **To add a new route** (e.g., `/admin/dashboard`):
  1. Define a new blueprint or extend an existing one.
  2. Write your route under the relevant blueprint.
  3. Register the blueprint in `app.py`.

### **3. `models.py`**
- Defines the database models.
- Contains the `User` table for storing user details (e.g., username, email, password).
- **To add a new table**:
  1. Define the new table as a class in `models.py`.
  2. Run the following commands to update the database:
     ```bash
     flask db migrate -m "Added new table"
     flask db upgrade
     ```

### **4. `config.py`**
- Holds configuration settings for the app.
- Reads secrets (e.g., `SECRET_KEY`, `JWT_SECRET_KEY`) and the database URI from environment variables or `.env`.
- If you change the database type or add configuration values, update this file.

### **5. `extensions.py`**
- Initializes app extensions like SQLAlchemy (`db`), Flask-JWT-Extended (`jwt`), and Flask-Migrate (`migrate`).
- Centralizes extension setup to avoid circular imports.

### **6. `token_validation.py`**
- Utility functions for handling JWT tokens.
- Includes helper functions for generating tokens and validating users.
- Use these functions in routes that require token-based authentication.

### **7. `.env` File**
- Stores sensitive information like keys and database URIs.
- Example:
  ```
  SECRET_KEY=your_secret_key_here
  JWT_SECRET_KEY=your_jwt_secret_key_here
  DATABASE_URL=sqlite:///instance/database.db
  ```
- **Never expose this file in public repositories.**

### **8. `migrations/`**
- Contains migration files for managing database schema changes.
- Automatically created and updated by Flask-Migrate.
- Use the following commands to manage migrations:
  - Initialize migrations:
    ```bash
    flask db init
    ```
  - Create a migration:
    ```bash
    flask db migrate -m "Migration message"
    ```
  - Apply migrations:
    ```bash
    flask db upgrade
    ```

### **9. `instance/`**
- Contains the SQLite database file (`database.db`).
- This folder is used for instance-specific data that should not be part of the source control.

---

## Adding New Features

### **1. Add a New Route (e.g., Admin Routes)**
- In `controllers.py`:
  1. Define a new Blueprint:
     ```python
     admin_routes = Blueprint('admin_routes', __name__)
     ```
  2. Add routes under the blueprint:
     ```python
     @admin_routes.route('/dashboard', methods=['GET'])
     def admin_dashboard():
         return {"message": "Admin Dashboard"}
     ```
- In `app.py`:
  1. Import and register the blueprint:
     ```python
     from controllers import admin_routes
     app.register_blueprint(admin_routes, url_prefix='/admin')
     ```

### **2. Add a New Table to the Database**
- In `models.py`:
  1. Define a new table as a class:
     ```python
     class Course(db.Model):
         id = db.Column(db.Integer, primary_key=True)
         name = db.Column(db.String(100), nullable=False)
         description = db.Column(db.Text, nullable=True)
     ```
- Run the following commands to update the database:
  ```bash
  flask db migrate -m "Added Course table"
  flask db upgrade
  ```

---

## How to Run the Application
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv myenv
   myenv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
2. Set up the database:
   ```bash
   flask db upgrade
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Access the app at `http://127.0.0.1:5000`.

---


