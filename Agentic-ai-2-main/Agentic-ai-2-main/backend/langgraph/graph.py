"""
LangGraph Orchestration: Coordinates multiple agents to fetch and analyze student data
"""
from typing import Dict, Any, TypedDict
from sqlalchemy.orm import Session

# Try to import LangGraph, fallback to simple orchestration
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: LangGraph not available, using simple orchestration")

# Import agents
from langgraph.agents import AcademicProgressAgent, AttendanceAgent, EngagementAgent, AnalysisAgent


class GraphState(TypedDict):
    """State structure for LangGraph"""
    student_id: int
    db_session: Session
    academic_data: Dict[str, Any]
    attendance_data: Dict[str, Any]
    engagement_data: Dict[str, Any]
    analysis: Dict[str, Any]
    errors: list


def fetch_academic_node(state: GraphState) -> GraphState:
    """Node: Fetch academic progress data (Agent-A)"""
    try:
        agent = AcademicProgressAgent(state["db_session"])
        academic_data = agent.fetch_academic_data(state["student_id"])
        return {
            **state,
            "academic_data": academic_data
        }
    except Exception as e:
        return {
            **state,
            "academic_data": {"status": "error", "error": str(e)},
            "errors": state.get("errors", []) + [f"Academic agent error: {str(e)}"]
        }


def fetch_attendance_node(state: GraphState) -> GraphState:
    """Node: Fetch attendance data (Agent-B)"""
    try:
        agent = AttendanceAgent(state["db_session"])
        attendance_data = agent.fetch_attendance_data(state["student_id"])
        return {
            **state,
            "attendance_data": attendance_data
        }
    except Exception as e:
        return {
            **state,
            "attendance_data": {"status": "error", "error": str(e)},
            "errors": state.get("errors", []) + [f"Attendance agent error: {str(e)}"]
        }


def fetch_engagement_node(state: GraphState) -> GraphState:
    """Node: Fetch engagement data (Agent-C)"""
    try:
        agent = EngagementAgent(state["db_session"])
        engagement_data = agent.fetch_engagement_data(state["student_id"])
        return {
            **state,
            "engagement_data": engagement_data
        }
    except Exception as e:
        return {
            **state,
            "engagement_data": {"status": "error", "error": str(e)},
            "errors": state.get("errors", []) + [f"Engagement agent error: {str(e)}"]
        }


def analyze_node(state: GraphState) -> GraphState:
    """Node: Analyze and generate insights (Analysis Agent)"""
    try:
        agent = AnalysisAgent(state["db_session"])
        analysis = agent.analyze_and_generate_insights(
            state.get("academic_data", {}),
            state.get("attendance_data", {}),
            state.get("engagement_data", {}),
            state["student_id"]
        )
        return {
            **state,
            "analysis": analysis
        }
    except Exception as e:
        return {
            **state,
            "analysis": {"status": "error", "error": str(e)},
            "errors": state.get("errors", []) + [f"Analysis agent error: {str(e)}"]
        }


def create_student_dashboard_graph():
    """
    Create and compile the LangGraph for student dashboard data aggregation
    """
    if not LANGGRAPH_AVAILABLE:
        return None
    
    # Create state graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("fetch_academic", fetch_academic_node)
    workflow.add_node("fetch_attendance", fetch_attendance_node)
    workflow.add_node("fetch_engagement", fetch_engagement_node)
    workflow.add_node("analyze", analyze_node)
    
    # Set entry point - run all three agents sequentially
    workflow.set_entry_point("fetch_academic")
    workflow.add_edge("fetch_academic", "fetch_attendance")
    workflow.add_edge("fetch_attendance", "fetch_engagement")
    workflow.add_edge("fetch_engagement", "analyze")
    workflow.add_edge("analyze", END)
    
    # Compile graph
    app = workflow.compile()
    
    return app


def run_simple_orchestration(student_id: int, db_session: Session) -> Dict[str, Any]:
    """
    Simple orchestration without LangGraph (fallback)
    Executes agents sequentially
    """
    state: Dict[str, Any] = {
        "student_id": student_id,
        "db_session": db_session,
        "academic_data": {},
        "attendance_data": {},
        "engagement_data": {},
        "analysis": {},
        "errors": []
    }
    
    # Execute agents sequentially
    state = fetch_academic_node(state)
    state = fetch_attendance_node(state)
    state = fetch_engagement_node(state)
    state = analyze_node(state)
    
    return {
        "student_id": student_id,
        "academic": state.get("academic_data", {}),
        "attendance": state.get("attendance_data", {}),
        "engagement": state.get("engagement_data", {}),
        "analysis": state.get("analysis", {}),
        "errors": state.get("errors", [])
    }


def run_dashboard_graph(student_id: int, db_session: Session) -> Dict[str, Any]:
    """
    Execute the LangGraph orchestration for student dashboard
    
    Args:
        student_id: Student ID to fetch data for
        db_session: Database session
        
    Returns:
        Dictionary containing all aggregated data and insights
    """
    # Try to use LangGraph if available
    if LANGGRAPH_AVAILABLE:
        try:
            graph = create_student_dashboard_graph()
            
            # Initial state
            initial_state: GraphState = {
                "student_id": student_id,
                "db_session": db_session,
                "academic_data": {},
                "attendance_data": {},
                "engagement_data": {},
                "analysis": {},
                "errors": []
            }
            
            # Run graph
            final_state = graph.invoke(initial_state)
            
            # Compile response
            return {
                "student_id": student_id,
                "academic": final_state.get("academic_data", {}),
                "attendance": final_state.get("attendance_data", {}),
                "engagement": final_state.get("engagement_data", {}),
                "analysis": final_state.get("analysis", {}),
                "errors": final_state.get("errors", [])
            }
        except Exception as e:
            # Fallback to simple orchestration if LangGraph fails
            print(f"LangGraph execution failed: {e}, falling back to simple orchestration")
            return run_simple_orchestration(student_id, db_session)
    else:
        # Use simple orchestration
        return run_simple_orchestration(student_id, db_session)

