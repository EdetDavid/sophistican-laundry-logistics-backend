from django.apps import AppConfig
from pathlib import Path


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    # Explicitly set the filesystem path for this app to avoid issues where
    # the module is found in multiple locations (PythonAnywhere/WSGI setups
    # sometimes add duplicate entries like './users' and '/home/.../users').
    path = str(Path(__file__).resolve().parent)
