"""
Streaming LLM client for OpenRouter API.

Handles streaming responses from LLM models, providing progressive updates
as the response is generated.
"""
import asyncio
import json
import logging
from typing import Callable, Awaitable, Optional, Dict, Any
import httpx

from core.config import settings
from core.streaming.json_parser import PartialJSONParser

logger = logging.getLogger(__name__)


class StreamingLLMClient:
    """
    Client for streaming LLM responses from OpenRouter.
    
    Handles Server-Sent Events (SSE) streaming and provides callbacks
    for progressive content updates.
    """
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize streaming client.
        
        Args:
            api_key: OpenRouter API key
            base_url: Base URL for OpenRouter API
        """
        self.api_key = api_key
        self.base_url = base_url or settings.openrouter_base_url
        self.timeout = settings.streaming_timeout
        
    async def stream_completion(
        self,
        messages: list[dict],
        model: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        on_content_update: Optional[Callable[[str], Awaitable[None]]] = None,
    ) -> Dict[str, Any]:
        """
        Stream a chat completion from OpenRouter.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (e.g., 'deepseek/deepseek-v3.2')
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            on_content_update: Async callback called with accumulated content
            
        Returns:
            Complete response dict with usage info
            
        Raises:
            httpx.HTTPError: If request fails
            asyncio.TimeoutError: If stream times out
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/PavelBelove/factorial_52",
            "X-Title": "PlexMem RPG Bot"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True  # Enable streaming
        }
        
        accumulated_content = ""
        accumulated_chunks = []
        response_id = None
        created = None
        model_used = None
        finish_reason = None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        # Skip empty lines
                        if not line.strip():
                            continue
                        
                        # Check for SSE data prefix
                        if not line.startswith("data: "):
                            continue
                        
                        # Extract JSON data
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        # Check for end marker
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            chunk_data = json.loads(data_str)
                            accumulated_chunks.append(chunk_data)
                            
                            # Extract metadata from first chunk
                            if response_id is None:
                                response_id = chunk_data.get("id")
                                created = chunk_data.get("created")
                                model_used = chunk_data.get("model")
                            
                            # Extract content delta
                            choices = chunk_data.get("choices", [])
                            if choices:
                                choice = choices[0]
                                delta = choice.get("delta", {})
                                content_delta = delta.get("content", "")
                                
                                if content_delta:
                                    accumulated_content += content_delta
                                    
                                    # Call update callback if provided
                                    if on_content_update:
                                        await on_content_update(accumulated_content)
                                
                                # Check for finish reason
                                if "finish_reason" in choice and choice["finish_reason"]:
                                    finish_reason = choice["finish_reason"]
                        
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse SSE chunk: {data_str[:100]}... Error: {e}")
                            continue
            
            # Calculate token usage from accumulated chunks
            usage = self._calculate_usage(accumulated_chunks)
            
            # Build complete response in OpenRouter format
            complete_response = {
                "id": response_id,
                "created": created,
                "model": model_used or model,
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": accumulated_content
                    },
                    "finish_reason": finish_reason or "stop"
                }],
                "usage": usage
            }
            
            return complete_response
            
        except httpx.TimeoutException as e:
            logger.error(f"Stream timeout after {self.timeout}s")
            raise asyncio.TimeoutError(f"Stream timeout: {e}")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during streaming: {e}")
            raise
    
    async def stream_gm_response(
        self,
        messages: list[dict],
        model: str,
        max_tokens: int = 2000,
        on_narrative_update: Optional[Callable[[str], Awaitable[None]]] = None,
    ) -> Dict[str, Any]:
        """
        Stream GM response with JSON parsing for progressive narrative updates.
        
        This method specifically handles GM responses in JSON format:
        {
          "reply": "narrative text...",
          "mechanics": {...},
          "quant_commands": [...]
        }
        
        The on_narrative_update callback receives only the narrative text,
        progressively as it's generated.
        
        Args:
            messages: Chat messages
            model: Model name
            max_tokens: Max tokens
            on_narrative_update: Callback for narrative text updates
            
        Returns:
            Complete response with parsed JSON content
        """
        parser = PartialJSONParser()
        last_update_time = asyncio.get_event_loop().time()
        min_update_interval = settings.streaming_chunk_interval
        last_content_length = 0  # Track how much we've already fed to parser
        
        async def on_content_chunk(full_content: str):
            """Handle raw content updates and parse JSON."""
            nonlocal last_update_time, last_content_length
            
            # Extract only NEW content since last call
            new_chunk = full_content[last_content_length:]
            logger.info(f"🔥 LLM: full_content={len(full_content)} chars, last_pos={last_content_length}, new_chunk={len(new_chunk)} chars")
            last_content_length = len(full_content)
            
            # Feed NEW chunk to parser
            narrative_update = parser.feed_chunk(new_chunk)
            
            # Check if we should send update (respect interval)
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - last_update_time
            
            logger.info(f"📝 Narrative update: {len(narrative_update) if narrative_update else 0} chars, complete: {parser.is_complete()}")
            
            if narrative_update and on_narrative_update:
                # Only update if enough time passed or narrative is complete
                if time_since_last >= min_update_interval or parser.is_complete():
                    # Check minimum characters threshold
                    if len(narrative_update) >= settings.streaming_min_chars_for_update or parser.is_complete():
                        logger.info(f"🔄 Calling narrative callback with {len(narrative_update)} chars")
                        await on_narrative_update(narrative_update)
                        last_update_time = current_time
        
        # Stream with content callback
        response = await self.stream_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            on_content_update=on_content_chunk
        )
        
        # Parse the complete JSON response
        content = response["choices"][0]["message"]["content"]
        
        try:
            parsed_json = json.loads(content)
            
            # Send final narrative update if parser hasn't caught everything
            if on_narrative_update and parser.get_complete_narrative() != parsed_json.get("reply", ""):
                await on_narrative_update(parsed_json.get("reply", ""))
            
            # Update response with parsed content
            response["choices"][0]["message"]["content"] = parsed_json
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse complete GM response JSON: {e}")
            logger.error(f"Content: {content[:500]}...")
            
            # Fallback: try to extract what parser got
            if parser.get_complete_narrative():
                response["choices"][0]["message"]["content"] = {
                    "reply": parser.get_complete_narrative(),
                    "mechanics": {},
                    "quant_commands": []
                }
            else:
                # Last resort: return raw content
                response["choices"][0]["message"]["content"] = {
                    "reply": content,
                    "mechanics": {},
                    "quant_commands": []
                }
        
        return response
    
    def _calculate_usage(self, chunks: list[dict]) -> dict:
        """
        Calculate token usage from accumulated chunks.
        
        Args:
            chunks: List of SSE chunk data
            
        Returns:
            Usage dict with prompt_tokens, completion_tokens, total_tokens, cost
        """
        # Look for usage info in chunks (usually in last chunk)
        for chunk in reversed(chunks):
            if "usage" in chunk:
                return chunk["usage"]
        
        # If no usage found, return empty dict
        # (Will be populated later from x-ratelimit headers if available)
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost": 0.0
        }

