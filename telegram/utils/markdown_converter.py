"""
Markdown to Telegram HTML converter.
Converts markdown-style formatting to Telegram-compatible HTML tags.
"""
import re


def convert_markdown_to_html(text: str) -> str:
    """
    Convert markdown formatting to Telegram HTML tags.
    
    Converts:
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

