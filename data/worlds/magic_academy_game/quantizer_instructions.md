# Magic Academy World - Quantizer Specifics

## Key Concepts

- **Academy Structure**: Years 1-5, faculties/houses, professors, student hierarchy
- **Magic Disciplines**: Elemental, enchantment, alchemy, naming, divination, illusion, battle magic, healing
- **Social Dynamics**: Nobles vs commoners, faculty rivalries, cliques, romance, reputation
- **Academic Life**: Classes, exams, homework, study groups, library research
- **Mysteries**: Restricted sections, secret societies, ancient artifacts, hidden passages

---

## Typical Quants for This World

### NPCs - Students
- Include: year, faculty, social class (noble/commoner/scholarship), personality, academic strengths
- Example: `Elena_Third_Year` (3rd year, Arcane faculty, noble, studious but kind)

### NPCs - Staff
- Include: position, subject taught, personality, quirks, potential plot hooks
- Example: `Professor_Moran` (Battle Magic, strict but fair, veteran of mage wars)

### Locations - Academy
- Classrooms, dormitories, library sections
- Common rooms, dining hall, courtyards
- Secret passages, restricted areas
- Practice grounds, dueling arena

### Academic Elements
- Specific classes and their content
- Exams and assignments
- Research projects, club activities

### Items & Artifacts
- Personal wands/staves
- Academy-issued equipment
- Rare books, scrolls, mysterious artifacts

### Mysteries & Plots
- Secret society activities
- Ancient academy secrets
- Political intrigues
- Forbidden magic discoveries

---

## World-Specific Rules

1. **Track academic progress**: Year, grades, professor relationships
2. **Manage social standing**: Noble politics, friendship networks, rivalries
3. **Handle magic learning**: Which disciplines studied, skill progression
4. **Create layered mysteries**: Not everything revealed at once, clues over time
5. **Develop relationships**: Friends, rivals, mentors, romantic interests evolve

---

## Reference Sources for This World

**Magic school media:**
- Harry Potter (Harry, Hermione, Ron, Draco, Snape, Dumbledore, McGonagall, Luna, Neville)
- The Name of the Wind (Kvothe, Denna, Ambrose, Elodin, Kilvin)
- A Wizard of Earthsea (Ged, Ogion, Jasper, Vetch)
- The Magicians (Quentin, Alice, Eliot, Margo, Penny)
- Little Witch Academia (Akko, Diana, Sucy, Lotte, Ursula)
- Mother of Learning (Zorian, Zach, Xvim, Ilsa, Taiven)

**Personality archetypes:**
- The prodigy (effortless talent)
- The hard worker (determination over talent)
- The noble snob (privileged but possibly redeemable)
- The mysterious professor (hidden depths)
- The kind mentor (supportive teacher)
- The strict master (harsh but effective)
- The rival (competitive but respectful)

**Good reference examples:**
```json
{"reference": "Like Hermione but from noble family, more politically aware"}
{"reference": "Snape's strictness with Dumbledore's hidden warmth"}
{"reference": "Kvothe's brilliance but without the arrogance, shy"}
{"reference": "Akko from Little Witch Academia but actually talented"}
```

---

## Example Quants for This World

```json
{
  "create_Professor_Eldrin": {
    "type": "npc",
    "synopsis": "Naming professor at =Arcane_Faculty=, eccentric genius, tests students unconventionally",
    "body": {
      "role": "Professor of Naming",
      "faculty": "Arcane Studies",
      "personality": "Eccentric, speaks in riddles, genuinely cares but shows it oddly",
      "reference": "Elodin from Name of the Wind but calmer, with Luna Lovegood's dreaminess",
      "teaching_style": "No textbooks, strange assignments, rewards creativity",
      "secret": "Can hear true names of things, slowly going deaf to normal speech"
    },
    "links": {
      "Faculties": "teaches at Arcane faculty",
      "Magic_Disciplines": "master of Naming",
      "Academy_Secrets": "knows more than he tells"
    }
  }
}
```

```json
{
  "create_Viktor_Aristov": {
    "type": "npc",
    "synopsis": "4th year noble, =Battle_Magic_Faculty=, arrogant rival but honorable in duels",
    "body": {
      "year": "4th",
      "faculty": "Battle Magic",
      "social_class": "High noble - Duke's son",
      "personality": "Proud, competitive, secretly respects genuine skill",
      "reference": "Draco Malfoy's pride mixed with Sasuke's combat focus, but more honorable",
      "appearance": "Silver-blond hair, always immaculate uniform, family signet ring"
    },
    "links": {
      "Faculties": "star of Battle Magic faculty",
      "Tournaments": "three-time dueling champion",
      "Social_Dynamics": "leader of noble clique"
    }
  }
}
```

---

## Notes

- Track both academic progress AND social relationships
- Academy setting = relationships matter as much as magic
- Create quants for recurring characters, not one-time mentions
- Add references after 3+ interactions to make NPCs memorable
