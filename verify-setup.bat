@echo off
echo ========================================
echo Smart Investment Advisor - Setup Verification
echo ========================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    goto :error
)
echo [OK] Python is installed
echo.

echo Checking Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    goto :error
)
echo [OK] Node.js is installed
echo.

echo Checking npm installation...
npm --version
if %errorlevel% neq 0 (
    echo ERROR: npm is not installed or not in PATH
    goto :error
)
echo [OK] npm is installed
echo.

echo Checking backend virtual environment...
if exist backend\venv\ (
    echo [OK] Virtual environment exists
) else (
    echo [WARNING] Virtual environment not found
    echo Run: cd backend && python -m venv venv
)
echo.

echo Checking backend dependencies...
if exist backend\venv\Lib\site-packages\fastapi\ (
    echo [OK] FastAPI installed
) else (
    echo [WARNING] FastAPI not found
    echo Run: cd backend && venv\Scripts\activate && pip install -r requirements.txt
)
echo.

echo Checking frontend dependencies...
if exist frontend\node_modules\ (
    echo [OK] Node modules installed
) else (
    echo [WARNING] Node modules not found
    echo Run: cd frontend && npm install
)
echo.

echo Checking database...
if exist backend\investment_advisor.db (
    echo [OK] Database exists
) else (
    echo [WARNING] Database not found
    echo Run: cd backend && python -m app.db_init
)
echo.

echo Checking environment files...
if exist backend\.env (
    echo [OK] Backend .env exists
) else (
    echo [WARNING] Backend .env not found
    echo Run: cd backend && copy .env.example .env
)

if exist frontend\.env (
    echo [OK] Frontend .env exists
) else (
    echo [WARNING] Frontend .env not found
    echo Run: cd frontend && copy .env.example .env
)
echo.

echo ========================================
echo Verification Complete!
echo ========================================
echo.
echo If all checks passed, you're ready to start development:
echo   1. Run start-dev.bat
echo   2. Or follow manual start instructions in QUICK_REFERENCE.md
echo.
goto :end

:error
echo.
echo ========================================
echo Setup verification failed!
echo Please install missing dependencies and try again.
echo See SETUP_GUIDE.md for detailed instructions.
echo ========================================
echo.

:end
pause
