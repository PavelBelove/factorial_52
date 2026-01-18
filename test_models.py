"""Test to find available Grok models on OpenRouter."""
import asyncio
import httpx
from core.config import settings


async def list_models():
    """List all available models."""
    print("Fetching available models from OpenRouter...\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {settings.openrouter_api_key}"}
            )
            
            if response.status_code == 200:
                models = response.json()["data"]
                
                # Find Grok models
                grok_models = [m for m in models if "grok" in m["id"].lower() or "x-ai" in m["id"].lower()]
                
                print(f"Found {len(grok_models)} Grok/X.AI models:\n")
                for model in grok_models:
                    print(f"  • {model['id']}")
                    if "name" in model:
                        print(f"    Name: {model['name']}")
                    print()
                
                if grok_models:
                    print(f"\nRecommended model: {grok_models[0]['id']}")
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(list_models())

