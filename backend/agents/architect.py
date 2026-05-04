from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import json

from pydantic import SecretStr

load_dotenv()

SYSTEM_PROMPT = """You are a software architect. Given a project brief, generate a detailed architecture.

You MUST respond with ONLY a valid JSON object, no extra text, no markdown, no backticks.

The JSON must follow this exact structure:
{
  "folder_structure": {
    "frontend": {
      "src": {
        "components": [],
        "pages": [],
        "hooks": [],
        "utils": []
      }
    },
    "backend": {
      "routes": [],
      "models": [],
      "schemas": [],
      "utils": []
    }
  },
  "db_schema": [
    {
      "table": "users",
      "fields": [
        {"name": "id", "type": "UUID", "primary_key": true},
        {"name": "email", "type": "VARCHAR(255)", "unique": true},
        {"name": "created_at", "type": "TIMESTAMP"}
      ]
    }
  ],
  "tech_decisions": {
    "auth": "JWT",
    "database": "PostgreSQL",
    "styling": "TailwindCSS",
    "state_management": "React useState/useContext"
  },
  "api_endpoints_needed": [
    {"method": "POST", "path": "/auth/register", "description": "Register new user"},
    {"method": "POST", "path": "/auth/login", "description": "Login user"}
  ]
}"""


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=SecretStr(api_key) if api_key else None,
        timeout=30
    )


def generate_architecture(brief: str) -> dict:
    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Generate architecture for this project:\n\n{brief}")
    ]

    response = llm.invoke(messages)

    def _extract_content(value):
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return _extract_content(value.get("content", ""))
        if isinstance(value, list):
            return "".join(_extract_content(item) for item in value)
        return str(value)

    try:
        # Clean response in case model adds backticks


        content = _extract_content(response.content).strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        architecture = json.loads(content)
    except json.JSONDecodeError:
        architecture = {"raw": response.content, "parse_error": True}

    return {
        "architecture": architecture,
        "raw": response.content
    }