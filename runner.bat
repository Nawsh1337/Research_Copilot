@echo off
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Running Streamlit app...
uv run streamlit run main.py

pause
