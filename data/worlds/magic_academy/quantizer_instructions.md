# Magic Academy Chronicle - Memory Specifics

## Key Story Elements

- **Academy Life**: Years 1-5, faculties/houses, professors, student hierarchies
- **Magical Arts**: Elemental, enchantment, alchemy, naming, divination, illusion, battle magic, healing
- **Social Fabric**: Nobles vs commoners, faculty rivalries, friendships, reputation, romance
- **Academic Journey**: Classes, exams, studies, research, discovery
- **Hidden Depths**: Restricted sections, secret societies, ancient artifacts, concealed passages

---

## Typical Chronicle Elements

### Characters - Students
- Include: year, faculty, social standing (noble/common/scholar), personality, academic strengths
- Example: `Elena_Third_Year` (3rd year, Arcane faculty, noble, studious but kind)

### Characters - Faculty
- Include: position, subject taught, personality, quirks, potential story threads
- Example: `Professor_Moran` (Battle Magic, strict but fair, war veteran)

### Places - Academy Grounds
- Lecture halls, dormitories, library wings
- Common rooms, dining hall, courtyards
- Hidden passages, forbidden areas
- Practice grounds, dueling circles

### Story Elements - Academic
- Specific classes and their nature
- Examinations and assignments
- Research threads, student societies

### Objects & Mysteries
- Personal wands/staves
- Academy-issued tools
- Rare grimoires, scrolls, enigmatic artifacts

### Plot Threads & Secrets
- Secret society activities
- Ancient academy mysteries
- Political intrigue
- Forbidden knowledge discoveries

---

## Chronicle-Specific Principles

1. **Track story progression**: Academic year, relationships growth, character development
2. **Manage social web**: Noble politics, friendship networks, rivalries evolving
3. **Handle magical learning**: Which disciplines studied, breakthroughs, setbacks
4. **Weave mysteries slowly**: Not everything revealed at once, clues over chapters
5. **Develop authentic bonds**: Friends, rivals, mentors, romantic threads deepen naturally

---

## Reference Sources for Magic Academy Chronicle

Use these works and archetypes when creating character references (system will add them automatically after 3+ interactions).

### Good reference examples for Magic Academy setting:

```json
{"reference": "Like Hermione but from noble family, more politically aware"}
{"reference": "Snape's strictness with Dumbledore's hidden warmth"}
{"reference": "Kvothe's brilliance but without the arrogance, shy"}
{"reference": "Akko from Little Witch Academia but actually talented"}
```

**Magic academy literature:**
- Harry Potter (Harry, Hermione, Ron, Draco, Snape, Dumbledore, McGonagall, Luna, Neville)
- The Name of the Wind (Kvothe, Denna, Ambrose, Elodin, Kilvin)
- A Wizard of Earthsea (Ged, Ogion, Jasper, Vetch)
- The Magicians (Quentin, Alice, Eliot, Margo, Penny)
- Little Witch Academia (Akko, Diana, Sucy, Lotte, Ursula)
- Mother of Learning (Zorian, Zach, Xvim, Ilsa, Taiven)

**Character archetypes:**
- The prodigy (effortless talent)
- The determined scholar (grit over gifts)
- The noble with layers (privileged but complex)
- The mysterious professor (hidden depths)
- The kind mentor (supportive guide)
- The demanding master (harsh but effective)
- The worthy rival (competitive but respectful)

---

## Example Chronicle Entries

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
    },
    "is_game": true
  }
}
```

```json
{
  "create_Viktor_Aristov": {
    "type": "npc",
    "synopsis": "4th year noble, =Battle_Magic_Faculty=, proud rival but honorable",
    "body": {
      "year": "4th",
      "faculty": "Battle Magic",
      "social_class": "High noble - Duke's son",
      "personality": "Proud, competitive, secretly respects genuine skill",
      "reference": "Draco Malfoy's pride mixed with Sasuke's combat focus, but more honorable",
      "appearance": "Silver-blond hair, immaculate uniform, family signet ring"
    },
    "links": {
      "Faculties": "star of Battle Magic faculty",
      "Academy_Events": "three-time dueling champion",
      "Social_Dynamics": "leader of noble circle"
    },
    "is_game": true
  }
}
```

---

## Notes

- Magic Academy chronicle = relationships matter as much as magic
- Track both academic progress AND evolving social bonds
- Academy life weaves routine with mystery
- Every character should feel authentic, memorable
- Focus on story elements, not game mechanics
