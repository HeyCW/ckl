import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_CONFIG = {
    'app_name': 'My Tkinter App',
    'version': '1.0.0',
    'default_size': '800x600',
    'min_size': (400, 300),
    'assets_dir': os.path.join(BASE_DIR, 'assets'),
    'images_dir': os.path.join(BASE_DIR, 'assets', 'images'),
}

# Primary engine is Postgres, configured via environment variables (a
# local .env file works too, see .env.example). SQLite is the offline
# fallback: it's used automatically whenever DB_HOST isn't set, or
# Postgres can't be reached — see src/models/db/config.py and
# src/models/database.py (SQLiteDatabase._connect_backend).
DATABASE_CONFIG = {
    'type': 'postgres',
    'sqlite_fallback_path': os.path.join(BASE_DIR, 'data', 'app.db'),
}