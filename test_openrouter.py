"""
Test OpenRouter API connection using the core Client.
Checks connection and logic + DEBUG MODE.
"""
import asyncio
from core.config import settings
from core.llm.openrouter_client import OpenRouterClient


async def test_openrouter():
    """Test OpenRouter API through Client."""
    print("=" * 80)
    print("Testing OpenRouter API (Client Wrapper)")
    print("=" * 80)
    
    # Enable verbose debug for this test
    settings.debug_verbose = True
    print("Debug Verbose Mode: ENABLED")
    
    client = OpenRouterClient()
    
    print(f"\nSending test request via {settings.gm_model}...\n")
    
    try:
        reply = await client.simple_completion(
            prompt="Привет! Скажи 'DEBUG MODE WORKS' если видишь это.",
            model=settings.gm_model
        )
        
        print(f"\n✅ Client returned: {reply}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_openrouter())

