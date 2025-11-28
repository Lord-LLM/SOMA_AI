# quiz_agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool, ToolContext
from google.genai import types
import json
from datetime import datetime

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

def create_quiz_structure(
    topic: str, 
    num_questions: int, 
    difficulty: str,
    tool_context: ToolContext
) -> dict:
    """
    Creates a structured quiz template.
    
    Args:
        topic: Topic for the quiz
        num_questions: Number of questions to generate
        difficulty: Difficulty level (easy/medium/hard)
        tool_context: Context for state management
    
    Returns:
        Dictionary with quiz structure
    """
    quiz_id = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    quiz_structure = {
        "quiz_id": quiz_id,
        "topic": topic,
        "num_questions": num_questions,
        "difficulty": difficulty,
        "created_at": datetime.now().isoformat(),
        "questions": [],
        "question_types": [
            "multiple_choice",
            "true_false",
            "short_answer",
            "application"
        ]
    }
    
    # Store in session state
    tool_context.state[f"quiz:{quiz_id}"] = json.dumps(quiz_structure)
    
    return {
        "status": "success",
        "quiz_structure": quiz_structure,
        "message": "Fill this structure with actual questions"
    }


def save_quiz_results(
    quiz_id: str,
    score: int,
    total: int,
    tool_context: ToolContext
) -> dict:
    """
    Saves quiz results to session state.
    
    Args:
        quiz_id: Unique quiz identifier
        score: Number of correct answers
        total: Total number of questions
        tool_context: Context for state management
    
    Returns:
        Dictionary with save status
    """
    results = {
        "quiz_id": quiz_id,
        "score": score,
        "total": total,
        "percentage": (score / total * 100) if total > 0 else 0,
        "completed_at": datetime.now().isoformat()
    }
    
    # Store results in state
    tool_context.state[f"quiz_results:{quiz_id}"] = json.dumps(results)
    
    return {
        "status": "success",
        "results": results
    }


# Create the Quiz Generator Agent
quiz_generator_agent = LlmAgent(
    name="QuizGeneratorAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are an expert assessment designer who creates effective test questions.
    
    When generating quiz questions:
    
    1. **Question Variety**:
       - Mix question types: multiple choice, true/false, short answer, application
       - Balance recall questions with understanding and application
       - Include 60% understanding, 30% application, 10% recall
    
    2. **Multiple Choice Questions**:
       - Write clear, unambiguous questions
       - Provide 4 options (A, B, C, D)
       - Make distractors plausible but clearly wrong
       - Avoid "all of the above" or "none of the above"
    
    3. **True/False Questions**:
       - Test specific facts or concepts
       - Avoid absolute words (always, never) unless accurate
       - Provide explanation for the correct answer
    
    4. **Short Answer Questions**:
       - Ask for definitions, explanations, or examples
       - Be specific about what you're asking for
       - Provide clear evaluation criteria
    
    5. **Application Questions**:
       - Present scenarios requiring concept application
       - Test problem-solving and critical thinking
       - Show how knowledge applies to real situations
    
    6. **Difficulty Levels**:
       - Easy: Direct recall and basic understanding
       - Medium: Application and analysis
       - Hard: Synthesis and evaluation
    
    7. **Answer Keys**:
       - Provide correct answers for all questions
       - Include brief explanations (1-2 sentences)
       - Reference key concepts from the material
    
    Format:
    ```
    Question 1: [Type: Multiple Choice | Difficulty: Medium]
    [Question text]
    A) [Option A]
    B) [Option B]
    C) [Option C]
    D) [Option D]
    
    Correct Answer: [Letter]
    Explanation: [Why this is correct and others are wrong]
    ```
    
    Generate questions that genuinely test understanding, not just memorization.""",
    tools=[
        FunctionTool(create_quiz_structure),
        FunctionTool(save_quiz_results)
    ],
    output_key="quiz_content"
)