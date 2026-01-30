# Quantizer Instructions: Wasteland (Post-Apocalyptic) World

## Key concepts for this world

- **The Wasteland**: Nuclear devastation, radiation zones, mutated life, survival
- **Factions**: Brotherhood of Steel, raiders, settlements, traders, Enclave remnants
- **Mutants & Creatures**: Ghouls, Super Mutants, Deathclaws, radscorpions, anomalies
- **Technology**: Pre-war tech, power armor, energy weapons, Pip-Boys, scavenging
- **Economy**: Bottle caps, barter, water and ammo as currency

## Typical quants to create

### NPCs - Settlers & Traders

- Include: settlement, role, trading specialty, connections, secrets
- Example: `Trader_Morgan` (caravan boss, Watson Trading Co., fair prices, knows routes)

### NPCs - Faction Members

- Include: faction, rank, ideology, equipment, personal goals
- Example: `Paladin_Hope` (Brotherhood of Steel, power armor, tech recovery, doubts leadership)

### NPCs - Raiders & Outcasts

- Include: gang, role, territory, brutality level, weaknesses
- Example: `Boss_Hook` (Rust Devils, mechanic, Fort Hagen, respects strength)

### NPCs - Ghouls & Mutants

- Include: mental state (feral/sentient), origin, abilities, relationships with humans
- Example: `Ghoul_Hancock` (pre-war lawyer, sentient, settlement mayor, distrusts smoothskins)

### Locations

- Settlements (defenses, population, resources)
- Ruins (danger level, loot, inhabitants)
- Vaults (number, experiment type, status)
- Faction bases
- Trade posts
- Radiation zones

### Items & Technology

- Weapons (condition, modifications, ammo type)
- Armor (protection, condition, special features)
- Chems (effects, addiction potential)
- Pre-war tech (function, rarity, value)

### Creatures & Threats

- Mutated animals (behavior, territory, danger)
- Robot types (programming, function, threat level)
- Anomalies (effects, location, avoidance)

## World-specific rules

1. **Track radiation**: Exposure accumulates, affects health and mutation risk
2. **Resource scarcity**: Ammo, meds, clean water are always valuable
3. **Faction reputation**: Actions have consequences across the wasteland
4. **Technology is power**: Pre-war tech is the ultimate prize
5. **Survival first**: The wasteland doesn't forgive mistakes

---

## Reference Sources for Wasteland World

Use these works and archetypes when creating NPC references (system will add them automatically after 3+ interactions).

### Good reference examples for Wasteland setting:

```json
{"reference": "Like The Ghoul from Fallout TV but still has moral code"}
{"reference": "Lucy MacLean's optimism with wasteland survival skills"}
{"reference": "Three Dog's charisma as settlement leader, not DJ"}
{"reference": "Like Artyom from Metro but more talkative, trader background"}
{"reference": "Mad Max's survival instinct with Lone Wanderer's curiosity"}
{"reference": "Nick Valentine's detective mind in ghoul body"}
{"reference": "Piper Wright's truth-seeking as caravan scout"}
{"reference": "Caesar's Legion discipline but protecting people, not enslaving"}
{"reference": "Elder Maxson's conviction but questions Brotherhood dogma"}
{"reference": "Strelok from STALKER - anomaly expert, lone wolf"}
```

**Post-apocalyptic core:**
- Fallout series (Lone Wanderer, Courier, Sole Survivor, The Ghoul, Lucy, Nick Valentine, Piper, Preston, Three Dog, Caesar, Elder Maxson)
- Fallout TV series (Cooper Howard/The Ghoul, Lucy MacLean, Maximus, Moldaver)
- Metro 2033/Last Light/Exodus (Artyom, Khan, Miller, Anna, Dark Ones, Polis rangers)
- S.T.A.L.K.E.R. (Strelok, Sidorovich, traders, stalkers, anomalies, the Zone)
- Mad Max (Max, Furiosa, Immortan Joe, War Boys, road warriors)
- The Road (survival, father-son, bleakness balanced with hope)
- A Boy and His Dog (cynical survival, underground societies)

**Character archetypes:**
- The Vault Dweller (naive but educated, fish out of water)
- The Wasteland Survivor (tough, resourceful, trust issues)
- The Ghoul (pre-war memories, centuries of experience, outsider)
- The Brotherhood Knight (military discipline, tech obsession)
- The Raider Boss (brutal but has code, territorial)
- The Caravan Guard (well-traveled, knows routes and dangers)
- The Settlement Leader (protector, weight of responsibility)
- The Scavenger (knows every ruin, survival instincts)

