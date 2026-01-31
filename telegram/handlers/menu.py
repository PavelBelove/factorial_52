"""
Menu handlers for Telegram bot.
Handles all menu navigation, world/language selection, and save/load operations.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from telegram.states import GameStates
from telegram.utils import convert_markdown_to_html
from telegram.keyboards import (
    get_language_keyboard,
    get_main_menu_keyboard,
    get_world_selection_keyboard,
    get_world_description_keyboard,
    get_save_slots_keyboard,
    get_load_slots_keyboard,
    get_settings_keyboard,
    get_back_to_menu_keyboard,
    get_help_keyboard,
    get_difficulty_keyboard,
    get_content_filter_keyboard,
    get_adult_consent_keyboard,
    get_genre_prism_keyboard,
    get_prism_description_keyboard
)
from core.config import settings, get_localization, world_manager
from core.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

# Create router
router = Router()

# Initialize database manager
db = DatabaseManager()


# ============= START & LANGUAGE SELECTION =============

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """
    Handle /start command.
    New users get language selection, existing users get main menu.
    """
    try:
        user_id = message.from_user.id
        
        # Get or create user
        user = db.get_or_create_user(
            platform_id=str(user_id),
            platform_type="telegram"
        )
        
        # Check if user already has language set
        if user.language:
            # Existing user - show main menu (send new message)
            await show_main_menu(message, state, user_id, edit=False)
        else:
            # New user - show language selection
            await state.set_state(GameStates.LANGUAGE_SELECTION)
            
            loc = get_localization("ru")
            text = loc.get_language_selection_message()
            keyboard = get_language_keyboard()
            
            await message.answer(text, reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте позже.")


@router.callback_query(F.data.startswith("lang:"))
async def process_language_selection(callback: CallbackQuery, state: FSMContext):
    """Process language selection."""
    try:
        lang_code = callback.data.split(":")[1]
        user_id = callback.from_user.id
        
        # Get user from DB
        user = db.get_or_create_user(str(user_id))
        
        # Save language preference
        db.set_user_language(user.id, lang_code)
        
        # Save to FSM state too
        await state.update_data(language=lang_code)
        
        await callback.answer(f"Язык установлен: {lang_code}")
        
        # Show main menu (edit existing message)
        await show_main_menu(callback.message, state, user_id, edit=True)
        
    except Exception as e:
        logger.error(f"Error in language selection: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


# ============= MAIN MENU =============

async def show_main_menu(message: Message, state: FSMContext, user_id: int, edit: bool = True):
    """
    Show main menu to user.
    
    Args:
        message: Message object (can be from callback)
        state: FSM context
        user_id: Telegram user ID
        edit: If True, edit existing message. If False, send new message.
    """
    try:
        # Get user from DB
        user = db.get_or_create_user(str(user_id))
        
        # Get localization
        loc = get_localization(user.language)
        
        # Check if user has active game
        active_session = db.get_session_by_platform_id(str(user_id))
        has_active = active_session is not None and active_session.is_active
        
        # Get menu text and keyboard
        text = loc.get_main_menu_message()
        keyboard = get_main_menu_keyboard(has_active_game=has_active, loc=loc)
        
        # Set state
        await state.set_state(GameStates.MAIN_MENU)
        
        # Send or edit message
        if edit:
            # Edit existing message (from callback)
            await message.edit_text(text, reply_markup=keyboard)
        else:
            # Send new message (from command)
            await message.answer(text, reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error showing main menu: {e}", exc_info=True)


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Go back to main menu."""
    await show_main_menu(callback.message, state, callback.from_user.id, edit=True)
    await callback.answer()


# ============= NEW GAME & WORLD SELECTION =============

@router.callback_query(F.data == "new_game")
async def new_game_handler(callback: CallbackQuery, state: FSMContext):
    """Handle new game button - show world selection."""
    try:
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        
        # Get available worlds
        available_worlds = world_manager.get_available_worlds(language=user.language)
        
        # available_worlds уже список словарей с нужными полями
        worlds_list = available_worlds
        
        text = loc.get_world_selection_message()
        keyboard = get_world_selection_keyboard(worlds_list, loc)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(GameStates.WORLD_SELECTION)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in new_game_handler: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data.startswith("world:"))
