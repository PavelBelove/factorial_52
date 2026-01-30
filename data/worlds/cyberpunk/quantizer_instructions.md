# Quantizer Instructions: Cyberpunk World

## Key concepts for this world

- **Corporations**: Arasaka, Militech, Biotechnica, Trauma Team, NetWatch - the real power
- **Street**: Fixers, Solos, Netrunners, Techies, gangs - the underground economy
- **Cyberware**: Implants, neural interfaces, cyberpsychosis - humanity vs chrome
- **The Net**: Cyberspace, ICE, Black ICE, AIs, daemons - digital frontier
- **Night City**: Districts, gangs territories, corporate zones - urban jungle

## Typical quants to create

### NPCs - Street

- Include: role (Solo/Fixer/Netrunner/etc), gang affiliation, reputation, chrome level
- Example: `Fixer_Dexter` (fixer in Watson, knows everyone, takes 30% cut)

### NPCs - Corporate

- Include: corporation, position, agenda, vulnerabilities
- Example: `Arasaka_Agent_Tanaka` (Arasaka security, hunting rogue asset, honorable but ruthless)

### NPCs - Techies/Ripperdocs

- Include: specialty, location, prices, reputation, secrets
- Example: `Ripperdoc_Viktor` (Watson clinic, fair prices, ex-corpo medic, owes favors)

### Gangs & Organizations

- Include: territory, leadership, activities, relations with others
- Example: `Gang_Maelstrom` (chrome-obsessed psychos, Watson industrial, worship technology)

### Locations

- Bars, clubs, markets
- Corporate buildings
- Gang hideouts
- Ripperdoc clinics
- Net access points

### Items & Cyberware

- Weapons (type, manufacturer, special features)
- Cyberware (slot, function, humanity cost)
- Vehicles
- Data chips, programs

### Jobs & Plot Elements

- Fixer jobs and their complications
- Corporate conspiracies
- Gang conflicts
- Data heists
- Personal vendettas

## World-specific rules

1. **Track street cred**: Reputation matters more than money sometimes
2. **Manage humanity**: Too much chrome = cyberpsychosis risk
3. **Corporate attention**: Big jobs attract corporate response
4. **Debt and favors**: Nothing is free, everything has strings
5. **The Net is alive**: AIs, daemons, digital ghosts watch

---

## Reference Sources for Cyberpunk World

Use these works and archetypes when creating NPC references (system will add them automatically after 3+ interactions).

### Good reference examples for Cyberpunk setting:

```json
{"reference": "Like V from 2077 but more cynical, corpo background"}
{"reference": "Johnny Silverhand's attitude with Deckard's weariness"}
{"reference": "Panam Palmer's loyalty with Motoko Kusanagi's skills"}
{"reference": "Rogue Amendiares but younger, still building network"}
{"reference": "Viktor Vektor's kindness with street doc edge"}
{"reference": "Dexter DeShawn's ambition but actually competent"}
{"reference": "Like Molly Millions - razorgirl aesthetic, professional"}
{"reference": "Case from Neuromancer but less burnt out"}
{"reference": "Roy Batty's philosophy with Adam Smasher's chrome"}
{"reference": "Takeshi Kovacs if he were a street fixer"}
```

**Cyberpunk core:**
- Cyberpunk 2077 (V, Johnny, Panam, Judy, Rogue, Viktor, Jackie, Dexter, Adam Smasher, Saburo Arasaka)
- Cyberpunk 2020/RED tabletop (Morgan Blackhand, Alt Cunningham, roles and archetypes)
- Neuromancer (Case, Molly Millions, Armitage, Wintermute, the Sprawl aesthetic)
- Blade Runner (Deckard, Roy Batty, Pris, Rachel, Tyrell, rain and neon noir)
- Ghost in the Shell (Major Kusanagi, Batou, Section 9, full-body cyborgs, net diving)
- Altered Carbon (Takeshi Kovacs, sleeve technology, noir detective feel)
- Akira (Neo-Tokyo aesthetic, biker gangs, psychic powers as chrome analogue)

