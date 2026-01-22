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
        self.dp.message.register(self.cmd_inventory, Command("inventory"))
        self.dp.message.register(self.cmd_session, Command("session"))
        self.dp.message.register(self.cmd_cost, Command("cost"))
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
        """Show character stats."""
        user_id = message.from_user.id
        session_id = await self._get_or_restore_session(user_id)
        
        if not session_id:
            await message.answer("❌ Нет активной игры. Используйте /start")
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_BASE_URL}/sessions/{session_id}/character")
                
                if response.status_code == 200:
                    char = response.json()
                    stats = (
                        f"⚔️ **Характеристики персонажа**\n\n"
                        f"❤️ HP: {char['hp']}/{char['max_hp']}\n"
                        f"💙 Mana: {char['mana']}/{char['max_mana']}\n"
                        f"💰 Gold: {char['gold']}\n\n"
                        f"**Характеристики:**\n"
                        f"♠️ Сила (Spades): {char['spades']}\n"
                        f"♥️ Магия (Hearts): {char['hearts']}\n"
                        f"♦️ Харизма (Diamonds): {char['diamonds']}\n"
                        f"♣️ Ловкость (Clubs): {char['clubs']}\n\n"
                        f"⭐ Уровень: {char['level']}\n"
                        f"✨ Опыт: {char['xp']}"
                    )
                    await message.answer(stats, parse_mode="Markdown")
                elif response.status_code == 404:
                    await message.answer("❌ Персонаж не создан. Используйте /start")
                else:
                    await message.answer("❌ Ошибка получения характеристик")
        
        except Exception as e:
            logger.error(f"Error in stats: {e}")
            await message.answer("❌ Ошибка")
    
    async def cmd_inventory(self, message: Message):
        """Show inventory."""
        user_id = message.from_user.id
        session_id = await self._get_or_restore_session(user_id)
        
        if not session_id:
            await message.answer("❌ Нет активной игры. Используйте /start")
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_BASE_URL}/sessions/{session_id}/inventory")
                
                if response.status_code == 200:
                    data = response.json()
                    inventory = data['inventory']
                    equipped = data['equipped']
                    
                    # Format equipped items
                    equipped_text = ""
                    if equipped:
                        equipped_text = "**Экипировано:**\n"
                        for slot, item in equipped.items():
                            suit_emoji = item.get('suit', '')
                            bonus = item.get('bonus', 0)
                            equipped_text += f"• {slot}: {item['id']} {suit_emoji} (+{bonus})\n"
                        equipped_text += "\n"
                    
                    # Format inventory items
                    if inventory:
                        inv_text = f"🎒 **Инвентарь** ({len(inventory)} предметов)\n\n"
                        inv_text += equipped_text
                        
                        inv_text += "**В сумке:**\n"
                        for item in inventory:
                            suit_emoji = item.get('suit', '')
                            bonus = item.get('bonus', 0)
                            item_type = item.get('type', '')
                            
                            if bonus > 0:
                                inv_text += f"• {item['id']} {suit_emoji} (+{bonus}) [{item_type}]\n"
                            else:
                                inv_text += f"• {item['id']} [{item_type}]\n"
                        
                        # Split if too long
                        if len(inv_text) > 4000:
                            inv_text = inv_text[:3950] + "\n\n... (список обрезан)"
                        
                        await message.answer(inv_text, parse_mode="Markdown")
                    else:
                        await message.answer("🎒 Инвентарь пуст")
                        
                elif response.status_code == 404:
                    await message.answer("❌ Персонаж не создан. Используйте /start")
                else:
                    await message.answer("❌ Ошибка получения инвентаря")
        
        except Exception as e:
            logger.error(f"Error in inventory: {e}")
            await message.answer("❌ Ошибка")
    
    async def cmd_session(self, message: Message):
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
                        f"📊 **Статистика сессии**\n\n"
                        f"🎲 Ходов: {info['current_turn']}\n"
                        f"🧠 Квантов: {info['quants_count']}\n"
                        f"📝 Размер сводки: {info['summary_length']} символов"
                    )
                    await message.answer(stats, parse_mode="Markdown")
                else:
                    await message.answer("❌ Ошибка получения статистики")
        
        except Exception as e:
            logger.error(f"Error in session: {e}")
            await message.answer("❌ Ошибка")
    
    async def cmd_cost(self, message: Message):
        """Show cost breakdown for session."""
        user_id = message.from_user.id
        session_id = await self._get_or_restore_session(user_id)
        
        if not session_id:
            await message.answer("❌ Нет активной игры")
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_BASE_URL}/sessions/{session_id}/costs")
                
                if response.status_code == 200:
                    data = response.json()
                    costs = data["costs"]
                    formatted = data["costs_formatted"]
                    num_turns = data["num_turns"]
                    
                    cost_text = (
                        f"💰 Расходы за сессию\n\n"
                        f"🎲 Ходов: {num_turns}\n\n"
                        f"📊 Затраты по агентам:\n"
                        f"🎭 ГМ:          {formatted['gm']}\n"
                        f"🧠 Квантователь: {formatted['quantizer']}\n"
                        f"📝 Суммаризатор: {formatted['summarizer']}\n"
                        f"🔄 Переводчик:   {formatted['translator']}\n\n"
                        f"💵 Всего: {formatted['total']}\n\n"
                    )
                    
                    # Add per-turn average
                    if num_turns > 0:
                        avg = costs['total'] / num_turns
                        cost_text += f"📉 В среднем за ход: ${avg:.6f}"
                    
                    await message.answer(cost_text)
                else:
                    await message.answer("❌ Ошибка получения статистики затрат")
        
        except Exception as e:
            logger.error(f"Error in cost: {e}")
            await message.answer("❌ Ошибка")
    
    async def cmd_help(self, message: Message):
        """Show help."""
        help_text = (
            "🎮 **PlexMem RPG: Ваше Приключение с ИИ**\n\n"
            
            "**Добро пожаловать в уникальную текстовую RPG!**\n\n"
            
            "Это не просто игра — это живой мир, где каждое решение имеет значение. "
            "Искусственный интеллект выступает вашим Гейм-Мастером, создавая уникальную историю "
            "специально для вас.\n\n"
            
            "🎭 **Что делает эту игру особенной:**\n"
            "• **Квантовая память** — ИИ помнит всё: персонажей, места, события, обещания\n"
            "• **Карточная механика \"Factorial 52!\"** — проверки на картах, бой, развитие персонажа\n"
            "• **Полная свобода действий** — нет сценария, только ваша фантазия\n"
            "• **Реальные последствия** — каждое действие меняет мир вокруг вас\n"
            "• **Живые NPC** — персонажи помнят вас и реагируют на ваши поступки\n\n"
            
            "📜 **Как играть:**\n"
            "1️⃣ Используйте /start чтобы создать персонажа и начать приключение\n"
            "2️⃣ Просто пишите свои действия обычным текстом — ГМ всё поймёт\n"
            "3️⃣ Игра автоматически тянет карты для проверок и боя\n"
            "4️⃣ ГМ описывает результаты и реакцию мира\n"
            "5️⃣ Повторяйте — ваша история разворачивается!\n\n"
            
            "🎲 **Механика игры:**\n"
            "• Карты определяют успех действий (чем выше — тем лучше)\n"
            "• Четыре характеристики: ♠ Сила, ♥ Магия, ♦ Харизма, ♣ Ловкость\n"
            "• Комбинации карт дают бонусы (пара, масть)\n"
            "• Критические успехи и провалы (АА, 22)\n"
            "• Инвентарь, квесты, опыт — всё как в настоящей RPG\n\n"
            
            "🎯 **Роль Гейм-Мастера:**\n"
            "ИИ-ГМ ведёт повествование, играет всех NPC, управляет миром и механикой. "
            "Он создаёт атмосферные описания, ведёт диалоги, подкидывает сюжетные повороты. "
            "Все расчёты, проверки и последствия — автоматические. Вам остаётся только играть!\n\n"
            
            "💡 **Советы:**\n"
            "• Описывайте действия детально — ГМ оценит креативность\n"
            "• Взаимодействуйте с NPC — у них своя жизнь и секреты\n"
            "• Исследуйте мир — награды ждут смелых\n"
            "• Используйте /stats чтобы видеть характеристики персонажа\n"
            "• Используйте /undo если хотите изменить последнее действие\n\n"
            
            "⚡ **Команды:**\n"
            "/stats — характеристики персонажа (HP, мана, характеристики)\n"
            "/inventory — инвентарь и экипировка\n"
            "/retry — повторить последний ход (если ГМ завис)\n"
            "/undo — отменить последний ход\n"
            "/session — статистика сессии (ходы, кванты)\n"
            "/cost — расходы на API (для разработчиков)\n"
            "/help — эта справка\n\n"
            
            "🌟 **Каждая игра уникальна!**\n"
            "Начните приключение прямо сейчас командой /start\n\n"
            
            "Удачи, искатель приключений! 🗡️"
        )
        await message.answer(help_text, parse_mode="Markdown")
    
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
                    
                    # Split long messages (Telegram limit: 4096 chars)
                    if len(reply) > 4000:
                        # Split into chunks
                        header = f"🎲 Ход #{data['turn_number']}\n\n"
                        content = data['reply']
                        chunk_size = 3900  # Leave margin for safety
                        
                        chunks = []
                        for i in range(0, len(content), chunk_size):
                            chunk = content[i:i + chunk_size]
                            if i == 0:
                                chunks.append(header + chunk)
                            else:
                                chunks.append(chunk)
                        
                        logger.info(f"Message split into {len(chunks)} chunks")
                        
                        for idx, chunk in enumerate(chunks):
                            await message.answer(chunk, parse_mode=None)
                            if idx < len(chunks) - 1:
                                await asyncio.sleep(0.5)  # Small delay between chunks
                    else:
                        # Send normally
                        await message.answer(reply, parse_mode=None)
                    
                    logger.info(f"Turn {data['turn_number']} completed for user {user_id}")
                else:
                    await message.answer("❌ Ошибка API")
        
        except httpx.TimeoutException:
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