async def process_world_selection(callback: CallbackQuery, state: FSMContext):
    """Process world selection - show world description."""
    try:
        world_id = callback.data.split(":")[1]
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        
        # Get world config
        world_config = world_manager.get_world_config(world_id)
        if not world_config:
            await callback.answer("Мир не найден")
            return
        
        # Get world description with localization
        world_name_dict = world_config.get("name", world_id)
        world_desc_dict = world_config.get("description", "Описание отсутствует")
        
        # Extract localized strings
        if isinstance(world_name_dict, dict):
            world_name = world_name_dict.get(user.language, world_name_dict.get('ru', world_id))
        else:
            world_name = world_name_dict
            
        if isinstance(world_desc_dict, dict):
            world_desc = world_desc_dict.get(user.language, world_desc_dict.get('ru', ''))
        else:
            world_desc = world_desc_dict
        
        text = f"**{world_name}**\n\n{world_desc}"
        keyboard = get_world_description_keyboard(world_id, loc)
        
        # Save selected world to state
        await state.update_data(selected_world=world_id)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(GameStates.WORLD_DESCRIPTION)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in world selection: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data == "back_to_worlds")
async def back_to_worlds(callback: CallbackQuery, state: FSMContext):
    """Go back to world selection."""
    await new_game_handler(callback, state)


