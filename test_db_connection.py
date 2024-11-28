from app import create_app, db
from sqlalchemy import inspect

# Create the app context
app = create_app()

with app.app_context():
    # Use the inspector to list table names
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")

    # Optional: Print columns for each table
    for table_name in tables:
        print(f"Table: {table_name}")
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f" - {column['name']} ({column['type']})")
