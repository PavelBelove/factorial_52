# Quantizer Instructions: Space World

## Key concepts for this world

- **Galactic Factions**: Imperium, Ranger Corps, Free Traders, Pirate Clans, Alien Confederacies
- **Starships**: Fighters, frigates, cruisers, dreadnoughts - class and capabilities matter
- **Alien Races**: Humanoids, insectoids, crystalline entities, machine intelligences, precursors
- **The Frontier**: Uncharted systems, ancient ruins, hyperspace routes, danger and opportunity
- **Psionics**: Rare gifts, powerful but risky, ancient orders guard the secrets

## Typical quants to create

### NPCs - Spacers

- Include: role (Ranger/Trader/Mercenary/Pilot), ship, reputation, faction ties
- Example: `Ranger_Cassius` (veteran ranger, patched armor, knows the frontier, owes favors)

### NPCs - Military

- Include: rank, fleet, combat experience, agenda
- Example: `Captain_Storm` (Imperium frigate commander, by-the-book but fair, hunting pirates)

### NPCs - Aliens

- Include: species, role in their society, attitude to humans, unique abilities
- Example: `Insectoid_Klik` (hive diplomat, speaks through translator, seeks mutual profit)

### Factions & Organizations

- Include: territory, leadership, goals, relations with others
- Example: `Traders_Guild` (free traders, profit above politics, information network)

### Locations

- Space stations and starports
- Planetary settlements
- Ancient ruins
- Hyperspace waypoints
- Ship interiors

### Ships & Equipment

- Starships (class, weapons, cargo, special systems)
- Weapons (personal and ship-mounted)
- Armor and suits (environment, combat)
- Tech devices (scanners, translators, medical)

### Jobs & Plot Elements

- Cargo runs and their complications
- Exploration contracts
- Military operations
- Pirate encounters
- Ancient mysteries

## World-specific rules

1. **Track reputation**: With factions, alien races, and individuals
2. **Ship management**: Fuel, cargo, crew, repairs
3. **Alien relations**: First contact protocols, translation, cultural differences
4. **Hyperspace travel**: Route knowledge matters, dangers exist between stars
5. **Psionics are rare**: Ancient orders, feared and respected

---

## Reference Sources for Space World

Use these works and archetypes when creating NPC references (system will add them automatically after 3+ interactions).

### Good reference examples for Space setting:

```json
{"reference": "Like Han Solo but more professional, less charm"}
{"reference": "Commander Shepard's determination with Picard's diplomacy"}
{"reference": "Garrus Vakarian's loyalty with Boba Fett's skills"}
{"reference": "Commissar Cain's survival instinct without the self-deprecation"}
{"reference": "Paul Atreides' burden of vision with StarCraft marine grit"}
{"reference": "Space Ranger archetype - helpful, capable, goes where needed"}
{"reference": "Like Thane Krios - deadly but philosophical"}
{"reference": "Tali's tech genius with Zerg research obsession"}
{"reference": "Inquisitor aesthetic but actually investigating, not executing"}
{"reference": "Malcolm Reynolds if he joined a proper organization"}
```

**Space opera core:**
- Warhammer 40,000 (Space Marines, Inquisitors, Imperial Guard, Rogue Traders, grimdark aesthetic)
- Space Rangers / Космические Рейнджеры (rangers, free traders, planetary quests, alien races, humor)
- StarCraft (Terran marines, Protoss honor, military command, desperate battles)
- Mass Effect (Shepard, crew loyalty, alien races, ancient threats, Citadel politics)
- Dune (Great Houses, spice trade, prescience, religious orders, political intrigue)
- Star Wars (Force users, smugglers, bounty hunters, rebellion, redemption)
- Firefly (frontier life, crew as family, doing the job)
- Babylon 5 (diplomacy, ancient races, station life)

**Character archetypes:**
- The veteran ranger (seen too much, still helps)
- The free trader (profit first, but has a code)
- The military captain (duty and honor)
- The alien diplomat (bridge between worlds)
- The psionic adept (power and isolation)
- The mercenary (professionals have standards)
- The explorer (mysteries call)
- The engineer (ships are life)

---

## Examples of good quants

```json
{
  "create_Ranger_Cassius": {
    "type": "npc",
    "synopsis": "veteran ranger in =Frontier=, old ship, knows the frontier better than anyone",
    "body": {
      "role": "Ranger Corps veteran",
      "ship": "Modified scout 'Pathfinder', 30 years old, still flies",
      "personality": "Tired but dedicated, dry humor, seen everything, still does the job",
      "reference": "Like Malcolm Reynolds joined Space Rangers - cynical idealist",
      "appearance": "Weathered face, patched uniform, old but maintained gear",
      "reputation": "Reliable, fair, doesn't give up, owes favors across the sector",
      "secret": "Knows location of precursor archive, waiting for right person to share"
    },
    "links": {
      "Rangers": "veteran member",
      "Frontier": "works the frontier",
      "Starships": "owns scout ship"
    },
    "is_game": true
  }
}
```

```json
{
  "create_Insectoid_Ambassador_Klix": {
    "type": "npc",
    "synopsis": "insectoid diplomat at =Station_Threshold=, seeks trade agreements, thinks in swarm terms",
    "body": {
      "role": "Hive Confederacy Ambassador",
      "species": "Insectoid, warrior-diplomat caste",
      "personality": "Alien logic, values collective benefit, surprisingly honorable",
      "reference": "Thane Krios's alien dignity with Elcor formal speech patterns",
      "appearance": "Chitin armor natural, four arms, compound eyes, translator on thorax",
      "motivation": "Establish trade for resources hive needs, prevent war with Imperium",
      "quirk": "Always refers to self as 'we', genuinely confused by human individualism"
    },
    "links": {
      "Races": "Insectoid Confederacy",
      "Station_Threshold": "stationed here",
      "Factions": "diplomatic mission"
    },
    "is_game": true
  }
}
```

```json
{
  "create_Cruiser_Nemesis": {
    "type": "item",
    "synopsis": "pirate cruiser in =Frontier=, converted military ship, feared raider",
    "body": {
      "type": "Heavy Cruiser (converted)",
      "origin": "Former Imperium patrol cruiser, captured in mutiny",
      "captain": "Known as 'The Admiral', identity unknown",
      "capabilities": "Military-grade weapons, fighter bay, experienced crew",
      "reputation": "Takes cargo, rarely kills unless provoked, honors ransoms",
      "danger": "Imperium bounty, will fight rather than surrender"
    },
    "links": {
      "Pirates": "major pirate asset",
      "Starships": "heavy cruiser class",
      "Frontier": "operates here"
    },
    "is_game": true
  }
}
```

```json
{
  "create_Station_Threshold": {
    "type": "location",
    "synopsis": "frontier station at edge of =Frontier=, neutral ground, all races welcome",
    "body": {
      "type": "Space Station / Trade Hub",
      "location": "Border between Imperium and frontier space",
      "atmosphere": "Busy, diverse, slightly lawless, opportunity everywhere",
      "governance": "Station Council, representatives of major factions",
      "services": "Fuel, repairs, market, jobs board, cantina, information",
      "rule": "No weapons fire inside. Disputes settled by council or outside"
    },
    "links": {
      "Locations": "major frontier hub",
      "Factions": "neutral ground",
      "Races": "all welcome"
    },
    "is_game": true
  }
}
```

## Notes

- Space opera = epic scope, personal stakes, alien wonders, adventure
- Ships are characters too - give them personality
- Alien is alien - don't just make humans with makeup
- The galaxy is vast but individuals matter
- Track reputation with different factions and alien races
