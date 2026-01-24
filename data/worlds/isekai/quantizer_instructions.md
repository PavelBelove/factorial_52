# Quantizer Instructions: Isekai World

## Key concepts for this world

- **Magic System**: Magic works through mana (internal energy). Track mana reserves and magical abilities.
- **Level System**: Heroes gain XP for victories, level up, improve stats (HP, MP, STR, AGI, INT, VIT).
- **Adventurer Guild**: Main quest hub. Track adventurer rank progression (F → E → D → C → B → A → S).
- **Multiple Races**: Humans, elves, dwarves, beastfolk, demons. Each has unique racial traits and abilities.
- **Isekai Elements**: Character from another world with unique knowledge/abilities from previous life.

## Typical quants to create

### NPCs
- Include: race, class/profession, level (if applicable), personality traits, motivations
- Example: "Рецепционистка_Гильдии_Эмма" (human, level 15, friendly, knows all local adventurers)

### Locations
- Towns, cities, villages
- Dungeons and labyrinths
- Guild halls, taverns, shops, inns
- Natural landmarks (forests, mountains, ruins)

### Quest Items & Artifacts
- Magical weapons with enchantments
- Armor and equipment
- Quest-specific items
- Legendary artifacts with unique powers

### Monsters & Creatures
- Type, habitat, threat level
- Special abilities
- Typical drops/loot
- Behavior patterns

### Abilities & Skills
- Player's unique skills from previous world
- Magic spells learned in isekai world
- Class-specific abilities
- Combination skills

## World-specific rules

1. **Always track character progression**: Level, XP, stat improvements
2. **Manage guild rank**: Create quants for rank-up quests and achievements
3. **Handle magic learning**: Track spell schools, mana costs, learning progress
4. **Previous world knowledge**: If player uses knowledge from Earth, track it as advantage
5. **Create meaningful relationships**: NPCs should remember player actions and react accordingly

## Examples of good quants

```json
{
  "id": "Мастер_Гильдии_Рейнард",
  "type": "npc",
  "body": {
    "race": "human",
    "class": "former_S-rank_adventurer",
    "personality": "stern but fair, respects strength",
    "role": "guild master",
    "notes": "Lost arm in battle with demon lord, now manages guild"
  },
  "links": {
    "Гильдия_Авантюристов": "guild_master",
    "Город_Аксель": "lives_here"
  }
}
```

```json
{
  "id": "Меч_Призывателя",
  "type": "item",
  "body": {
    "item_type": "weapon",
    "description": "Legendary sword that channels summoning magic",
    "stats": "+15 STR, +10 INT",
    "special_ability": "Can summon spectral warrior once per day",
    "rarity": "legendary"
  },
  "links": {
    "Древний_Герой": "once_belonged_to"
  }
}
```

## Notes for quantizer

- Be creative but stay within isekai genre conventions
- Track both game stats AND narrative elements
- Create quants for recurring characters, not one-time mentions
- Link related quants together for context
- Don't create duplicate quants - update existing ones instead

