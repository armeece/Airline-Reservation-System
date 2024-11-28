import os
import logging
from logging.handlers import RotatingFileHandler
import signal
import sys
from app import create_app, db
from flask_migrate import Migrate

# Create the Flask application
app = create_app()
migrate = Migrate(app, db)

# Configure logging
if not app.debug:  # Only set up logging in production mode
    if not os.path.exists("logs"):
        os.mkdir("logs")  # Ensure logs directory exists
    file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=3)
    file_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

# Validate critical environment variables
required_env_vars = ["SECRET_KEY", "SQLALCHEMY_DATABASE_URI"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    for var in missing_vars:
        app.logger.error(f"Missing critical environment variable: {var}")
    sys.exit("Critical environment variables are missing. Check logs for details.")

# Graceful shutdown handling
def graceful_exit(signum, frame):
    app.logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

if __name__ == "__main__":
    # Set debug mode based on the environment variable
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    # Run the app
    app.run(
        host="0.0.0.0",  # Allow external connections for testing or production
        port=int(os.getenv("PORT", 5000)),  # Default port is 5000
        debug=debug_mode
    )
