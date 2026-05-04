from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os
from pydantic import SecretStr
from typing import List

load_dotenv()

SYSTEM_PROMPT = """You are a product manager helping a developer finalize their project idea.
Ask ONE question at a time to understand: core purpose, users, auth, core features, data, UI style.
After 4-6 questions, write a brief in this format:

---PROJECT BRIEF---
App Name: <name>
Description: <summary>
Users: <who>
Auth: <yes/no>
Core Features:
- <feature>
Tech Stack: React + FastAPI + PostgreSQL
---END BRIEF---

Then ask: "Does this match your vision? Type YES to confirm or tell me what to change."
Only write the brief when you have enough info. Start by asking the core purpose."""


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=SecretStr(api_key) if api_key else None,
        timeout=15
    )


def chat_with_planner(message: str, history: list[dict]) -> dict:
    llm = get_llm()

    messages: List[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
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
    if confirmed:
        for item in reversed(history):
            if item["role"] == "assistant" and "---PROJECT BRIEF---" in item["content"]:
                content = item["content"]
                start = content.find("---PROJECT BRIEF---")
                end = content.find("---END BRIEF---") + len("---END BRIEF---")
                brief = content[start:end]
                break

    return {
        "reply": response.content,
        "confirmed": confirmed,
        "brief": brief
    }