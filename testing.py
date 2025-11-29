import asyncio
import os
from dotenv import load_dotenv 

load_dotenv() 

from google.adk.runners import InMemoryRunner
from content_summary_agent import content_summary_agent

async def main():
    runner = InMemoryRunner(agent=content_summary_agent)
    response = await runner.run_debug("Summarize: https://en.wikipedia.org/wiki/Machine_learning")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())