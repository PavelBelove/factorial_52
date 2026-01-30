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
            print(f"\n{'='*80}")
            print(f"🤖 LLM REQUEST ({model})")
            print(f"{'='*80}")
            
            for i, msg in enumerate(messages):
                content = msg['content']
                role = msg['role']
                
                # Parse message content to show only relevant parts
                if role == 'system':
                    # Show only header for system prompt (it's static)
                    if '# Роль:' in content or '# Role:' in content:
                        header = content.split('\n')[0:3]
                        print(f"\n[{i}] [{role.upper()}] System Prompt ({len(content)} chars)")
                        print(f"  {header[0] if header else '...'}")
                    else:
                        # For summaries, quants, etc - show full
                        print(f"\n[{i}] [{role.upper()}]")
                        # Check for summary
                        if '# Summary' in content or 'История:' in content or 'События:' in content:
                            print(f"📜 SUMMARY:\n{content[:500]}{'...' if len(content) > 500 else ''}")
                        # Check for quants
                        elif '# Активная память' in content or 'кванты' in content.lower():
                            print(f"💾 ACTIVE QUANTS:\n{content[:800]}{'...' if len(content) > 800 else ''}")
                        # Check for synopsis
                        elif '# Доступные кванты' in content or 'синопсис' in content.lower():
                            print(f"📋 SYNOPSIS:\n{content[:800]}{'...' if len(content) > 800 else ''}")
                        # Check for mechanics
                        elif 'карты' in content.lower() or 'HP:' in content or 'Мана:' in content:
                            print(f"🎲 MECHANICS:\n{content}")
                        else:
                            print(content[:300] + ('...' if len(content) > 300 else ''))
                
                elif role == 'user':
                    # Show full user messages (they're short)
                    print(f"\n[{i}] [USER MESSAGE]")
                    print(content)
                
                elif role == 'assistant':
                    # Show full assistant messages (they're short)
                    print(f"\n[{i}] [ASSISTANT REPLY]")
                    print(content[:300] + ('...' if len(content) > 300 else ''))
            
            print(f"\n{'='*80}")
            print(f"Total messages: {len(messages)}")
            print(f"{'='*80}\n")
        
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
                
                # Log token usage
                if "usage" in result:
                    usage = result["usage"]
                    logger.info(f"📊 Tokens: {usage.get('prompt_tokens', 0)} prompt + {usage.get('completion_tokens', 0)} completion = {usage.get('total_tokens', 0)} total")
                
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

        if not content or not content.strip():
            logger.error("Empty content from LLM response")
            logger.error(f"Full response: {response}")
            return {}

        # Try to parse as JSON
        try:
            result = json.loads(content)
            if isinstance(result, dict):
                return result
            logger.warning(f"JSON parsed but not a dict: {type(result)}")
            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"Direct JSON parse failed: {e}")

        # Try to extract JSON from markdown code block
        if "```json" in content:
            try:
                json_str = content.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_str)
                if isinstance(result, dict):
                    return result
            except (json.JSONDecodeError, IndexError) as e:
                logger.warning(f"Markdown JSON parse failed: {e}")

        # Try to extract JSON object from text (non-greedy, balanced braces)
        import re

        # Find the outermost balanced braces
        brace_count = 0
        start_idx = None
        for i, char in enumerate(content):
            if char == '{':
                if start_idx is None:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx is not None:
                    json_str = content[start_idx:i+1]
                    try:
                        result = json.loads(json_str)
                        if isinstance(result, dict):
                            return result
                    except json.JSONDecodeError:
                        pass
                    break

        logger.error(f"Failed to parse JSON from response ({len(content)} chars): {content[:500]}...")
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
            max_tokens=max_tokens,
            response_format={"type": "json_object"}  # Force JSON mode
        )

        return self.extract_json(response)

