@echo off
cd "c:\Users\aliri\Desktop\Craftsmanship\backend"
call venv\Scripts\activate.bat
python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0
