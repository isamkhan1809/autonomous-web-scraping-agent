import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agent.executor import WebScrapingAgent

load_dotenv()

app = FastAPI(title="Autonomous Web Scraping Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    goal: str
    max_steps: int = 10


@app.get("/health")
async def health():
    return {"status": "ok", "service": "autonomous-web-scraping-agent"}


@app.post("/run")
async def run_agent(request: RunRequest):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set in environment")

    if not request.goal or not request.goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty")

    # Cap max_steps at 20
    max_steps = min(request.max_steps, 20)

    agent = WebScrapingAgent(anthropic_api_key=api_key)
    result = await agent.run(goal=request.goal.strip(), max_steps=max_steps)
    return result
