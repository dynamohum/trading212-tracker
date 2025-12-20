from flask import Flask
from app.config import Config
from app.database.db_manager import DatabaseManager
from app.services.tracker_service import TrackerService

def create_app(config_class=Config):
    # Explicitly set template and static folders to root directory
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    # Initialize Database Manager
    db_manager = DatabaseManager(app.config['DB_FILE'])
    db_manager.init_db()
    app.db_manager = db_manager # Attach to app for easy access

    # Initialize Background Tracker if not already running (for reloader safety we might need checks)
    # Note: In debug mode with reloader, this might run twice. 'run.py' handles reloader=False typically.
    tracker_service = TrackerService(db_manager)
    tracker_service.start_background_tracking()
    app.tracker_service = tracker_service

    # Register Blueprints
    from app.routes import main, api, ticker
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(ticker.bp)

    return app
