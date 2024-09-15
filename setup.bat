@echo off

python -m venv .venv
call .venv/Scripts/activate.bat

echo SECRET_KEY= > .\.env
echo SQLALCHEMY_DATABASE_URI= >> .\.env
echo GOOGLE_CLIENT_ID= >> .\.env
echo GOOGLE_CLIENT_SECRET= >> .\.env

pip install -r requirements.txt