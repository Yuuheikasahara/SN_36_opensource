from typing import List, Dict, Any, Optional
import json
import logging
from enum import Enum

from pydantic import BaseModel
from src.config import Settings
from src.llm_client import LLMClient
from src.prompts import WEB_ACTION_GENERATOR_PROMPT


class ActionGenerator:
    """Generates next action for webagent based on task, HTML state, and history"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm_client = LLMClient(settings)
        self._logger = logging.getLogger("webagent.action_parser")

    def parse_action(self, action_text: str) -> str:
        """Parse LLM output into a structured action string.

        The action generator prompt asks for a JSON object such as:
        {
          "action": "ClickAction",
          "selector": {"type": "xpathSelector", "value": "..."}
        }

        For backward compatibility, if parsing fails, returns the raw string.
        """
        if not action_text:
            return action_text

        try:
            data = json.loads(action_text)
        except Exception:
            return action_text.strip()

        try:
            action_type = data.get("type") or data.get("action")
            if not action_type:
                raise ValueError("Missing 'action'/'type' field")

            if not action_type.endswith("Action"):
                action_type = f"{action_type}Action"

            selector_data = data.get("selector")
            selector = Selector(**selector_data) if isinstance(selector_data, dict) else None

            if action_type == "ClickAction":
                obj = ClickAction(type=action_type, selector=selector)
            elif action_type == "NavigateAction":
                obj = NavigateAction(type=action_type, url=data.get("url"))
            elif action_type == "TypeAction":
                obj = TypeAction(type=action_type, text=data.get("text", ""), selector=selector)
            elif action_type == "SelectAction":
                obj = SelectAction(type=action_type, value=data.get("value", ""), selector=selector)
            elif action_type == "WaitAction":
                obj = WaitAction(type=action_type, time_seconds=data.get("time_seconds"))
            else:
                obj = BaseAction(type=action_type, selector=selector)

            return str(obj)
        except Exception as e:
            self._logger.warning("Failed to parse action JSON: %s", str(e))
            return action_text.strip()
    
    async def generate_action(
        self,
        prompt: str,
        optimized_html: str,
        step_index: int,
        history: List[Dict[str, Any]],
        url: str
    ) -> str:
        """
        Generate the next action based on task, optimized HTML, step index, and history.
        
        Args:
            prompt: Human-readable task description
            optimized_html: Optimized HTML content
            step_index: Current step number
            history: List of previous actions and states
            
        Returns:
            Action string (e.g., "click", "type", "navigate", etc.)
        """
        action_prompt = self._build_action_prompt(
            prompt=prompt,
            optimized_html=optimized_html,
            step_index=step_index,
            history=history,
            url=url
        )
        
        action = await self.llm_client.generate(
            prompt=action_prompt,
            model=self.settings.action_generation_model,
            temperature=self.settings.action_generation_temperature,
            max_tokens=self.settings.action_generation_max_tokens,
            use_html_optimization_llm=False
        )
        
        return action.strip()
    
    def _build_action_prompt(
        self,
        prompt: str,
        optimized_html: str,
        step_index: int,
        history: List[Dict[str, Any]],
        url: str
    ) -> str:
        """Build the prompt for action generation"""

        history_text = self._format_history(history)

        return WEB_ACTION_GENERATOR_PROMPT.substitute(
            task=prompt,
            url=url,
            step_index=step_index,
            previous_actions=history_text if history_text else "No previous actions",
            optimized_html=optimized_html,
        )
    
    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """Format history into readable text"""
        if not history:
            return ""
        
        formatted = []
        for i, entry in enumerate(history, 1):
            action = entry.get("action", "unknown")
            result = entry.get("result", "")
            formatted.append(f"Step {i}: {action}")
            if result:
                formatted.append(f"  Result: {result}")
        
        return "\n".join(formatted)


class SelectorType(str, Enum):
    ATTRIBUTE_VALUE_SELECTOR = "attributeValueSelector"
    TAG_CONTAINS_SELECTOR = "tagContainsSelector"
    XPATH_SELECTOR = "xpathSelector"


class Selector(BaseModel):
    type: SelectorType
    attribute: str | None = None
    value: str


class BaseAction(BaseModel):
    type: str
    selector: Selector | None = None


class ClickAction(BaseAction):
    selector: Selector


class NavigateAction(BaseAction):
    url: str | None = None


class TypeAction(BaseAction):
    text: str
    selector: Selector


class SelectAction(BaseAction):
    value: str
    selector: Selector


class WaitAction(BaseAction):
    time_seconds: float | None = None

