"""
Database models for Student Progress Tracking System
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class User(Base):
    """Parent user model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to students
    students = relationship("Student", back_populates="parent")


class Student(Base):
    """Student model"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    parent = relationship("User", back_populates="students")
    attendance_records = relationship("AttendanceRecord", back_populates="student")
    academic_scores = relationship("AcademicScore", back_populates="student")
    engagement_logs = relationship("EngagementLog", back_populates="student")


class AttendanceRecord(Base):
    """Attendance records model"""
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False)  # 'present', 'absent', 'late', 'excused'
    class_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    student = relationship("Student", back_populates="attendance_records")


class AcademicScore(Base):
    """Academic scores and grades model"""
    __tablename__ = "academic_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(String(255), nullable=False)
    assessment_type = Column(String(100), nullable=False)  # 'exam', 'quiz', 'assignment', 'project'
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    student = relationship("Student", back_populates="academic_scores")


class EngagementLog(Base):
    """Engagement and LMS activity logs"""
    __tablename__ = "engagement_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_type = Column(String(100), nullable=False)  # 'login', 'assignment_submitted', 'video_watched', 'quiz_taken'
    activity_details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    student = relationship("Student", back_populates="engagement_logs")


class Alert(Base):
    """System alerts and notifications"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    alert_type = Column(String(100), nullable=False)  # 'attendance_drop', 'grade_drop', 'missing_assignment', 'engagement_drop'
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    student = relationship("Student")


