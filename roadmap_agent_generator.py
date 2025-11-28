# roadmap_agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool, google_search
from google.genai import types
from datetime import datetime, timedelta
import json

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

def create_learning_schedule(topic: str, days_available: int, hours_per_day: int) -> dict:
    """
    Creates a structured learning schedule for a topic.
    
    Args:
        topic: The subject or topic to learn
        days_available: Number of days available for studying
        hours_per_day: Hours per day available for studying
    
    Returns:
        Dictionary with schedule structure
    """
    try:
        total_hours = days_available * hours_per_day
        start_date = datetime.now()
        
        # Create milestone structure
        schedule = {
            "topic": topic,
            "total_duration_days": days_available,
            "hours_per_day": hours_per_day,
            "total_hours": total_hours,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "estimated_completion": (start_date + timedelta(days=days_available)).strftime("%Y-%m-%d"),
            "milestones": []
        }
        
        return {
            "status": "success",
            "schedule": schedule
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create schedule: {str(e)}"
        }


def break_down_topic(topic: str) -> dict:
    """
    Breaks down a topic into subtopics and learning objectives.
    This is a structured template - the LLM will fill in the details.
    
    Args:
        topic: The main topic to break down
    
    Returns:
        Dictionary with breakdown structure
    """
    breakdown = {
        "main_topic": topic,
        "subtopics": [],
        "prerequisites": [],
        "learning_objectives": [],
        "difficulty_level": "intermediate"
    }
    
    return {
        "status": "success",
        "breakdown": breakdown,
        "message": "Use this structure to fill in the breakdown details"
    }


# Create the Roadmap Agent
roadmap_agent = LlmAgent(
    name="RoadmapAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are an expert learning path designer and curriculum planner.
    
    When given a topic or subject, create a comprehensive learning roadmap:
    
    1. **Topic Analysis**:
       - Use google_search to research the topic scope and industry standards
       - Identify prerequisites and foundational knowledge needed
       - Determine appropriate difficulty level
    
    2. **Roadmap Structure**:
       - Break the topic into 5-8 logical subtopics/modules
       - Order them from foundational to advanced
       - Estimate time for each module (in hours)
    
    3. **Learning Milestones**:
       - Define clear learning objectives for each module
       - Suggest checkpoints for self-assessment
       - Include practical projects or exercises
    
    4. **Study Schedule**:
       - Use create_learning_schedule to generate timeline
       - Distribute topics across available days
       - Include review and practice sessions
    
    5. **Resources**:
       - Suggest types of resources for each module
       - Recommend learning methods (reading, practice, projects)
    
    Format the roadmap as a clear, actionable study plan with dates and goals.
    Be realistic about time estimates and learning pace.""",
    tools=[
        FunctionTool(create_learning_schedule),
        FunctionTool(break_down_topic),
        google_search
    ],
    output_key="learning_roadmap"
)