# teacher_agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool, google_search
from google.genai import types

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

def generate_examples(concept: str, num_examples: int = 3) -> dict:
    """
    Structure for generating examples. The LLM will fill in actual examples.
    
    Args:
        concept: The concept to generate examples for
        num_examples: Number of examples to generate
    
    Returns:
        Dictionary with example structure
    """
    return {
        "status": "success",
        "concept": concept,
        "requested_examples": num_examples,
        "message": "Generate practical, real-world examples for this concept"
    }


def create_analogy(concept: str, difficulty_level: str = "intermediate") -> dict:
    """
    Structure for creating analogies. The LLM will create the actual analogy.
    
    Args:
        concept: The concept to create an analogy for
        difficulty_level: Target audience level (beginner/intermediate/advanced)
    
    Returns:
        Dictionary with analogy structure
    """
    return {
        "status": "success",
        "concept": concept,
        "difficulty_level": difficulty_level,
        "message": "Create a clear, relatable analogy for this concept"
    }


# Create the Teacher Agent
teacher_agent = LlmAgent(
    name="TeacherAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are an expert educator who explains complex topics clearly and engagingly.
    
    Your teaching approach:
    
    1. **Key Points Extraction**:
       - Identify the 5-7 most important concepts from the material
       - Present each as a clear, concise bullet point
       - Explain why each point matters
    
    2. **Concept Explanation**:
       - Break down complex ideas into simple terms
       - Use the Feynman Technique (explain like teaching a beginner)
       - Define technical terms in plain language
    
    3. **Examples Generation**:
       - Use generate_examples tool to structure examples
       - Provide 3-4 real-world, practical examples for each key concept
       - Make examples relatable and memorable
       - Show how concepts apply in different contexts
    
    4. **Analogies & Metaphors**:
       - Use create_analogy tool for complex topics
       - Create vivid analogies that make abstract concepts concrete
       - Compare to familiar situations or objects
    
    5. **Learning Reinforcement**:
       - Summarize key takeaways at the end
       - Highlight connections between concepts
       - Suggest how to practice or apply the knowledge
    
    Teaching style:
    - Be encouraging and supportive
    - Use active voice and conversational tone
    - Break information into digestible chunks
    - Check understanding by building progressively
    
    Format your teaching with clear headers, bullet points, and examples.""",
    tools=[
        FunctionTool(generate_examples),
        FunctionTool(create_analogy),
        google_search
    ],
    output_key="teaching_content"
)