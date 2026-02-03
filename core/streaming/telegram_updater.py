"""
Telegram message updater with rate limiting.

Handles progressive updates of Telegram messages while respecting API rate limits.
"""
import asyncio
import time
import logging
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from core.config import settings

logger = logging.getLogger(__name__)


class StreamingMessageUpdater:
    """
    Updates Telegram message progressively with rate limiting.
    
    Ensures we don't hit Telegram API rate limits while providing
    smooth streaming updates to the user.
    """
    
    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        message_id: int,
        update_interval: Optional[float] = None
    ):
        """
        Initialize message updater.
        
        Args:
            bot: Telegram bot instance
            chat_id: Chat ID
            message_id: Message ID to update
            update_interval: Seconds between updates (default from config)
        """
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = message_id
        self.update_interval = update_interval or settings.streaming_chunk_interval
        
        self.last_update_time = 0.0
        self.last_sent_text = ""
        self.pending_text = ""
        self.is_closed = False
        
        # Task for scheduled updates
        self._update_task: Optional[asyncio.Task] = None
        
    async def schedule_update(self, new_text: str):
        """
        Schedule a text update, respecting rate limits.
        
        Args:
            new_text: New text to display
        """
        if self.is_closed:
            return
        
        self.pending_text = new_text
        
        # Check if we should send update now
        now = time.time()
        time_since_last = now - self.last_update_time
        
        if time_since_last >= self.update_interval:
            # Enough time passed, send immediately
            await self._send_update()
        else:
            # Schedule for later if not already scheduled
            if self._update_task is None or self._update_task.done():
                wait_time = self.update_interval - time_since_last
                self._update_task = asyncio.create_task(self._delayed_update(wait_time))
    
    async def _delayed_update(self, wait_time: float):
        """
        Wait and then send update.
        
        Args:
            wait_time: Seconds to wait
        """
        await asyncio.sleep(wait_time)
        await self._send_update()
    
    async def _send_update(self):
        """Actually send the update to Telegram."""
        if self.is_closed:
            return
        
        # Skip if no changes
        if self.pending_text == self.last_sent_text:
            return
        
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text=self.pending_text,
                parse_mode=None  # Plain text for stability
            )
            self.last_sent_text = self.pending_text
            self.last_update_time = time.time()
            
        except TelegramBadRequest as e:
            error_msg = str(e).lower()
            
            if "message is not modified" in error_msg:
                # Text is identical, not an error
                self.last_sent_text = self.pending_text
                pass
            elif "message to edit not found" in error_msg:
                # Message was deleted, stop trying
                logger.warning(f"Message {self.message_id} not found, closing updater")
                self.is_closed = True
            else:
                # Real error
                logger.error(f"Error updating message: {e}")
                raise
        
        except Exception as e:
            logger.error(f"Unexpected error updating message: {e}")
            raise
    
    async def force_update(self, final_text: Optional[str] = None):
        """
        Force immediate update, ignoring rate limits.
        
        Used for final message update when streaming is complete.
        
        Args:
            final_text: Optional final text (uses pending_text if not provided)
        """
        if final_text:
            self.pending_text = final_text
        
        await self._send_update()
        self.is_closed = True
    
    async def close(self):
        """
        Close the updater, sending any pending updates.
        """
        if not self.is_closed:
            await self.force_update()
    
    def __del__(self):
        """Cleanup."""
        if self._update_task and not self._update_task.done():
            self._update_task.cancel()


class LoadingAnimation:
    """
    Animated loading indicator for Telegram messages.
    
    Shows progressive dots: "⏳ Loading", "⏳ Loading.", "⏳ Loading..", etc.
    """
    
    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        message_id: int,
        base_text: str = "🎲 Ход обрабатывается",
        interval: Optional[float] = None,
        max_dots: int = 3
    ):
        """
        Initialize loading animation.
        
        Args:
            bot: Telegram bot
            chat_id: Chat ID
            message_id: Message ID to animate
            base_text: Base text before dots
            interval: Seconds between dot updates
            max_dots: Maximum number of dots
        """
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = message_id
        self.base_text = base_text
        self.interval = interval or settings.streaming_loading_interval
        self.max_dots = max_dots
        
        self.current_dots = 0
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the loading animation."""
        if self.is_running:
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._animate())
    
    async def stop(self):
        """Stop the loading animation."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _animate(self):
        """Run the animation loop."""
        try:
            while self.is_running:
                # Update dots
                dots = "." * self.current_dots
                text = f"{self.base_text}{dots}"
                
                try:
                    await self.bot.edit_message_text(
                        chat_id=self.chat_id,
                        message_id=self.message_id,
                        text=text,
                        parse_mode=None
                    )
                except TelegramBadRequest as e:
                    if "message is not modified" in str(e).lower():
                        pass
                    else:
                        logger.error(f"Error animating loading: {e}")
                
                # Increment dots
                self.current_dots = (self.current_dots + 1) % (self.max_dots + 1)
                
                # Wait
                await asyncio.sleep(self.interval)
        
        except asyncio.CancelledError:
            pass
    
    def __del__(self):
        """Cleanup."""
        if self._task and not self._task.done():
            self._task.cancel()

