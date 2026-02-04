"""
Loading indicator with animated Armenian characters (Arevakhach).
"""
import asyncio
import logging
from typing import Optional
from aiogram import Bot
from aiogram.types import Message

logger = logging.getLogger(__name__)

# Armenian symbols for loading animation
# U+058D: ֍ (Right Arevakhach)
# U+058E: ֎ (Left Arevakhach)
SYMBOL_RIGHT = "\u058D"
SYMBOL_LEFT = "\u058E"


class LoadingIndicator:
    """
    Animated loading indicator with Armenian Arevakhach symbols.
    Updates message every 2 seconds, alternating between ֍ and ֎.
    """
    
    def __init__(self, bot: Bot, chat_id: int, initial_text: str):
        """
        Initialize loading indicator.
        
        Args:
            bot: Telegram bot instance
            chat_id: Chat ID where to show indicator
            initial_text: Text to show before animation (e.g., "Thinking...")
        """
        self.bot = bot
        self.chat_id = chat_id
        self.initial_text = initial_text
        self.message: Optional[Message] = None
        self.task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self) -> None:
        """Start the loading animation."""
        if self._running:
            logger.warning("LoadingIndicator already running")
            return
        
        self._running = True
        
        # Send initial message with first symbol
        text = f"{self.initial_text}\n{SYMBOL_RIGHT}"
        self.message = await self.bot.send_message(self.chat_id, text)
        
        # Start animation task
        self.task = asyncio.create_task(self._animate())
    
    async def _animate(self) -> None:
        """Animation loop that updates the message every 1 second."""
        symbols = []
        max_symbols = 10
        use_right = False  # Start with left, since we already showed right
        
        try:
            while self._running:
                await asyncio.sleep(1)
                
                if not self._running:
                    break
                
                # Add next symbol
                symbols.append(SYMBOL_LEFT if use_right else SYMBOL_RIGHT)
                use_right = not use_right
                
                # Reset if reached max
                if len(symbols) > max_symbols:
                    symbols = [symbols[-1]]  # Keep last symbol and restart
                
                # Update message
                animation_line = "".join(symbols)
                text = f"{self.initial_text}\n{animation_line}"
                
                try:
                    await self.message.edit_text(text)
                except Exception as e:
                    logger.debug(f"Failed to update loading indicator: {e}")
                    # Continue animation even if edit fails
        
        except asyncio.CancelledError:
            logger.debug("Loading animation cancelled")
        except Exception as e:
            logger.error(f"Error in loading animation: {e}", exc_info=True)
    
    async def stop(self) -> None:
        """Stop the animation."""
        self._running = False
        
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
    
    async def update_text(self, new_text: str) -> None:
        """
        Update the indicator text (e.g., from "Thinking..." to "Retrying...").
        
        Args:
            new_text: New text to display
        """
        self.initial_text = new_text
        
        # If message exists, update it immediately
        if self.message and self._running:
            try:
                # Keep current symbols, just update text
                current_text = self.message.text or ""
                lines = current_text.split("\n")
                animation_line = lines[-1] if len(lines) > 1 else SYMBOL_RIGHT
                
                text = f"{new_text}\n{animation_line}"
                await self.message.edit_text(text)
            except Exception as e:
                logger.debug(f"Failed to update indicator text: {e}")
    
    async def replace_with_text(self, final_text: str, parse_mode: Optional[str] = None) -> None:
        """
        Stop animation and replace message with final text.
        
        Args:
            final_text: Final text to show
            parse_mode: Parse mode for the final text (e.g., "HTML")
        """
        await self.stop()
        
        if self.message:
            try:
                await self.message.edit_text(final_text, parse_mode=parse_mode)
            except Exception as e:
                logger.error(f"Failed to replace indicator with final text: {e}")
                # If edit fails, send as new message
                await self.bot.send_message(self.chat_id, final_text, parse_mode=parse_mode)

