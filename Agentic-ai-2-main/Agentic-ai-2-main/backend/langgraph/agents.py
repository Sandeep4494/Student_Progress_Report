"""
LangGraph Agents for Student Data Fetching and Analysis
Agent-A: Academic Progress
Agent-B: Attendance Data
Agent-C: Engagement Metrics
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from db.models import Student, AttendanceRecord, AcademicScore, EngagementLog, Alert


class AcademicProgressAgent:
    """Agent-A: Fetches and analyzes academic progress data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def fetch_academic_data(self, student_id: int) -> Dict[str, Any]:
        """
        Fetch academic progress data for a student
        """
        try:
            # Get all academic scores for the student
            scores = self.db.query(AcademicScore).filter(
                AcademicScore.student_id == student_id
            ).order_by(AcademicScore.date.desc()).all()
            
            if not scores:
                return {
                    "status": "success",
                    "data": {
                        "total_assessments": 0,
                        "average_score": 0,
                        "subjects": {},
                        "recent_scores": [],
                        "trend": "no_data"
                    }
                }
            
            # Calculate statistics
            total_assessments = len(scores)
            average_score = sum(s.percentage for s in scores) / total_assessments if scores else 0
            
            # Group by subject
            subjects = {}
            for score in scores:
                if score.subject not in subjects:
                    subjects[score.subject] = {
                        "average": 0,
                        "count": 0,
                        "recent_scores": []
                    }
                subjects[score.subject]["count"] += 1
                subjects[score.subject]["recent_scores"].append({
                    "type": score.assessment_type,
                    "score": score.score,
                    "max_score": score.max_score,
                    "percentage": score.percentage,
                    "date": score.date.isoformat()
                })
            
            # Calculate subject averages
            for subject in subjects:
                subject_scores = [s.percentage for s in scores if s.subject == subject]
                subjects[subject]["average"] = sum(subject_scores) / len(subject_scores) if subject_scores else 0
            
            # Get recent scores (last 10)
            recent_scores = [
                {
                    "subject": s.subject,
                    "type": s.assessment_type,
                    "score": s.score,
                    "max_score": s.max_score,
                    "percentage": s.percentage,
                    "date": s.date.isoformat()
                }
                for s in scores[:10]
            ]
            
            # Calculate trend (compare last 30 days to previous 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            sixty_days_ago = datetime.now() - timedelta(days=60)
            
            recent_scores_30d = [s.percentage for s in scores if s.date >= thirty_days_ago]
            previous_scores_30d = [s.percentage for s in scores if sixty_days_ago <= s.date < thirty_days_ago]
            
            if recent_scores_30d and previous_scores_30d:
                recent_avg = sum(recent_scores_30d) / len(recent_scores_30d)
                previous_avg = sum(previous_scores_30d) / len(previous_scores_30d)
                trend = "improving" if recent_avg > previous_avg else "declining" if recent_avg < previous_avg else "stable"
            else:
                trend = "insufficient_data"
            
            return {
                "status": "success",
                "data": {
                    "total_assessments": total_assessments,
                    "average_score": round(average_score, 2),
                    "subjects": subjects,
                    "recent_scores": recent_scores,
                    "trend": trend
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


class AttendanceAgent:
    """Agent-B: Fetches and analyzes attendance data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def fetch_attendance_data(self, student_id: int) -> Dict[str, Any]:
        """
        Fetch attendance data for a student
        """
        try:
            # Get attendance records for last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            attendance_records = self.db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.student_id == student_id,
                    AttendanceRecord.date >= thirty_days_ago
                )
            ).order_by(AttendanceRecord.date.desc()).all()
            
            if not attendance_records:
                return {
                    "status": "success",
                    "data": {
                        "total_classes": 0,
                        "present_count": 0,
                        "absent_count": 0,
                        "attendance_percentage": 0,
                        "daily_attendance": [],
                        "trend": "no_data"
                    }
                }
            
            # Calculate statistics
            total_classes = len(attendance_records)
            present_count = sum(1 for r in attendance_records if r.status == "present")
            absent_count = sum(1 for r in attendance_records if r.status == "absent")
            late_count = sum(1 for r in attendance_records if r.status == "late")
            excused_count = sum(1 for r in attendance_records if r.status == "excused")
            
            # Calculate attendance percentage (present + late + excused count as present)
            effective_present = present_count + late_count + excused_count
            attendance_percentage = (effective_present / total_classes * 100) if total_classes > 0 else 0
            
            # Group by date for daily attendance
            daily_attendance = {}
            for record in attendance_records:
                date_key = record.date.date().isoformat()
                if date_key not in daily_attendance:
                    daily_attendance[date_key] = {
                        "date": date_key,
                        "present": 0,
                        "absent": 0,
                        "late": 0,
                        "excused": 0,
                        "total": 0
                    }
                daily_attendance[date_key][record.status] += 1
                daily_attendance[date_key]["total"] += 1
            
            daily_attendance_list = sorted(daily_attendance.values(), key=lambda x: x["date"], reverse=True)
            
            # Calculate trend (compare last 15 days to previous 15 days)
            fifteen_days_ago = datetime.now() - timedelta(days=15)
            
            recent_records = [r for r in attendance_records if r.date >= fifteen_days_ago]
            previous_records = [r for r in attendance_records if r.date < fifteen_days_ago]
            
            if recent_records and previous_records:
                recent_present = sum(1 for r in recent_records if r.status in ["present", "late", "excused"])
                previous_present = sum(1 for r in previous_records if r.status in ["present", "late", "excused"])
                
                recent_percentage = (recent_present / len(recent_records) * 100) if recent_records else 0
                previous_percentage = (previous_present / len(previous_records) * 100) if previous_records else 0
                
                if recent_percentage > previous_percentage:
                    trend = "improving"
                elif recent_percentage < previous_percentage:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            return {
                "status": "success",
                "data": {
                    "total_classes": total_classes,
                    "present_count": present_count,
                    "absent_count": absent_count,
                    "late_count": late_count,
                    "excused_count": excused_count,
                    "attendance_percentage": round(attendance_percentage, 2),
                    "daily_attendance": daily_attendance_list[:30],  # Last 30 days
                    "trend": trend
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


class EngagementAgent:
    """Agent-C: Fetches and analyzes engagement metrics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def fetch_engagement_data(self, student_id: int) -> Dict[str, Any]:
        """
        Fetch engagement data for a student
        """
        try:
            # Get engagement logs for last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            engagement_logs = self.db.query(EngagementLog).filter(
                and_(
                    EngagementLog.student_id == student_id,
                    EngagementLog.timestamp >= thirty_days_ago
                )
            ).order_by(EngagementLog.timestamp.desc()).all()
            
            if not engagement_logs:
                return {
                    "status": "success",
                    "data": {
                        "total_activities": 0,
                        "login_count": 0,
                        "assignment_submissions": 0,
                        "daily_engagement": [],
                        "trend": "no_data"
                    }
                }
            
            # Calculate statistics
            total_activities = len(engagement_logs)
            login_count = sum(1 for log in engagement_logs if log.activity_type == "login")
            assignment_submissions = sum(1 for log in engagement_logs if log.activity_type == "assignment_submitted")
            video_watched = sum(1 for log in engagement_logs if log.activity_type == "video_watched")
            quiz_taken = sum(1 for log in engagement_logs if log.activity_type == "quiz_taken")
            
            # Group by activity type
            activity_breakdown = {}
            for log in engagement_logs:
                if log.activity_type not in activity_breakdown:
                    activity_breakdown[log.activity_type] = 0
                activity_breakdown[log.activity_type] += 1
            
            # Group by date for daily engagement
            daily_engagement = {}
            for log in engagement_logs:
                date_key = log.timestamp.date().isoformat()
                if date_key not in daily_engagement:
                    daily_engagement[date_key] = {
                        "date": date_key,
                        "activities": 0,
                        "logins": 0,
                        "assignments": 0
                    }
                daily_engagement[date_key]["activities"] += 1
                if log.activity_type == "login":
                    daily_engagement[date_key]["logins"] += 1
                if log.activity_type == "assignment_submitted":
                    daily_engagement[date_key]["assignments"] += 1
            
            daily_engagement_list = sorted(daily_engagement.values(), key=lambda x: x["date"], reverse=True)
            
            # Calculate trend (compare last 15 days to previous 15 days)
            fifteen_days_ago = datetime.now() - timedelta(days=15)
            
            recent_logs = [log for log in engagement_logs if log.timestamp >= fifteen_days_ago]
            previous_logs = [log for log in engagement_logs if log.timestamp < fifteen_days_ago]
            
            if recent_logs and previous_logs:
                recent_avg = len(recent_logs) / 15 if recent_logs else 0
                previous_avg = len(previous_logs) / 15 if previous_logs else 0
                
                if recent_avg > previous_avg:
                    trend = "improving"
                elif recent_avg < previous_avg:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            return {
                "status": "success",
                "data": {
                    "total_activities": total_activities,
                    "login_count": login_count,
                    "assignment_submissions": assignment_submissions,
                    "video_watched": video_watched,
                    "quiz_taken": quiz_taken,
                    "activity_breakdown": activity_breakdown,
                    "daily_engagement": daily_engagement_list[:30],  # Last 30 days
                    "trend": trend
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


class AnalysisAgent:
    """Analysis Agent: Merges data and generates insights using LLM reasoning"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_and_generate_insights(
        self,
        academic_data: Dict[str, Any],
        attendance_data: Dict[str, Any],
        engagement_data: Dict[str, Any],
        student_id: int
    ) -> Dict[str, Any]:
        """
        Analyze combined data and generate insights and alerts
        """
        insights = []
        alerts = []
        
        # Analyze academic performance
        if academic_data.get("status") == "success":
            academic = academic_data["data"]
            avg_score = academic.get("average_score", 0)
            
            if avg_score < 70:
                insights.append("⚠️ Academic performance is below average (below 70%)")
                alerts.append({
                    "type": "grade_drop",
                    "severity": "high",
                    "message": f"Average score is {avg_score:.1f}%, which is below the threshold of 70%"
                })
            elif avg_score < 80:
                insights.append("📊 Academic performance is satisfactory but could improve")
            else:
                insights.append("✅ Academic performance is strong")
            
            if academic.get("trend") == "declining":
                insights.append("📉 Academic performance is showing a declining trend")
                alerts.append({
                    "type": "grade_drop",
                    "severity": "medium",
                    "message": "Academic scores are declining compared to previous period"
                })
        
        # Analyze attendance
        if attendance_data.get("status") == "success":
            attendance = attendance_data["data"]
            attendance_pct = attendance.get("attendance_percentage", 0)
            
            if attendance_pct < 75:
                insights.append(f"⚠️ Attendance is below threshold ({attendance_pct:.1f}%)")
                alerts.append({
                    "type": "attendance_drop",
                    "severity": "high",
                    "message": f"Attendance is {attendance_pct:.1f}%, below the 75% threshold"
                })
            elif attendance_pct < 85:
                insights.append("📊 Attendance is acceptable but could be better")
            else:
                insights.append("✅ Attendance is excellent")
            
            if attendance.get("trend") == "declining":
                insights.append("📉 Attendance trend is declining")
                alerts.append({
                    "type": "attendance_drop",
                    "severity": "medium",
                    "message": "Attendance is showing a declining trend"
                })
        
        # Analyze engagement
        if engagement_data.get("status") == "success":
            engagement = engagement_data["data"]
            login_count = engagement.get("login_count", 0)
            assignments = engagement.get("assignment_submissions", 0)
            
            # Check for low engagement
            if login_count < 15:  # Less than 15 logins in 30 days
                insights.append("⚠️ Low LMS login activity detected")
                alerts.append({
                    "type": "engagement_drop",
                    "severity": "medium",
                    "message": f"Only {login_count} logins in the last 30 days"
                })
            
            if assignments < 5:  # Less than 5 assignment submissions
                insights.append("⚠️ Low assignment submission rate")
                alerts.append({
                    "type": "missing_assignment",
                    "severity": "medium",
                    "message": f"Only {assignments} assignments submitted in the last 30 days"
                })
            
            if engagement.get("trend") == "declining":
                insights.append("📉 Engagement is showing a declining trend")
                alerts.append({
                    "type": "engagement_drop",
                    "severity": "medium",
                    "message": "Engagement activity is declining compared to previous period"
                })
            
            if engagement.get("trend") == "improving":
                insights.append("✅ Engagement is improving")
        
        # Save alerts to database
        for alert_data in alerts:
            alert = Alert(
                student_id=student_id,
                alert_type=alert_data["type"],
                severity=alert_data["severity"],
                message=alert_data["message"]
            )
            self.db.add(alert)
        
        self.db.commit()
        
        # Generate overall summary
        overall_status = "good"
        if any(a.get("severity") in ["high", "critical"] for a in alerts):
            overall_status = "critical"
        elif any(a.get("severity") == "medium" for a in alerts):
            overall_status = "attention_needed"
        
        return {
            "overall_status": overall_status,
            "insights": insights,
            "alerts": alerts,
            "summary": self._generate_summary(academic_data, attendance_data, engagement_data)
        }
    
    def _generate_summary(
        self,
        academic_data: Dict[str, Any],
        attendance_data: Dict[str, Any],
        engagement_data: Dict[str, Any]
    ) -> str:
        """Generate a text summary of the student's performance"""
        summary_parts = []
        
        if academic_data.get("status") == "success":
            avg_score = academic_data["data"].get("average_score", 0)
            summary_parts.append(f"Academic average: {avg_score:.1f}%")
        
        if attendance_data.get("status") == "success":
            attendance_pct = attendance_data["data"].get("attendance_percentage", 0)
            summary_parts.append(f"Attendance: {attendance_pct:.1f}%")
        
        if engagement_data.get("status") == "success":
            login_count = engagement_data["data"].get("login_count", 0)
            summary_parts.append(f"LMS logins: {login_count}")
        
        return " | ".join(summary_parts) if summary_parts else "No data available"


