from app import create_app

app = create_app()

with app.app_context():
    print("Template folder path:", app.template_folder)
    print("Available templates:", app.jinja_env.list_templates())
