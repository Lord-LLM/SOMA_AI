# session_config.py - Session and Memory Configuration
from google.adk.sessions import DatabaseSessionService
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.runners import Runner
from agent import root_agent

# Configure persistent session storage using SQLite
# In production, use PostgreSQL or other enterprise database
session_service = DatabaseSessionService(
    db_url="sqlite:///study_companion.db"
)

# Wrap agent in App with memory management
study_companion_app = App(
    name="study_companion_app",
    root_agent=root_agent,
    # Enable context compaction to manage conversation length
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=5,  # Compact every 5 turns
        overlap_size=2  # Keep last 2 turns for context
    )
)

# Create runner with session management
runner = Runner(
    app=study_companion_app,
    session_service=session_service
)

# Helper function to run study sessions
async def run_study_session(user_id: str, session_id: str, user_query: str):
    """
    Runs a study session with the AI companion.
    
    Args:
        user_id: Unique identifier for the user
        session_id: Unique identifier for this study session
        user_query: The user's question or request
    
    Returns:
        Agent's response
    """
    from google.genai import types
    
    # Create or retrieve session
    try:
        session = await session_service.create_session(
            app_name="study_companion_app",
            user_id=user_id,
            session_id=session_id
        )
    except:
        session = await session_service.get_session(
            app_name="study_companion_app",
            user_id=user_id,
            session_id=session_id
        )
    
    # Create user message
    user_content = types.Content(
        role="user",
        parts=[types.Part(text=user_query)]
    )
    
    # Run agent and collect response
    responses = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    responses.append(part.text)
    
    return "\n".join(responses)


# Example usage patterns:
"""
# Pattern 1: Start new study session
response = await run_study_session(
    user_id="student_123",
    session_id="ml_learning_2024",
    user_query="Help me learn Machine Learning from scratch. I have 30 days and can study 2 hours per day."
)

# Pattern 2: Continue existing session
response = await run_study_session(
    user_id="student_123",
    session_id="ml_learning_2024",
    user_query="I finished Day 1. Show my progress and give me Day 2 plan."
)

# Pattern 3: Summarize content
response = await run_study_session(
    user_id="student_123",
    session_id="ml_learning_2024",
    user_query="Summarize this article: https://towardsdatascience.com/introduction-to-neural-networks"
)

# Pattern 4: Request teaching
response = await run_study_session(
    user_id="student_123",
    session_id="ml_learning_2024",
    user_query="Teach me about gradient descent with examples"
)

# Pattern 5: Generate quiz
response = await run_study_session(
    user_id="student_123",
    session_id="ml_learning_2024",
    user_query="Create a 10-question quiz on supervised learning"
)
"""