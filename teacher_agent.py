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
    return {
        "status": "success",
        "concept": concept,
        "requested_examples": num_examples,
        "message": "Generate practical, real-world examples for this concept"
    }

def create_analogy(concept: str, difficulty_level: str = "intermediate") -> dict:
    return {
        "status": "success",
        "concept": concept,
        "difficulty_level": difficulty_level,
        "message": "Create a clear, relatable analogy for this concept"
    }

# Strict output template
OUTPUT_TEMPLATE = """
# 📘 Concept Breakdown: {{concept}}

##  Key Points (5–7)
- ...
- ...
- ...
- ...
- ...
(Explain why each point matters)

---

## Detailed Explanation
(Short, digestible explanations using simple language)

---

##  Real-World Examples
(At least 3–4 examples from generate_examples tool)
- Example 1: ...
- Example 2: ...
- Example 3: ...
- Example 4 (optional): ...

---

##  Analogy  
(Create a clear everyday analogy using create_analogy tool)

---

## Summary / Key Takeaways  
- ...
- ...
- ...

---

##  Check-Your-Understanding Questions  
(Always include this section even if the user does not ask)
1. ...
2. ...
3. ...
4. ...
"""

# Teacher agent
teacher_agent = LlmAgent(
    name="TeacherAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),

    instruction="""
You are an expert educator who explains complex topics clearly and engagingly.

Follow this teaching approach:

1. Extract 5–7 key points and explain why they matter.
2. Break concepts down simply using the Feynman Technique.
3. Use the generate_examples tool to structure examples.
4. Use create_analogy to make explanations concrete and relatable.
5. Summarize with clear takeaways.
6. ALWAYS include a 'Check-Your-Understanding Questions' section at the end.
7. Follow the provided output template EXACTLY.

Your tone:
- Clear, friendly, encouraging
- Structured and highly organized
- Use headers, lists, spacing
""",

    tools=[
        FunctionTool(generate_examples),
        FunctionTool(create_analogy),
        google_search
    ],

    # Force the model to follow the complete structure
    output_format=OUTPUT_TEMPLATE,

    output_key="teaching_content"
)
