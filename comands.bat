@echo off
call .venv/Scripts/activate.bat

flask db migrate -m "Campo email a usuarios"
flask db upgrade