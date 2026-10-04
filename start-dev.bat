@echo off
echo ========================================
echo Smart Investment Advisor - Development
echo ========================================
echo.

REM Apply any pending database migrations before the server starts.
REM Without this, a model change is invisible to an existing database:
REM create_all() only creates missing TABLES, never missing columns.
echo Applying database migrations...
pushd backend
call venv\Scripts\activate && alembic upgrade head
if errorlevel 1 (
    echo.
    echo ERROR: migrations failed. Fix this before starting the servers.
    echo Run "python check_installation.py" from the repository root to diagnose.
    popd
    pause
    exit /b 1
)
popd
echo.

echo Starting Backend Server...
start cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo Development servers are starting...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Note: the frontend can take several minutes to compile the first
echo time. That is normal for Create React App on a cold cache.
echo.
echo Press any key to close this window...
pause > nul
