import os
import requests
from dotenv import load_dotenv

load_dotenv()

LYZR_API_KEY = os.getenv("LYZR_API_KEY")
AGENT_ID = os.getenv("LYZR_AGENT_ID")

API_URL = "https://agent-prod.studio.lyzr.ai/v3/inference/chat/"

def ask_ai_agent(message: str, user_id: str, session_id: str) -> str:
    """
    Sends a query to the Lyzr AI agent and returns response
    """

    if not LYZR_API_KEY:
        return "AI service is not configured properly."

    payload = {
        "user_id": user_id,
        "agent_id": AGENT_ID,
        "session_id": session_id,
        "message": message
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": LYZR_API_KEY
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response from AI agent.")
        else:
            return f"AI Error: {response.status_code}"

    except Exception as e:
        return f"AI connection failed: {str(e)}"
