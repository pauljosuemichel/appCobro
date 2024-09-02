@echo off
call .venv/Scripts/activate.bat

flask db migrate -m "Propiedad comprado"
flask db upgrade