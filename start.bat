@echo off
cd /d "%~dp0"
echo Downloading site...
python download_site.py
echo Patching JS (bypass checks)...
python patch_site.py
echo Starting local server at http://127.0.0.1:8080
python server.py
