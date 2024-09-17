@echo off
call .venv/Scripts/activate.bat

flask db migrate -m "Transacciones"
flask db upgrade