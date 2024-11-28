from sqlalchemy import inspect
from app import create_app, db
from app.models import User, Flight, Booking

# Create the Flask application
app = create_app()

with app.app_context():
    # Check template configuration
    print("Template folder path:", app.template_folder)
    print("Available templates:", app.jinja_env.list_templates())

    # Test database connection
    try:
        # Attempt a simple query to verify the connection
        user_count = User.query.count()
        print(f"Database connected successfully. User count: {user_count}")
    except Exception as e:
        print("Database connection failed:", str(e))

    # Use the inspector to check if tables exist
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        required_tables = ["user", "flight", "booking"]
        for table in required_tables:
            if table in tables:
                print(f"Table '{table}' exists.")
            else:
                print(f"Table '{table}' is missing.")
    except Exception as e:
        print("Error checking table existence:", str(e))
