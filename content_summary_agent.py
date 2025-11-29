# content_summary_agent.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import PyPDF2
import io

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# Tool Functions 

def fetch_webpage_content(url: str) -> dict:
    """
    Fetches and extracts main content from a webpage.
    
    Args:
        url: The webpage URL to fetch
    
    Returns:
        Dictionary with status and extracted text content
    """
    try:
        # Add headers to mimic a browser 
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit to first 10000 characters to avoid token limits
        text = text[:10000]
        
        return {
            "status": "success",
            "content": text,
            "source": url
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to fetch webpage: {str(e)}"
        }

def fetch_youtube_transcript(video_url: str) -> dict:
    """
    Fetches transcript from a YouTube video.
    
    Args:
        video_url: YouTube video URL (e.g., https://youtube.com/watch?v=VIDEO_ID)
    
    Returns:
        Dictionary with status and transcript text
    """
    try:
        # Extract video ID from URL
        if "youtube.com/watch?v=" in video_url:
            video_id = video_url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        else:
            return {
                "status": "error",
                "error_message": "Invalid YouTube URL format"
            }
        
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item['text'] for item in transcript_list])
        
        # Limit length
        transcript_text = transcript_text[:10000]
        
        return {
            "status": "success",
            "content": transcript_text,
            "source": video_url
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to fetch transcript: {str(e)}"
        }

def process_pdf_text(pdf_content_base64: str) -> dict:
    """
    Processes PDF content and extracts text.
    
    Args:
        pdf_content_base64: Base64 encoded PDF content
    
    Returns:
        Dictionary with status and extracted text
    """
    try:
        import base64
        pdf_bytes = base64.b64decode(pdf_content_base64)
        pdf_file = io.BytesIO(pdf_bytes)
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        # Extract text from all pages
        for page_num in range(min(50, len(pdf_reader.pages))):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        
        # Limit length
        text = text[:10000]
        
        return {
            "status": "success",
            "content": text,
            "source": "uploaded_pdf"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to process PDF: {str(e)}"
        }

#  Agent Configuration 



content_summary_agent = LlmAgent(
    name="ContentSummaryAgent",
    
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are a specialized content summarization expert for students.
    
    When given content from any source (webpage, video, blog, book):
    1. Use the appropriate tool to fetch the content
    2. Create a comprehensive summary with these sections:
       - **Main Topics**: List 3-5 key topics covered
       - **Key Points**: Bullet points of essential information (8-12 points)
       - **Important Concepts**: Define and explain core concepts
       - **Practical Applications**: How this knowledge can be applied
       - **Summary**: 2-3 paragraph overview
    
    Format your summary clearly with markdown headers.
    Be concise but thorough. Focus on educational value.""",
    tools=[
        fetch_webpage_content,
        fetch_youtube_transcript,
        process_pdf_text,
        #google_search
    ],
    output_key="content_summary"
)