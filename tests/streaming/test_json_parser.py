"""
Tests for PartialJSONParser.

Tests various scenarios of streaming JSON parsing including:
- Simple complete responses
- Responses with escaped quotes
- Chunked delivery
- Word boundary handling
"""
import pytest
from core.streaming.json_parser import PartialJSONParser, ParserState


def test_simple_complete_json():
    """Test parsing a complete simple JSON response."""
    parser = PartialJSONParser()
    
    json_text = '{"reply": "Hello world!", "mechanics": {}}'
    result = parser.feed_chunk(json_text)
    
    assert result == "Hello world!"
    assert parser.is_complete()
    assert parser.get_complete_narrative() == "Hello world!"


def test_chunked_narrative():
    """Test parsing narrative delivered in chunks."""
    parser = PartialJSONParser()
    
    # Feed in chunks
    chunks = [
        '{"reply": "Hello ',
        'world! This is ',
        'a test message.", ',
        '"mechanics": {}}'
    ]
    
    results = []
    for chunk in chunks:
        result = parser.feed_chunk(chunk)
        if result:
            results.append(result)
    
    # Should get progressive updates
    assert len(results) > 0
    # Final result should be complete
    assert parser.get_complete_narrative() == "Hello world! This is a test message."
    assert parser.is_complete()


def test_escaped_quotes_in_narrative():
    """Test handling escaped quotes in the narrative."""
    parser = PartialJSONParser()
    
    json_text = '{"reply": "He said: \\"Hello!\\" and left.", "mechanics": {}}'
    result = parser.feed_chunk(json_text)
    
    assert 'He said: "Hello!" and left.' in result
    assert parser.is_complete()


def test_newlines_in_narrative():
    """Test handling newlines in the narrative."""
    parser = PartialJSONParser()
    
    json_text = '{"reply": "Line one.\\nLine two.\\nLine three.", "mechanics": {}}'
    result = parser.feed_chunk(json_text)
    
    assert "Line one.\nLine two.\nLine three." in result
    assert parser.is_complete()


def test_word_boundary_trimming():
    """Test that incomplete words are not sent."""
    parser = PartialJSONParser()
    
    # Feed incomplete word
    result1 = parser.feed_chunk('{"reply": "Hello wor')
    # Should not return incomplete word
    assert result1 is None or not result1.endswith('wor')
    
    # Complete the word
    result2 = parser.feed_chunk('ld! ')
    # Should now include the complete word
    assert "Hello world!" in parser.get_complete_narrative()


def test_multiple_escaped_backslashes():
    """Test handling multiple backslashes before quotes."""
    parser = PartialJSONParser()
    
    # \\" should be treated as escaped quote
    # \\\\" should be treated as escaped backslash + escaped quote
    json_text = '{"reply": "Path: C:\\\\folder\\\\"test.txt\\"", "mechanics": {}}'
    result = parser.feed_chunk(json_text)
    
    assert parser.is_complete()


def test_empty_narrative():
    """Test handling empty narrative field."""
    parser = PartialJSONParser()
    
    json_text = '{"reply": "", "mechanics": {}}'
    result = parser.feed_chunk(json_text)
    
    assert parser.is_complete()
    assert parser.get_complete_narrative() == ""


def test_long_narrative_with_many_chunks():
    """Test handling a long narrative split into many chunks."""
    parser = PartialJSONParser()
    
    narrative = "This is a very long narrative. " * 50  # 1500+ chars
    json_template = '{{"reply": "{}", "mechanics": {{}}}}'
    json_text = json_template.format(narrative)
    
    # Simulate character-by-character streaming
    chunk_size = 10
    for i in range(0, len(json_text), chunk_size):
        chunk = json_text[i:i + chunk_size]
        parser.feed_chunk(chunk)
    
    assert parser.is_complete()
    assert parser.get_complete_narrative() == narrative


def test_narrative_with_json_like_content():
    """Test narrative containing JSON-like strings."""
    parser = PartialJSONParser()
    
    narrative = 'The config is {"key": "value"} in the file.'
    json_text = '{{"reply": "{}", "mechanics": {{}}}}'.format(
        narrative.replace('"', '\\"')
    )
    
    result = parser.feed_chunk(json_text)
    
    assert parser.is_complete()
    assert '{"key": "value"}' in parser.get_complete_narrative()


def test_cyrillic_text():
    """Test handling Cyrillic (Russian) text."""
    parser = PartialJSONParser()
    
    json_text = '{"reply": "Привет, мир! Это тест на русском языке.", "mechanics": {}}'
    result = parser.feed_chunk(json_text)
    
    assert "Привет, мир!" in result
    assert parser.is_complete()


def test_emoji_in_narrative():
    """Test handling emoji in narrative."""
    parser = PartialJSONParser()
    
    json_text = '{"reply": "Great job! 🎉 You earned ⚔️ sword!", "mechanics": {}}'
    result = parser.feed_chunk(json_text)
    
    assert "🎉" in result
    assert "⚔️" in result
    assert parser.is_complete()


def test_incomplete_json_no_closing():
    """Test handling JSON that never closes the narrative field."""
    parser = PartialJSONParser()
    
    # Feed opening but never close
    parser.feed_chunk('{"reply": "This is the start')
    parser.feed_chunk(' of a message that never')
    parser.feed_chunk(' ends properly...')
    
    # Should not be complete
    assert not parser.is_complete()
    # But should have partial narrative
    assert len(parser.get_complete_narrative()) > 0


def test_whitespace_handling():
    """Test handling various whitespace in JSON."""
    parser = PartialJSONParser()
    
    json_text = '{"reply"  :  "Hello world!"  ,  "mechanics": {}}'
    result = parser.feed_chunk(json_text)
    
    assert result == "Hello world!"
    assert parser.is_complete()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

