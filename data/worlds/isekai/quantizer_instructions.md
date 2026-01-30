# Isekai World - Quantizer Specifics

## Key Concepts

- **Magic System**: Magic works through mana (internal energy). Track mana reserves and magical abilities.
- **Level System**: Heroes gain XP for victories, level up, improve stats (HP, MP, STR, AGI, INT, VIT).
- **Adventurer Guild**: Main quest hub. Track adventurer rank progression (F → E → D → C → B → A → S).
- **Multiple Races**: Humans, elves, dwarves, beastfolk, demons. Each has unique racial traits.
- **Isekai Elements**: Character from another world with unique knowledge/abilities from previous life.

---

## Typical Quants for This World

### NPCs
- Include: race, class/profession, level (if applicable), personality traits, motivations
- Example: `Emma_Guild_Receptionist` (human, level 15, friendly, knows all local adventurers)

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

---

## World-Specific Rules

1. **Always track character progression**: Level, XP, stat improvements
2. **Manage guild rank**: Create quants for rank-up quests and achievements
3. **Handle magic learning**: Track spell schools, mana costs, learning progress
4. **Previous world knowledge**: If player uses knowledge from Earth, track as advantage
5. **Create meaningful relationships**: NPCs should remember player actions

---

## Reference Sources for This World

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

**Good reference examples:**
```json
{"reference": "Like Hinata Hyuga but with red hair and confident personality"}
{"reference": "Raphtalia from Shield Hero but older, more cynical"}
{"reference": "Aqua's attitude with Megumin's appearance"}
{"reference": "Klein from SAO but actually competent"}
```

---

## Example Quants for This World

```json
{
  "create_Guildmaster_Reinard": {
    "type": "npc",
    "synopsis": "guild master of =Adventurers_Guild=, former S-rank, respects strength, lost arm in battle",
    "body": {
      "race": "human",
      "class": "former S-rank adventurer",
      "personality": "stern but fair, respects strength",
      "reference": "Like Ainz's serious moments but human warrior, one-armed like Shanks",
      "notes": "Lost arm in battle with demon lord, now manages guild"
    },
    "links": {
      "Adventurers_Guild": "guild master",
      "City_Axel": "lives here"
    }
  }
}
```

```json
{
  "create_Summoner_Sword": {
    "type": "item",
    "synopsis": "legendary sword of =Ancient_Hero=, channels summoning magic",
    "body": {
      "item_type": "weapon",
      "description": "Legendary sword that channels summoning magic",
      "stats": "+15 STR, +10 INT",
      "special_ability": "Can summon spectral warrior once per day",
      "rarity": "legendary"
    },
    "links": {
      "Ancient_Hero": "once belonged to"
    }
  }
}
```

---

## Notes

- Track both game stats AND narrative elements
- Be creative but stay within isekai genre conventions
- Create quants for recurring characters, not one-time mentions
- Add references after 3+ interactions to make NPCs memorable
