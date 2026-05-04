from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import json

from pydantic import Secret, SecretStr

from pydantic import Secret

load_dotenv()

SYSTEM_PROMPT = """You are an API architect. Given a project architecture, generate a formal OpenAPI 3.0 specification.

You MUST respond with ONLY a valid JSON object, no extra text, no markdown, no backticks.

The JSON must follow this exact structure:
{
  "openapi": "3.0.0",
  "info": {
    "title": "<app name>",
    "version": "1.0.0"
  },
  "paths": {
    "/auth/register": {
      "post": {
        "summary": "Register a new user",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "email": {"type": "string"},
                  "password": {"type": "string"}
                },
                "required": ["email", "password"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "token": {"type": "string"}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

Generate ALL endpoints from the architecture. Be thorough with request/response schemas."""


def get_llm():
    
    api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=SecretStr(api_key) if api_key else None,
        timeout=30
    )


def generate_api_contract(architecture: dict) -> dict:
    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Generate OpenAPI spec for this architecture:\n\n{json.dumps(architecture, indent=2)}")
    ]

    response = llm.invoke(messages)

    raw_content = response.content
    if isinstance(raw_content, list):
        content = "".join(
            item if isinstance(item, str) else json.dumps(item)
            for item in raw_content
        )
    elif isinstance(raw_content, dict):
        content = json.dumps(raw_content)
    else:
        content = raw_content

    try:
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        contract = json.loads(content)
    except json.JSONDecodeError:
        contract = {"raw": raw_content, "parse_error": True}

    return {
        "contract": contract,
        "raw": response.content
    }