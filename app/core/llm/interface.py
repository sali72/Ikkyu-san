"""
Interface definitions for LLM service providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMProvider(ABC):
    """Interface for LLM service providers"""
    
    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a completion from the LLM provider"""
        pass