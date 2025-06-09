from flask import Flask
import os
from dotenv import load_dotenv
from extensions import db, login_manager, csrf, bootstrap
from models import User, SCHEMA  # Added SCHEMA import

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)
login_manager.login_view = 'login'  # type: ignore # Grouped logically after init_app
bootstrap.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

import routes

if __name__ == '__main__':
    with app.app_context():
        with db.engine.connect() as conn:
            # Create the 'public' schema if it doesn't exist
            conn.execute(db.text('CREATE SCHEMA IF NOT EXISTS public;'))
            # Create your custom schema if it doesn't exist
            conn.execute(db.text(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA};'))
            conn.commit()
        db.create_all()
    app.run(debug=True)