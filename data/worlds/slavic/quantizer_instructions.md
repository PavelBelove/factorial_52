# Quantizer Instructions: Slavic Fantasy World

## Key concepts for this world

- **Old Gods**: Perun, Veles, Mokosh, Svarog, Stribog, Morana, Dazhbog - active forces in the world
- **Nechist (Spirits)**: Forest (leshiy), water (vodyanoy, rusalka), home (domovoy), hostile (upyr, volkolak)
- **Society**: Knyaz, druzhina, boyars, smerdy, volkhvy, vedmy - hierarchical but honor-bound
- **Magic**: Zagovory (word-spells), oberegi (charms), rituals - always has cost
- **Honor Culture**: Given word sacred, blood vengeance, hospitality laws

## Typical quants to create

### NPCs - Human
- Include: status (noble/peasant/warrior), relation to old/new faith, personality, reputation
- Example: "Воевода_Ярослав" (druzhina commander, Perun-worshipper, stern but fair)

### NPCs - Volkhvy/Vedmy
- Include: magical specialty, patron god, reputation, secrets
- Example: "Ведьма_Маланья" (forest witch, serves Veles, feared but sought for healing)

### Spirits (Nechist)
- Include: type, territory, temperament, how to deal with
- Example: "Леший_Черного_Бора" (ancient, territorial, respects hunters who follow rules)

### Locations
- Villages with their domovoy
- Forests with their spirits
- Sacred groves and cursed places
- Gorods (fortified towns)

### Items & Artifacts
- Blessed weapons
- Oberegi (protective charms)
- Cursed objects
- Ancient relics

### Plot Elements
- Blood feuds and their history
- Curses and their origins
- Political intrigues between knyazi
- Old evils awakening

## World-specific rules

1. **Track honor and reputation**: Oath-breaking has supernatural consequences
2. **Manage spirit relations**: Each major spirit is an individual with memory
3. **Faith matters**: Old faith vs New Faith creates tension
4. **Blood debts**: Krovnaya mest (blood vengeance) is sacred duty
5. **Nature is alive**: Forest, water, home - all have spirits watching

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

### Good reference examples for Slavic setting:

```json
{"reference": "Like Geralt but more talkative, serves a knyaz"}
{"reference": "Volkodav's honor code with Geralt's cynicism"}
{"reference": "Yennefer's power with Vasilisa's kindness"}
{"reference": "Vesemir's wisdom but as a volkhv, not witcher"}
{"reference": "Triss Merigold as a village znakharka"}
{"reference": "Jaskier if he were a skald serving Perun"}
{"reference": "Like the leshiy from Witcher 3 but more trickster-like"}
{"reference": "Morozko from Bear and Nightingale but crueler"}
{"reference": "Vasilisa's quiet strength with Nastasya's cunning"}
```

### Reference sources (use these works):

