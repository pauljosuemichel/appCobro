@echo off
call .venv/Scripts/activate.bat

flask db migrate -m "Campo plata a usuarios"
flask db upgrade