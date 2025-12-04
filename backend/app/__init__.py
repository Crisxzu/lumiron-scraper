from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5101", "http://localhost:5173"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    app.config['FIRECRAWL_API_KEY'] = os.getenv('FIRECRAWL_API_KEY')

    # Initialiser la base de données SQLite
    from app.db.database import init_db
    init_db()

    from app.routes import api_routes
    app.register_blueprint(api_routes.bp)

    return app
