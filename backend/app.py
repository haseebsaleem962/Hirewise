from flask import Flask
from flask_cors import CORS
from config import Config
from models import db, bcrypt
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    CORS(app, supports_credentials=True)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MODEL_DIR'], exist_ok=True)
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.hiring import hiring_bp
    from routes.candidates import candidates_bp
    from routes.dashboard import dashboard_bp
    from routes.email_routes import email_bp
    from routes.ml import ml_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(hiring_bp, url_prefix='/api/hiring')
    app.register_blueprint(candidates_bp, url_prefix='/api/candidates')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(email_bp, url_prefix='/api/email')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')

    # Create database tables
    with app.app_context():
        db.create_all()

    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'HireWise API is running'}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
