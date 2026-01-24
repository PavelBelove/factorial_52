# Factorial 52! 🎲

AI-powered text RPG with quantum memory system based on Zettelkasten methodology.

## Features

- 🤖 **AI Game Master** - Dynamic narrative powered by DeepSeek V3.2 and Grok-4.1-Fast
- 🧠 **Quantum Memory** - Zettelkasten-based knowledge graph for consistent world building
- 🎴 **Card-based Mechanics** - Unique "Factorial 52!" game system with suits and bonuses
- 📱 **Telegram Bot** - Play directly in Telegram
- 💾 **Persistent Memory** - Every NPC, location, and event is remembered
- 🌐 **Multi-agent System** - Specialized AI agents for game mastering, memory management, and summarization

## Game System

**Suits:**
- ♠ Spades: Strength (melee combat, intimidation)
- ♥ Hearts: Magic (spells, communication)
- ♦ Diamonds: Stamina (defense, trading)
- ♣ Clubs: Agility (ranged combat, stealth)

**Agents:**
- **Game Master** - Creates narrative and manages gameplay
- **Quantizer** - Manages memory quants (NPCs, locations, items, quests)
- **Summarizer** - Condenses history for efficient context
- **Translator** - Optimizes token usage by structuring turns

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite
- **LLM:** OpenRouter API (DeepSeek V3.2, Grok-4.1-Fast)
- **Bot:** aiogram (Telegram Bot API)
- **Memory:** Custom Zettelkasten implementation with fuzzy matching

## Quick Start

### Local Development

```bash
# Clone repository
git clone git@github.com:PavelBelove/factorial_52.git
cd factorial_52

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run API
python run_api.py

# Run bot (in another terminal)
python run_bot.py
```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed server setup instructions.

Quick deploy on configured server:
```bash
cd /home/plexmem/plexmem
./deploy.sh
```

## Project Structure

```
factorial_52/
├── core/
│   ├── agents/          # AI agents (GM, Quantizer, Summarizer, Translator)
│   ├── api/             # FastAPI application
│   ├── database/        # SQLAlchemy models and database manager
│   ├── llm/             # OpenRouter client
│   ├── managers/        # Context, Memory managers
│   ├── mechanics/       # Game mechanics (cards, checks, combat)
│   └── models/          # Pydantic models
├── telegram/            # Telegram bot
├── prompts/             # Agent system prompts
├── data/                # Database and initial data
├── logs/                # Application logs
└── scripts/             # Utility scripts and migrations
```

## Commands

- `/start` - Start new game
- `/help` - Show game rules
- `/stats` - Character statistics
- `/inventory` - View items
- `/session` - Session info
- `/cost` - Token usage costs
- `/retry` - Retry last turn
- `/undo` - Undo last action

## Architecture

### Memory System
Based on Zettelkasten methodology:
- **Quants** - Atomic units of knowledge (NPC, Location, Item, Quest, etc.)
- **Links** - Bidirectional connections between quants
- **Synopsis** - Brief semantic descriptions for context navigation
- **Markers** - `=QuantName=` tags for semantic anchoring

### Agent Pipeline
1. **Player Input** → Context Manager builds full context
2. **Game Master** → Generates narrative + requests quants
3. **Quantizer** → Creates/updates memory quants (async)
4. **Translator** → Structures turn to English JSON for token efficiency (async)
5. **Summarizer** → Condenses old turns when threshold reached (async)

### Token Optimization
- English prompts + context (25-30% token reduction)
- Translator agent structures raw turns to JSON
- Automatic summarization after 10 turns
- Quant auto-summarization for long content (>3000 chars)

## Development

```bash
# Run in debug mode
DEBUG=True python run_api.py

# View agent debug logs
ls -la logs/agents/
cat logs/agents/gm_last.log

# Database migrations
python scripts/add_translator_fields.py
python scripts/add_needs_summarization.py
```

## License

MIT

## Author

Pavel Belove - [@PavelBelove](https://github.com/PavelBelove)

## Links

- Domain: https://factorial.agints.ru
- Bot: [@factorial_52_bot](https://t.me/factorial_52_bot)
