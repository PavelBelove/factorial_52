# Sandbox World Integration Guide

## Созданные файлы

```
data/worlds/sandbox/
├── config.json              # Метаданные мира
├── gm_system.md             # Промпт GM для ведения истории
├── initial_summary.md       # Минимальный стартовый summary
├── initial_quants.json      # Кванты с инструкциями по созданию мира
└── quantizer_instructions.md # Инструкции для квантователя

prompts/
└── summarizer_world_lock.md # Промпт для фиксации мира
```

## Требуемые изменения в коде

### 1. Обработка флага `story_started` в orchestrator.py

В методе `process_turn`, после получения ответа GM (~строка 172-177):

```python
# После извлечения response_data
response_data = gm_response.get("response_data", {})

# ДОБАВИТЬ: Проверка на начало истории (sandbox world lock)
story_started = gm_response.get("story_started", False)
if story_started and db_session.world_id == "sandbox":
    logger.info("Sandbox story started - triggering world lock")
    asyncio.create_task(
        self._world_lock_summarizer(
            session_id=session_id,
            current_turn=current_turn
        )
    )
```

### 2. Добавить метод `_world_lock_summarizer` в orchestrator.py

```python
async def _world_lock_summarizer(
    self,
    session_id: int,
    current_turn: int
) -> None:
    """
    Special summarizer mode for sandbox worlds.
    Crystallizes the world description after creation phase.
    """
    try:
        logger.info(f"Running world lock summarizer for session {session_id}")

        # Get all turns (the world creation dialogue)
        all_turns = self.db.get_recent_turns(session_id, limit=current_turn)

        # Run special summarizer mode
        world_summary = await self.summarizer_agent.summarize(
            existing_summary="",
            turns_to_summarize=all_turns,
            mode="world_lock"
        )

        # Update session summary
        self.db.update_session_summary(session_id, world_summary)

        logger.info(f"World locked for session {session_id}")

    except Exception as e:
        logger.error(f"Error in world lock summarizer: {e}")
```

### 3. Добавить режим `world_lock` в summarizer_agent.py

В классе `SummarizerAgent`:

```python
async def summarize(
    self,
    existing_summary: str,
    turns_to_summarize: List[Dict[str, str]],
    mode: str = "append"
) -> str:
    """
    Create or update summary.

    Modes:
    - "append": Add new turns to existing summary
    - "rewrite": Condense entire history
    - "world_lock": Special mode for sandbox - crystallize world description
    """
    if not turns_to_summarize:
        return existing_summary

    if mode == "append":
        return await self._append_mode(existing_summary, turns_to_summarize)
    elif mode == "rewrite":
        return await self._rewrite_mode(existing_summary, turns_to_summarize)
    elif mode == "world_lock":
        return await self._world_lock_mode(turns_to_summarize)
    else:
        logger.error(f"Unknown summarizer mode: {mode}")
        return existing_summary

async def _world_lock_mode(
    self,
    creation_turns: List[Dict[str, str]]
) -> str:
    """
    World lock mode: Transform creation dialogue into permanent world description.
    Used only for sandbox worlds after story_started flag.
    """
    # Build context from all creation turns
    turns_text = []
    for turn in creation_turns:
        turns_text.append(f"Reader: {turn['user_message']}")
        if turn.get('agent_reply'):
            turns_text.append(f"Narrator: {turn['agent_reply']}")

    context = "# World Creation Dialogue\n\n" + "\n\n".join(turns_text)

    # Get world lock prompt
    system_prompt = self._get_world_lock_system_prompt()

    try:
        world_summary = await self.llm.simple_completion(
            prompt=context,
            system_prompt=system_prompt,
            model=self.model,
            temperature=0.5,
            max_tokens=2000
        )

        log_agent_call(
            agent_name="summarizer_world_lock",
            context=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            response=world_summary
        )

        return world_summary

    except Exception as e:
        logger.error(f"Error in Summarizer (world_lock mode): {e}")
        return ""

def _get_world_lock_system_prompt(self) -> str:
    """System prompt for world lock mode."""
    return get_prompt("summarizer_world_lock")
```

### 4. Добавить константу в utils/prompts.py

```python
PROMPT_SUMMARIZER_WORLD_LOCK = "summarizer_world_lock"
```

И обновить импорты где нужно.

### 5. Обновить gm_agent.py для извлечения story_started

В методе `_parse_json_response`, добавить извлечение флага:

```python
# Существующий код
result["quants"] = data.get("quant_requests", [])
result["response_data"] = data.get("response_data", {})

# ДОБАВИТЬ:
result["story_started"] = data.get("story_started", False)
```

---

## Порядок миров в меню

Сейчас миры отображаются в алфавитном порядке директорий. Чтобы sandbox был последним:

**Вариант 1**: Переименовать в `z_sandbox` (хак)

**Вариант 2**: Добавить поле `order` в config.json и сортировать:

```python
# В world_manager.py, метод get_available_worlds
available.sort(key=lambda w: w.get('order', 100))
```

И в каждом config.json добавить:
```json
{
  "order": 1,  // cyberpunk
  "order": 2,  // fallout
  ...
  "order": 99  // sandbox - последний
}
```

---

## Тестирование

1. Выбрать мир "Чистый лист" в меню
2. Описать мир (можно одним сообщением или по шагам)
3. Описать героя и его Дар (♥)
4. Сказать "начинай" или подтвердить готовность
5. GM должен:
   - Вернуть `story_started: true` в JSON
   - Начать историю
6. Система должна:
   - Запустить world_lock summarizer
   - Сохранить структурированное описание мира в summary
7. Дальнейшая игра идёт как обычно

---

## Пасхальные команды (будущее)

Для скрытых миров типа `/vigook`, `/naruto`:

```python
# В telegram/handlers/commands.py
HIDDEN_WORLDS = {
    "vigook": "idol_yaoi",
    "naruto": "konoha",
    "potter": "hogwarts",
    # ...
}

@router.message(Command("vigook", "naruto", "potter", ...))
async def hidden_world_command(message: Message):
    command = message.text.lstrip("/")
    world_id = HIDDEN_WORLDS.get(command)
    if world_id:
        # Start game with hidden world
        await start_game_with_world(message.from_user.id, world_id)
```

Каждый скрытый мир — отдельная папка в `data/worlds/` с `enabled: true` но `hidden: true` в config.json.
