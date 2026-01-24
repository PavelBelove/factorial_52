"""
Translator Agent - converts Russian turns to English structured JSON
"""
import json
import logging
from typing import Dict, Any, Optional

from core.llm.openrouter_client import OpenRouterClient
from core.config import settings
from core.utils.agent_logger import log_agent_call

logger = logging.getLogger(__name__)


class TranslatorAgent:
    """
    Translates and compresses game turns from Russian to English JSON.
    
    Takes player action + GM response and converts to structured English format,
    removing unnecessary details and keeping essential narrative elements.
    """
    
    def __init__(self, llm_client: OpenRouterClient):
        self.llm = llm_client
        self.model = "x-ai/grok-4.1-fast"  # Optimal: cheap + fast + good quality
    
    async def translate_turn(
        self,
        player_action: str,
        gm_response: str,
        turn_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        Translate and compress one turn to English JSON.
        
        Args:
            player_action: Player's action in Russian
            gm_response: GM's response in Russian
            turn_number: Turn number
        
        Returns:
            Structured English JSON or None if translation fails
        """
        try:
            # Build translation prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(player_action, gm_response, turn_number)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Call LLM
            response = await self.llm.chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.3,  # Low temperature for consistent translation
                max_tokens=800    # Compressed output
            )
            
            if not response:
                logger.error("Translator: empty response from LLM")
                return None
            
            # Extract content from response structure
            try:
                content = response["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"Translator: failed to extract content from response: {e}")
                logger.debug(f"Full response: {response}")
                return None
            
            if not content or content == "...":
                logger.error("Translator: empty or placeholder content from LLM")
                return None
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            if not content:
                logger.error("Translator: content empty after cleanup")
                return None
            
            translated = json.loads(content)
            
            # Validate structure
            required_fields = ["turn", "player", "gm_summary", "key_events"]
            if not all(field in translated for field in required_fields):
                logger.error(f"Translator: missing required fields. Got: {list(translated.keys())}")
                return None
            
            # Add cost info
            if "usage" in response:
                translated["cost"] = response["usage"].get("cost", 0.0)
            
            # Log agent call for debugging
            log_agent_call(
                agent_name="translator",
                context=messages,
                response=translated,
                turn_number=turn_number
            )
            
            logger.info(
                f"Translated turn {turn_number}: "
                f"{len(player_action)} + {len(gm_response)} RU chars -> "
                f"{len(json.dumps(translated, ensure_ascii=False))} EN chars"
            )
            
            return translated
            
        except json.JSONDecodeError as e:
            logger.error(f"Translator: failed to parse JSON: {e}")
            logger.debug(f"Content was: {content[:200]}...")
            return None
        except Exception as e:
            logger.error(f"Translator: error translating turn: {e}")
            return None
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for translator."""
        return """You are a game turn translator and compressor. Your task:

1. Translate from Russian to English
2. Compress and structure the content
3. Remove unnecessary descriptive fluff
4. Keep all essential plot elements, NPC names, locations, items, actions

Output ONLY valid JSON with this structure:
{
  "turn": <number>,
  "player": "Brief player action",
  "gm_summary": "Concise GM response summary (100-200 words max)",
  "key_events": ["event1", "event2", ...],
  "npcs_involved": ["Name1", "Name2", ...],
  "locations": ["Location1", ...],
  "items": ["Item1", ...],
  "changes": {
    "hp": <delta or null>,
    "mana": <delta or null>,
    "gold": <delta or null>,
    "xp": {"spades": <delta>, ...} or null
  }
}

Rules:
- Keep NPC names, locations, item names in Russian (transliteration if needed)
- Translate narrative and descriptions to English
- Be concise but preserve plot important details
- Remove atmospheric descriptions unless plot-critical
- Focus on actions, decisions, consequences
- Maximum 200 words for gm_summary

Example:
Input (RU):
Player: "Я иду в гильдию авантюристов и сдаю квест"
GM: "Ты входишь в гильдию. Торгард встречает тебя с улыбкой. Он проверяет твой отчёт... (3000 chars)"

Output (EN JSON):
{
  "turn": 15,
  "player": "Goes to adventurers guild, completes quest",
  "gm_summary": "Торгард greets player at guild. Reviews quest report on Подгорье. Awards 350 gold, guild reputation +10. Offers new quest: griffon hunt or elf ruins exploration.",
  "key_events": ["quest_completed", "reward_received", "new_quests_offered"],
  "npcs_involved": ["Торгард"],
  "locations": ["Гильдия_Авантюристов"],
  "items": [],
  "changes": {"gold": 350, "xp": {"clubs": 1}}
}"""
    
    def _build_user_prompt(
        self,
        player_action: str,
        gm_response: str,
        turn_number: int
    ) -> str:
        """Build user prompt with turn data."""
        return f"""Turn #{turn_number}

Player action (RU):
{player_action}

GM response (RU):
{gm_response}

Translate and compress to English JSON:"""

