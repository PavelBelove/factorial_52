"""
World Manager - manages game worlds configuration and data loading.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class WorldManager:
    """
    Manages game worlds:
    - Scans available worlds from filesystem
    - Loads world configurations
    - Provides initial data for new games
    - Supports dynamic world addition
    """
    
    def __init__(self, worlds_dir: Path):
        """
        Initialize WorldManager.
        
        Args:
            worlds_dir: Path to worlds directory (usually data/worlds/)
        """
        self.worlds_dir = Path(worlds_dir)
        self._config_cache: Dict[str, dict] = {}  # Cache for world configs
        logger.info(f"WorldManager initialized with directory: {self.worlds_dir}")
    
    def scan_worlds(self) -> List[str]:
        """
        Scan worlds directory and find all available worlds.
        A world is valid if it has a config.json file.
        
        Returns:
            List of world IDs
        """
        if not self.worlds_dir.exists():
            logger.warning(f"Worlds directory does not exist: {self.worlds_dir}")
            return []
        
        worlds = []
        for world_dir in self.worlds_dir.iterdir():
            if world_dir.is_dir():
                config_file = world_dir / "config.json"
                if config_file.exists():
                    worlds.append(world_dir.name)
        
        logger.info(f"Found {len(worlds)} worlds: {worlds}")
        return worlds
    
    def get_world_config(self, world_id: str) -> Optional[Dict]:
        """
        Get configuration for a specific world.
        Uses cache to avoid repeated file reads.
        
        Args:
            world_id: World identifier (e.g., 'isekai')
            
        Returns:
            World configuration dict or None if not found
        """
        # Check cache first
        if world_id in self._config_cache:
            return self._config_cache[world_id]
        
        # Load from file
        config_path = self.worlds_dir / world_id / "config.json"
        if not config_path.exists():
            logger.error(f"Config not found for world: {world_id}")
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate required fields
            if 'id' not in config or 'name' not in config:
                logger.error(f"Invalid config for world {world_id}: missing required fields")
                return None
            
            # Cache it
            self._config_cache[world_id] = config
            logger.debug(f"Loaded config for world: {world_id}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading config for world {world_id}: {e}")
            return None
    
    def get_available_worlds(self, language: str = "ru") -> List[Dict]:
        """
        Get list of available worlds (enabled and with content).
        
        Args:
            language: Language code for names/descriptions
            
        Returns:
            List of world info dicts with keys: id, name, description, icon
        """
        world_ids = self.scan_worlds()
        available = []
        
        for world_id in world_ids:
            config = self.get_world_config(world_id)
            if not config:
                continue
            
            # Filter: only enabled worlds with content
            if not config.get('enabled', False) or not config.get('has_content', False):
                continue
            
            # Extract localized data
            world_info = {
                'id': config['id'],
                'name': config.get('name', {}).get(language, config.get('name', {}).get('ru', world_id)),
                'description': config.get('description', {}).get(language, config.get('description', {}).get('ru', '')),
                'icon': config.get('icon', '🌍'),
                'tags': config.get('tags', [])
            }
            available.append(world_info)
        
        logger.info(f"Found {len(available)} available worlds")
        return available
    
    def load_world_initial_data(self, world_id: str, language: str = "ru") -> Optional[Dict]:
        """
        Load initial game data for a world.
        
        Args:
            world_id: World identifier
            language: Language code (for future multi-language support)
            
        Returns:
            Dict with keys: initial_quants, initial_summary, quantizer_instructions
            or None if world not found or data missing
        """
        world_dir = self.worlds_dir / world_id
        if not world_dir.exists():
            logger.error(f"World directory not found: {world_id}")
            return None
        
        data = {}
        
        # Load initial quants
        quants_file = world_dir / f"initial_quants.json"
        if quants_file.exists():
            try:
                with open(quants_file, 'r', encoding='utf-8') as f:
                    data['initial_quants'] = json.load(f)
                logger.debug(f"Loaded {len(data['initial_quants'])} initial quants for {world_id}")
            except Exception as e:
                logger.error(f"Error loading initial quants for {world_id}: {e}")
                data['initial_quants'] = []
        else:
            logger.warning(f"Initial quants file not found for {world_id}")
            data['initial_quants'] = []
        
        # Load initial summary
        summary_file = world_dir / f"initial_summary.md"
        if summary_file.exists():
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    data['initial_summary'] = f.read().strip()
                logger.debug(f"Loaded initial summary for {world_id}")
            except Exception as e:
                logger.error(f"Error loading initial summary for {world_id}: {e}")
                data['initial_summary'] = ""
        else:
            logger.warning(f"Initial summary file not found for {world_id}")
            data['initial_summary'] = ""
        
        # Load quantizer instructions
        instructions_file = world_dir / f"quantizer_instructions.md"
        if instructions_file.exists():
            try:
                with open(instructions_file, 'r', encoding='utf-8') as f:
                    data['quantizer_instructions'] = f.read().strip()
                logger.debug(f"Loaded quantizer instructions for {world_id}")
            except Exception as e:
                logger.error(f"Error loading quantizer instructions for {world_id}: {e}")
                data['quantizer_instructions'] = ""
        else:
            logger.warning(f"Quantizer instructions file not found for {world_id}")
            data['quantizer_instructions'] = ""
        
        logger.info(f"Loaded initial data for world: {world_id}")
        return data
    
    def get_quantizer_instructions(self, world_id: str) -> str:
        """
        Get world-specific instructions for Quantizer agent.
        These are appended to base Quantizer prompt.
        
        Args:
            world_id: World identifier
            
        Returns:
            Instructions text or empty string if not found
        """
        instructions_file = self.worlds_dir / world_id / "quantizer_instructions.md"
        if not instructions_file.exists():
            logger.warning(f"Quantizer instructions not found for {world_id}")
            return ""
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error reading quantizer instructions for {world_id}: {e}")
            return ""
    
    def get_initial_quants(self, world_id: str) -> List[Dict]:
        """
        Get initial quants for a world.
        
        Args:
            world_id: World identifier
            
        Returns:
            List of quant data dicts
        """
        quants_file = self.worlds_dir / world_id / "initial_quants.json"
        if not quants_file.exists():
            logger.warning(f"Initial quants file not found for {world_id}")
            return []
        
        try:
            with open(quants_file, 'r', encoding='utf-8') as f:
                quants = json.load(f)
            logger.debug(f"Loaded {len(quants)} initial quants for {world_id}")
            return quants
        except Exception as e:
            logger.error(f"Error loading initial quants for {world_id}: {e}")
            return []
    
    def get_initial_summary(self, world_id: str) -> str:
        """
        Get initial summary for a world.
        
        Args:
            world_id: World identifier
            
        Returns:
            Summary text or empty string if not found
        """
        summary_file = self.worlds_dir / world_id / "initial_summary.md"
        if not summary_file.exists():
            logger.warning(f"Initial summary file not found for {world_id}")
            return ""
        
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = f.read().strip()
            logger.debug(f"Loaded initial summary for {world_id}")
            return summary
        except Exception as e:
            logger.error(f"Error loading initial summary for {world_id}: {e}")
            return ""
    
    def get_gm_system_prompt(
        self,
        world_id: str,
        language: str = "ru",
        content_filter: str = "safe"
    ) -> str:
        """
        Get world-specific GM system prompt with dynamic variable substitution.

        Args:
            world_id: World identifier
            language: User's language preference (ru/en)
            content_filter: Content filter level (safe/romantic/adult)

        Returns:
            GM system prompt text with variables substituted
        """
        gm_system_file = self.worlds_dir / world_id / "gm_system.md"
        if not gm_system_file.exists():
            logger.debug(f"No world-specific gm_system.md for {world_id}")
            return ""

        try:
            with open(gm_system_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # Substitute language
            language_map = {
                "ru": "Russian",
                "en": "English",
                "de": "German",
                "fr": "French",
                "es": "Spanish",
            }
            language_name = language_map.get(language, "Russian")
            content = content.replace("Russian language", f"{language_name} language")
            content = content.replace("IN RUSSIAN", f"IN {language_name.upper()}")
            content = content.replace("in Russian", f"in {language_name}")
            content = content.replace("Respond in Russian", f"Respond in {language_name}")

            # Substitute content filter - replace the consent line
            content_texts = {
                "safe": (
                    "**IMPORTANT: Avoid erotic and sexual themes. "
                    "Keep romantic scenes tasteful and fade to black for intimate moments. "
                    "Focus on adventure and story.**"
                ),
                "romantic": (
                    "**Content rating: 16+. Light romantic and erotic context is allowed. "
                    "Artistic descriptions of bodies without explicit sexual acts. "
                    "Fade to black for intimate scenes.**"
                ),
                "adult": (
                    "**User has given voluntary informed consent to explicit erotic content. "
                    "Adult sexual scenes without restrictions are permitted when contextually appropriate.**"
                ),
            }
            content_text = content_texts.get(content_filter, content_texts["safe"])

            # Replace existing consent lines with appropriate filter
            import re
            # Match lines about consent/content
            consent_patterns = [
                r"User has consented to.*?\.",
                r"\*\*IMPORTANT:.*?fade to black.*?\*\*",
                r"\*\*Content rating:.*?\*\*",
            ]
            for pattern in consent_patterns:
                content = re.sub(pattern, "", content, flags=re.IGNORECASE | re.DOTALL)

            # Insert content filter text after the role line
            role_marker = "# Role:"
            if role_marker in content:
                lines = content.split('\n')
                new_lines = []
                inserted = False
                for line in lines:
                    new_lines.append(line)
                    if not inserted and line.startswith(role_marker):
                        # Find the next empty line after role description
                        pass
                    if not inserted and line.strip() == "" and len(new_lines) > 2:
                        new_lines.append(content_text)
                        new_lines.append("")
                        inserted = True
                if not inserted:
                    new_lines.insert(2, content_text)
                    new_lines.insert(3, "")
                content = '\n'.join(new_lines)

            logger.debug(f"Loaded GM prompt for {world_id} (lang={language}, filter={content_filter})")
            return content
        except Exception as e:
            logger.error(f"Error reading gm_system.md for {world_id}: {e}")
            return ""

    def clear_cache(self):
        """Clear configuration cache. Useful for development/testing."""
        self._config_cache.clear()
        logger.debug("World config cache cleared")