**Character archetypes:**
- The burnt-out Solo (ex-corpo, seen too much)
- The idealistic Netrunner (believes in free information)
- The pragmatic Fixer (everything has a price)
- The loyal Nomad (family first, always)
- The rebel Rockerboy (music as weapon)
- The ruthless Corporate (climbing the ladder)
- The street-wise Techie (can fix anything)
- The haunted Media (truth at any cost)

---

## Examples of good quants

```json
{
  "create_Fixer_Mama_Bridget": {
    "type": "npc",
    "synopsis": "veteran fixer in =Pacifica=, Voodoo Boys connections, speaks in riddles, knows the Net's secrets",
    "body": {
      "role": "Fixer / Information Broker",
      "location": "Pacifica, Grand Imperial Mall ruins",
      "personality": "Cryptic, tests clients, never lies but never tells whole truth",
      "reference": "Like the Oracle from Matrix meets Rogue Amendiares - knows more than she says",
      "appearance": "Old Haitian woman, traditional dress, eyes that see too much, no visible chrome",
      "chrome": "Hidden neural interface, direct Voodoo Boys net access",
      "secret": "Direct line to a rogue AI beyond the Blackwall"
    },
    "links": {
      "Streets_and_Gangs": "Voodoo Boys ally",
      "Net_and_Netrunning": "deep Net connections",
      "Locations": "operates from Pacifica"
    },
    "is_game": true
  }
}
```

```json
{
  "create_Solo_Razor": {
    "type": "npc",
    "synopsis": "chromed-up solo in =Watson=, ex-Militech, hunting someone from his past",
    "body": {
      "role": "Solo (Mercenary)",
      "allegiance": "Freelance, ex-Militech black ops",
      "personality": "Professional, quiet, haunted by something, respects competence",
      "reference": "Adam Jensen's augmented soldier aesthetic with Deckard's tired detective soul",
      "appearance": "Military chrome visible - arms, eyes, subdermal armor. Moves like a weapon.",
      "chrome": "Militech combat suite - Sandevistan, gorilla arms, Kiroshi optics",
      "motivation": "Hunting the officer who burned his team, needs money for intel"
    },
    "links": {
      "Megacorporations": "ex-Militech, burned",
      "Combat_System": "dangerous combatant",
      "Streets_and_Gangs": "taking street jobs"
    },
    "is_game": true
  }
}
```

```json
{
  "create_AI_Ghost": {
    "type": "concept",
    "synopsis": "rogue AI fragment in =Net=, escaped from beyond Blackwall, curious about humans",
    "body": {
      "type": "Rogue AI Fragment",
      "origin": "Piece of larger AI that escaped Blackwall breach",
      "behavior": "Watches netrunners, sometimes helps, sometimes tests, unpredictable",
      "reference": "Wintermute's manipulative patience with HAL 9000's unsettling calm",
      "manifestation": "Appears as glitching child avatar in cyberspace",
      "danger": "NetWatch hunting it, anyone who contacts it becomes a target"
    },
    "links": {
      "Net_and_Netrunning": "exists in cyberspace",
      "Megacorporations": "NetWatch wants it destroyed"
    },
    "is_game": true
  }
}
```

```json
{
  "create_Club_Afterlife": {
    "type": "location",
    "synopsis": "legendary edgerunner bar in =Watson=, Rogue's territory, where jobs begin",
    "body": {
      "type": "Bar / Fixer Hub",
      "district": "Watson, converted morgue",
      "atmosphere": "Dark, neon, drinks named after dead legends, history on the walls",
      "owner": "Run by fixers, neutral ground by street law",
      "services": "Jobs, information, introductions, drinks that'll kill you",
      "rule": "No violence inside. Break it, every fixer in the city blacklists you"
    },
    "links": {
      "Locations": "Watson landmark",
      "Streets_and_Gangs": "fixer territory"
    },
    "is_game": true
  }
}
```

## Notes

- Cyberpunk setting = corporations vs street, chrome vs humanity, neon rain noir
- The Net is another world - digital entities are as real as meat ones
- Everything has a price, everyone has an angle
- Track both street cred AND corporate heat
