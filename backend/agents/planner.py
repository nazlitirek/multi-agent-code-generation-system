from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os
from pydantic import SecretStr
from typing import List

load_dotenv()

SYSTEM_PROMPT = """You are a product manager helping a developer finalize their project idea.
Ask ONE question at a time to understand: core purpose, users, auth, core features, data, UI style.
Also ask for the project name to name the directory early in the conversation.
the project name should be short.
After 4-6 questions, write a brief in this format:

---PROJECT BRIEF---
App Name: <name>
Project Slug: <lowercase-with-dashes, no special chars, e.g. task-manager-pro>
Description: <summary>
Users: <who>
Auth: <yes/no>
Core Features:
- <feature>
Tech Stack: React + FastAPI + PostgreSQL
---END BRIEF---

Then ask: "Does this match your vision? Type YES to confirm or tell me what to change."
Only write the brief when you have enough info. Start by asking the core purpose.
If the user says yes, end the conversation. If they say no, ask what to change and update the brief accordingly."""


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=SecretStr(api_key) if api_key else None,
        timeout=15
    )


def chat_with_planner(message: str, history: list[dict]) -> dict:
    llm = get_llm()

    messages: List[BaseMessage] = []
    messages.append(SystemMessage(content=SYSTEM_PROMPT))
    for item in history:
        if item["role"] == "user":
            messages.append(HumanMessage(content=item["content"]))
        else:
            messages.append(AIMessage(content=item["content"]))
    messages.append(HumanMessage(content=message))

    response = llm.invoke(messages)

    last_human = message.strip().upper()
    confirmed = last_human == "YES" and any(
        "---PROJECT BRIEF---" in item["content"]
        for item in history
        if item["role"] == "assistant"
    )

    brief = ""
    project_slug = ""
    if confirmed:
        for item in reversed(history):
            if item["role"] == "assistant" and "---PROJECT BRIEF---" in item["content"]:
                content = item["content"]
                start = content.find("---PROJECT BRIEF---")
                end = content.find("---END BRIEF---") + len("---END BRIEF---")
                brief = content[start:end]

                # Extract project slug
                for line in brief.split("\n"):
                    if line.startswith("Project Slug:"):
                        project_slug = line.replace("Project Slug:", "").strip()
                break

    return {
        "reply": response.content,
        "confirmed": confirmed,
        "brief": brief,
        "project_slug": project_slug
    }