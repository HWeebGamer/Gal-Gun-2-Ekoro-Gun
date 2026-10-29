@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start Laser Bridge.ps1"
if errorlevel 1 pause
