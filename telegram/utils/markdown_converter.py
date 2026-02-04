"""
Markdown to Telegram HTML converter.
Converts markdown-style formatting to Telegram-compatible HTML tags.
"""
import re
import logging

logger = logging.getLogger(__name__)


def convert_markdown_to_html(text: str) -> str:
    """
    Convert markdown formatting to Telegram HTML tags.
    
    Converts:
    - # Heading → <b>Heading</b> (all heading levels)
    - **bold** → <b>bold</b>
    - *italic* → <i>italic</i>
    - __underline__ → <u>underline</u>
    - ~~strikethrough~~ → <s>strikethrough</s>
    - `code` → <code>code</code>
    - ```code block``` → <pre>code block</pre>
    - [link](url) → <a href="url">link</a>
    
    Args:
        text: Text with markdown formatting
        
    Returns:
        Text with HTML tags
    """
    if not text:
        return text
    
    # Code blocks first (``` ... ```)
    text = re.sub(r'```([^`]+)```', r'<pre>\1</pre>', text)
    
    # Inline code (` ... `)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Headings (# Text, ## Text, etc.) → <b>Text</b>
    # Match start of line or after newline, 1-6 #, space, then text until end of line
    text = re.sub(r'(^|\n)#{1,6}\s+(.+?)(?=\n|$)', r'\1<b>\2</b>', text)
    
    # Bold (**text** or __text__)
    # Use non-greedy match and ensure we don't match empty strings
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # Italic (*text* or _text_)
    # More careful pattern to avoid conflicts with bold
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<i>\1</i>', text)
    
    # Strikethrough (~~text~~)
    text = re.sub(r'~~(.+?)~~', r'<s>\1</s>', text)
    
    # Links ([text](url))
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
    
    return text


def strip_html_tags(text: str) -> str:
    """
    Remove all HTML tags from text.
    Useful for fallback when HTML parsing fails.
    
    Args:
        text: Text with HTML tags
        
    Returns:
        Plain text
    """
    return re.sub(r'<[^>]+>', '', text)


def validate_and_fix_html(text: str) -> str:
    """
    Validate HTML tags and fix mismatches.
    
    Telegram requires:
    - All tags properly nested
    - All opening tags have matching closing tags
    - No orphaned closing tags
    
    Args:
        text: Text with HTML tags
        
    Returns:
        Fixed HTML text, or plain text if unfixable
    """
    if not text:
        return text
    
    # Telegram supported tags
    supported_tags = ['b', 'i', 'u', 's', 'code', 'pre', 'a']
    
    # Track open tags (stack-based validation)
    tag_stack = []
    fixed_parts = []
    pos = 0
    
    # Find all tags
    tag_pattern = re.compile(r'<(/?)(\w+)([^>]*)>')
    
    for match in tag_pattern.finditer(text):
        # Add text before tag
        fixed_parts.append(text[pos:match.start()])
        
        is_closing = match.group(1) == '/'
        tag_name = match.group(2).lower()
        attributes = match.group(3)
        
        # Skip unsupported tags
        if tag_name not in supported_tags:
            logger.warning(f"Unsupported HTML tag: <{tag_name}>")
            pos = match.end()
            continue
        
        if is_closing:
            # Closing tag
            if tag_stack and tag_stack[-1] == tag_name:
                # Matching closing tag
                tag_stack.pop()
                fixed_parts.append(match.group(0))
            else:
                # Mismatched closing tag
                logger.warning(f"Mismatched closing tag: </{tag_name}>, expected: {tag_stack[-1] if tag_stack else 'none'}")
                # Try to close all open tags until we find matching one
                while tag_stack:
                    open_tag = tag_stack.pop()
                    fixed_parts.append(f'</{open_tag}>')
                    if open_tag == tag_name:
                        break
        else:
            # Opening tag
            tag_stack.append(tag_name)
            fixed_parts.append(match.group(0))
        
        pos = match.end()
    
    # Add remaining text
    fixed_parts.append(text[pos:])
    
    # Close any remaining open tags
    while tag_stack:
        open_tag = tag_stack.pop()
        logger.warning(f"Auto-closing unclosed tag: <{open_tag}>")
        fixed_parts.append(f'</{open_tag}>')
    
    result = ''.join(fixed_parts)
    
    # Final validation: if still invalid, strip all tags
    if not _is_valid_html_simple(result):
        logger.error(f"HTML still invalid after fix, stripping all tags")
        return strip_html_tags(result)
    
    return result


def _is_valid_html_simple(text: str) -> bool:
    """
    Simple HTML validation - check if all tags are balanced.
    
    Args:
        text: Text with HTML tags
        
    Returns:
        True if valid, False otherwise
    """
    tag_stack = []
    tag_pattern = re.compile(r'<(/?)(\w+)[^>]*>')
    
    for match in tag_pattern.finditer(text):
        is_closing = match.group(1) == '/'
        tag_name = match.group(2).lower()
        
        if is_closing:
            if not tag_stack or tag_stack[-1] != tag_name:
                return False
            tag_stack.pop()
        else:
            tag_stack.append(tag_name)
    
    return len(tag_stack) == 0


def split_message_into_chunks(text: str, max_length: int = 4000) -> list[str]:
    """
    Split long message into chunks, breaking at paragraph boundaries.
    
    Tries to split at:
    1. Double newlines (paragraph breaks) - preferred
    2. Single newlines - if no paragraph break nearby
    3. Spaces - if no newline nearby
    4. Hard cut - only as last resort
    
    Args:
        text: Text to split
        max_length: Maximum length per chunk (default 4000 for Telegram safety)
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    remaining = text
    
    while len(remaining) > max_length:
        # Try to find a good split point
        split_point = max_length
        
        # Look for double newline (paragraph break) in last 500 chars before limit
        search_start = max(0, max_length - 500)
        double_newline = remaining.rfind('\n\n', search_start, max_length)
        if double_newline > 0:
            split_point = double_newline + 2  # Include the newlines
        else:
            # Look for single newline in last 300 chars
            single_newline = remaining.rfind('\n', max(0, max_length - 300), max_length)
            if single_newline > 0:
                split_point = single_newline + 1  # Include the newline
            else:
                # Look for space in last 100 chars
                space = remaining.rfind(' ', max(0, max_length - 100), max_length)
                if space > 0:
                    split_point = space + 1  # Include the space
                # else: hard cut at max_length (fallback)
        
        # Add chunk
        chunks.append(remaining[:split_point].rstrip())
        remaining = remaining[split_point:].lstrip()
    
    # Add remaining text
    if remaining:
        chunks.append(remaining)
    
    return chunks

