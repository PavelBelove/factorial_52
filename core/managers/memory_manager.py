"""
Memory Manager - manages quants (atomic memory units).
Handles creation, updates, retrieval, and command parsing.
"""
import json
import logging
from typing import List, Optional, Dict, Any
from rapidfuzz import fuzz

from core.database.db_manager import DatabaseManager
from core.models import Quant, QuantType, QuantCommand
from core.config import settings

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages all operations with quants (memory units).
    
    Key responsibilities:
    - Parse commands from Quantizer agent
    - Create, update, delete quants
    - Fuzzy search for quant names
    - Retrieve quants by IDs
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize memory manager."""
        self.db = db_manager
    
    # ============= RETRIEVAL =============
    
    def get_quants_by_names(
        self,
        session_id: int,
        quant_names: List[str],
        fuzzy: bool = True,
        threshold: Optional[int] = None
    ) -> List[Quant]:
        """
        Get quants by their names with fuzzy matching support.
        
        Args:
            session_id: Session ID
            quant_names: List of quant names to retrieve
            fuzzy: Whether to use fuzzy matching
            threshold: Fuzzy match threshold (0-100). If None, uses config value.
        
        Returns:
            List of Quant objects
        """
        # Use threshold from config if not specified
        if threshold is None:
            threshold = settings.fuzzy_match_threshold
        if not quant_names:
            return []
        
        # Get all quants for the session
        all_quants = self.db.get_all_quants(session_id)
        
        if not fuzzy:
            # Exact match
            found_quants = [
                q for q in all_quants
                if q.quant_id in quant_names
            ]
        else:
            # Fuzzy match (including aliases)
            found_quants = []
            for requested_name in quant_names:
                best_match = None
                best_score = 0
                match_type = "id"
                
                for db_quant in all_quants:
                    # Check main ID
                    score = fuzz.ratio(requested_name.lower(), db_quant.quant_id.lower())
                    if score > best_score and score >= threshold:
                        best_score = score
                        best_match = db_quant
                        match_type = "id"
                    
                    # Check aliases
                    if db_quant.aliases:
                        for alias in db_quant.aliases:
                            alias_score = fuzz.ratio(requested_name.lower(), alias.lower())
                            if alias_score > best_score and alias_score >= threshold:
                                best_score = alias_score
                                best_match = db_quant
                                match_type = f"alias '{alias}'"
                
                if best_match and best_match not in found_quants:
                    found_quants.append(best_match)
                    logger.debug(
                        f"Fuzzy matched '{requested_name}' to '{best_match.quant_id}' "
                        f"via {match_type} (score: {best_score})"
                    )
        
        # Convert to Pydantic models
        return [self._db_quant_to_model(q) for q in found_quants]
    
    def get_all_quants(self, session_id: int) -> List[Quant]:
        """Get all quants for a session."""
        db_quants = self.db.get_all_quants(session_id)
        return [self._db_quant_to_model(q) for q in db_quants]
    
    # ============= COMMAND PROCESSING =============
    
    def process_commands(
        self,
        session_id: int,
        commands: Dict[str, Any],
        current_turn: int
    ) -> Dict[str, Any]:
        """
        Process commands from Quantizer agent.
        
        Commands format:
        {
            "create_Елена": {...full quant data...},
            "append_Маша_body_notes": "новая заметка",
            "replace_Маша_links_Таверна": "уволилась",
            "delete_Старый_квант": null
        }
        
        Returns:
            Dict with results and errors
        """
        results = {
            "created": [],
            "updated": [],
            "deleted": [],
            "errors": []
        }
        
        for command_str, value in commands.items():
            try:
                # Parse command: action_quantid or action_quantid_path
                # Split only by first underscore to get action
                parts = command_str.split("_", 1)
                if len(parts) < 2:
                    raise ValueError(f"Invalid command format: {command_str}")
                
                action = parts[0].lower()
                remaining = parts[1]
                
                # For create/delete: remaining is just quant_id
                # For append/replace: remaining is quant_id_path
                if action in ["create", "delete"]:
                    quant_id = remaining
                    path = None
                else:
                    # For append/replace, split remaining by underscore to separate quant_id and path
                    # Need to find where quant_id ends and path begins
                    # Path is typically: body_notes, links_Name, etc
                    # So look for known path prefixes
                    if "_body_" in remaining:
                        parts = remaining.split("_body_", 1)
                        quant_id = parts[0]
                        path = "body_" + parts[1]
                    elif "_links_" in remaining:
                        parts = remaining.split("_links_", 1)
                        quant_id = parts[0]
                        path = "links_" + parts[1]
                    else:
                        # Fallback: assume last underscore separates quant_id from path
                        parts = remaining.rsplit("_", 1)
                        if len(parts) == 2:
                            quant_id, path = parts
                        else:
                            quant_id = remaining
                            path = None
                
                # Execute command
                if action == "create":
                    self._execute_create(session_id, quant_id, value, current_turn, results)
                
                elif action == "append":
                    self._execute_append(session_id, quant_id, path, value, current_turn, results)
                
                elif action == "replace":
                    self._execute_replace(session_id, quant_id, path, value, current_turn, results)
                
                elif action == "delete":
                    self._execute_delete(session_id, quant_id, results)
                
                elif action == "rename":
                    self._execute_rename(session_id, quant_id, value, current_turn, results)
                
                else:
                    results["errors"].append(f"Unknown action: {action}")
                
            except Exception as e:
                logger.error(f"Error processing command '{command_str}': {e}")
                results["errors"].append(f"{command_str}: {str(e)}")
        
        return results
    
    def _execute_create(
        self,
        session_id: int,
        quant_id: str,
        data: Dict[str, Any],
        current_turn: int,
        results: Dict
    ):
        """Execute create command."""
        # Check if quant already exists
        existing = self.db.get_quant(session_id, quant_id)
        if existing:
            # Update instead of create
            self._execute_replace(session_id, quant_id, None, data, current_turn, results)
            return
        
        # Create new quant
        quant = Quant(
            id=quant_id,
            type=QuantType(data.get("type", "other")),
            synopsis=data.get("synopsis"),
            body=data.get("body", {}),
            links=data.get("links", {}),
            created_at=current_turn,
            updated_at=current_turn,
            is_game=data.get("is_game", False)
        )
        
        self.db.create_quant(session_id, quant)
        results["created"].append(quant_id)
        logger.info(f"Created quant: {quant_id}")
    
    def _execute_append(
        self,
        session_id: int,
        quant_id: str,
        path: Optional[str],
        value: Any,
        current_turn: int,
        results: Dict
    ):
        """Execute append command with deduplication."""
        db_quant = self.db.get_quant(session_id, quant_id)
        if not db_quant:
            results["errors"].append(f"Quant not found: {quant_id}")
            return
        
        if not path:
            results["errors"].append(f"Path required for append: {quant_id}")
            return
        
        # Parse path (e.g., "body_notes" or "links_Таверна")
        path_parts = path.split("_", 1)
        if len(path_parts) != 2:
            results["errors"].append(f"Invalid path format: {path}")
            return
        
        section, key = path_parts
        
        # Append to section
        if section == "body":
            body = db_quant.body.copy()
            if key in body:
                # Check for duplicates before appending
                if isinstance(body[key], str) and isinstance(value, str):
                    # Fuzzy check for duplicate content
                    if self._is_duplicate_content(body[key], value):
                        logger.info(f"Skipping duplicate append to {quant_id}.{key}: '{value[:50]}...'")
                        results["skipped"] = results.get("skipped", 0) + 1
                        return
                    body[key] = f"{body[key]}; {value}"
                elif isinstance(body[key], list):
                    # Check if value already in list
                    if value not in body[key]:
                        body[key].append(value)
                    else:
                        logger.info(f"Skipping duplicate list item in {quant_id}.{key}")
                        results["skipped"] = results.get("skipped", 0) + 1
                        return
                else:
                    body[key] = value
            else:
                body[key] = value
            
            self.db.update_quant(
                session_id,
                quant_id,
                body=body,
                updated_at=current_turn
            )
        
        elif section == "links":
            links = db_quant.links.copy()
            links[key] = value
            
            self.db.update_quant(
                session_id,
                quant_id,
                links=links,
                updated_at=current_turn
            )
        
        else:
            results["errors"].append(f"Unknown section: {section}")
            return
        
        results["updated"].append(quant_id)
        logger.info(f"Appended to quant {quant_id}: {section}.{key}")
    
    def _execute_replace(
        self,
        session_id: int,
        quant_id: str,
        path: Optional[str],
        value: Any,
        current_turn: int,
        results: Dict
    ):
        """Execute replace command."""
        db_quant = self.db.get_quant(session_id, quant_id)
        if not db_quant:
            results["errors"].append(f"Quant not found: {quant_id}")
            return
        
        # Full replacement
        if not path:
            if isinstance(value, dict):
                # Replace entire quant
                self.db.update_quant(
                    session_id,
                    quant_id,
                    body=value.get("body", db_quant.body),
                    links=value.get("links", db_quant.links),
                    updated_at=current_turn
                )
                results["updated"].append(quant_id)
                logger.info(f"Replaced entire quant: {quant_id}")
            else:
                results["errors"].append(f"Full replace requires dict: {quant_id}")
            return
        
        # Partial replacement
        # Special case: "synopsis" without underscore
        if path == "synopsis":
            self.db.update_quant(
                session_id,
                quant_id,
                synopsis=value,
                updated_at=current_turn
            )
            results["updated"].append(quant_id)
            logger.info(f"Replaced synopsis for quant: {quant_id}")
            return
        
        path_parts = path.split("_", 1)
        if len(path_parts) != 2:
            results["errors"].append(f"Invalid path format: {path}")
            return
        
        section, key = path_parts
        
        if section == "body":
            body = db_quant.body.copy()
            body[key] = value
            
            self.db.update_quant(
                session_id,
                quant_id,
                body=body,
                updated_at=current_turn
            )
        
        elif section == "links":
            links = db_quant.links.copy()
            links[key] = value
            
            self.db.update_quant(
                session_id,
                quant_id,
                links=links,
                updated_at=current_turn
            )
        
        else:
            results["errors"].append(f"Unknown section: {section}")
            return
        
        results["updated"].append(quant_id)
        logger.info(f"Replaced in quant {quant_id}: {section}.{key}")
    
    def _execute_delete(
        self,
        session_id: int,
        quant_id: str,
        results: Dict
    ):
        """Execute delete command."""
        db_quant = self.db.get_quant(session_id, quant_id)
        if not db_quant:
            results["errors"].append(f"Quant not found: {quant_id}")
            return
        
        self.db.delete_quant(session_id, quant_id)
        results["deleted"].append(quant_id)
        logger.info(f"Deleted quant: {quant_id}")
    
    def _execute_rename(
        self,
        session_id: int,
        old_id: str,
        new_id: str,
        current_turn: int,
        results: Dict
    ):
        """
        Rename quant: change main ID, add old name as alias.
        Format: rename_OldName: "NewName"
        """
        db_quant = self.db.get_quant(session_id, old_id)
        if not db_quant:
            results["errors"].append(f"Quant not found for rename: {old_id}")
            return
        
        # Check if new name already exists
        existing = self.db.get_quant(session_id, new_id)
        if existing:
            results["errors"].append(f"Cannot rename to {new_id}: already exists")
            return
        
        # Add old name to aliases if not already there
        aliases = db_quant.aliases or []
        if old_id not in aliases:
            aliases.append(old_id)
        
        # Update quant with new ID
        self.db.update_quant(
            session_id,
            old_id,
            body=db_quant.body,
            links=db_quant.links,
            updated_at=current_turn
        )
        
        # Actually rename in database (need new method)
        self.db.rename_quant(session_id, old_id, new_id, aliases)
        
        results["renamed"] = results.get("renamed", [])
        results["renamed"].append(f"{old_id} → {new_id}")
        logger.info(f"Renamed quant: {old_id} → {new_id} (old name added as alias)")
    
    def _is_duplicate_content(self, existing: str, new: str, threshold: int = 85) -> bool:
        """
        Check if new content is duplicate of existing using fuzzy matching.
        
        Args:
            existing: Existing content string
            new: New content to check
            threshold: Similarity threshold (0-100)
        
        Returns:
            True if new content is similar to existing (likely duplicate)
        """
        from fuzzywuzzy import fuzz
        
        # Split existing content by separators
        existing_parts = existing.split(';')
        
        # Check if new content is similar to any existing part
        for part in existing_parts:
            part = part.strip()
            if not part:
                continue
            
            # Calculate similarity
            similarity = fuzz.token_set_ratio(part.lower(), new.lower())
            
            if similarity >= threshold:
                logger.debug(f"Found duplicate content (similarity: {similarity}%): '{new[:50]}...' ≈ '{part[:50]}...'")
                return True
        
        return False
    
    def get_recent_quants_synopsis(
        self,
        session_id: int,
        current_turn: int,
        window: int = None
    ) -> str:
        """
        Get synopsis list of quants updated/created in last N turns.
        Returns formatted string for context: "ID: synopsis"
        
        Args:
            session_id: Session ID
            current_turn: Current turn number
            window: Number of turns to look back (default from settings)
        
        Returns:
            Formatted string with synopsis list
        """
        from core.config import settings
        
        if window is None:
            window = settings.quants_synopsis_window
        
        # Get all quants
        all_quants = self.db.get_all_quants(session_id)
        
        # Filter quants updated/created in last N turns
        min_turn = max(0, current_turn - window)
        recent_quants = [
            q for q in all_quants
            if (q.updated_at and q.updated_at >= min_turn) or 
               (q.created_at and q.created_at >= min_turn)
        ]
        
        if not recent_quants:
            return ""
        
        # Sort by updated_at desc
        recent_quants.sort(key=lambda q: q.updated_at or q.created_at or 0, reverse=True)
        
        # Format as list
        synopsis_lines = []
        for q in recent_quants:
            synopsis = q.synopsis or f"[{q.type}]"
            synopsis_lines.append(f"- **{q.quant_id}**: {synopsis}")
        
        return "\n".join(synopsis_lines)
    
    # ============= UTILITIES =============
    
    def _db_quant_to_model(self, db_quant) -> Quant:
        """Convert database quant to Pydantic model."""
        return Quant(
            id=db_quant.quant_id,
            type=QuantType(db_quant.type),
            synopsis=db_quant.synopsis,
            body=db_quant.body or {},
            links=db_quant.links or {},
            aliases=db_quant.aliases or [],
            created_at=db_quant.created_at,
            updated_at=db_quant.updated_at,
            is_game=db_quant.is_game
        )

