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

---

## NPC References System

**IMPORTANT: Create vivid character images through cultural references!**

### When to add references:

Add a `reference` field to NPC quants when:
- Player has interacted with NPC **3 or more times**
- NPC is important for ongoing story
- NPC has distinctive personality/appearance

### How to create references:

Reference should be:
- **Short** (5-15 words max)
- **Evocative** - instantly activates GM's knowledge of that character
- **Modified** - note differences from original

**Reference format in body:**
```json
{
  "reference": "Like [Character] from [Work] but [difference]"
}
```

### Good reference examples:

```json
{"reference": "Like Hinata Hyuga but with red hair and confident personality"}
{"reference": "Raphtalia from Shield Hero but older, more cynical"}
{"reference": "Aqua's attitude with Megumin's appearance"}
{"reference": "Klein from SAO but actually competent"}
{"reference": "Maple from Bofuri but as an NPC shopkeeper"}
{"reference": "Rudeus's teacher vibe but female dwarf"}
```

### Reference sources (use these works):

**Isekai anime/manga:**
- Mushoku Tensei (Rudeus, Roxy, Eris, Ruijerd, Sylphiette)
- Shield Hero (Raphtalia, Filo, Naofumi, Glass)
- Spider isekai (Kumoko, Ariel, Sophia)
- Log Horizon (Shiroe, Akatsuki, Nyanta)
- Bofuri (Maple, Sally, Kasumi)
- KonoSuba (Aqua, Megumin, Darkness, Kazuma)
- Re:Zero (Emilia, Rem, Ram, Beatrice)
- Overlord (Ainz, Albedo, Shalltear)
- SAO (Kirito, Asuna, Klein, Sinon)

**Classic fantasy:**
- LOTR characters
- D&D archetypes
- Studio Ghibli characters

### Reference rules:

1. **DON'T copy directly** - always add a twist or difference
2. **DON'T use obscure references** - stick to well-known works
3. **DO combine references** when NPC has mixed traits
4. **DO update references** if character develops significantly

---

## Examples of good quants

```json
{
  "id": "Мастер_Гильдии_Рейнард",
  "type": "npc",
  "synopsis": "guild master of =Гильдия_Авантюристов=, former S-rank, respects strength, lost arm in battle",
  "body": {
    "race": "human",
    "class": "former_S-rank_adventurer",
    "personality": "stern but fair, respects strength",
    "role": "guild master",
    "reference": "Like Ainz's serious moments but human warrior, one-armed like Shanks",
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
  "id": "Эмма_Рецепционистка",
  "type": "npc",
  "synopsis": "half-elf receptionist at =Гильдия_Авантюристов=, friendly, knows everyone",
  "body": {
    "race": "half-elf",
    "role": "guild receptionist",
    "personality": "cheerful, helpful, secretly sharp observer",
    "reference": "Like guild girls from Goblin Slayer but half-elf, more playful",
    "appearance": "green eyes, pointed ears, always smiling"
  },
  "links": {
    "Гильдия_Авантюристов": "works_here",
    "Мастер_Гильдии_Рейнард": "respects_boss"
  }
}
```

```json
{
  "id": "Меч_Призывателя",
  "type": "item",
  "synopsis": "legendary sword of =Древний_Герой=, channels summoning magic",
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
- **Add references after 3+ interactions to make NPCs memorable**
- References help GM maintain consistent character portrayal
