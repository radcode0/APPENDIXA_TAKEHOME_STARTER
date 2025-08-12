@echo off
rem -------------------------------------------------------------
rem run.bat – create/activate venv, install deps, run pipeline,
rem          then run evaluation
rem -------------------------------------------------------------

rem Create virtual environment (if not already there)
if not exist ".venv" (
    echo Creating virtual environment ...
    python -m venv .venv
)

rem Activate it
call .venv\Scripts\activate.bat
echo Virtual environment activated ...

rem Upgrade pip
python -m pip install --upgrade pip

rem Install the two requirement files
echo Installing starter requirements ...
pip install -r starter\requirements.txt

echo Installing agent requirements
pip install -r agent\requirements.txt

rem Run the pipeline
echo Running agent\pipeline.py ...
python agent\pipeline.py
IF ERRORLEVEL 1 (
    echo.
    echo *** ERROR: agent\pipeline.py exited with code %ERRORLEVEL%. ***
    echo *** The pipeline raised an exception or crashed. ***
    echo *** Aborting further execution. ***
    exit /b 1
)

rem Run the evaluation script
echo Running starter\eval.py ...
python starter\eval.py

echo Finished