"""
Markdown to Telegram HTML converter.
Converts markdown-style formatting to Telegram-compatible HTML tags.
"""
import re


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

