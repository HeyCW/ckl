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

DATABASE_CONFIG = {
    'type': 'sqlite',
    'path': os.path.join(BASE_DIR, 'data', 'app.db'),
}