"""
Telegram bot for PlexMem system.
Provides interface for interacting with game master.
"""
import asyncio
import logging
from typing import Optional, Dict

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import httpx

from core.config import settings
from core.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = "http://localhost:8000"


class UserState(StatesGroup):
    """User states."""
    in_game = State()


class PlexMemBot:
    """
    Telegram bot for PlexMem system.
    Handles user interactions and communicates with API.
    """
    
    def __init__(self, token: str):
        """Initialize bot with increased Telegram API timeouts."""
        # Create bot with custom session for better timeout handling
        from aiogram.client.session.aiohttp import AiohttpSession
        
        # Timeout for Telegram API calls (sending messages, not our API)
        # Should be relatively short since Telegram API is fast
        session = AiohttpSession(timeout=20.0)
        
        self.bot = Bot(token=token, session=session)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        
        # Store last user messages for retry functionality
        self.last_user_messages: Dict[int, str] = {}
        
        # User sessions mapping: telegram_id -> session_id
        self.user_sessions: Dict[int, int] = {}
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register message handlers."""
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_retry, Command("retry"))
        self.dp.message.register(self.cmd_undo, Command("undo"))
        self.dp.message.register(self.cmd_stats, Command("stats"))
        self.dp.message.register(self.handle_message, F.text)
    
    async def cmd_start(self, message: Message, state: FSMContext):
        """Handle /start command - ALWAYS create NEW game session."""
        user_id = message.from_user.id
        logger.info(f"User {user_id} started NEW game with /start")
        
        try:
            # ALWAYS create NEW session (deactivate old ones)
            session_id = await self._create_new_session(user_id)
            
            await state.set_state(UserState.in_game)
            
            # Immediately send first game message from user perspective
            auto_message = "Давай начнем новую игру! Объясни суть и дальнейшие действия, приступим к созданию персонажа"
            
            # Send "preparing" message that we'll edit later
            preparing_msg = await message.answer("⏳ Готовлю ответ...")
            
            try:
                async with httpx.AsyncClient(timeout=180.0) as client:  # Увеличен таймаут
                    # Send auto-message to API
                    response = await client.post(
                        f"{API_BASE_URL}/sessions/{session_id}/messages",
                        json={
                            "session_id": session_id,
                            "message": auto_message
                        }
                    )
                    
                    if response.status_code != 200:
                        error_detail = response.json().get("detail", "Unknown error")
                        logger.error(f"API error: {error_detail}")
                        await preparing_msg.edit_text("❌ Ошибка при создании сессии. Попробуй /start снова.")
                        return
                    
                    data = response.json()
                    reply = data["reply"]
                    turn_number = data["turn_number"]
                    
                    # Format response
                    formatted_reply = f"🎲 Ход #{turn_number}\n\n{reply}"
                    
                    # Always delete preparing message and send new one
                    # This avoids connection timeout issues with edit_text after long waits
                    try:
                        await preparing_msg.delete()
                    except Exception:
                        pass  # Ignore if already deleted or expired
                    
                    # Send response as new message(s)
                    if len(formatted_reply) > 4000:
                        parts = [formatted_reply[i:i+4000] for i in range(0, len(formatted_reply), 4000)]
                        for part in parts:
                            await self.bot.send_message(message.chat.id, part)
                    else:
                        await self.bot.send_message(message.chat.id, formatted_reply)
            
            except httpx.TimeoutException:
                logger.error("API timeout")
                await self.bot.send_message(message.chat.id, "⏱ Превышено время ожидания. Попробуй ещё раз.")
            
            except Exception as e:
                logger.error(f"Error starting game: {e}", exc_info=True)
                await self.bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуй ещё раз или /start для новой игры.")
        
        except Exception as e:
            logger.error(f"Error in start command: {e}", exc_info=True)
            await message.answer(
                "❌ Ошибка при создании сессии. Попробуй /start снова."
            )
    
    async def cmd_help(self, message: Message):
        """Handle /help command."""
        await message.answer(
            "📖 Справка PlexMem Bot\n\n"
            "Как играть:\n"
            "Просто пиши свои действия, и ГМ будет описывать что происходит.\n\n"
            "Команды:\n"
            "/start - начать новую игру\n"
            "/retry - повторить последний запрос\n"
            "/undo - отменить последний ход (если ГМ заглючил)\n"
            "/stats - статистика: ходы, кванты памяти\n"
            "/help - эта справка\n\n"
            "Система памяти:\n"
            "ГМ помнит NPC, локации, события. Память работает "
            "предиктивно - активируются только релевантные кванты.\n\n"
            "Особенности:\n"
            "• Сущности выделяются маркерами (=Имя=)\n"
            "• Мир реагирует на твои действия\n"
            "• NPC имеют характер и цели\n"
            "• История конденсируется, но не забывается",
            parse_mode="HTML"
        )
    
    async def cmd_retry(self, message: Message, state: FSMContext):
        """Handle /retry command - repeat last user message."""
        user_id = message.from_user.id
        
        # Get last message
        last_msg = self.last_user_messages.get(user_id)
        if not last_msg:
            await message.answer("❌ Нет сохранённого сообщения для повтора.")
            return
        
        await message.answer(f"🔄 Повторяю запрос: \"{last_msg[:50]}{'...' if len(last_msg) > 50 else ''}\"")
        
        # Create a new message object with the last text
        # We can't modify the frozen Message, so we'll call handle_message directly
        # but pass the last message text instead
        
        # Temporarily override the message text in our tracking
        original_text = message.text
        
        # Save last message again (in case it was lost)
        self.last_user_messages[user_id] = last_msg
        
        # Call handle_message with a modified context
        # We'll create a wrapper that uses the saved message
        session_id = self.user_sessions.get(user_id)
        
        if not session_id:
            await message.answer("❌ Нет активной сессии. Используй /start для начала новой игры.")
            return
        
        # Show typing indicator
        typing_task = asyncio.create_task(
            self._keep_typing(message.chat.id)
        )
        
        # Send "preparing" message
        preparing_msg = await message.answer("⏳ Готовлю ответ...")
        
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                # Send the SAVED message (not the current /retry command)
                response = await client.post(
                    f"{API_BASE_URL}/sessions/{session_id}/messages",
                    json={
                        "session_id": session_id,
                        "message": last_msg  # Use saved message, not "/retry"
                    }
                )
                
                # Stop typing
                typing_task.cancel()
                
                if response.status_code != 200:
                    error_detail = response.json().get("detail", "Unknown error")
                    logger.error(f"API error on retry: {error_detail}")
                    await self._safe_edit(
                        preparing_msg,
                        f"❌ Ошибка API: {error_detail}\n\n"
                        "Попробуй ещё раз или /start для новой игры."
                    )
                    return
                
                data = response.json()
                reply = data["reply"]
                turn_number = data["turn_number"]
                
                # Format response
                formatted_reply = f"🎲 Ход #{turn_number}\n\n{reply}"
                
                # Try to send response with retries
                await self._send_response_with_retry(
                    message=message,
                    preparing_msg=preparing_msg,
                    formatted_reply=formatted_reply,
                    max_attempts=3
                )
                
                # Log quants info (debug)
                if data.get("quants_requested"):
                    logger.info(
                        f"Turn {turn_number}: Requested quants: {data['quants_requested']}"
                    )
        
        except httpx.TimeoutException:
            typing_task.cancel()
            logger.error("API timeout on retry")
            try:
                await preparing_msg.delete()
            except Exception:
                pass
            await self.bot.send_message(
                message.chat.id,
                "⏱ Превышено время ожидания. ГМ думает слишком долго.\n\n"
                "Попробуй:\n"
                "/retry - повторить запрос\n"
                "/undo - отменить ход"
            )
        
        except Exception as e:
            typing_task.cancel()
            logger.error(f"Error in retry command: {e}", exc_info=True)
            try:
                await preparing_msg.delete()
            except Exception:
                pass
            await self.bot.send_message(
                message.chat.id,
                "❌ Произошла ошибка при повторе.\n\n"
                "Попробуй:\n"
                "/retry - повторить запрос снова\n"
                "/start - начать новую игру"
            )
    
    async def cmd_undo(self, message: Message):
        """Handle /undo command - cancel last turn."""
        user_id = message.from_user.id
        session_id = self.user_sessions.get(user_id)
        
        if not session_id:
            await message.answer(
                "❌ Сначала начни игру командой /start"
            )
            return
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Get session info
                response = await client.get(f"{API_BASE_URL}/sessions/{session_id}")
                
                if response.status_code != 200:
                    await message.answer("❌ Ошибка получения информации о сессии")
                    return
                
                session_info = response.json()
                current_turn = session_info.get("current_turn", 0)
                
                if current_turn == 0:
                    await message.answer("❌ Нет ходов для отмены")
                    return
                
                # Get history to show what we're undoing
                response = await client.get(
                    f"{API_BASE_URL}/sessions/{session_id}/history",
                    params={"limit": 1}
                )
                
                if response.status_code == 200:
                    history = response.json()
                    if history.get("turns"):
                        last_turn = history["turns"][-1]
                        await message.answer(
                            f"⏪ <b>Отменяю последний ход #{current_turn}</b>\n\n"
                            f"<i>Твоё действие:</i> {last_turn['user_message'][:100]}...\n\n"
                            f"<i>Ответ ГМ:</i> {last_turn['agent_reply'][:100]}...",
                            parse_mode="HTML"
                        )
                
                # TODO: Implement actual undo in API
                # For now, just inform user
                await message.answer(
                    "⚠️ Функция UNDO в разработке.\n\n"
                    "Пока просто продолжи игру - напиши \"Отменяем предыдущее\" "
                    "и ГМ поймёт."
                )
        
        except Exception as e:
            logger.error(f"Error in undo command: {e}", exc_info=True)
            await message.answer("❌ Ошибка при отмене хода")
    
    async def cmd_stats(self, message: Message):
        """Handle /stats command - show session statistics."""
        user_id = message.from_user.id
        session_id = self.user_sessions.get(user_id)
        
        if not session_id:
            await message.answer(
                "❌ Сначала начни игру командой /start"
            )
            return
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Get session info
                response = await client.get(f"{API_BASE_URL}/sessions/{session_id}")
                
                if response.status_code != 200:
                    await message.answer("❌ Ошибка получения статистики")
                    return
                
                info = response.json()
                
                await message.answer(
                    f"📊 <b>Статистика сессии</b>\n\n"
                    f"🎲 Ходов сделано: {info['current_turn']}\n"
                    f"🧠 Квантов в памяти: {info['quants_count']}\n"
                    f"📝 Размер сводки: {info['summary_length']} символов\n"
                    f"✅ Статус: {'активна' if info['is_active'] else 'неактивна'}\n\n"
                    f"Продолжай приключение!",
                    parse_mode="HTML"
                )
        
        except Exception as e:
            logger.error(f"Error in stats command: {e}", exc_info=True)
            await message.answer("❌ Ошибка при получении статистики")
    
    async def handle_message(self, message: Message, state: FSMContext):
        """Handle regular messages - game actions."""
        user_id = message.from_user.id
        session_id = self.user_sessions.get(user_id)
        
        # Check if session exists
        if not session_id:
            await message.answer(
                "❌ Сначала начни игру командой /start"
            )
            return
        
        # Save last user message for retry
        self.last_user_messages[user_id] = message.text
        
        # Show typing indicator
        typing_task = asyncio.create_task(
            self._keep_typing(message.chat.id)
        )
        
        # Send "preparing" message
        preparing_msg = await message.answer("⏳ Готовлю ответ...")
        
        try:
            logger.debug(f"Sending request to API for session {session_id}")
            async with httpx.AsyncClient(timeout=180.0) as client:  # Увеличен таймаут для медленных ответов
                # Send message to API
                response = await client.post(
                    f"{API_BASE_URL}/sessions/{session_id}/messages",
                    json={
                        "session_id": session_id,
                        "message": message.text
                    }
                )
                
                logger.debug(f"Received response from API, status={response.status_code}")
                
                # Stop typing
                typing_task.cancel()
                
                if response.status_code != 200:
                    error_detail = response.json().get("detail", "Unknown error")
                    logger.error(f"API error: {error_detail}")
                    try:
                        await preparing_msg.delete()
                    except Exception:
                        pass
                    await self.bot.send_message(
                        message.chat.id,
                        f"❌ Ошибка API: {error_detail}\n\n"
                        "Попробуй ещё раз или /start для новой игры."
                    )
                    return
                
                logger.debug("Parsing JSON response")
                data = response.json()
                reply = data["reply"]
                turn_number = data["turn_number"]
                
                logger.debug(f"Formatting reply for turn {turn_number}")
                # Format response (simple text, no HTML to avoid Telegram issues)
                formatted_reply = f"🎲 Ход #{turn_number}\n\n{reply}"
                
                logger.debug("Sending response to Telegram")
                # Try to send response with retries
                await self._send_response_with_retry(
                    message=message,
                    preparing_msg=preparing_msg,
                    formatted_reply=formatted_reply,
                    max_attempts=3
                )
                logger.debug("Response sent successfully")
                
                # Log quants info (debug)
                if data.get("quants_requested"):
                    logger.info(
                        f"Turn {turn_number}: Requested quants: {data['quants_requested']}"
                    )
        
        except httpx.TimeoutException:
            typing_task.cancel()
            logger.error("API timeout")
            try:
                await preparing_msg.delete()
            except Exception:
                pass
            await self.bot.send_message(
                message.chat.id,
                "⏱ Превышено время ожидания. ГМ думает слишком долго.\n\n"
                "Попробуй:\n"
                "/retry - повторить запрос\n"
                "/undo - отменить ход"
            )
        
        except Exception as e:
            typing_task.cancel()
            logger.error(f"Error handling message: {e}", exc_info=True)
            try:
                await preparing_msg.delete()
            except Exception:
                pass
            await self.bot.send_message(
                message.chat.id,
                "❌ Произошла ошибка при обработке.\n\n"
                "Попробуй:\n"
                "/retry - повторить запрос\n"
                "/undo - отменить ход\n"
                "/start - начать новую игру"
            )
    
    async def _send_response_with_retry(
        self, 
        message: Message, 
        preparing_msg: Message, 
        formatted_reply: str,
        max_attempts: int = 5  # Increased from 3
    ):
        """Send response with retry logic for Telegram API timeouts."""
        # Always delete preparing message first (avoids connection timeout issues)
        try:
            await preparing_msg.delete()
        except Exception as e:
            logger.debug(f"Could not delete preparing message: {e}")
        
        chat_id = message.chat.id
        
        for attempt in range(max_attempts):
            try:
                logger.debug(f"Attempt {attempt + 1}/{max_attempts} to send message to chat {chat_id}")
                
                # Send as new message(s) using bot directly (creates fresh connection)
                if len(formatted_reply) > 4000:
                    parts = [formatted_reply[i:i+4000] for i in range(0, len(formatted_reply), 4000)]
                    for part in parts:
                        await self.bot.send_message(chat_id, part)
                else:
                    await self.bot.send_message(chat_id, formatted_reply)
                
                logger.debug(f"Message sent successfully on attempt {attempt + 1}")
                # Success!
                return
            
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {e}")
                
                if attempt < max_attempts - 1:
                    # Shorter wait between retries (1 sec instead of 2)
                    await asyncio.sleep(1)
                else:
                    # Last attempt failed
                    logger.error(f"All {max_attempts} attempts to send response failed")
                    try:
                        await self.bot.send_message(
                            chat_id,
                            "❌ Не удалось доставить ответ (проблема с Telegram API).\n\n"
                            "Ответ получен, но не доставлен.\n"
                            "Попробуй:\n"
                            "/retry - повторить запрос\n"
                            "/undo - отменить ход"
                        )
                    except Exception:
                        logger.error("Failed to send error message")
    
    async def _keep_typing(self, chat_id: int):
        """Keep sending typing indicator while processing."""
        try:
            while True:
                await self.bot.send_chat_action(chat_id, "typing")
                await asyncio.sleep(4)  # Telegram typing lasts ~5 seconds
        except asyncio.CancelledError:
            pass  # Normal cancellation
    
    async def _get_or_create_session(self, user_id: int) -> int:
        """Get existing session or create new one (for continuing game)."""
        # Check if already have session in memory
        if user_id in self.user_sessions:
            return self.user_sessions[user_id]
        
        # Try to get existing session from API
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(
                    f"{API_BASE_URL}/sessions/user/{user_id}",
                    params={"platform_type": "telegram"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    session_id = data["session_id"]
                    self.user_sessions[user_id] = session_id
                    logger.info(f"Found existing session {session_id} for user {user_id}")
                    return session_id
            except Exception as e:
                logger.info(f"No existing session for user {user_id}: {e}")
        
        # Create new session if not found
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/sessions",
                json={
                    "platform_id": str(user_id),
                    "platform_type": "telegram",
                    "session_type": "game"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to create session: {response.text}")
            
            data = response.json()
            session_id = data["session_id"]
            
            # Store mapping
            self.user_sessions[user_id] = session_id
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id
    
    async def _create_new_session(self, user_id: int) -> int:
        """ALWAYS create new session, deactivating old ones."""
        # First, deactivate all old sessions for this user
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # Try to deactivate old session via API
                response = await client.post(
                    f"{API_BASE_URL}/sessions/deactivate",
                    json={
                        "platform_id": str(user_id),
                        "platform_type": "telegram"
                    }
                )
                if response.status_code == 200:
                    logger.info(f"Deactivated old sessions for user {user_id}")
            except Exception as e:
                logger.warning(f"Could not deactivate old sessions: {e}")
        
        # Remove from memory cache
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        # Create new session
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/sessions",
                json={
                    "platform_id": str(user_id),
                    "platform_type": "telegram",
                    "session_type": "game"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to create session: {response.text}")
            
            data = response.json()
            session_id = data["session_id"]
            
            # Store mapping
            self.user_sessions[user_id] = session_id
            
            logger.info(f"Created NEW session {session_id} for user {user_id}")
            return session_id
    
    async def start(self):
        """Start the bot."""
        logger.info("Starting PlexMem Telegram Bot...")
        logger.info(f"Bot token: {settings.telegram_bot_token[:20]}...")
        
        try:
            # Check API availability
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{API_BASE_URL}/")
                if response.status_code == 200:
                    logger.info("API is available")
                else:
                    logger.warning(f"API returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Cannot connect to API: {e}")
            logger.warning("Bot will start anyway, but may not work correctly")
        
        # Start polling
        await self.dp.start_polling(self.bot)
    
    async def stop(self):
        """Stop the bot."""
        logger.info("Stopping PlexMem Telegram Bot...")
        await self.bot.session.close()


async def main():
    """Main entry point."""
    if not settings.telegram_bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        return
    
    bot = PlexMemBot(settings.telegram_bot_token)
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())

