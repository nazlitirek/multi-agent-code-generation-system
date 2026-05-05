from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from pydantic import SecretStr
from utils.file_writer import write_files
import os
import json
import re

load_dotenv()

SYSTEM_PROMPT = """You are a software architect. Given a project brief, generate a detailed project architecture.

You MUST respond with ONLY a valid JSON object, no extra text, no markdown, no backticks.

The JSON must follow this exact structure:
{
  "project_name": "my-app",
  "files": [
    {
      "path": "backend/database.py",
      "description": "SQLAlchemy database connection setup"
    },
    {
      "path": "backend/models/user.py",
      "description": "User SQLAlchemy model"
    },
    {
      "path": "backend/routes/auth.py",
      "description": "Authentication endpoints"
    },
    {
      "path": "frontend/src/pages/Home.jsx",
      "description": "Home page component"
    }
  ],
  "db_schema": [
    {
      "table": "users",
      "fields": [
        {"name": "id", "type": "UUID", "primary_key": true},
        {"name": "email", "type": "VARCHAR(255)", "unique": true},
        {"name": "password_hash", "type": "VARCHAR(255)"},
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
}

Always include these base files:
- backend/main.py
- backend/database.py
- backend/requirements.txt
- backend/.env.example
- frontend/package.json
- frontend/src/main.jsx
- frontend/src/App.jsx
- docker-compose.yml
- README.md"""


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(
      
        model="llama-3.1-8b-instant",
        api_key= SecretStr(api_key) if api_key else None,
        timeout=30
    )


def generate_architecture(brief: str) -> dict:
    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Generate architecture for this project:\n\n{brief}")
    ]

    response = llm.invoke(messages)
    content = ""
    def extract_text(value):
        if isinstance(value, list):
            return "".join(str(item) for item in value).strip()
        return str(value).strip()

    try:
        content = extract_text(response.content)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        architecture = json.loads(content)
    except json.JSONDecodeError:
        try:
            fixed = re.sub(r'\],(\s*"api_endpoints_needed")', r'},\1', content)
            fixed = re.sub(r'\],(\s*\})', r'},\1', fixed)
            architecture = json.loads(fixed)
        except json.JSONDecodeError:
            fix_messages = [
                SystemMessage(content="Fix this invalid JSON. Return ONLY the fixed JSON, no extra text, no backticks."),
                HumanMessage(content=content)
            ]
            fix_response = llm.invoke(fix_messages)
            try:
                architecture = json.loads(extract_text(fix_response.content))
            except json.JSONDecodeError:
                return {"error": "Failed to parse architecture JSON", "raw": response.content}

    return {
        "architecture": architecture,
        "raw": response.content
    }


def save_architecture(project_name: str, architecture: dict) -> dict:
    files = [
        {
            "path": "architecture.json",
            "content": json.dumps(architecture, indent=2)
        }
    ]
    return write_files(project_name, files)