# Backend (Django + DRF) scaffold

This folder contains a minimal Django project and an app `requests_app` with models and REST API endpoints for `LaundryRequest` and `Driver`.

Quick start (Windows / PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API root will be available at http://127.0.0.1:8000/api/ once the server is running.
