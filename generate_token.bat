@echo off
cd /d "%~dp0"
echo Generating JWT token for admin@example.com (valid 10080 minutes = 7 days) ...
.\.venv\Scripts\python.exe -m mcpgateway.utils.create_jwt_token ^
  --username admin@example.com ^
  --exp 10080 ^
  --secret 0c145663f07e5fd510da295239dc8186839d3092ff2f73797154b8c248b13660
pause
