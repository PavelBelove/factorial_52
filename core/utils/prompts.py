"""
Utilities for loading prompts from files with Jinja2 templating support.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Template

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_prompt(prompt_name: str) -> str:
    """
    Load prompt from markdown file.
    
    Args:
        prompt_name: Name of prompt file (without .md extension)
        
    Returns:
        Prompt content as string
        
    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    prompt_path = PROJECT_ROOT / "prompts" / f"{prompt_name}.md"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


# Cache for loaded prompts
_prompts_cache: Dict[str, str] = {}


def get_prompt(prompt_name: str, use_cache: bool = True) -> str:
    """
    Get prompt content, with optional caching.
    
    Args:
        prompt_name: Name of prompt file (without .md extension)
        use_cache: Whether to use cached version
        
    Returns:
        Prompt content as string
    """
    if not use_cache or prompt_name not in _prompts_cache:
        _prompts_cache[prompt_name] = load_prompt(prompt_name)
    
    return _prompts_cache[prompt_name]


def clear_prompts_cache():
    """Clear prompts cache. Useful for development/testing."""
    _prompts_cache.clear()


def render_prompt(prompt_name: str, variables: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> str:
    """
    Load prompt and render it with Jinja2 template variables.

    Args:
        prompt_name: Name of prompt file (without .md extension)
        variables: Dictionary of template variables (e.g., {"language": "Russian"})
        use_cache: Whether to use cached template

    Returns:
        Rendered prompt content
    """
    template_content = get_prompt(prompt_name, use_cache=use_cache)

    if not variables:
        return template_content

    template = Template(template_content)
    return template.render(**variables)


def render_world_prompt(world_prompt: str, variables: Optional[Dict[str, Any]] = None) -> str:
    """
    Render world-specific prompt with Jinja2 template variables.

    Args:
        world_prompt: Raw prompt content from world file
        variables: Dictionary of template variables

    Returns:
        Rendered prompt content
    """
    if not variables:
        return world_prompt

    template = Template(world_prompt)
    return template.render(**variables)


# Convenience constants for prompt names
PROMPT_GM = "gm_system"
PROMPT_QUANTIZER = "quantizer_system"
PROMPT_SUMMARIZER_APPEND = "summarizer_append"
PROMPT_SUMMARIZER_REWRITE = "summarizer_rewrite"