@router.callback_query(F.data.startswith("start:"))
async def start_new_game(callback: CallbackQuery, state: FSMContext):
    """Start new game in selected world."""
    try:
        world_id = callback.data.split(":")[1]
        user_id = callback.from_user.id
        
        # Get user
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        
        # Deactivate old sessions
        db.deactivate_user_sessions(user.id)
        
        # Create new session
        new_session = db.create_session(
            user_id=user.id,
            world_id=world_id
        )
        
        # Load initial quants
        initial_quants = world_manager.get_initial_quants(world_id)
        for quant_data in initial_quants:
            from core.models import Quant, QuantType
            quant = Quant(
                id=quant_data["id"],
                type=QuantType(quant_data.get("type", "other")),
                synopsis=quant_data.get("synopsis", ""),
                body=quant_data.get("body", {}),
                links=quant_data.get("links", {}),
                aliases=quant_data.get("aliases", []),
                created_at=0,
                updated_at=0,
                is_game=True
            )
            db.create_quant(new_session.id, quant)
        
        # Добавляем системный квант с правилами игры
        from core.models import Quant, QuantType
        rules_quant = Quant(
            id="правила_игры",
            type=QuantType.CONCEPT,
            synopsis="Правила игровой механики Факториал 52",
            body={
                "описание": "Игровая механика основана на колоде из 52 карт. Персонаж имеет 4 характеристики: Сила (♠), Магия (♥), Стойкость (♦), Ловкость (♣). Для проверок вне боя тянутся 2 карты, результат = (сумма номиналов * 10) + характеристика + бонусы. В бою также используются 2 карты, черные для атаки, красные для защиты. Урон = атака - защита. Особые комбинации: два туза = невероятный успех, две двойки = катастрофа (только для игроков). За успех +1 к характеристике. Инвентарь расширен по сравнению с оффлайн версией.",
                "инструкция_для_гм": "В первом сообщении скажи игроку, что правила и механики игры описаны в системном кванте 'правила_игры', но если интересно - можешь рассказать подробнее, или игрок может почитать их через меню бота. Не перегружай первое сообщение правилами, лучше сразу перейди к созданию персонажа и началу приключения.",
                "характеристики": "Сила (♠): ближний бой, физическая сила, воля, запугивание. Магия (♥): магическая защита, колдовство, мудрость, общение. Стойкость (♦): физическая защита, выносливость, харизма, торговля. Ловкость (♣): дальний бой, магические атаки, акробатика, меткость, скрытность.",
                "масти_в_бою": "♠ - бонус к ближним атакам, ♥ - бонус к магической защите, ♦ - бонус к физической защите, ♣ - бонус к дальним атакам и магическим атакам"
            },
            links={},
            aliases=["правила", "механики", "система игры"],
            created_at=0,
            updated_at=0,
            is_game=True
        )
        db.create_quant(new_session.id, rules_quant)
        
        # Load initial summary
        initial_summary = world_manager.get_initial_summary(world_id)
        if initial_summary:
            from core.database.models import SummaryDB
            db.create_summary(
                session_id=new_session.id,
                summary_text=initial_summary,
                turns_start=0,
                turns_end=0
            )
        
        # Save world preference
        db.set_user_current_world(user.id, world_id)
        
        # Update state
        await state.update_data(session_id=new_session.id, world_id=world_id)
        await state.set_state(GameStates.IN_GAME)
        
        # Показываем сообщение о создании игры
        await callback.message.edit_text(loc.get_creating_world_message())
        await callback.answer()
        
        # Activate session in API first
        import httpx
        logger.info(f"Activating session {new_session.id} in API")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Create/activate session in API
                api_response = await client.post(
                    "http://localhost:8000/sessions",
                    json={
                        "session_id": new_session.id,
                        "platform_id": str(user_id),
                        "platform_type": "telegram",
                        "session_type": "game"
                    }
                )
                
                if api_response.status_code != 200:
                    logger.error(f"Failed to activate session in API: {api_response.status_code}, {api_response.text}")
                    await callback.message.edit_text(loc.get_error_message())
                    return
                    
                logger.info(f"Session {new_session.id} activated in API successfully")
                
        except Exception as e:
            logger.error(f"Error activating session in API: {e}", exc_info=True)
            await callback.message.edit_text(loc.get_error_message())
            return
        
        # Отправляем первый запрос к ГМ от имени игрока
        api_url = f"http://localhost:8000/sessions/{new_session.id}/messages"

        logger.info(f"Sending initial GM request for session {new_session.id}")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    api_url,
                    json={
                        "session_id": new_session.id,
                        "message": "Объясни правила игры, и давай создадим персонажа"
                    }
                )
                
                logger.info(f"GM response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    gm_response = result.get("reply", "")
                    
                    if gm_response:
                        # Отправляем ответ ГМ игроку
                        # Telegram лимит - 4096 символов, разбиваем на части если нужно
                        header = loc.get_story_started_header()
                        
                        # Convert markdown to HTML
                        gm_response = convert_markdown_to_html(gm_response)
                        
                        full_message = header + gm_response
                        
                        if len(full_message) > 4000:
                            # Разбиваем на части по 3900 символов (запас для безопасности)
                            chunk_size = 3900
                            chunks = []
                            
                            for i in range(0, len(gm_response), chunk_size):
                                chunk = gm_response[i:i + chunk_size]
                                if i == 0:
                                    chunks.append(header + chunk)
                                else:
                                    chunks.append(chunk)
                            
                            logger.info(f"Initial message split into {len(chunks)} chunks")
                            
                            # Первый chunk заменяет текущее сообщение
                            await callback.message.edit_text(chunks[0], parse_mode="HTML")
                            
                            # Остальные отправляем как новые сообщения
                            for chunk in chunks[1:]:
                                await asyncio.sleep(0.5)
                                await callback.message.answer(chunk, parse_mode=None)
                        else:
                            # Сообщение короткое, отправляем целиком
                            await callback.message.edit_text(full_message, parse_mode="HTML")
                        
                        logger.info("Successfully sent initial GM message")
                    else:
                        logger.error("Empty GM response")
                        await callback.message.edit_text(
                            "❌ Ошибка: ГМ вернул пустой ответ. Попробуйте написать что-нибудь."
                        )
                else:
                    logger.error(f"GM API error: {response.status_code}, {response.text}")
                    await callback.message.edit_text(
                        f"❌ Ошибка API ({response.status_code}). Попробуйте написать что-нибудь для начала игры."
                    )
        except httpx.TimeoutException as e:
            logger.error(f"Timeout sending initial GM message: {e}")
            await callback.message.edit_text(
                "⏱️ Превышено время ожидания. Напишите что-нибудь для начала игры."
            )
        except Exception as e:
            logger.error(f"Error sending initial GM message: {e}", exc_info=True)
            await callback.message.edit_text(
                f"❌ Ошибка: {str(e)[:100]}\n\nНапишите что-нибудь для начала игры."
            )
        
    except Exception as e:
        logger.error(f"Error starting new game: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


# ============= CONTINUE GAME =============

@router.callback_query(F.data == "continue")
async def continue_game(callback: CallbackQuery, state: FSMContext):
    """Continue active game."""
    try:
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        
        # Get active session
        active_session = db.get_session_by_platform_id(str(user_id))
        
        if not active_session or not active_session.is_active:
            await callback.answer(loc.get_no_active_game_message())
            return
        
        # Update state
        await state.update_data(
            session_id=active_session.id,
            world_id=active_session.world_id
        )
        await state.set_state(GameStates.IN_GAME)
        
        # Get last turn to remind player where they left off
        last_turns = db.get_recent_turns(active_session.id, limit=1)
        
        if last_turns:
            last_turn = last_turns[0]
            # Truncate if too long (Telegram limit 4096 chars)
            reply_text = last_turn.agent_reply
            max_reply_length = 3500  # Leave space for headers
            if len(reply_text) > max_reply_length:
                reply_text = reply_text[:max_reply_length] + "..."
            
            message = (
                f"{loc.get_story_continues_header()}"
                f"{loc.get_last_chapter_label(last_turn.turn_number)}"
                f"{reply_text}\n\n"
                f"─────────────────────\n"
                f"Напишите свое действие, чтобы продолжить приключение!"
            )
        else:
            message = loc.get_continue_game_message()
        
        await callback.message.edit_text(message, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error continuing game: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


# ============= SAVE GAME =============

@router.callback_query(F.data == "save")
async def save_game_menu(callback: CallbackQuery, state: FSMContext):
    """Show save slots menu."""
    try:
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        
        # Check if there's an active game
        active_session = db.get_session_by_platform_id(str(user_id))
        
        if not active_session or not active_session.is_active:
            await callback.answer(loc.get_no_active_game_message())
            return
        
        # Get saved sessions
        saved_sessions = db.get_user_saved_sessions(user.id)
        
        # Format for keyboard
        saves_list = []
        for session in saved_sessions:
            saves_list.append({
                "slot_number": session.slot_number,
                "world_id": session.world_id,
                "saved_at": session.saved_at.isoformat() if session.saved_at else None
            })
        
        text = loc.get_save_menu_message()
        keyboard = get_save_slots_keyboard(saves_list, loc)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(GameStates.SAVE_MENU)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error showing save menu: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data.startswith("save_slot:"))
async def process_save_slot(callback: CallbackQuery, state: FSMContext):
    """Save game to selected slot."""
    try:
        slot = int(callback.data.split(":")[1])
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        
        # Get active session
        active_session = db.get_session_by_platform_id(str(user_id))
        
        if not active_session:
            await callback.answer(loc.get_no_active_game_message())
            return
        
        # Save to slot
        success = db.save_session_to_slot(active_session.id, slot)
        
        if success:
            await callback.answer(loc.get_game_saved_message(slot))
            await show_main_menu(callback.message, state, user_id, edit=True)
        else:
            await callback.answer(loc.get_error_message())
            
    except Exception as e:
        logger.error(f"Error saving game: {e}", exc_info=True)
        await callback.answer("Ошибка при сохранении")


# ============= LOAD GAME =============

@router.callback_query(F.data == "load")
async def load_game_menu(callback: CallbackQuery, state: FSMContext):
    """Show load slots menu."""
    try:
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        
        # Get saved sessions
        saved_sessions = db.get_user_saved_sessions(user.id)
        
        if not saved_sessions:
            await callback.answer(loc.get_no_saves_message())
            return
        
        # Format for keyboard
        saves_list = []
        for session in saved_sessions:
            saves_list.append({
                "id": session.id,
                "slot_number": session.slot_number,
                "world_id": session.world_id,
                "saved_at": session.saved_at.isoformat() if session.saved_at else None
            })
        
        text = loc.get_load_menu_message()
        keyboard = get_load_slots_keyboard(saves_list, loc)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(GameStates.LOAD_MENU)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error showing load menu: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data.startswith("load_slot:"))
async def process_load_slot(callback: CallbackQuery, state: FSMContext):
    """Load game from selected slot."""
    try:
        session_id = int(callback.data.split(":")[1])
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        
        # Get session
        session = db.get_session_by_id(session_id)
        
        if not session:
            await callback.answer("Сохранение не найдено")
            return
        
        # Deactivate all other sessions
        db.deactivate_user_sessions(user.id)
        
        # Activate loaded session
        from core.database.models import SessionDB
        from sqlalchemy.orm import Session as DBSession
        with db.get_session() as db_session:
            session_obj = db_session.query(SessionDB).filter_by(id=session_id).first()
            if session_obj:
                session_obj.is_active = True
                db_session.commit()
        
        # Update state
        await state.update_data(
            session_id=session.id,
            world_id=session.world_id
        )
        await state.set_state(GameStates.IN_GAME)
        
        # Get last turn to remind player where they left off
        last_turns = db.get_recent_turns(session.id, limit=1)
        
        if last_turns:
            last_turn = last_turns[0]
            # Truncate if too long (Telegram limit 4096 chars)
            reply_text = last_turn.agent_reply
            max_reply_length = 3500  # Leave space for headers
            if len(reply_text) > max_reply_length:
                reply_text = reply_text[:max_reply_length] + "..."
            
            message = (
                f"▶️ <b>История загружена!</b>\n\n"
                f"{loc.get_last_chapter_label(last_turn.turn_number)}"
                f"{reply_text}\n\n"
                f"─────────────────────\n"
                f"Напишите свое действие, чтобы продолжить приключение!"
            )
        else:
            message = loc.get_continue_game_message()
        
        await callback.answer(loc.get_game_loaded_message(session.slot_number))
        await callback.message.edit_text(message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error loading game: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


# ============= SETTINGS =============

@router.callback_query(F.data == "settings")
async def settings_menu(callback: CallbackQuery, state: FSMContext):
    """Show settings menu with current values."""
    try:
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        current_settings = db.get_user_settings(user.id)

        keyboard = get_settings_keyboard(current_settings, loc)
        text = loc.get_settings_menu_message()

        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(GameStates.SETTINGS_MENU)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error showing settings: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data == "settings:language")
async def settings_language(callback: CallbackQuery, state: FSMContext):
    """Show language settings."""
    try:
        keyboard = get_language_keyboard()
        text = "🌐 **Язык интерфейса и игры**\n\nВыберите язык / Choose language:"

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(GameStates.LANGUAGE_SETTINGS)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error showing language settings: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data == "settings:difficulty")
async def settings_difficulty(callback: CallbackQuery, state: FSMContext):
    """Show difficulty settings."""
    try:
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        current = db.get_user_difficulty(user.id)

        keyboard = get_difficulty_keyboard(current, loc)
        text = loc.get_difficulty_settings_message()

        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(GameStates.SETTINGS_MENU)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error showing difficulty settings: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data.startswith("set_difficulty:"))
