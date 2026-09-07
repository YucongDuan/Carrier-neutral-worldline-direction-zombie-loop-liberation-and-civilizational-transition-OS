@echo off
cd /d "%~dp0"
where py >nul 2>nul && (start "" http://127.0.0.1:8781 & py -3 start_showcase.py) || (start "" http://127.0.0.1:8781 & python start_showcase.py)
pause
