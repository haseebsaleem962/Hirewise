"""
WSGI entrypoint for production servers (gunicorn).
Usage: gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 wsgi:app

Serves the same app factory as the dev server (python app.py), but through
a plain "wsgi:app" reference — no parentheses in the command line, which
bash cannot misparse when hosts run the start command via `bash -c`.
"""
from app import create_app

app = create_app()
