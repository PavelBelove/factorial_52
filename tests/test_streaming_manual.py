"""
Manual test script for streaming functionality.

Run this to test streaming without full Telegram integration.
This simulates a streaming GM response with progressive console updates.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.llm.openrouter_client import OpenRouterClient
from core.agents.gm_agent import GMAgent
import time


async def test_streaming():
    """Test streaming GM response with console output."""
    
    print("=== Streaming GM Response Test ===\n")
    print(f"✓ Streaming enabled: {settings.enable_streaming}")
    print(f"✓ Chunk interval: {settings.streaming_chunk_interval}s")
    print(f"✓ Loading interval: {settings.streaming_loading_interval}s")
    print(f"✓ Min chars for update: {settings.streaming_min_chars_for_update}")
    print()
    
    # Initialize LLM client and GM agent
    llm_client = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url
    )
    
    gm_agent = GMAgent(llm_client, model=settings.gm_model)
    
    # Prepare test context
    system_prompt = """You are a Game Master for a text RPG.
Respond in JSON format:
{
  "reply": "Your narrative response in Russian",
  "quants": ["Character", "Location"]
}

Be descriptive and engaging."""
    
    context_messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    user_message = "Я хочу начать новую игру. Расскажи о мире и создай моего персонажа."
    
    # Track updates
    update_count = 0
    last_update_time = time.time()
    last_length = 0
    
    print("🎮 User: " + user_message)
    print("\n📝 GM Response (streaming):")
    print("-" * 60)
    
    async def on_narrative_update(narrative: str):
        """Callback for streaming updates."""
        nonlocal update_count, last_update_time, last_length
        
        update_count += 1
        current_time = time.time()
        time_since_last = current_time - last_update_time
        new_chars = len(narrative) - last_length
        
        # Clear previous line and print new content
        if update_count > 1:
            # Move cursor up and clear line
            print("\033[F\033[K", end='')  # ANSI codes
        
        print(f"Update #{update_count} (+{new_chars} chars, {time_since_last:.2f}s): {narrative[:100]}{'...' if len(narrative) > 100 else ''}")
        
        last_update_time = current_time
        last_length = len(narrative)
    
    try:
        print("🔄 Starting streaming request...")
        start_time = time.time()
        
        # Call streaming GM
        response = await gm_agent.generate_response_streaming(
            context_messages=context_messages,
            user_message=user_message,
            on_narrative_update=on_narrative_update,
            max_tokens=1000
        )
        
        elapsed = time.time() - start_time
        
        print("-" * 60)
        print(f"\n✅ Streaming complete!")
        print(f"   Total time: {elapsed:.2f}s")
        print(f"   Updates: {update_count}")
        print(f"   Avg interval: {elapsed/max(update_count, 1):.2f}s")
        print()
        
        # Show full response
        reply = response.get("reply", "")
        quants = response.get("quants", [])
        usage = response.get("usage", {})
        
        print("📄 Full Response:")
        print(reply)
        print()
        print(f"🔖 Requested quants: {quants}")
        print()
        print(f"💰 Cost: ${usage.get('cost', 0):.6f}")
        print(f"   Prompt tokens: {usage.get('prompt_tokens', 0)}")
        print(f"   Completion tokens: {usage.get('completion_tokens', 0)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_loading_animation():
    """Test loading animation."""
    print("\n=== Loading Animation Test ===\n")
    
    from core.streaming.telegram_updater import LoadingAnimation
    from aiogram import Bot
    
    # Mock bot for testing
    class MockBot:
        async def edit_message_text(self, chat_id, message_id, text, parse_mode=None):
            print(f"   {text}")
            await asyncio.sleep(0.1)  # Simulate API delay
    
    bot = MockBot()
    animation = LoadingAnimation(
        bot=bot,
        chat_id=123,
        message_id=456,
        base_text="🎲 Ход обрабатывается",
        interval=0.5,
        max_dots=3
    )
    
    print("Starting animation for 5 seconds...")
    await animation.start()
    await asyncio.sleep(5)
    await animation.stop()
    print("Animation stopped.\n")


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print(" STREAMING FUNCTIONALITY TEST")
    print("="*60 + "\n")
    
    # Test 1: Loading animation (quick)
    # await test_loading_animation()
    
    # Test 2: Actual streaming GM response
    success = await test_streaming()
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ TESTS FAILED")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

