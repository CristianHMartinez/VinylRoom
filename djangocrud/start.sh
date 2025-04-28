#!/bin/bash
chmod 664 $BASE_DIR/db.sqlite3
python manage.py migrate
gunicorn tu_proyecto.wsgi --bind 0.0.0.0:$PORT