"""
Configuration module for PlexMem system.
Loads settings from environment variables and provides application-wide configuration.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenRouter API Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Model configuration per agent (can be customized separately)
    # Grok 4.1 Fast - быстрая агентская модель с 128K контекстом
    # https://openrouter.ai/x-ai/grok-4.1-fast
    gm_model: str = "deepseek/deepseek-v3.2"  # Game Master model
    quantizer_model: str = "x-ai/grok-4.1-fast"  # Quantizer model  
    summarizer_model: str = "x-ai/grok-4.1-fast"  # Summarizer model
    translator_model: str = "x-ai/grok-4.1-fast"  # Translator model (cheapest for simple JSON)
    
    # Max tokens for each agent (output length)
    gm_max_tokens: int = 3500  # GM can give longer, detailed responses
    quantizer_max_tokens: int = 4000  # Quantizer needs MORE space for multiple commands
    summarizer_max_tokens: int = 4000  # Summarizer condenses text
    
    # Database Configuration
    database_url: str = "sqlite:///data/plexmem.db"
    
    # Application Settings
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    debug_verbose: bool = False  # If True, print raw LLM inputs/outputs to console
    
    # Memory System Configuration
    
    # Quants activation
    min_quants_per_request: int = 3  # Minimum quants GM should request
    max_quants_per_request: int = 10  # Maximum quants GM can request
    recommended_quants: int = 7  # Recommended number (Character + Inventory + 5 context)
    
    # Synopsis window - quants from last N turns for quick navigation
    quants_synopsis_window: int = 30  # Show synopsis of quants updated/created in last 30 turns
    
    # Raw turns management
    raw_turns_keep: int = 5  # How many raw turns to keep after summarization (trimmed to this after summarizer runs)
    raw_turns_max: int = 10  # When raw turns >= this, trigger Summarizer (then trim to raw_turns_keep)
    
    # Summarizer configuration
    summary_append_threshold: int = 2000  # Characters threshold for append mode
    summary_max_length: int = 5000  # Maximum summary length before forced rewrite
    
    # Quantizer configuration
    quantizer_max_commands: int = 15  # Maximum commands per Quantizer execution
    
    # Fuzzy matching for quant names
    fuzzy_match_threshold: int = 85  # Similarity threshold (0-100) for quant name matching
    
    # Quant summarization
    quant_summarization_threshold: int = 3000  # Max length for quant content before needs_summarization flag is set
    
    # Telegram Bot (Phase 2)
    telegram_bot_token: str = ""
    
    # Quant name marker (for summary and context)
    quant_marker: str = "="
    
    # Localization & Worlds
    default_language: str = "ru"  # Default language
    available_languages: list[str] = ["ru", "en"]  # Available languages (only ru is fully translated)
    default_world: str = "isekai"  # Default world if not specified
    max_save_slots: int = 5  # Maximum save slots per user
    
    # Telegram FSM
    fsm_ttl_seconds: int = 3600  # FSM state TTL (1 hour)
    
    # Prompt templating (future feature - for user gameplay customization)
    prompt_use_templates: bool = True  # Enable Jinja2 templating in prompts
    # Future template variables: {difficulty}, {content_policy}, {game_style}, {world_setting}
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env for backwards compatibility


# Initialize settings
try:
    settings = Settings()
except Exception as e:
    print(f"Warning: Could not load settings from .env file: {e}")
    print("Using default values. Make sure to create .env file from .env.example")
    # Create minimal settings for development
    settings = Settings(
        openrouter_api_key=""
    )


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
WORLDS_DIR = DATA_DIR / "worlds"  # Worlds configuration directory
PROMPTS_DIR = PROJECT_ROOT / "prompts"  # Prompts directory

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
WORLDS_DIR.mkdir(exist_ok=True)

# Localization
LOCALIZATION_DIR = PROJECT_ROOT / "core" / "localization"

# Initialize localizations
from core.localization.ru import RussianLocalization
from core.localization.en import EnglishLocalization

_available_localizations = {
    "ru": RussianLocalization(),
    "en": EnglishLocalization()
}

def get_localization(lang_code: str):
    """Get localization instance by language code."""
    return _available_localizations.get(lang_code, _available_localizations[settings.default_language])

# World manager
from core.managers.world_manager import WorldManager
world_manager = WorldManager(WORLDS_DIR)

