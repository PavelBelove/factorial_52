# Blank Canvas — Memory Specifics

## Key Principle

This is a **user-created world**. The Quantizer must preserve the unique elements the Reader defined.

---

## What to Preserve as Quants

### World Elements (Critical)
- **Setting rules**: How this world works (magic system, technology level, social structure)
- **Unique concepts**: Terms, factions, organizations specific to THIS world
- **Locations**: Important places the Reader described or visited

### Characters
- **The Hero**: Their Gift (♥), background, unique traits
- **Key NPCs**: Anyone with significant interaction (3+ exchanges)
- **Relationships**: Allies, rivals, mentors, love interests

### Story Elements
- **Plot threads**: Mysteries, quests, unresolved situations
- **Secrets**: Hidden information, revelations
- **Consequences**: Important choices and their effects

---

## The Gift (♥ Hearts)

**Critical**: The hero's Gift is their unique ability. When creating the hero quant:

```json
{
  "id": "Hero_Name",
  "body": {
    "gift": "Description of their unique ability",
    "gift_examples": "How it manifests in this world",
    ...
  }
}
```

Always preserve what the Gift IS and HOW it works in this setting.

---

## Reference System

Since this is a custom world, references help maintain tone:

```json
{"reference": "Like Tony Stark's genius but applied to magic"}
{"reference": "Sasuke's intensity with Luna Lovegood's dreaminess"}
{"reference": "Blade Runner aesthetic meets fantasy elements"}
```

Use references to anchor characters and settings to known works when applicable.

---

## Typical Quant Patterns

### World/Setting Quant
```json
{
  "id": "World_Core",
  "type": "concept",
  "synopsis": "Core world rules and atmosphere",
  "body": {
    "setting": "Brief description",
    "rules": "How things work here",
    "tone": "Atmosphere and style",
    "references": "Works this is similar to"
  }
}
```

### Character with Gift
```json
{
  "id": "Hero_Kira",
  "type": "npc",
  "synopsis": "Main character, =Gift_Voice= singer in =Idol_Agency=",
  "body": {
    "role": "Protagonist",
    "gift": "Voice that affects emotions",
    "appearance": "...",
    "personality": "...",
    "reference": "Like a darker version of K-pop idol trope"
  }
}
```

### Custom Faction/Organization
```json
{
  "id": "Shadow_Council",
  "type": "faction",
  "synopsis": "Secret organization controlling the city from shadows",
  "body": {
    "purpose": "...",
    "structure": "...",
    "known_members": ["=Agent_X=", "=The_Director="],
    "hero_relation": "..."
  }
}
```

---

## DON'T Create Quants For

- Generic game mechanics (they're in initial_quants)
- Character stats/inventory (handled by game system)
- Temporary situations
- Information already in summary

---

## Notes

- This world is defined by the Reader — preserve their vision
- Use =markers= for cross-references
- Keep quants focused and atomic
- Story elements matter more than mechanics
