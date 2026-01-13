from typing import Optional
from src.config import Settings
from src.llm_client import LLMClient
from src.prompts import HTML_OPTIMIZER_PROMPT


class HTMLOptimizer:
    """Optimizes HTML content by removing noise and meaningless content using LLM"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm_client = LLMClient(settings)
    
    async def optimize(
        self,
        html: str,
        url: str,
        task_context: Optional[str] = None
    ) -> str:
        """
        Optimize HTML by removing noise and keeping only relevant content.
        
        Args:
            html: Raw HTML content from snapshot
            url: Current URL
            task_context: Optional task description for context-aware optimization
            
        Returns:
            Optimized HTML string
        """
        prompt = self._build_optimization_prompt(html, url, task_context)
        
        optimized_html = await self.llm_client.generate(
            prompt=prompt,
            model=self.settings.html_optimization_model,
            temperature=self.settings.html_optimization_temperature,
            max_tokens=self.settings.html_optimization_max_tokens,
            use_html_optimization_llm=True
        )
        
        return optimized_html.strip()
    
    def _build_optimization_prompt(
        self,
        html: str,
        url: str,
        task_context: Optional[str] = None
    ) -> str:
        """Build the prompt for HTML optimization"""

        raw_html = html
        if task_context:
            raw_html = f"Task Context:\n{task_context}\n\n{html}"

        return HTML_OPTIMIZER_PROMPT.substitute(
            url=url,
            raw_html=raw_html,
        )

