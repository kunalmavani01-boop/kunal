@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHONPATH=%ROOT%src"
set "PROMPT_ASSISTANT_HOME=%ROOT%.prompt_assistant"
set "PROMPT_ASSISTANT_PORT=51450"

if not exist "%ROOT%.venv\Scripts\python.exe" (
  echo The local project environment was not found.
  echo Expected: %ROOT%.venv\Scripts\python.exe
  pause
  exit /b 1
)

"%ROOT%.venv\Scripts\python.exe" -m project_360_degree_ai_prompt_assistant_platform.main web
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo.
  echo Prompt Assistant closed with an error. See:
  echo %PROMPT_ASSISTANT_HOME%\launch-session.log
  pause
)

endlocal
exit /b %EXIT_CODE%