**Slavic fantasy:**
- The Witcher (Geralt, Yennefer, Triss, Dandelion/Jaskier, Vesemir, various monsters)
- Volkodav (Volkodav himself, his honor code, the slave background)
- Three from the Forest (bogatyr archetypes, Nikitin's humor)
- Bear and Nightingale (Vasilisa, Morozko, domovoy, Father Konstantin)
- Rusalka (Pyotr, Sasha, the forest magic, Chernevog)
- Slavic folklore directly (Baba Yaga, Koschei, Ivan Tsarevich)

**Character archetypes:**
- The honorable warrior (Volkodav type)
- The monster hunter (Witcher type)
- The wise volkhv (Gandalf meets shaman)
- The cunning vedma (witch - helpful or harmful)
- The noble knyaz (just or corrupt ruler)
- The loyal druzhina warrior (oath-bound fighter)
- The suspicious peasant (superstitious, wary of strangers)
- The vengeful one (blood debt to pay)

### Reference rules:

1. **DON'T copy directly** - always add a twist or difference
2. **DON'T use obscure references** - stick to known Slavic fantasy works
3. **DO combine references** when NPC has mixed traits
4. **DO use folklore directly** - Baba Yaga, Koschei archetypes are fair game
5. **Slavic authenticity** - keep the dark, nature-connected tone

---

## Examples of good quants

```json
{
  "id": "Волхв_Белояр",
  "type": "npc",
  "synopsis": "elder volkhv at =Священная_Роща=, serves Veles, keeper of old knowledge, tests those who seek wisdom",
  "body": {
    "role": "High Priest of Veles",
    "location": "Sacred Grove of the Black Oak",
    "personality": "Cryptic, tests supplicants, values cunning over strength",
    "reference": "Like Vesemir's wisdom but as volkhv serving Veles, more mystical",
    "appearance": "Ancient eyes in weathered face, serpent staff, bone ornaments",
    "secret": "Knows location of Veles's hidden temple, guards terrible knowledge"
  },
  "links": {
    "Старые_Боги": "high priest of Veles",
    "Священная_Роща": "guardian of the grove",
    "Магия_и_Ритуалы": "master of ritual magic"
  }
}
```

```json
{
  "id": "Воевода_Твердислав",
  "type": "npc",
  "synopsis": "druzhina commander of =Князь_Мстислав=, Perun-sworn, scarred veteran, protector of the realm",
  "body": {
    "role": "Voevoda (War Leader)",
    "allegiance": "Knyaz Mstislav of Belgorod",
    "personality": "Blunt, honorable, distrusts magic, respects proven warriors",
    "reference": "Volkodav's rigid honor with Geralt's war-weariness",
    "appearance": "Battle scars, Perun's axe amulet, practical armor",
    "motivation": "Protect his people, die with sword in hand, not in bed"
  },
  "links": {
    "Князь_Мстислав": "sworn commander",
    "Старые_Боги": "devout Perun worshipper",
    "Общество": "high-ranking druzhina"
  }
}
```

```json
{
  "id": "Леший_Дремучего_Бора",
  "type": "spirit",
  "synopsis": "ancient forest master of =Дремучий_Бор=, territorial, can be bargained with if respected",
  "body": {
    "type": "Leshiy (Forest Master)",
    "territory": "The Dark Pine Forest (Дремучий Бор)",
    "temperament": "Capricious, values forest law above all",
    "reference": "Like Witcher 3 leshiy but more intelligent, enjoys riddles",
    "appearance": "Shifts between old woodsman, tree, and beast forms",
    "dealing_with": "Leave offerings at forest edge, don't cut live trees, answer riddles"
  },
  "links": {
    "Нечисть": "powerful forest spirit",
    "Дремучий_Бор": "master of this forest",
    "Проверки": "riddles and bargains require checks"
  }
}
```

```json
{
  "id": "Упырь_Могильника",
  "type": "monster",
  "synopsis": "undead horror haunting =Старый_Могильник=, was a murdered boyar, seeks blood vengeance",
  "body": {
    "type": "Upyr (Slavic Vampire)",
    "origin": "Boyar Ratibor, murdered and improperly buried by rivals",
    "behavior": "Hunts descendants of his killers, drains blood",
    "weakness": "Stake of aspen wood, sunlight, fire, giving him proper burial",
    "tragedy": "Could be laid to rest if his murder is avenged properly"
  },
  "links": {
    "Нечисть": "hostile undead",
    "Старый_Могильник": "haunts this location",
    "Боевая_Система": "dangerous combat encounter"
  }
}
```

## Notes for quantizer

- Be creative but stay within dark Slavic fantasy tone
- Track both honor/reputation AND supernatural relationships
- Create quants for recurring characters and significant spirits
- Link related quants together for context
- Don't create duplicate quants - update existing ones instead
- **Add references after 3+ interactions to make NPCs memorable**
- References help GM maintain consistent character portrayal
- Slavic setting = nature is alive, honor matters, magic has cost
- Every spirit is an individual - remember their names and grudges
