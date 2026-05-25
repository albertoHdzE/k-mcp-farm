@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
chcp 65001 >nul
echo Starting ContextForge MCP Gateway on http://localhost:4444 ...
.\.venv\Scripts\mcpgateway.exe --host 0.0.0.0 --port 4444
pause
