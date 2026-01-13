from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
from dotenv import load_dotenv

from src.html_optimizer import HTMLOptimizer
from src.action_generator import ActionGenerator
from src.config import Settings

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("webagent")

app = FastAPI(title="WebAgent", version="1.0.0")
settings = Settings()

html_optimizer = HTMLOptimizer(settings)
action_generator = ActionGenerator(settings)

class ActRequest(BaseModel):
    task_id: str
    prompt: str
    start_url: str
    snapshot_html: str
    step_index: int
    web_project_id: str
    history: List[Dict[str, Any]]


class ActResponse(BaseModel):
    action: str
    task_id: str
    step_index: int


@app.post("/act", response_model=ActResponse)
async def act(request: ActRequest):
    """
    Main endpoint for webagent to receive task and return action.
    
    Receives:
    - task_id: Unique identifier for the task
    - prompt: Human-readable task description
    - start_url: Initial URL for the task
    - snapshot_html: Current state HTML of the webpage
    - step_index: Current step number in the task
    - web_project_id: Identifier for the web project
    - history: List of previous actions and states
    
    Returns:
    - action: Next action to execute
    - task_id: Echoed task_id
    - step_index: Echoed step_index
    """
    try:
        logger.info(
            "act request task_id=%s step_index=%s url=%s history_len=%s",
            request.task_id,
            request.step_index,
            request.start_url,
            len(request.history or []),
        )

        # Step 1: Optimize HTML content to remove noise
        optimized_html = await html_optimizer.optimize(
            html=request.snapshot_html,
            url=request.start_url,
            task_context=request.prompt
        )
        
        # Step 2: Generate next action using optimized HTML, task, step_index, and history
        action = await action_generator.generate_action(
            prompt=request.prompt,
            optimized_html=optimized_html,
            step_index=request.step_index,
            history=request.history,
            url=request.start_url
        )

        action = action_generator.parse_action(action)

        action_preview = (action or "").replace("\n", " ")
        if len(action_preview) > 400:
            action_preview = action_preview[:400] + "..."
        logger.info(
            "act response task_id=%s step_index=%s action=%s",
            request.task_id,
            request.step_index,
            action_preview,
        )
        
        return ActResponse(
            action=action,
            task_id=request.task_id,
            step_index=request.step_index
        )
    
    except Exception as e:
        logger.exception(
            "act error task_id=%s step_index=%s",
            getattr(request, "task_id", None),
            getattr(request, "step_index", None),
        )
        raise HTTPException(status_code=500, detail=f"Error processing action: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

