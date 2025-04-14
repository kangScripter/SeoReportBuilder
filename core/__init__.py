# app/__init__.py

from flask import Flask
from flask_caching import Cache
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', "#qsdcv@#((gbgb))")

# Configure cache
cache = Cache()

def create_app():
    # Configure cache
    app.config['CACHE_TYPE'] = os.getenv('CACHE_TYPE', 'SimpleCache')
    app.config['CACHE_DEFAULT_TIMEOUT'] = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Initialize cache with app
    cache.init_app(app)
    
    # Set environment variables
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = os.getenv('OAUTHLIB_RELAX_TOKEN_SCOPE', '1')
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = os.getenv('OAUTHLIB_INSECURE_TRANSPORT', '1')
    os.environ['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')

    # Register blueprints
    from .routes import main_bp
    from .auth import auth_bp
    from .report_builder.routes import report_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(report_bp, url_prefix='/reports')
    
    # Attach cache to app
    app.cache = cache
    
    return app
