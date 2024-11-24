import os
import logging
from app import create_app, db
from flask_migrate import Migrate

# Create the Flask application
app = create_app()
migrate = Migrate(app, db)

# Configure logging
if not app.debug:  # Only set up logging in production mode
    if not os.path.exists("logs"):
        os.mkdir("logs")  # Ensure logs directory exists
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

if __name__ == "__main__":
    # Set debug mode based on the environment variable
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    # Run the app
    app.run(
        host="0.0.0.0",  # Allow external connections for testing or production
        port=int(os.getenv("PORT", 5000)),  # Default port is 5000
        debug=debug_mode
    )
