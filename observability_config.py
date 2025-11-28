# observability_config.py - Logging and Monitoring Setup
import logging
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.runners import Runner
from session_config import study_companion_app, session_service

# Configure Python logging
logging.basicConfig(
    filename="study_companion.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("StudyCompanion")

# Create runner with LoggingPlugin for production observability
production_runner = Runner(
    app=study_companion_app,
    session_service=session_service,
    plugins=[
        LoggingPlugin()  # Automatic logging of all agent activities
    ]
)

# Custom logging helpers
def log_study_session_start(user_id: str, session_id: str, topic: str):
    """Log when a student starts a new study session."""
    logger.info(
        f"Study session started - User: {user_id}, Session: {session_id}, Topic: {topic}"
    )

def log_milestone_completion(user_id: str, milestone: str):
    """Log when a student completes a learning milestone."""
    logger.info(
        f"Milestone completed - User: {user_id}, Milestone: {milestone}"
    )

def log_quiz_result(user_id: str, quiz_id: str, score: int, total: int):
    """Log quiz performance."""
    percentage = (score / total * 100) if total > 0 else 0
    logger.info(
        f"Quiz completed - User: {user_id}, Quiz: {quiz_id}, Score: {score}/{total} ({percentage:.1f}%)"
    )

def log_error(user_id: str, error_type: str, error_message: str):
    """Log errors for debugging."""
    logger.error(
        f"Error occurred - User: {user_id}, Type: {error_type}, Message: {error_message}"
    )

# Enhanced session runner with logging
async def run_logged_study_session(
    user_id: str,
    session_id: str,
    user_query: str,
    log_topic: str = None
):
    """
    Run study session with comprehensive logging.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        user_query: User's query
        log_topic: Optional topic for logging
    
    Returns:
        Agent's response
    """
    from google.genai import types
    
    try:
        # Log session start
        if log_topic:
            log_study_session_start(user_id, session_id, log_topic)
        
        # Create or retrieve session
        try:
            session = await session_service.create_session(
                app_name="study_companion_app",
                user_id=user_id,
                session_id=session_id
            )
            logger.info(f"New session created: {session_id}")
        except:
            session = await session_service.get_session(
                app_name="study_companion_app",
                user_id=user_id,
                session_id=session_id
            )
            logger.info(f"Existing session retrieved: {session_id}")
        
        # Create user message
        user_content = types.Content(
            role="user",
            parts=[types.Part(text=user_query)]
        )
        
        logger.info(f"User query: {user_query[:100]}...")
        
        # Run agent with logging
        responses = []
        async for event in production_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        responses.append(part.text)
        
        final_response = "\n".join(responses)
        logger.info(f"Response generated successfully, length: {len(final_response)} chars")
        
        return final_response
    
    except Exception as e:
        log_error(user_id, "SessionError", str(e))
        return f"An error occurred: {str(e)}. Please try again."


# Example: Running with observability
"""
response = await run_logged_study_session(
    user_id="student_123",
    session_id="python_basics_jan2024",
    user_query="Help me learn Python basics",
    log_topic="Python Programming"
)

# Check logs at: study_companion.log
# Monitor with: tail -f study_companion.log
"""