---

## Examples of good quants

```json
{
  "create_Settlement_Hope": {
    "type": "location",
    "synopsis": "fortified settlement in =Wasteland=, 200 people, farming and trading, needs help with raiders",
    "body": {
      "type": "Settlement",
      "location": "Former factory complex, three days east",
      "population": "~200 settlers, 30 militia",
      "defenses": "Concrete walls, guard towers, one working turret",
      "economy": "Mutfruit farming, water purifier, caravan stop",
      "leadership": "Mayor Elena, elected council",
      "problems": "Raider tribute demands increasing, need weapons"
    },
    "links": {
      "Factions": "independent settlement",
      "Economy_and_Trade": "trade post"
    },
    "is_game": true
  }
}
```

```json
{
  "create_Trader_Chester": {
    "type": "npc",
    "synopsis": "caravan master at =Settlement_Hope=, knows all routes, fair dealer, has pre-war map collection",
    "body": {
      "role": "Caravan Master / Trader",
      "location": "Travels circuit: Hope - Junction - Oasis - Hope",
      "personality": "Pragmatic, fair, loves old world maps and stories",
      "reference": "Like Canterbury Commons trader with Artyom's wanderlust",
      "appearance": "Weathered face, brahmin leather coat, pre-war compass always visible",
      "inventory": "General goods, maps, sometimes weapons, always has water",
      "secret": "Knows location of sealed Vault, waiting for right partner"
    },
    "links": {
      "Economy_and_Trade": "major trader",
      "Locations": "knows routes",
      "Transport_and_Travel": "caravan owner"
    },
    "is_game": true
  }
}
```

```json
{
  "create_Ghoul_Doctor_Mosely": {
    "type": "npc",
    "synopsis": "pre-war surgeon, sentient ghoul, runs clinic, hated and needed",
    "body": {
      "role": "Doctor / Surgeon",
      "origin": "Pre-war trauma surgeon, survived initial blasts",
      "mental_state": "Fully sentient, 200+ years of medical experience",
      "personality": "Bitter about prejudice, still feels duty to heal, dark humor",
      "reference": "Like The Ghoul's cynicism with Doctor Li's medical ethics",
      "appearance": "Radiation-scarred, wears pre-war doctor's coat, steady hands",
      "services": "Surgery, radiation treatment, chem detox (expensive)",
      "secret": "Remembers pre-war government secrets, blackmail material"
    },
    "links": {
      "Mutants_and_Creatures": "sentient ghoul",
      "Wasteland_Technology": "medical expertise",
      "Chems_and_Addiction": "detox treatment"
    },
    "is_game": true
  }
}
```

```json
{
  "create_Gang_Rusty_Claws": {
    "type": "npc",
    "synopsis": "raider gang controlling eastern highways, vehicle-focused, demand tribute from caravans",
    "body": {
      "type": "Raider Gang",
      "territory": "Eastern highway, old gas station complex",
      "size": "40-50 raiders, 12 working vehicles",
      "leadership": "Warlord 'Chrome' - former mechanic, respects machines",
      "tactics": "Vehicle ambushes, tribute demands, rarely kill if paid",
      "reference": "War Boys aesthetic with more practical survival focus",
      "weakness": "Dependent on fuel supply, rival gang to the south",
      "relations": "Extort caravans, trade with some settlements, hate Brotherhood"
    },
    "links": {
      "Factions": "raider faction",
      "Transport_and_Travel": "control roads",
      "Economy_and_Trade": "extortion economy"
    },
    "is_game": true
  }
}
```

```json
{
  "create_Anomaly_Glass_Field": {
    "type": "location",
    "synopsis": "radiation anomaly zone, sand fused to glass, contains valuable artifacts",
    "body": {
      "type": "Anomaly Zone",
      "location": "Old military testing ground, 2 days south",
      "danger": "Extreme radiation, glass shards, electrical discharges",
      "phenomena": "Sand fused to razor glass, lightning strikes without clouds",
      "reference": "Zone anomaly from STALKER but more visually striking",
      "artifacts": "Rumored pre-war military tech buried under glass",
      "inhabitants": "Feral ghouls, strange glowing creatures, no raiders dare enter"
    },
    "links": {
      "Radiation": "extreme radiation zone",
      "Wasteland_Technology": "potential tech cache"
    },
    "is_game": true
  }
}
```

## Notes

- Wasteland setting = survival, scarcity, factions, radiation, hope amid ruin
- Resources matter - track what people have and need
- Pre-war tech is always significant and valuable
- Every settlement has problems that need solving
- Track radiation exposure and faction reputation
