@echo off
call .venv/Scripts/activate.bat

flask db migrate -m "Ruta de imagen, en los productos"
flask db upgrade