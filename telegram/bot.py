"""
PlexMem Telegram Bot with FSM navigation and world selection.
Integrates menu system with game logic.
"""
import asyncio
import logging
from typing import Optional
import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import settings
from core.utils.logger import setup_logging
from core.database.db_manager import DatabaseManager

# Import handlers
from telegram.handlers import menu_router
from telegram.states import GameStates

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Initialize database
db = DatabaseManager()


class PlexMemBot:
    """PlexMem Telegram bot with menu system."""
    
    def __init__(self, token: str):
        """Initialize bot."""
        # Initialize Bot
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        
        # Include menu router
        self.dp.include_router(menu_router)
        
        # Register command handlers FIRST (priority over game messages)
        self.dp.message.register(self.cmd_menu, Command("menu"))
        self.dp.message.register(self.cmd_menu, Command("start"))  # /start тоже открывает меню
        self.dp.message.register(self.cmd_retry, Command("retry"))
        self.dp.message.register(self.cmd_undo, Command("undo"))
        self.dp.message.register(self.cmd_stats, Command("stats"))
        self.dp.message.register(self.cmd_inventory, Command("inventory"))
        self.dp.message.register(self.cmd_session, Command("session"))
        self.dp.message.register(self.cmd_cost, Command("cost"))
        self.dp.message.register(self.cmd_help, Command("help"))
        
        # Register game message handler for IN_GAME state
        self.dp.message.register(self.handle_game_message, GameStates.IN_GAME, F.text)

        # Fallback handler for text messages when state is lost (after restart)
        # This catches messages when user is NOT in IN_GAME state but has active session
        self.dp.message.register(self.handle_orphan_message, F.text)

        # Store last message for retry
        self.last_user_messages = {}
    
    # ============= SESSION RESTORATION =============

    async def handle_orphan_message(self, message: Message, state: FSMContext):
        """
        Handle text messages when FSM state is lost (after bot/API restart).
        Tries to restore session from DB and process the message.
        """
        user_id = message.from_user.id

        # Try to restore session from DB
        session_id = await self._restore_session_if_needed(user_id, state)

        if session_id:
            # Session restored! Process message as normal game message
            logger.info(f"Restored session {session_id} for orphan message from user {user_id}")
            self.last_user_messages[user_id] = message.text
            await self._process_game_message(message, session_id, message.text)
        else:
            # No active session - prompt user to use menu
            await message.answer(
                "👋 Привет! У вас нет активной игры.\n\n"
                "Используйте /menu чтобы начать новую игру или продолжить сохранённую."
            )

    async def _restore_session_if_needed(self, user_id: int, state: FSMContext) -> Optional[int]:
        """
        Restore session from DB if not in FSM state.
        Returns session_id or None if no active session.
        """
        state_data = await state.get_data()
        session_id = state_data.get('session_id')

        if session_id:
            return session_id

        # Try to restore from DB
        active_session = db.get_session_by_platform_id(str(user_id))

        if active_session and active_session.is_active:
            # Restore FSM state
            await state.update_data(
                session_id=active_session.id,
                world_id=active_session.world_id
            )
            await state.set_state(GameStates.IN_GAME)
            logger.info(f"Session {active_session.id} restored for user {user_id}")
            return active_session.id

        return None

    # ============= IN-GAME MESSAGE HANDLING =============

    async def handle_game_message(self, message: Message, state: FSMContext):
        """Handle messages during active game."""
        user_id = message.from_user.id

        # Try to get or restore session
        session_id = await self._restore_session_if_needed(user_id, state)

        if not session_id:
            await message.answer("❌ Нет активной игры. Используйте /menu для начала")
            return
                
        # Save for retry
        self.last_user_messages[user_id] = message.text
        
        # Process message
        await self._process_game_message(message, session_id, message.text)
    
    async def _process_game_message(self, message: Message, session_id: int, text: str):
        """Process game message and send to API."""
        user_id = message.from_user.id
        
        try:
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
                
                if response.status_code == 200:
                    data = response.json()

                    # Extract only narrative if reply contains JSON
                    reply_text = data['reply']

                    # Try to parse as JSON and extract narrative
                    import json as json_module
                    import re

                    if reply_text.strip().startswith('{'):
                        extracted = False

                        # Method 1: Try full JSON parse
                        try:
                            parsed = json_module.loads(reply_text)
                            if 'narrative' in parsed:
                                reply_text = parsed['narrative']
                                extracted = True
                            elif 'gm_narrative' in parsed:
                                reply_text = parsed['gm_narrative']
                                extracted = True
                        except json_module.JSONDecodeError:
                            pass

                        # Method 2: Regex for truncated JSON
                        if not extracted:
                            # Try to extract narrative field from truncated JSON
                            match = re.search(r'"(?:narrative|gm_narrative)"\s*:\s*"((?:[^"\\]|\\.)*)(?:"|\Z)', reply_text, re.DOTALL)
                            if match:
                                narrative = match.group(1)
                                # Unescape JSON string
                                narrative = narrative.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
                                reply_text = narrative
                                extracted = True
                                logger.info("Extracted narrative from truncated JSON via regex")

                        # Method 3: Last resort - strip JSON wrapper
                        if not extracted:
                            # Try to extract any readable text from malformed JSON
                            # Remove JSON structure and clean up
                            cleaned = re.sub(r'^[\s\{]*"[^"]*"\s*:\s*"?', '', reply_text)
                            cleaned = re.sub(r'"\s*[,\}].*$', '', cleaned, flags=re.DOTALL)
                            if len(cleaned) > 50:  # Only use if substantial content
                                reply_text = cleaned.replace('\\n', '\n').replace('\\"', '"')
                                logger.warning("Used last-resort JSON cleanup")
                    
                    reply = f"🎲 Ход #{data['turn_number']}\n\n{reply_text}"
                    
                    # Split long messages
                    if len(reply) > 4000:
                        header = f"🎲 Ход #{data['turn_number']}\n\n"
                        content = reply_text  # Use extracted narrative, not raw reply!
                        chunk_size = 3900
                        
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
                                await asyncio.sleep(0.5)
                    else:
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
    
    # ============= COMMAND HANDLERS =============
    
    async def cmd_menu(self, message: Message, state: FSMContext):
        """Return to main menu."""
        from telegram.handlers.menu import show_main_menu
        await show_main_menu(message, state, message.from_user.id, edit=False)
    
    async def cmd_retry(self, message: Message, state: FSMContext):
        """Retry last message."""
        user_id = message.from_user.id

        last_msg = self.last_user_messages.get(user_id)
        if not last_msg:
            await message.answer("❌ Нет сообщения для повтора")
            return

        session_id = await self._restore_session_if_needed(user_id, state)

        if not session_id:
            await message.answer("❌ Нет активной игры. Используйте /menu")
            return
        
        try:
            # Undo last turn
            async with httpx.AsyncClient(timeout=30.0) as client:
                undo_response = await client.post(
                    f"{API_BASE_URL}/sessions/{session_id}/undo"
                )
                
                if undo_response.status_code != 200:
                    await message.answer("❌ Не могу откатить последний ход")
                    return
                
                undo_data = undo_response.json()
            
            await message.answer(f"🔄 Повторяю с хода {undo_data['current_turn']}: {last_msg[:50]}...")
            
            # Process as regular message
            await self._process_game_message(message, session_id, last_msg)
        
        except Exception as e:
            logger.error(f"Error in /retry: {e}", exc_info=True)
            await message.answer(f"❌ Ошибка retry: {str(e)[:100]}")
    
    async def cmd_undo(self, message: Message, state: FSMContext):
        """Undo last turn."""
        user_id = message.from_user.id
        session_id = await self._restore_session_if_needed(user_id, state)

        if not session_id:
            await message.answer("❌ Нет активной игры. Используйте /menu")
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
                elif response.status_code == 400:
                    await message.answer("❌ Нечего отменять (игра на 0 ходу)")
                else:
                    await message.answer(f"❌ Ошибка отмены: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error in /undo: {e}", exc_info=True)
            await message.answer(f"❌ Ошибка: {str(e)[:100]}")
    
    async def cmd_stats(self, message: Message, state: FSMContext):
        """Show character stats."""
        user_id = message.from_user.id
        session_id = await self._restore_session_if_needed(user_id, state)

        if not session_id:
            await message.answer("❌ Нет активной игры. Используйте /menu")
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_BASE_URL}/sessions/{session_id}/character")
                
                if response.status_code == 200:
                    char = response.json()
                    stats = (
                        f"⚔️ ХАРАКТЕРИСТИКИ ПЕРСОНАЖА\n\n"
                        f"❤️ HP: {char['hp']}/{char['max_hp']}\n"
                        f"💙 Mana: {char['mana']}/{char['max_mana']}\n"
                        f"💰 Gold: {char['gold']}\n\n"
                        f"📊 Характеристики:\n"
                        f"  ♠️ Сила (Spades): {char['spades']} (XP: {char['spades_xp']}/10)\n"
                        f"  ♥️ Магия (Hearts): {char['hearts']} (XP: {char['hearts_xp']}/10)\n"
                        f"  ♦️ Харизма (Diamonds): {char['diamonds']} (XP: {char['diamonds_xp']}/10)\n"
                        f"  ♣️ Ловкость (Clubs): {char['clubs']} (XP: {char['clubs_xp']}/10)\n\n"
                        f"💡 При 10 XP характеристика повышается на 1"
                    )
                    await message.answer(stats)
                elif response.status_code == 404:
                    await message.answer("❌ Персонаж не создан")
                else:
                    await message.answer("❌ Ошибка получения характеристик")
        
        except Exception as e:
            logger.error(f"Error in stats: {e}")
            await message.answer("❌ Ошибка")
    
    async def cmd_inventory(self, message: Message, state: FSMContext):
        """Show inventory."""
        user_id = message.from_user.id
        session_id = await self._restore_session_if_needed(user_id, state)

        if not session_id:
            await message.answer("❌ Нет активной игры. Используйте /menu")
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_BASE_URL}/sessions/{session_id}/inventory")
                
                if response.status_code == 200:
                    data = response.json()
                    inventory = data['inventory']
                    equipped = data['equipped']
                    
                    equipped_text = ""
                    if equipped:
                        equipped_text = "📌 Экипировано:\n"
                        for slot, item in equipped.items():
                            suit_emoji = item.get('suit', '')
                            bonus = item.get('bonus', 0)
                            equipped_text += f"  • {slot}: {item['id']} {suit_emoji} (+{bonus})\n"
                        equipped_text += "\n"
                    
                    if inventory:
                        inv_text = f"🎒 Инвентарь ({len(inventory)} предметов)\n\n"
                        inv_text += equipped_text
                        
                        inv_text += "🎁 В сумке:\n"
                        for item in inventory:
                            suit_emoji = item.get('suit', '')
                            bonus = item.get('bonus', 0)
                            item_type = item.get('type', '')
                            
                            if bonus > 0:
                                inv_text += f"  • {item['id']} {suit_emoji} (+{bonus}) [{item_type}]\n"
                            else:
                                inv_text += f"  • {item['id']} [{item_type}]\n"
                        
                        if len(inv_text) > 4000:
                            inv_text = inv_text[:3950] + "\n\n... (список обрезан)"
                        
                        await message.answer(inv_text)
                    else:
                        await message.answer("🎒 Инвентарь пуст")
                        
                elif response.status_code == 404:
                    await message.answer("❌ Персонаж не создан")
                else:
                    await message.answer("❌ Ошибка получения инвентаря")
        
        except Exception as e:
            logger.error(f"Error in inventory: {e}")
            await message.answer("❌ Ошибка")
    
    async def cmd_session(self, message: Message, state: FSMContext):
        """Show session stats."""
        user_id = message.from_user.id
        session_id = await self._restore_session_if_needed(user_id, state)

        if not session_id:
            await message.answer("❌ Нет активной игры. Используйте /menu")
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_BASE_URL}/sessions/{session_id}")
                
                if response.status_code == 200:
                    info = response.json()
                    stats = (
                        f"📊 СТАТИСТИКА СЕССИИ\n\n"
                        f"🎲 Ходов: {info['current_turn']}\n"
                        f"🧠 Квантов: {info['quants_count']}\n"
                        f"📝 Размер сводки: {info['summary_length']} символов"
                    )
                    await message.answer(stats)
                else:
                    await message.answer("❌ Ошибка получения статистики")
        
        except Exception as e:
            logger.error(f"Error in session: {e}")
            await message.answer("❌ Ошибка")
    
    async def cmd_cost(self, message: Message, state: FSMContext):
        """Show cost breakdown."""
        user_id = message.from_user.id
        session_id = await self._restore_session_if_needed(user_id, state)

        if not session_id:
            await message.answer("❌ Нет активной игры. Используйте /menu")
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
                    
                    if num_turns > 0:
                        avg = costs['total'] / num_turns
                        cost_text += f"📉 В среднем за ход: ${avg:.6f}"
                    
                    await message.answer(cost_text)
                else:
                    await message.answer("❌ Ошибка получения статистики затрат")
        
        except Exception as e:
            logger.error(f"Error in cost: {e}")
            await message.answer("❌ Ошибка")
    
    async def cmd_help(self, message: Message, state: FSMContext):
        """Show help."""
        help_text = (
            "🎮 **PlexMem RPG: Ваше Приключение с ИИ**\n\n"
            
            "**Добро пожаловать в уникальную текстовую RPG!**\n\n"
            
            "Это не просто игра — это живой мир, где каждое решение имеет значение. "
            "Искусственный интеллект выступает вашим Гейм-Мастером, создавая уникальную историю "
            "специально для вас.\n\n"
            
            "🎭 **Что делает эту игру особенной:**\n"
            "• **Квантовая память** — ИИ помнит всё: персонажей, места, события\n"
            "• **Карточная механика \"Factorial 52!\"** — проверки, бой, развитие\n"
            "• **Полная свобода действий** — нет сценария, только фантазия\n"
            "• **Множество миров** — исекай, киберпанк, стимпанк и другие\n"
            "• **Живые NPC** — персонажи помнят вас и реагируют\n\n"
            
            "⚡ **Команды:**\n"
            "/menu — главное меню (новая игра, загрузка, настройки)\n"
            "/stats — характеристики персонажа\n"
            "/inventory — инвентарь и экипировка\n"
            "/retry — повторить последний ход\n"
            "/undo — отменить последний ход\n"
            "/session — статистика сессии\n"
            "/cost — расходы на API\n"
            "/help — эта справка\n\n"
            
            "🌟 **Начните приключение командой /menu!** 🗡️"
        )
        await message.answer(help_text, parse_mode="Markdown")
    
    # ============= BOT LIFECYCLE =============
    
    async def start(self):
        """Start bot."""
        logger.info("Starting PlexMem Bot with FSM navigation")
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
    
    bot = PlexMemBot(settings.telegram_bot_token)
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
