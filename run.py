import os
import logging
import signal
import sys
from app import create_app, db
from flask_migrate import Migrate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask application
app = create_app()
migrate = Migrate(app, db)

# Check for required environment variables
required_env_vars = ["SQLALCHEMY_DATABASE_URI", "SECRET_KEY"]
optional_env_vars = ["FLASK_DEBUG"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

for var in missing_vars:
    app.logger.error(f"Missing required environment variable: {var}")
    sys.exit(1)  # Exit if a required variable is missing

for var in optional_env_vars:
    if not os.getenv(var):
        app.logger.warning(f"Optional environment variable {var} is not set.")

# Graceful shutdown handling
def graceful_exit(signum, frame):
    app.logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

if __name__ == "__main__":
    # Set debug mode based on the environment variable
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    # Log debug status
    app.logger.info(f"Debug mode: {debug_mode}")

    # Run the app
    app.run(
        host="0.0.0.0",  # Allow external connections for testing or production
        port=int(os.getenv("PORT", 5000)),  # Default port is 5000
        debug=debug_mode
    )
