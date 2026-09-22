@echo off
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%~dp0extnest_host.py"
  exit /b %errorlevel%
)
python "%~dp0extnest_host.py"
