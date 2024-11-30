from app import create_app  # Import the create_app function

# Create the app instance
app = create_app()

# Access and print the database URI
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
