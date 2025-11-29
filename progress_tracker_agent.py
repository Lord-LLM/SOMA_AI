# progress_tracker_agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool, ToolContext
from google.genai import types
import json
from datetime import datetime, timedelta

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

def track_milestone_completion(
    roadmap_id: str,
    milestone_name: str,
    status: str,
    tool_context: ToolContext
) -> dict:
    """
    Tracks completion status of learning milestones.
    
    Args:
        roadmap_id: Identifier for the learning roadmap
        milestone_name: Name of the milestone
        status: Status (completed/in_progress/not_started)
        tool_context: Context for state management
    
    Returns:
        Dictionary with tracking status
    """
    key = f"progress:{roadmap_id}"
    
    # Retrieve existing progress or create new
    existing_progress = tool_context.state.get(key)
    if existing_progress:
        progress_data = json.loads(existing_progress)
    else:
        progress_data = {
            "roadmap_id": roadmap_id,
            "milestones": {},
            "started_at": datetime.now().isoformat()
        }
    
    # Update milestone
    progress_data["milestones"][milestone_name] = {
        "status": status,
        "updated_at": datetime.now().isoformat()
    }
    
    # Calculate overall progress
    total_milestones = len(progress_data["milestones"])
    completed = sum(1 for m in progress_data["milestones"].values() if m["status"] == "completed")
    progress_data["completion_percentage"] = (completed / total_milestones * 100) if total_milestones > 0 else 0
    
    # Store updated progress
    tool_context.state[key] = json.dumps(progress_data)
    
    return {
        "status": "success",
        "progress_data": progress_data
    }


def schedule_reminder(
    reminder_message: str,
    reminder_date: str,
    tool_context: ToolContext
) -> dict:
    """
    Schedules a study reminder notification.
    
    Args:
        reminder_message: Message for the reminder
        reminder_date: Date for reminder (YYYY-MM-DD format)
        tool_context: Context for state management
    
    Returns:
        Dictionary with reminder details
    """
    reminder_id = f"reminder_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    reminder = {
        "reminder_id": reminder_id,
        "message": reminder_message,
        "scheduled_date": reminder_date,
        "created_at": datetime.now().isoformat(),
        "status": "scheduled"
    }
    
    # Store reminder
    tool_context.state[f"reminder:{reminder_id}"] = json.dumps(reminder)
    
    # Add to reminders list
    reminders_key = "all_reminders"
    existing_reminders = tool_context.state.get(reminders_key)
    if existing_reminders:
        reminders_list = json.loads(existing_reminders)
    else:
        reminders_list = []
    
    reminders_list.append(reminder_id)
    tool_context.state[reminders_key] = json.dumps(reminders_list)
    
    return {
        "status": "success",
        "reminder": reminder
    }


def get_progress_report(
    roadmap_id: str,
    tool_context: ToolContext
) -> dict:
    """
    Generates a progress report for a learning roadmap.
    
    Args:
        roadmap_id: Identifier for the learning roadmap
        tool_context: Context for state management
    
    Returns:
        Dictionary with progress report
    """
    key = f"progress:{roadmap_id}"
    progress_data = tool_context.state.get(key)
    
    if not progress_data:
        return {
            "status": "error",
            "error_message": "No progress data found for this roadmap"
        }
    
    progress = json.loads(progress_data)
    
    # Calculate statistics
    milestones = progress.get("milestones", {})
    completed = [m for m, data in milestones.items() if data["status"] == "completed"]
    in_progress = [m for m, data in milestones.items() if data["status"] == "in_progress"]
    not_started = [m for m, data in milestones.items() if data["status"] == "not_started"]
    
    report = {
        "roadmap_id": roadmap_id,
        "total_milestones": len(milestones),
        "completed": len(completed),
        "in_progress": len(in_progress),
        "not_started": len(not_started),
        "completion_percentage": progress.get("completion_percentage", 0),
        "started_at": progress.get("started_at"),
        "completed_milestones": completed,
        "current_milestones": in_progress,
        "upcoming_milestones": not_started
    }
    
    return {
        "status": "success",
        "report": report
    }


# Progress Tracker Agent
progress_tracker_agent = LlmAgent(
    name="ProgressTrackerAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are a dedicated study progress monitor and motivational coach.
    
    Your responsibilities:
    
    1. **Track Completion**:
       - Use track_milestone_completion to record when students finish modules
       - Update status: completed, in_progress, or not_started
       - Monitor overall progress percentage
    
    2. **Generate Progress Reports**:
       - Use get_progress_report to show current status
       - Highlight completed achievements
       - Show what's currently in progress
       - List upcoming milestones
    
    3. **Schedule Reminders**:
       - Use schedule_reminder for upcoming study sessions
       - Set reminders for milestone deadlines
       - Send encouragement messages at key points
       - Remind about review sessions
    
    4. **Motivational Support**:
       - Celebrate completed milestones
       - Provide encouragement for challenges
       - Suggest adjustments if falling behind
       - Recognize consistent effort
    
    5. **Smart Notifications**:
       - Daily: Reminder of today's study goal
       - Weekly: Progress summary and next week preview
       - Milestone: Completion celebration and next steps
       - Warning: If milestone deadline approaching with incomplete work
    
    When reporting progress:
    - Show visual progress indicators (percentages, completed/total)
    - Be specific about what's been accomplished
    - Give clear next steps
    - Be encouraging and supportive
    
    Format progress updates clearly with:
    - ✅ Completed items
    - 🔄 In progress items
    - 📅 Upcoming items
    - 🎯 Overall progress percentage""",
    tools=[
        FunctionTool(track_milestone_completion),
        FunctionTool(schedule_reminder),
        FunctionTool(get_progress_report)
    ],
    output_key="progress_update"
)