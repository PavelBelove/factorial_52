"""
Simple Telegram bot for PlexMem.
No complications, just works.
Uses NATIVE aiogram methods for maximum speed (persistent connection).
"""
import asyncio
import logging
from typing import Optional
import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import settings
from core.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = "http://localhost:8000"


class SimplePlexMemBot:
    """Simple Telegram bot - just send and receive messages."""
    
    def __init__(self, token: str):
        """Initialize bot."""
        # Initialize Bot with HTML parse mode
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        
        # Store user sessions: telegram_id -> session_id
        self.user_sessions = {}
        
        # Store last message for retry
        self.last_user_messages = {}
        
        # Register handlers
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_retry, Command("retry"))
        self.dp.message.register(self.cmd_undo, Command("undo"))
        self.dp.message.register(self.cmd_stats, Command("stats"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.handle_message, F.text)
    
    async def cmd_start(self, message: Message):
        """Start new game."""
        user_id = message.from_user.id
        logger.info(f"User {user_id} started new game")
        
        try:
            # Create new session
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Deactivate old sessions
                try:
                    await client.post(
                        f"{API_BASE_URL}/sessions/deactivate",
                        json={
                            "platform_id": str(user_id),
                            "platform_type": "telegram"
                        }
                    )
                except Exception:
                    pass
                
                # Create new session
                response = await client.post(
                    f"{API_BASE_URL}/sessions",
                    json={
                        "platform_id": str(user_id),
                        "platform_type": "telegram",
                        "session_type": "game"
                    }
                )
                
                if response.status_code != 200:
                    await message.answer("❌ Ошибка создания сессии")
                    return
                
                data = response.json()
                session_id = data["session_id"]
                self.user_sessions[user_id] = session_id
                
                logger.info(f"Created session {session_id} for user {user_id}")
            
            # Send initial message to activate agent
            initial_message = "Давай начнем новую игру! Объясни суть и дальнейшие действия, приступим к созданию персонажа"
            
            await message.answer("⏳ Создаю игру...")
            
            # Send to API (long timeout for LLM)
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{API_BASE_URL}/sessions/{session_id}/messages",
                    json={
                        "session_id": session_id,
                        "message": initial_message
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Escape HTML characters if needed, but for now trust the LLM output or just send text
                    # We will use simple text to avoid markup errors for now
                    reply = f"🎲 Ход #{data['turn_number']}\n\n{data['reply']}"
                    
                    # DIRECT NATIVE SEND - FASTEST METHOD
                    await message.answer(reply, parse_mode=None)
                else:
                    await message.answer("❌ Ошибка инициализации игры")
        
        except Exception as e:
            logger.error(f"Error in /start: {e}", exc_info=True)
            await message.answer(f"❌ Ошибка: {str(e)[:100]}")
    
    async def cmd_retry(self, message: Message):
        """Retry last message - undo last turn and send again."""
        user_id = message.from_user.id
        
        last_msg = self.last_user_messages.get(user_id)
        if not last_msg:
            await message.answer("❌ Нет сообщения для повтора")
            return
        
        session_id = await self._get_or_restore_session(user_id)
        if not session_id:
            await message.answer("❌ Нет активной игры. Используй /start")
            return
        
        try:
            # First, undo the last turn to restore correct context
            async with httpx.AsyncClient(timeout=30.0) as client:
                undo_response = await client.post(
                    f"{API_BASE_URL}/sessions/{session_id}/undo"
                )
                
                if undo_response.status_code != 200:
                    await message.answer("❌ Не могу откатить последний ход")
                    return
                
                undo_data = undo_response.json()
                logger.info(f"Undo successful: {undo_data}")
            
            await message.answer(f"🔄 Повторяю с хода {undo_data['current_turn']}: {last_msg[:50]}...")
            
            # Now process as regular message with correct context
            await self._process_message(message, session_id, last_msg)
        
        except Exception as e:
            logger.error(f"Error in /retry: {e}", exc_info=True)
            await message.answer(f"❌ Ошибка retry: {str(e)[:100]}")
    
    async def cmd_undo(self, message: Message):
        """Undo last turn - delete it from database."""
        user_id = message.from_user.id
        session_id = await self._get_or_restore_session(user_id)
        
        if not session_id:
            await message.answer("❌ Нет активной игры. Используй /start")
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{API_BASE_URL}/sessions/{session_id}/undo"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    await message.answer(
                        f"✅ Ход отменён. Теперь ход #{data['current_turn']}\n"
                        f"Напиши новое сообщение или /retry для повтора."
                    )
                    logger.info(f"Undo successful for user {user_id}, session {session_id}")
                elif response.status_code == 400:
                    await message.answer("❌ Нечего отменять (игра на 0 ходу)")
                else:
                    await message.answer(f"❌ Ошибка отмены: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error in /undo: {e}", exc_info=True)
            await message.answer(f"❌ Ошибка: {str(e)[:100]}")
    
    async def cmd_stats(self, message: Message):
        """Show session stats."""
        user_id = message.from_user.id
        session_id = await self._get_or_restore_session(user_id)
        
        if not session_id:
            await message.answer("❌ Нет активной игры")
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_BASE_URL}/sessions/{session_id}")
                
                if response.status_code == 200:
                    info = response.json()
                    stats = (
                        f"📊 Статистика сессии\n\n"
                        f"🎲 Ходов: {info['current_turn']}\n"
                        f"🧠 Квантов: {info['quants_count']}\n"
                        f"📝 Размер сводки: {info['summary_length']} символов"
                    )
                    await message.answer(stats)
                else:
                    await message.answer("❌ Ошибка получения статистики")
        
        except Exception as e:
            logger.error(f"Error in stats: {e}")
            await message.answer("❌ Ошибка")
    
    async def cmd_help(self, message: Message):
        """Show help."""
        help_text = (
            "📖 PlexMem Bot\n\n"
            "Команды:\n"
            "/start - начать новую игру\n"
            "/retry - повторить последний запрос\n"
            "/stats - статистика сессии\n"
            "/help - эта справка\n\n"
            "Как играть:\n"
            "Просто пиши свои действия текстом!"
        )
        await message.answer(help_text)
    
    async def handle_message(self, message: Message):
        """Handle regular game messages."""
        user_id = message.from_user.id
        
        # Try to get or restore session
        session_id = await self._get_or_restore_session(user_id)
        
        if not session_id:
            await message.answer("❌ Нет активной игры. Используй /start для начала новой игры")
            return
        
        # Save for retry
        self.last_user_messages[user_id] = message.text
        
        # Process message
        await self._process_message(message, session_id, message.text)
    
    async def _get_or_restore_session(self, user_id: int) -> Optional[int]:
        """
        Get session for user - from memory or by checking API.
        Allows continuing game after bot restart.
        """
        # Check memory first
        if user_id in self.user_sessions:
            return self.user_sessions[user_id]
        
        # Try to restore from API
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{API_BASE_URL}/sessions/user/{user_id}",
                    params={"platform_type": "telegram"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    session_id = data["session_id"]
                    self.user_sessions[user_id] = session_id
                    logger.info(f"Restored session {session_id} for user {user_id}")
                    return session_id
        except Exception as e:
            logger.debug(f"Could not restore session for user {user_id}: {e}")
        
        return None
    
    async def _process_message(self, message: Message, session_id: int, text: str):
        """Process message and send to API."""
        user_id = message.from_user.id
        
        try:
            # Show typing - this is now fast with persistent connection
            await self.bot.send_chat_action(user_id, "typing")
            
            logger.debug(f"Sending to API: session={session_id}, user={user_id}")
            
            # Send to API (long timeout for LLM)
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{API_BASE_URL}/sessions/{session_id}/messages",
                    json={
                        "session_id": session_id,
                        "message": text
                    }
                )
                
                logger.debug(f"API responded: status={response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    reply = f"🎲 Ход #{data['turn_number']}\n\n{data['reply']}"
                    
                    logger.debug(f"Sending to Telegram: {len(reply)} chars")
                    
                    # FAST NATIVE SEND
                    await message.answer(reply, parse_mode=None)
                    
                    logger.info(f"Turn {data['turn_number']} completed for user {user_id}")
                else:
                    await message.answer("❌ Ошибка API")
        
        except httpx.TimeoutError:
            logger.error("API timeout")
            await message.answer("⏱️ Превышено время ожидания. Попробуй /retry")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await message.answer(f"❌ Ошибка: {str(e)[:100]}")
    
    async def start(self):
        """Start bot."""
        logger.info("Starting PlexMem Bot (FAST native version)")
        logger.info(f"Bot token: {settings.telegram_bot_token[:20]}...")
        
        # Check API
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{API_BASE_URL}/")
                if response.status_code == 200:
                    logger.info("API is available")
                else:
                    logger.warning(f"API returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"Cannot connect to API: {e}")
        
        # Start polling
        await self.dp.start_polling(self.bot)
    
    async def stop(self):
        """Stop bot."""
        logger.info("Stopping bot...")
        await self.bot.session.close()


async def main():
    """Main entry point."""
    if not settings.telegram_bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set")
        return
    
    bot = SimplePlexMemBot(settings.telegram_bot_token)
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())

