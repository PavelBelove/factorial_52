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
    # OpenAI GPT-OSS-120B - стабильная модель с хорошим соотношением цена/качество
    # https://openrouter.ai/openai/gpt-oss-120b
    gm_model: str = "openai/gpt-oss-120b"  # Game Master model
    quantizer_model: str = "openai/gpt-oss-120b"  # Quantizer model  
    summarizer_model: str = "openai/gpt-oss-120b"  # Summarizer model
    translator_model: str = "openai/gpt-oss-120b"  # Translator model
    
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
    
    # Streaming Configuration
    enable_streaming: bool = True  # Enable streaming GM responses for better UX
    streaming_chunk_interval: float = 1  # Seconds between narrative chunk updates (Telegram limit ~1/sec)
    streaming_loading_interval: float = 0.5  # Seconds between loading animation dots
    streaming_min_chars_for_update: int = 150  # Minimum characters before sending update
    streaming_timeout: int = 30  # Seconds before considering stream as failed
    
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
    quantizer_trigger_turns: int = 3  # Run Quantizer every N turns (starting from turn 3)
    
    # Quants management
    quants_synopsis_window: int = 30  # How many turns back to show quants synopsis for GM/Quantizer
    
    # Summarizer configuration
    summary_append_threshold: int = 2000  # Characters threshold for append mode
    summary_max_length: int = 20000  # Maximum summary length before forced rewrite ("drying")
    
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
    
    # GM Response constraints
    gm_response_max_tokens: int = 1000  # Maximum tokens for GM response (not characters!)
    gm_response_min_tokens: int = 700   # Minimum tokens for GM response
    gm_quants_min_request: int = 3      # Minimum quants GM should request for next turn
    gm_quants_max_request: int = 10     # Maximum quants GM should request for next turn
    
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


def get_prompt_template_vars() -> dict:
    """Get template variables for prompt substitution."""
    return {
        "max_tokens": settings.gm_response_max_tokens,
        "min_tokens": settings.gm_response_min_tokens,
        "min_quants": settings.gm_quants_min_request,
        "max_quants": settings.gm_quants_max_request,
        # Future: difficulty, content_policy, game_style will be added here
    }

# World manager
from core.managers.world_manager import WorldManager
world_manager = WorldManager(WORLDS_DIR)

