"""
Partial JSON parser for streaming GM responses.

This module handles parsing incomplete JSON as it arrives from the LLM stream,
extracting the narrative text progressively while ensuring proper escaping.
"""
import re
from typing import Optional
from enum import Enum


class ParserState(Enum):
    """States of the JSON parsing process."""
    SEARCHING = "searching"      # Looking for "reply":"
    IN_NARRATIVE = "narrative"   # Reading narrative content
    COMPLETE = "complete"        # Found end of narrative


class PartialJSONParser:
    """
    Parse GM narrative from incomplete JSON stream.
    
    The GM response format is:
    {
      "reply": "Full narrative text...",
      "mechanics": {...},
      "quant_commands": [...]
    }
    
    This parser extracts the narrative text progressively as the stream arrives,
    handling escaped quotes and ensuring we don't break words.
    """
    
    def __init__(self):
        """Initialize parser state."""
        self.state = ParserState.SEARCHING
        self.buffer = ""  # Accumulated JSON text
        self.narrative = ""  # Extracted narrative
        self.last_sent_position = 0  # Position in narrative we last returned
        
    def feed_chunk(self, chunk: str) -> Optional[str]:
        """
        Feed a new chunk of JSON text to the parser.
        
        Args:
            chunk: New text from the stream
            
        Returns:
            New narrative text to display (or None if nothing new)
        """
        self.buffer += chunk
        
        if self.state == ParserState.SEARCHING:
            self._search_for_narrative_start()
            
        if self.state == ParserState.IN_NARRATIVE:
            self._extract_narrative()
            
        # Return new text if we have any
        if len(self.narrative) > self.last_sent_position:
            # Get text we haven't sent yet
            new_text = self.narrative[self.last_sent_position:]
            
            # Don't break words - cut at last space/newline if mid-word
            if self.state != ParserState.COMPLETE and new_text:
                new_text = self._trim_to_word_boundary(new_text)
            
            if new_text:
                self.last_sent_position += len(new_text)
                return self.narrative[:self.last_sent_position]
        
        return None
    
    def _search_for_narrative_start(self):
        """Search for the start of the narrative field."""
        # Look for "reply": " (with possible whitespace)
        match = re.search(r'"reply"\s*:\s*"', self.buffer)
        if match:
            # Found start of narrative
            self.state = ParserState.IN_NARRATIVE
            # Remove everything before the narrative start
            start_pos = match.end()
            self.buffer = self.buffer[start_pos:]
    
    def _extract_narrative(self):
        """Extract narrative text, handling escaping."""
        # Look for unescaped closing quote followed by comma or closing brace
        pos = 0
        while pos < len(self.buffer):
            # Find next quote
            quote_pos = self.buffer.find('"', pos)
            if quote_pos == -1:
                # No quote found, add all remaining text as narrative
                self.narrative += self.buffer[:].replace('\\"', '"').replace('\\n', '\n')
                self.buffer = ""
                break
            
            # Check if quote is escaped
            if self._is_escaped(quote_pos):
                # Escaped quote, continue searching
                pos = quote_pos + 1
                continue
            
            # Found unescaped quote - check what follows (skip whitespace)
            next_char_pos = quote_pos + 1
            while next_char_pos < len(self.buffer) and self.buffer[next_char_pos] in [' ', '\t', '\r', '\n']:
                next_char_pos += 1
            
            if next_char_pos < len(self.buffer):
                next_char = self.buffer[next_char_pos]
                if next_char in [',', '}']:
                    # End of narrative found!
                    self.narrative += self.buffer[:quote_pos].replace('\\"', '"').replace('\\n', '\n')
                    self.buffer = self.buffer[quote_pos:]
                    self.state = ParserState.COMPLETE
                    return
            
            # Quote found but not end of field yet, continue
            pos = quote_pos + 1
        
    def _is_escaped(self, pos: int) -> bool:
        """
        Check if character at position is escaped.
        
        Args:
            pos: Position in buffer
            
        Returns:
            True if character is escaped (preceded by odd number of backslashes)
        """
        if pos == 0:
            return False
        
        # Count consecutive backslashes before this position
        backslash_count = 0
        check_pos = pos - 1
        while check_pos >= 0 and self.buffer[check_pos] == '\\':
            backslash_count += 1
            check_pos -= 1
        
        # Odd number of backslashes means character is escaped
        return backslash_count % 2 == 1
    
    def _trim_to_word_boundary(self, text: str) -> str:
        """
        Trim text to last complete word to avoid breaking mid-word.
        
        Args:
            text: Text to trim
            
        Returns:
            Text trimmed to last word boundary
        """
        if not text:
            return text
        
        # If ends with space or newline, it's already at boundary
        if text[-1] in [' ', '\n', '\t']:
            return text
        
        # Find last space or newline
        for i in range(len(text) - 1, -1, -1):
            if text[i] in [' ', '\n', '\t']:
                return text[:i + 1]  # Include the space/newline
        
        # No word boundary found - return empty to wait for more
        return ""
    
    def get_complete_narrative(self) -> str:
        """
        Get the complete narrative text.
        
        Returns:
            Full narrative extracted so far
        """
        return self.narrative
    
    def is_complete(self) -> bool:
        """
        Check if narrative extraction is complete.
        
        Returns:
            True if we found the end of the narrative field
        """
        return self.state == ParserState.COMPLETE
    
    def get_remaining_json(self) -> str:
        """
        Get the remaining JSON after the narrative.
        
        Returns:
            Buffer containing mechanics and quant_commands
        """
        return self.buffer

