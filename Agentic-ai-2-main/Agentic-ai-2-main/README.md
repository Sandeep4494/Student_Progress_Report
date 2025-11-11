# Real-time Student Progress & Engagement Tracking – Parent Dashboard

A comprehensive full-stack application built with **FastAPI**, **LangGraph** (Agentic AI), and **React/HTML** for tracking student academic progress, attendance, and engagement metrics.

## 🚀 Features

### Backend
- **LangGraph Orchestration**: Multi-agent system for data fetching and analysis
  - **Agent-A**: Fetches academic progress (grades, test results)
  - **Agent-B**: Fetches attendance data (daily attendance, missed classes)
  - **Agent-C**: Fetches engagement metrics (LMS login activity, assignment submissions)
  - **Analysis Agent**: Merges data and generates insights + alerts using LLM reasoning

- **FastAPI REST API**:
  - `/student/{id}/dashboard` → Aggregated data from LangGraph
  - `/alerts` → Predicted alerts from LangGraph analysis
  - JWT-based authentication
  - Role-based access control (parents can only view their students)

### Frontend
- Modern, responsive dashboard with Chart.js visualizations
- Real-time data visualization:
  - Attendance trend charts
  - Academic progress charts
  - Engagement activity charts
  - Assignment completion charts
- Alert and notification system
- Insights and recommendations

### Database
- SQLite database (can be easily switched to PostgreSQL)
- Tables: `students`, `attendance_records`, `academic_scores`, `engagement_logs`, `alerts`
- Seed script to generate sample data

### Security
- JWT token-based authentication
- OAuth2 password flow
- Role-based access control (RBAC)
- Parents can only access their assigned students' data

## 📁 Project Structure

```
parent-dashboard-ai/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── langgraph/
│   │   ├── __init__.py
│   │   ├── agents.py           # Agent-A, Agent-B, Agent-C, Analysis Agent
│   │   └── graph.py            # LangGraph orchestration
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py         # Database configuration
│   │   ├── models.py           # SQLAlchemy models
│   │   └── seed.py             # Database seeding script
│   └── __init__.py
├── frontend/
│   └── index.html              # Dashboard UI
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository** (or navigate to the project directory)

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Initialize the database and seed sample data**:
```bash
# Option 1: Using the run script (recommended)
python run_seed.py

# Option 2: Manual way
cd backend
python db/seed.py
```

4. **Start the FastAPI server**:
```bash
# Option 1: Using the run script (recommended)
python run_server.py

# Option 2: Manual way
cd backend
python main.py

# Option 3: Using uvicorn directly
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

5. **Open the frontend**:
   - Open `frontend/index.html` in a web browser
   - Or serve it using a simple HTTP server:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Then open `http://localhost:8080` in your browser

## 📖 Usage

### API Documentation
Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Default Credentials
After seeding the database:
- **Username**: `parent1`
- **Password**: `password123`

### API Endpoints

#### Authentication
- `POST /token` - Login and get JWT token
  ```bash
  curl -X POST "http://localhost:8000/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=parent1&password=password123"
  ```

#### Student Dashboard
- `GET /student/{student_id}/dashboard` - Get aggregated dashboard data
  ```bash
  curl -X GET "http://localhost:8000/student/1/dashboard" \
    -H "Authorization: Bearer YOUR_TOKEN"
  ```

#### Alerts
- `GET /alerts?student_id=1&resolved=false` - Get alerts for a student
  ```bash
  curl -X GET "http://localhost:8000/alerts?student_id=1&resolved=false" \
    -H "Authorization: Bearer YOUR_TOKEN"
  ```

#### Students
- `GET /students` - Get all students for the current parent
  ```bash
  curl -X GET "http://localhost:8000/students" \
    -H "Authorization: Bearer YOUR_TOKEN"
  ```

## 🧠 LangGraph Agent Flow

1. **Parent requests dashboard** → FastAPI endpoint triggers LangGraph
2. **Graph execution**:
   - Agent-A fetches academic data
   - Agent-B fetches attendance data
   - Agent-C fetches engagement data
   - Analysis Agent merges data and generates insights
3. **Return JSON response** with aggregated data and alerts

### Alert Generation
Alerts are automatically generated when:
- Attendance drops below 75%
- Academic scores drop below threshold (70%)
- Low engagement detected (fewer than 15 logins in 30 days)
- Missing assignments detected
- Declining trends in any metric

## 🗄️ Database Schema

### Tables
- **users**: Parent user accounts
- **students**: Student information linked to parents
- **attendance_records**: Daily attendance records
- **academic_scores**: Grades and assessment scores
- **engagement_logs**: LMS activity and engagement metrics
- **alerts**: System-generated alerts and notifications

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing
- **Role-Based Access Control**: Parents can only access their students' data
- **CORS**: Configured for frontend integration
- **Input Validation**: Pydantic models for request validation

## 🎨 Frontend Features

- **Interactive Charts**: Chart.js visualizations
- **Real-time Updates**: Refresh dashboard to get latest data
- **Alert Management**: View and track alerts
- **Responsive Design**: Works on desktop and mobile devices
- **Student Selection**: Switch between multiple students

## 🚀 Deployment

### Production Considerations

1. **Change SECRET_KEY** in `backend/main.py`
2. **Use PostgreSQL** instead of SQLite for production
3. **Configure CORS** properly in `main.py`
4. **Use environment variables** for sensitive configuration
5. **Enable HTTPS** for secure communication
6. **Set up proper logging** and monitoring

### Environment Variables
Create a `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/parent_dashboard
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📝 Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Adding New Agents
1. Create a new agent class in `backend/langgraph/agents.py`
2. Add a node function in `backend/langgraph/graph.py`
3. Update the graph workflow to include the new agent

### Modifying Alert Rules
Edit the `AnalysisAgent.analyze_and_generate_insights()` method in `backend/langgraph/agents.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database errors**: Initialize the database first
   ```bash
   python backend/db/seed.py
   ```

3. **CORS errors**: Check CORS configuration in `main.py`

4. **LangGraph not available**: The system will fall back to simple orchestration if LangGraph is not installed

## 📞 Support

For issues and questions, please open an issue on the repository.

---

**Built with ❤️ using FastAPI, LangGraph, and Chart.js**

