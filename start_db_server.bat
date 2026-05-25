@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo Starting Database MCP Server on http://localhost:8765/sse ...
echo DB: demo.db  (employees, departments, projects, project_assignments)
echo.
.venv\Scripts\python.exe db_mcp_server.py
pause
