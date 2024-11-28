from app import create_app, db
from sqlalchemy.sql import text  # Import the text function for raw SQL

app = create_app()

with app.app_context():
    # Clear the alembic_version table
    db.session.execute(text("DELETE FROM alembic_version;"))
    db.session.commit()
    print("Alembic version table cleared.")
