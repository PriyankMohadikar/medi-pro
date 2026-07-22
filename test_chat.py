import sys
import asyncio
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path("backend").absolute()))

from backend.chat_router import chat_endpoint, ChatRequest
from fastapi import HTTPException

request = ChatRequest(message="Compare Vitamin D across providers", history=[])
async def main():
    try:
        response = chat_endpoint(request)
        print("SUCCESS:")
        async for chunk in response.body_iterator:
            print(chunk, end='', flush=True)
        print("\nDONE")
    except HTTPException as e:
        print(f"HTTPException: {e.status_code} - {e.detail}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
