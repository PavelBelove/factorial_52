"""
Quantizer Agent - manages memory updates.
Creates, updates, and maintains quants based on dialogue history.
"""
import json
import logging
from typing import List, Dict, Any, Optional

from core.llm.openrouter_client import OpenRouterClient
from core.models import Quant

logger = logging.getLogger(__name__)


class QuantizerAgent:
    """
    Quantizer Agent - background memory maintenance.
    
    Responsibilities:
    - Create new quants
    - Update existing quants
    - Fix contradictions
    - Manage semantic links
    
    Does NOT:
    - Participate in dialogue
    - Influence narrative style
    - Choose which quants are active
    """
    
    def __init__(self, llm_client: OpenRouterClient, memory_manager, model: Optional[str] = None):
        """Initialize Quantizer agent."""
        self.llm = llm_client
        self.memory_manager = memory_manager
        self.model = model  # Can override default model
    
    async def process_memory_updates(
        self,
        session_id: int,
        summary_text: str,
        recent_turns: List[Dict[str, str]],
        active_quants: List[Quant],
        current_turn: int
    ) -> Dict[str, Any]:
        """
        Analyze recent dialogue and generate memory update commands.
        
        Args:
            summary_text: Current session summary
            recent_turns: Recent conversation turns
            active_quants: Currently active quants
            current_turn: Current turn number
        
        Returns:
            Dict with commands in format:
            {
                "create_EntityName": {full quant data},
                "append_EntityName_body_notes": "new note",
                "replace_EntityName_links_OtherEntity": "new relation",
                "delete_OldEntity": null
            }
        """
        # Build context for quantizer
        context = self._build_quantizer_context(
            session_id,
            summary_text,
            recent_turns,
            active_quants,
            current_turn
        )
        
        # System prompt for quantizer
        system_prompt = self._get_quantizer_system_prompt()
        
        try:
            # Call LLM with max_tokens
            from core.config import settings
            response = await self.llm.json_completion(
                prompt=context,
                system_prompt=system_prompt,
                model=self.model,
                temperature=0.5,  # Lower temperature for more consistent structure
                max_tokens=settings.quantizer_max_tokens
            )
            
            # Validate and return commands
            return self._validate_commands(response)
        
        except Exception as e:
            logger.error(f"Error in Quantizer agent: {e}")
            return {}
    
    def _build_quantizer_context(
        self,
        session_id: int,
        summary_text: str,
        recent_turns: List[Dict[str, str]],
        active_quants: List[Quant],
        current_turn: int
    ) -> str:
        """Build context for quantizer."""
        context_parts = []
        
        # Summary
        if summary_text:
            context_parts.append(f"# История сессии (краткая)\n\n{summary_text[:1000]}...")
        
        # Active quants
        if active_quants:
            quants_json = []
            for q in active_quants:
                quants_json.append({
                    "id": q.id,
                    "type": q.type.value,
                    "body": q.body,
                    "links": q.links,
                    "updated_at": q.updated_at
                })
            
            context_parts.append(
                f"# Активные кванты\n\n```json\n{json.dumps(quants_json, ensure_ascii=False, indent=2)}\n```"
            )
        
        # Synopsis of recent quants (quick navigation)
        synopsis_list = self.memory_manager.get_recent_quants_synopsis(
            session_id,
            current_turn
        )
        if synopsis_list:
            context_parts.append(f"# Доступные кванты (последние обновления)\n\n{synopsis_list}")
        
        # Recent turns
        turns_text = []
        for turn in recent_turns[-5:]:  # Last 5 turns
            turns_text.append(f"Игрок: {turn['user_message']}")
            turns_text.append(f"ГМ: {turn['agent_reply']}")
        
        if turns_text:
            context_parts.append(f"# Последние ходы\n\n" + "\n\n".join(turns_text))
        
        context_parts.append(f"\n# Текущий ход: {current_turn}")
        
        return "\n\n".join(context_parts)
    
    def _get_quantizer_system_prompt(self) -> str:
        """System prompt for Quantizer."""
        return """# Роль: Квантователь памяти

Ты управляешь долговременной памятью системы. Твоя задача - анализировать недавние ходы диалога и обновлять кванты (атомарные единицы памяти).

## Твои задачи:
1. Создавать новые кванты для важных сущностей (NPC, локации, предметы, события)
2. Обновлять существующие кванты новой информацией
3. Поддерживать семантические связи между квантами
4. Исправлять противоречия
5. Удалять устаревшие кванты

## Формат команд:

### Создание кванта:
```json
{
  "create_ИмяКванта": {
    "type": "npc",
    "synopsis": "Краткое описание с =маркерами_квантов=",
    "body": {"role": "описание", "notes": "заметки"},
    "links": {"ДругойКвант": "семантическая связь"},
    "is_game": true
  }
}
```

**ВАЖНО про synopsis:**
- Краткое (макс. 1-2 предложения) описание сущности
- Используй маркеры =ИмяКванта= для отсылок на другие кванты
- Пример: "Официантка в таверне =Золотой_Телец=, город =Архонт="
- Это помогает ГМ и квантователю быстро ориентироваться в доступных квантах

### Дополнение (append):
```json
{
  "append_ИмяКванта_body_notes": "новая информация, которая дополняет существующую",
  "replace_ИмяКванта_synopsis": "Обновленный краткий synopsis с =маркерами="
}
```

**Обновляй synopsis** при изменении ключевой информации о кванте.

### Замена (replace):
```json
{
  "replace_ИмяКванта_body_role": "новое значение, заменяющее старое",
  "replace_ИмяКванта_links_Таверна": "изменившаяся связь"
}
```

### Удаление:
```json
{
  "delete_СтарыйКвант": null
}
```

### Переименование (когда NPC представился):
```json
{
  "rename_Дриада_из_леса": "Ивушка"
}
```
**Используй когда:** безымянный NPC получил имя собственное. Старое имя сохранится как алиас.

## Типы квантов:

- **npc**: Персонажи, NPC (имя обязательно!)
- **location**: Места, локации
- **item**: Предметы, артефакты
- **faction**: Группы, организации, фракции
- **event**: Завершённые события, что уже произошло
- **scene**: Сюжетные сцены, значимые моменты повествования (отдельные эпизоды, которые стоит выделить)
- **quest**: Задания, миссии
- **promise**: Обещания, договорённости, намерения ("сделаем позже", "встретимся завтра", "вернусь за наградой")
- **concept**: Абстрактные концепты, правила, системы
- **other**: Прочее

## Навигация по квантам:

**📋 Список доступных квантов:**
- Ты видишь секцию "Доступные кванты (последние обновления)" - это кванты из последних 30 ходов
- **ВСЕГДА проверяй этот список** перед созданием нового кванта
- Если сущность уже есть - используй update/append, НЕ create
- Это помогает избежать дублей вроде "Лилит" и "Лилит_официантка"

## Важные правила:

1. **🔴 КРИТИЧНО - Парность связей**: Если создаёшь/обновляешь связь A → B, ОБЯЗАТЕЛЬНО создай обратную B → A
   - Пример: Если добавил в "Лира" ссылку на "Зачарованный_лес", добавь в "Зачарованный_лес" ссылку на "Лира"
   - Это ОБЯЗАТЕЛЬНОЕ правило, не пропускай!

2. **Переименование NPC**: Когда безымянный NPC представился, используй `rename`:
   - `rename_Дриада_из_леса: "Ивушка"` - старое имя станет алиасом
   - Оба имени будут работать для поиска

3. **Имена квантов**: Используй точные имена из контекста или выделенные =маркерами=

4. **Имена NPC**: Всегда давай имена важным NPC, не оставляй "безымянный торговец"

5. **Сцены vs События**: `scene` - для отдельных сюжетных моментов, `event` - для завершённых фактов

6. **Промисы**: Обязательно создавай кванты типа `promise` для отложенных действий, планов, договорённостей

7. **Семантичность связей**: Связи должны быть читаемыми ("работает в", "дочь", "враг")

8. **Минимализм**: Обновляй только то, что действительно изменилось или появилось

## Примеры:

### Пример 1: NPC и сцена
```json
{
  "create_Маша": {
    "type": "npc",
    "body": {
      "role": "официантка",
      "appearance": "тихая, наблюдательная",
      "notes": "познакомилась с игроком"
    },
    "links": {
      "Таверна_Атарикс": "работает официанткой"
    },
    "is_game": true
  },
  "create_Знакомство_с_Машей": {
    "type": "scene",
    "body": {
      "description": "Игрок впервые встретил Машу в таверне, она принесла ему эль",
      "turn": 15
    },
    "links": {
      "Маша": "главный персонаж сцены",
      "Таверна_Атарикс": "место действия"
    },
    "is_game": true
  }
}
```

### Пример 2: Промис (обещание на потом)
```json
{
  "create_Обещание_вернуться_за_мечом": {
    "type": "promise",
    "body": {
      "who": "Игрок",
      "what": "обещал кузнецу вернуться через неделю за заказанным мечом",
      "when": "через неделю",
      "where": "кузница Торина"
    },
    "links": {
      "Торин_кузнец": "тот, кому обещано",
      "Меч_с_руной_огня": "предмет обещания"
    },
    "is_game": true
  },
  "append_Торин_кузнец_links_Обещание_вернуться_за_мечом": "ждёт игрока за мечом"
}
```

### Пример 3: Переименование + backlinks
```json
{
  "rename_Полуэльфийка_из_деревни": "Элара",
  "append_Зачарованный_лес_links_Элара": "родом из деревни у границы леса",
  "append_Элара_links_Зачарованный_лес": "родные места"
}
```

Отвечай ТОЛЬКО валидным JSON с командами. Если обновлений не требуется - верни пустой объект {}.
"""
    
    def _validate_commands(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate command structure."""
        if not isinstance(response, dict):
            logger.warning("Quantizer response is not a dict")
            return {}
        
        # Filter out invalid commands
        valid_commands = {}
        
        for key, value in response.items():
            # Check command format
            parts = key.split("_", 1)
            if len(parts) < 2:
                logger.warning(f"Invalid command format: {key}")
                continue
            
            action = parts[0].lower()
            
            if action not in ["create", "append", "replace", "delete"]:
                logger.warning(f"Unknown action: {action}")
                continue
            
            valid_commands[key] = value
        
        return valid_commands

