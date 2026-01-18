"""
OpenRouter API client.
Handles all LLM interactions with logging.
"""
import json
import logging
from typing import List, Dict, Any, Optional
import httpx

from core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    Client for OpenRouter API.
    Supports streaming and non-streaming requests with full logging.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """Initialize OpenRouter client."""
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model  # Model is set per agent, no default here
        self.base_url = base_url or settings.openrouter_base_url
        
        if not self.api_key:
            logger.warning("OpenRouter API key not set!")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (overrides default)
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            response_format: Format specification (e.g., {"type": "json_object"})
            **kwargs: Additional parameters
        
        Returns:
            API response dict
        """
        model = model or self.model
        
        # Prepare request
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        
        if response_format:
            request_data["response_format"] = response_format
        
        # Log full request
        if settings.debug:
            logger.debug("=" * 80)
            logger.debug("LLM REQUEST:")
            logger.debug(f"Model: {model}")
            logger.debug(f"Temperature: {temperature}")
            # Only log message count, not full content (too verbose for GM)
            logger.debug(f"Messages: {len(messages)} messages")
            logger.debug("=" * 80)
        
        # Console Verbose Output
        if settings.debug_verbose:
            print(f"\n[DEBUG_VERBOSE] LLM REQUEST ({model}):")
            for msg in messages:
                content_preview = msg['content']
                print(f"[{msg['role']}]\n{content_preview}\n")
            print("-" * 40)
        
        # Send request
        try:
            # Отключаем reasoning для всех моделей - слишком медленно
            request_data["reasoning"] = {"enabled": False}
            
            async with httpx.AsyncClient(timeout=180.0) as client:  # Увеличен таймаут
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=request_data
                )
                response.raise_for_status()
                result = response.json()
            
            # Log response (only content, not full JSON)
            if settings.debug:
                logger.debug("=" * 80)
                logger.debug("LLM RESPONSE:")
                content = self.extract_content(result)
                # For GM responses, only log parsed reply and quants
                try:
                    parsed = json.loads(content)
                    if "reply" in parsed and "quants" in parsed:
                        logger.debug(f"Reply: {parsed['reply'][:200]}...")
                        logger.debug(f"Quants: {parsed['quants']}")
                    else:
                        logger.debug(content[:500])
                except:
                    logger.debug(content[:500])
                logger.debug("=" * 80)

            # Console Verbose Output
            if settings.debug_verbose:
                print(f"\n[DEBUG_VERBOSE] LLM RESPONSE:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                print("=" * 80)
            
            return result
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from OpenRouter: {e}")
            logger.error(f"Response: {e.response.text}")
            raise
        
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            raise
    
    def extract_content(self, response: Dict[str, Any]) -> str:
        """Extract text content from API response."""
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract content from response: {e}")
            logger.error(f"Response: {response}")
            return ""
    
    def extract_json(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and parse JSON content from API response."""
        content = self.extract_content(response)
        
        # Try to parse as JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # Try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            logger.error(f"Failed to parse JSON from response: {content}")
            return {}
    
    async def simple_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Simple completion with optional system prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Max tokens
        
        Returns:
            Response text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return self.extract_content(response)
    
    async def json_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Completion expecting JSON response.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Max tokens
        
        Returns:
            Parsed JSON dict
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return self.extract_json(response)

