import os
import logging
import signal
import sys
from app import create_app, db
from flask_migrate import Migrate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the app
app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Graceful shutdown handling
def graceful_exit(signum, frame):
    app.logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

if __name__ == "__main__":
    # Run the app
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "True").lower() == "true"
    )