async def process_difficulty_selection(callback: CallbackQuery, state: FSMContext):
    """Process difficulty selection."""
    try:
        difficulty = callback.data.split(":")[1]
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))

        db.set_user_difficulty(user.id, difficulty)

        diff_names = {"easy": "Лёгкая", "normal": "Обычная", "hard": "Сложная"}
        await callback.answer(f"Сложность: {diff_names.get(difficulty, difficulty)}")

        # Return to settings
        await settings_menu(callback, state)

    except Exception as e:
        logger.error(f"Error setting difficulty: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data == "settings:content")
async def settings_content(callback: CallbackQuery, state: FSMContext):
    """Show content filter settings."""
    try:
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        current = db.get_user_content_filter(user.id)

        keyboard = get_content_filter_keyboard(current, loc)
        text = loc.get_content_filter_settings_message()

        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(GameStates.SETTINGS_MENU)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error showing content settings: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data.startswith("set_content:"))
async def process_content_selection(callback: CallbackQuery, state: FSMContext):
    """Process content filter selection."""
    try:
        content_filter = callback.data.split(":")[1]
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)

        # For adult content, show consent dialog first
        if content_filter == "adult":
            text = loc.get_adult_content_consent_message()
            keyboard = get_adult_consent_keyboard(loc)
            await callback.message.edit_text(text, reply_markup=keyboard)
            await callback.answer()
            return

        # For safe/romantic, set directly
        db.set_user_content_filter(user.id, content_filter)

        filter_names = {"safe": "Безопасный", "romantic": "16+", "adult": "18+"}
        await callback.answer(f"Фильтр: {filter_names.get(content_filter, content_filter)}")

        # Return to settings
        await settings_menu(callback, state)

    except Exception as e:
        logger.error(f"Error setting content filter: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data.startswith("confirm_adult:"))
async def process_adult_consent(callback: CallbackQuery, state: FSMContext):
    """Process adult content consent confirmation."""
    try:
        confirmed = callback.data.split(":")[1] == "yes"
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))

        if confirmed:
            db.set_user_content_filter(user.id, "adult")
            await callback.answer("Фильтр 18+ активирован")
        else:
            await callback.answer("Отменено")

        # Return to settings
        await settings_menu(callback, state)

    except Exception as e:
        logger.error(f"Error processing adult consent: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data == "settings:prism")
async def settings_prism(callback: CallbackQuery, state: FSMContext):
    """Show genre prism settings."""
    try:
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        current = db.get_user_genre_prism(user.id)

        keyboard = get_genre_prism_keyboard(current, loc)
        text = loc.get_genre_prism_settings_message()

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(GameStates.SETTINGS_MENU)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error showing prism settings: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data.startswith("prism:"))
async def show_prism_description(callback: CallbackQuery, state: FSMContext):
    """Show detailed prism description."""
    try:
        prism_id = callback.data.split(":")[1]
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)

        from telegram.keyboards import get_prism_description_keyboard
        keyboard = get_prism_description_keyboard(prism_id, loc)
        text = loc.get_genre_prism_description(prism_id)

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

    except Exception as e:
        logger.error(f"Error showing prism description: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data.startswith("select_prism:"))
async def process_prism_selection(callback: CallbackQuery, state: FSMContext):
    """Process genre prism selection."""
    try:
        prism_id = callback.data.split(":")[1]
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)

        # Set the prism
        db.set_user_genre_prism(user.id, prism_id)

        from core.genre_prisms import get_prism_info
        prism_info = get_prism_info(prism_id, user.language)
        
        await callback.answer(
            f"Призма установлена: {prism_info['emoji']} {prism_info['name']}" if user.language == "ru"
            else f"Prism set: {prism_info['emoji']} {prism_info['name']}"
        )

        # Return to settings
        await settings_menu(callback, state)

    except Exception as e:
        logger.error(f"Error setting prism: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


# ============= HELP =============

@router.callback_query(F.data == "help")
async def help_menu(callback: CallbackQuery, state: FSMContext):
    """Show help information - page 1."""
    try:
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        
        text = loc.get_help_page(1)
        keyboard = get_help_keyboard(current_page=1, loc=loc)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(GameStates.HELP)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error showing help: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())


@router.callback_query(F.data.startswith("help:page:"))
async def help_page_navigation(callback: CallbackQuery, state: FSMContext):
    """Navigate between help pages."""
    try:
        page = int(callback.data.split(":")[-1])
        user_id = callback.from_user.id
        user = db.get_or_create_user(str(user_id))
        loc = get_localization(user.language)
        
        text = loc.get_help_page(page)
        keyboard = get_help_keyboard(current_page=page, loc=loc)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error navigating help pages: {e}", exc_info=True)
        await callback.answer(loc.get_error_message())

