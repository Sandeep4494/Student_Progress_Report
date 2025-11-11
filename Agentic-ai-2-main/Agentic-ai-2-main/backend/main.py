"""
FastAPI Main Application - Parent Dashboard API
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from db.database import get_db, init_db
from db.models import User, Student, Alert
from langgraph.graph import run_dashboard_graph

# Initialize FastAPI app
app = FastAPI(
    title="Parent Dashboard API",
    description="Real-time Student Progress & Engagement Tracking - Parent Dashboard",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str

    class Config:
        from_attributes = True


class StudentResponse(BaseModel):
    id: int
    student_id: str
    full_name: str
    email: str

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    message: str
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    student_id: int
    academic: dict
    attendance: dict
    engagement: dict
    analysis: dict
    errors: List[str] = []


# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


async def get_user_student(student_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Verify that the student belongs to the current user"""
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.parent_id == current_user.id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found or access denied"
        )
    return student


# Routes
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Parent Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint - OAuth2 compatible token endpoint"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@app.get("/students", response_model=List[StudentResponse])
async def get_my_students(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all students associated with the current parent"""
    students = db.query(Student).filter(Student.parent_id == current_user.id).all()
    return students


@app.get("/student/{student_id}/dashboard", response_model=DashboardResponse)
async def get_student_dashboard(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get student dashboard data using LangGraph orchestration
    This endpoint triggers all three agents (Academic, Attendance, Engagement)
    and returns aggregated data with insights
    """
    # Verify student belongs to current user
    student = await get_user_student(student_id, current_user, db)
    
    # Run LangGraph orchestration
    try:
        dashboard_data = run_dashboard_graph(student_id, db)
        return DashboardResponse(**dashboard_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard: {str(e)}"
        )


@app.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    student_id: Optional[int] = None,
    resolved: Optional[bool] = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get alerts for students belonging to the current parent
    Alerts are generated by the LangGraph analysis agent
    """
    # Get all students for current user
    students = db.query(Student).filter(Student.parent_id == current_user.id).all()
    student_ids = [s.id for s in students]
    
    if not student_ids:
        return []
    
    # Build query
    query = db.query(Alert).filter(Alert.student_id.in_(student_ids))
    
    # Filter by student_id if provided
    if student_id:
        if student_id not in student_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this student's alerts"
            )
        query = query.filter(Alert.student_id == student_id)
    
    # Filter by resolved status
    query = query.filter(Alert.is_resolved == resolved)
    
    # Order by creation date (newest first)
    alerts = query.order_by(Alert.created_at.desc()).limit(50).all()
    
    return alerts


@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an alert as resolved"""
    # Get alert
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Verify student belongs to current user
    student = db.query(Student).filter(
        Student.id == alert.student_id,
        Student.parent_id == current_user.id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mark as resolved
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Alert resolved successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


