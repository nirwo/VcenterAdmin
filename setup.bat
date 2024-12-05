@echo off
echo Setting up vSphere Manager...

:: Create virtual environment
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
python -m pip install --upgrade pip

:: Install requirements
pip install -r requirements.txt

:: Create .env file with a random secret key
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(16))" > .env

:: Create necessary directories
mkdir static\css static\js templates 2>nul

echo.
echo Setup complete! To start the application:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run the application: python run.py
echo 3. Open http://localhost:5000 in your browser
