# Quick Reference Guide
# Smart Investment Portfolio Advisor

## 🚀 Quick Start Commands

### Start Development Servers

**Option 1: Using Batch Script (Windows)**
```bash
start-dev.bat
```

**Option 2: Manual Start**

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Access URLs
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

---

## 📁 Important File Locations

### Configuration Files
- **Backend Config:** `backend/.env`
- **Frontend Config:** `frontend/.env`
- **Backend Deps:** `backend/requirements.txt`
- **Frontend Deps:** `frontend/package.json`

### Database
- **Database File:** `backend/investment_advisor.db`
- **Init Script:** `backend/app/db_init.py`

### Entry Points
- **Backend:** `backend/app/main.py`
- **Frontend:** `frontend/src/index.js`

---

## 🔧 Common Commands

### Backend

**Activate Virtual Environment:**
```bash
# Windows
cd backend
venv\Scripts\activate

# macOS/Linux
cd backend
source venv/bin/activate
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Initialize Database:**
```bash
python -m app.db_init
```

**Run Server:**
```bash
uvicorn app.main:app --reload
```

**Run on Different Port:**
```bash
uvicorn app.main:app --reload --port 8001
```

**Deactivate Virtual Environment:**
```bash
deactivate
```

### Frontend

**Install Dependencies:**
```bash
npm install
```

**Start Development Server:**
```bash
npm start
```

**Build for Production:**
```bash
npm run build
```

**Run Tests:**
```bash
npm test
```

---

## 🗄️ Database Quick Reference

### Reset Database
```bash
cd backend
del investment_advisor.db  # Windows
# rm investment_advisor.db  # macOS/Linux
python -m app.db_init
```

### View Database Tables
```python
import sqlite3
conn = sqlite3.connect('investment_advisor.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
```

### Tables
- `users` - User accounts
- `financial_profiles` - Financial info
- `risk_profiles` - Risk assessments
- `portfolios` - Investment portfolios
- `sip_plans` - SIP plans
- `transactions` - Transactions

---

## 🔌 API Endpoints Cheat Sheet

### Authentication
```
POST   /api/auth/register    # Register user
POST   /api/auth/login       # Login user
GET    /api/auth/me          # Current user
```

### Users
```
GET    /api/users/{id}       # Get user
PUT    /api/users/{id}       # Update user
```

### Financial Profile
```
POST   /api/profile/?user_id={id}    # Create profile
GET    /api/profile/{user_id}        # Get profile
PUT    /api/profile/{user_id}        # Update profile
```

### Testing Endpoints (cURL)

**Register:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@test.com\",\"password\":\"test1234\",\"full_name\":\"Test User\"}"
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@test.com\",\"password\":\"test1234\"}"
```

---

## 🎨 Component Import Paths

### Layout Components
```javascript
import Layout from './components/Layout/Layout';
import Navbar from './components/Layout/Navbar';
import Footer from './components/Layout/Footer';
```

### Common Components
```javascript
import Card from './components/common/Card';
import Button from './components/common/Button';
import Input from './components/common/Input';
import Loading from './components/common/Loading';
```

### Context
```javascript
import { useAuth } from './context/AuthContext';
```

### Services
```javascript
import api from './services/api';
import authService from './services/authService';
import profileService from './services/profileService';
```

---

## 🔐 Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./investment_advisor.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000
```

---

## 🐛 Troubleshooting

### Backend Issues

**Port Already in Use:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

**Module Not Found:**
```bash
# Ensure venv is activated
venv\Scripts\activate
pip install -r requirements.txt
```

**Database Locked:**
```bash
# Close all connections and restart server
# Or delete and reinitialize database
```

### Frontend Issues

**Cannot Connect to API:**
- Check backend is running on port 8000
- Check `REACT_APP_API_BASE_URL` in `.env`
- Check browser console for CORS errors

**Port 3000 in Use:**
- You'll be prompted to use port 3001, accept it
- Update backend ALLOWED_ORIGINS if needed

**npm install fails:**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 Code Snippets

### Create New API Endpoint (Backend)

```python
# In backend/app/api/your_route.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.get("/endpoint")
async def your_endpoint(db: Session = Depends(get_db)):
    return {"message": "Hello"}
```

### Create New Page (Frontend)

```javascript
// In frontend/src/pages/YourPage.js
import React from 'react';
import Card from '../components/common/Card';

const YourPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1>Your Page</h1>
      <Card>
        <p>Content here</p>
      </Card>
    </div>
  );
};

export default YourPage;
```

### API Call (Frontend)

```javascript
// Using auth service
import authService from './services/authService';

const login = async () => {
  try {
    const result = await authService.login({
      email: 'user@example.com',
      password: 'password123'
    });
    console.log(result);
  } catch (error) {
    console.error(error);
  }
};
```

---

## 🔑 Key Concepts

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database
- **Pydantic** - Data validation
- **JWT** - Token-based authentication
- **CORS** - Cross-origin resource sharing

### Frontend
- **React** - Component-based UI
- **React Router** - Client-side routing
- **Context API** - State management
- **Axios** - HTTP client
- **Tailwind** - Utility-first CSS

---

## 📚 Documentation Links

### Project Documentation
- [README.md](README.md) - Overview
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Setup
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Summary

### Technology Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

---

## 🎯 Development Workflow

### 1. Start Development
```bash
# Terminal 1: Backend
cd backend && venv\Scripts\activate && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm start
```

### 2. Make Changes
- Edit files in `backend/app/` or `frontend/src/`
- Changes auto-reload in both servers

### 3. Test Changes
- Backend: Use http://localhost:8000/docs
- Frontend: Check http://localhost:3000

### 4. Commit Changes
```bash
git add .
git commit -m "Description of changes"
git push
```

---

## 📊 Project Structure at a Glance

```
📦 smart-investment-advisor
├── 📂 backend
│   ├── 📂 app
│   │   ├── 📂 api          # Routes
│   │   ├── 📂 core         # Config
│   │   ├── 📂 models       # Database
│   │   ├── 📂 schemas      # Validation
│   │   └── main.py         # Entry
│   ├── requirements.txt
│   └── .env
├── 📂 frontend
│   ├── 📂 src
│   │   ├── 📂 components   # UI Components
│   │   ├── 📂 pages        # Pages
│   │   ├── 📂 services     # API Calls
│   │   ├── 📂 context      # State
│   │   └── App.js          # Main App
│   ├── package.json
│   └── .env
└── 📄 Documentation files
```

---

## ⚡ Pro Tips

### Backend
- Use `/docs` for testing APIs
- Check terminal logs for errors
- Use `print()` for debugging
- Virtual environment must be activated

### Frontend
- Check browser console for errors
- Use React DevTools extension
- Clear browser cache if styles don't update
- `Ctrl+C` to stop dev server

### Database
- Use DB Browser for SQLite to view data
- Backup database before major changes
- Reinitialize if corrupted

### General
- Keep both servers running during development
- Use separate terminal windows
- Save files to trigger auto-reload
- Read error messages carefully

---

## 🎓 Learning Resources

### For Beginners
- FastAPI: https://fastapi.tiangolo.com/tutorial/
- React: https://react.dev/learn
- SQLAlchemy: https://docs.sqlalchemy.org/tutorial/
- Tailwind: https://tailwindcss.com/docs

### For Advanced
- JWT Auth: https://jwt.io/introduction
- REST API Design: https://restfulapi.net/
- React Best Practices: https://react.dev/learn/thinking-in-react
- Database Design: https://www.sqlshack.com/learn-sql-database-design/

---

**Quick Tip:** Bookmark this page for fast reference during development! 🔖
