# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Seed the Database
```bash
python run_seed.py
```

This will create:
- 2 parent users
- 3 students
- Sample attendance, academic, and engagement data

### Step 3: Start the Server
```bash
python run_server.py
```

The API will be available at `http://localhost:8000`

### Step 4: Open the Dashboard
1. Open `frontend/index.html` in your web browser
2. Login with:
   - **Username**: `parent1`
   - **Password**: `password123`
3. Select a student and view the dashboard!

## 📊 What You'll See

- **Academic Progress**: Grades, test scores, subject averages
- **Attendance**: Daily attendance records and trends
- **Engagement**: LMS login activity, assignment submissions
- **Alerts**: Automated alerts for low attendance, grade drops, etc.
- **Insights**: AI-generated insights and recommendations

## 🔍 API Endpoints

Visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints:
- `POST /token` - Login
- `GET /students` - Get your students
- `GET /student/{id}/dashboard` - Get dashboard data
- `GET /alerts` - Get alerts

## 🐛 Troubleshooting

### Import Errors
If you get import errors, make sure you're running from the project root:
```bash
python run_server.py
```

### Database Errors
If the database doesn't exist, run the seed script:
```bash
python run_seed.py
```

### CORS Errors
The frontend needs to be served from a web server or opened directly in the browser. The API allows all origins by default for development.

## 📝 Next Steps

1. **Customize Alert Rules**: Edit `backend/langgraph/agents.py`
2. **Add More Agents**: Extend the LangGraph workflow in `backend/langgraph/graph.py`
3. **Modify Frontend**: Edit `frontend/index.html`
4. **Add Authentication**: The JWT system is already in place!

## 🎓 Understanding the Architecture

1. **Frontend** → Makes API calls to FastAPI
2. **FastAPI** → Handles authentication and routes requests
3. **LangGraph** → Orchestrates multiple agents
4. **Agents** → Fetch data from database
5. **Analysis Agent** → Generates insights and alerts
6. **Database** → Stores all student data

Enjoy exploring the Parent Dashboard! 🎉


