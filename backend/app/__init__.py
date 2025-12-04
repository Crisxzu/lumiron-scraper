from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuration CORS depuis .env
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5101,http://localhost:5173')
    origins_list = [origin.strip() for origin in cors_origins.split(',')]

    CORS(app, resources={
        r"/api/*": {
            "origins": origins_list,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "expose_headers": ["Content-Type", "X-Total-Count"],
            "supports_credentials": False,
            "max_age": 3600
        }
    })

    print(f"[CORS] Allowed origins: {origins_list}")

    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    app.config['FIRECRAWL_API_KEY'] = os.getenv('FIRECRAWL_API_KEY')

    # Initialiser la base de données SQLite
    from app.db.database import init_db
    init_db()

    from app.routes import api_routes
    app.register_blueprint(api_routes.bp)

    return app
