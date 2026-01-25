# Quantizer Instructions: Magic Academy World

## Key concepts for this world

- **Academy Structure**: Years 1-5, faculties/houses, professors, student hierarchy
- **Magic Disciplines**: Elemental, enchantment, alchemy, naming, divination, illusion, battle magic, healing
- **Social Dynamics**: Nobles vs commoners, faculty rivalries, cliques, romance, reputation
- **Academic Life**: Classes, exams, homework, study groups, library research
- **Mysteries**: Restricted sections, secret societies, ancient artifacts, hidden passages

## Typical quants to create

### NPCs - Students
- Include: year, faculty, social class (noble/commoner/scholarship), personality, academic strengths
- Example: "Элиза_Третьекурсница" (3rd year, Arcane faculty, noble, studious but kind)

### NPCs - Staff
- Include: position, subject taught, personality, quirks, potential plot hooks
- Example: "Профессор_Моран" (Battle Magic, strict but fair, veteran of mage wars)

### Locations - Academy
- Classrooms, dormitories, library sections
- Common rooms, dining hall, courtyards
- Secret passages, restricted areas
- Practice grounds, dueling arena

### Academic Elements
- Specific classes and their content
- Exams and assignments
- Research projects
- Club activities

### Items & Artifacts
- Personal wands/staves
- Academy-issued equipment
- Rare books and scrolls
- Mysterious artifacts found in plot

### Mysteries & Plots
- Secret society activities
- Ancient academy secrets
- Political intrigues
- Forbidden magic discoveries

## World-specific rules

1. **Track academic progress**: Year, grades, professor relationships
2. **Manage social standing**: Noble politics, friendship networks, rivalries
3. **Handle magic learning**: Which disciplines studied, skill progression
4. **Create layered mysteries**: Not everything revealed at once, clues over time
5. **Develop relationships**: Friends, rivals, mentors, romantic interests evolve

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

### Good reference examples for academy setting:

```json
{"reference": "Like Hermione but from noble family, more politically aware"}
{"reference": "Snape's strictness with Dumbledore's hidden warmth"}
{"reference": "Kvothe's brilliance but without the arrogance, shy"}
{"reference": "Akko from Little Witch Academia but actually talented"}
{"reference": "Zorian from Mother of Learning but extroverted"}
{"reference": "Draco's pride with Neville's hidden courage"}
{"reference": "Quentin from Magicians but less depressed, more curious"}
{"reference": "Rock Lee's dedication with Shikamaru's intellect"}
```

### Reference sources (use these works):

**Magic school media:**
- Harry Potter (Harry, Hermione, Ron, Draco, Snape, Dumbledore, McGonagall, Luna, Neville)
- The Name of the Wind (Kvothe, Denna, Ambrose, Elodin, Kilvin)
- A Wizard of Earthsea (Ged, Ogion, Jasper, Vetch)
- The Magicians (Quentin, Alice, Eliot, Margo, Penny)
- Little Witch Academia (Akko, Diana, Sucy, Lotte, Ursula)
- Mother of Learning (Zorian, Zach, Xvim, Ilsa, Taiven)
- Naruto Academy (Iruka, young Naruto/Sasuke/Sakura dynamics)

**Personality archetypes:**
- The prodigy (effortless talent)
- The hard worker (determination over talent)
- The noble snob (privileged but possibly redeemable)
- The mysterious professor (hidden depths)
- The kind mentor (supportive teacher)
- The strict master (harsh but effective)
- The rival (competitive but respectful)
- The trickster (chaos agent, comic relief)

### Reference rules:

1. **DON'T copy directly** - always add a twist or difference
2. **DON'T use obscure references** - stick to well-known works
3. **DO combine references** when NPC has mixed traits
4. **DO update references** if character develops significantly
5. **Academic context** - consider their role (student/professor/staff)

---

## Examples of good quants

```json
{
  "id": "Профессор_Элдрин",
  "type": "npc",
  "synopsis": "Naming professor at =Факультет_Арканы=, eccentric genius, tests students unconventionally",
  "body": {
    "role": "Professor of Naming",
    "faculty": "Arcane Studies",
    "personality": "Eccentric, speaks in riddles, genuinely cares but shows it oddly",
    "reference": "Elodin from Name of the Wind but calmer, with Luna Lovegood's dreaminess",
    "teaching_style": "No textbooks, strange assignments, rewards creativity over memorization",
    "secret": "Can hear the true names of things, slowly going deaf to normal speech"
  },
  "links": {
    "Факультеты": "teaches at Arcane faculty",
    "Магические_Дисциплины": "master of Naming",
    "Тайны_Академии": "knows more than he tells"
  }
}
```

```json
{
  "id": "Виктор_Аристов",
  "type": "npc",
  "synopsis": "4th year noble student, =Факультет_Боевой_Магии=, arrogant rival but honorable in duels",
  "body": {
    "year": "4th",
    "faculty": "Battle Magic",
    "social_class": "High noble - Duke's son",
    "personality": "Proud, competitive, secretly respects genuine skill",
    "reference": "Draco Malfoy's pride mixed with Sasuke's combat focus, but more honorable",
    "appearance": "Silver-blond hair, always immaculate uniform, family signet ring",
    "motivation": "Prove worthy of family name, conflicted about father's expectations"
  },
  "links": {
    "Факультеты": "star of Battle Magic faculty",
    "Турниры": "three-time dueling champion",
    "Социальная_Динамика": "leader of noble clique"
  }
}
```

```json
{
  "id": "Мира_Стипендиатка",
  "type": "npc",
  "synopsis": "2nd year scholarship student, =Факультет_Природы=, talented alchemist, shy but fierce when pushed",
  "body": {
    "year": "2nd",
    "faculty": "Natural Magic",
    "social_class": "Scholarship - village healer's daughter",
    "personality": "Quiet, hardworking, sharp tongue when provoked",
    "reference": "Hermione's work ethic with Sucy's alchemy obsession, less confident",
    "appearance": "Ink-stained fingers, herbs in pockets, secondhand robes",
    "motivation": "Send money home, prove commoners can excel, discover new potions"
  },
  "links": {
    "Факультеты": "top of her class in Alchemy",
    "Социальная_Динамика": "target of noble bullying, has loyal friends"
  }
}
```

## Notes for quantizer

- Be creative but stay within magic school genre conventions
- Track both academic progress AND social relationships
- Create quants for recurring characters, not one-time mentions
- Link related quants together for context
- Don't create duplicate quants - update existing ones instead
- **Add references after 3+ interactions to make NPCs memorable**
- References help GM maintain consistent character portrayal
- Academy setting = relationships matter as much as magic
