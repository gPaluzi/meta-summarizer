@echo off

:: Activate virtual environment
echo Activating virtual environment...
call virtual_env\Scripts\activate.bat

:: Verify that the virtual environment is activated
echo Virtual environment activated!
echo Installing required libraries...

:: Install dependencies from requirements.txt inside the virtual environment
 if %errorlevel%==0 (
        echo All dependencies are already installed.
    ) else (
        echo Installing required libraries...
        pip install --upgrade pip
        pip install -r requirements.txt
    )

:: Run the main Python script
echo Running the project...
python main.py

:: Deactivate virtual environment
Deactivate

pause