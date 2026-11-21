@echo off
cd /d "%~dp0"
if not exist "venv" python -m venv venv
call venv\Scripts\activate
python -m pip install -r requirements.txt
where ffmpeg >nul 2>&1
if errorlevel 1 (
 echo ERROR: FFmpeg is not installed or not in PATH.
 echo Install FFmpeg then restart this launcher.
 pause
 exit /b 1
)
echo Starting ERNESTYT Segment Downloader...
echo Browser will open automatically when localhost is ready.
python app.py
pause
