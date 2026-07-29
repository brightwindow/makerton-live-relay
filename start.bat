@echo off
REM  MAKERTON - LIVE RELAY  /  double-click to start
chcp 65001 >nul
cd /d "%~dp0"
title MAKERTON - LIVE RELAY

set PY=
where python >nul 2>&1 && set PY=python
if not defined PY where py >nul 2>&1 && set PY=py
if not defined PY if exist "%USERPROFILE%\anaconda3\python.exe" set PY="%USERPROFILE%\anaconda3\python.exe"

if not defined PY (
  echo.
  echo   Python not found. Install it from https://python.org
  echo   and be sure to tick "Add Python to PATH".
  echo.
  pause
  exit /b 1
)

%PY% serve.py %*

echo.
echo   Server stopped.
pause
