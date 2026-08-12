"""Check installation status"""
import subprocess
import os

print("="*60)
print("INSTALLATION VERIFICATION")
print("="*60)
print()

# Check Python
print("1. Checking Python...")
try:
    result = subprocess.run(["python", "--version"], capture_output=True, text=True)
    print(f"   ✓ {result.stdout.strip()}")
except:
    print("   ✗ Python not found")

print()

# Check Node.js
print("2. Checking Node.js...")
try:
    result = subprocess.run(["node", "--version"], capture_output=True, text=True)
    print(f"   ✓ Node.js {result.stdout.strip()}")
except:
    print("   ✗ Node.js not found")

print()

# Check npm
print("3. Checking npm...")
try:
    result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
    print(f"   ✓ npm {result.stdout.strip()}")
except:
    print("   ✗ npm not found")

print()

# Check backend venv
print("4. Checking backend virtual environment...")
if os.path.exists("backend/venv"):
    print("   ✓ Virtual environment exists")
    
    # Check if packages are installed
    try:
        result = subprocess.run(
            ["backend/venv/Scripts/python.exe", "-c", "import fastapi, sqlalchemy, pydantic; print('Packages OK')"],
            capture_output=True,
            text=True
        )
        if "Packages OK" in result.stdout:
            print("   ✓ Core packages installed")
        else:
            print("   ⚠ Some packages may be missing")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"   ⚠ Could not verify packages: {e}")
else:
    print("   ✗ Virtual environment not found")

print()

# Check frontend node_modules
print("5. Checking frontend dependencies...")
if os.path.exists("frontend/node_modules"):
    print("   ✓ Node modules installed")
else:
    print("   ✗ Node modules not found")

print()

# Check env files
print("6. Checking environment files...")
if os.path.exists("backend/.env"):
    print("   ✓ Backend .env exists")
else:
    print("   ✗ Backend .env missing")

if os.path.exists("frontend/.env"):
    print("   ✓ Frontend .env exists")
else:
    print("   ✗ Frontend .env missing")

print()

# Check database
print("7. Checking database...")
if os.path.exists("backend/investment_advisor.db"):
    print("   ✓ Database file exists")
else:
    print("   ⚠ Database file not found (will be created on first run)")

print()
print("="*60)
print("NEXT STEPS:")
print("="*60)
print()
print("If all checks passed, you can start the servers:")
print("  1. Backend: cd backend && venv\\Scripts\\activate && uvicorn app.main:app --reload")
print("  2. Frontend: cd frontend && npm start")
print()
print("Or use: start-dev.bat")
print()
