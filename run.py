import os
import signal
import sys
from flask import Flask
from app import create_app, db
from flask_migrate import Migrate

# Create the Flask application
app = create_app()
migrate = Migrate(app, db)

# Graceful shutdown handling
def graceful_exit(signum, frame):
    app.logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

if __name__ == "__main__":
    # Ensure critical environment variables are set
    required_env_vars = ["FLASK_DEBUG", "PORT"]
    missing_env_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_env_vars:
        for var in missing_env_vars:
            app.logger.error(f"Missing required environment variable: {var}")
        sys.exit("Exiting due to missing environment variables.")

    # Set debug mode based on the environment variable
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    # Log server starting details
    app.logger.info("Starting Flask application...")
    app.logger.info(f"Debug mode: {'enabled' if debug_mode else 'disabled'}")
    app.logger.info(f"Listening on port {os.getenv('PORT', 5000)}")

    # Run the app
    try:
        app.run(
            host="0.0.0.0",  # Allow external connections for testing or production
            port=int(os.getenv("PORT", 5000)),  # Default port is 5000
            debug=debug_mode
        )
    except Exception as e:
        app.logger.error(f"Failed to start the Flask application: {e}")
        sys.exit(1)
