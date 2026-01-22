#!/usr/bin/env python3
"""
Test token costs for Russian vs English prompts
"""
import os
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Load prompts
def load_prompt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# Test message
USER_MESSAGE = "давай начнем новую игру"

# Load prompts
gm_ru = load_prompt("prompts/gm_system_ru.md")
gm_en = load_prompt("prompts/gm_system.md")

# API settings
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

if not OPENROUTER_API_KEY:
    print("❌ OPENROUTER_API_KEY not found in environment!")
    exit(1)

# Models to test
MODELS = [
    "deepseek/deepseek-chat",  # DeepSeek 3.2
    "x-ai/grok-4.1-fast",      # Grok Fast
]

def send_request(model, system_prompt, user_message):
    """Send request to OpenRouter and get token usage"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "PlexMem Token Test"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 100,  # Minimal response for cost testing
        "temperature": 0.7
    }
    
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None
        
        return response.json()

# Run tests
results = {}

for model in MODELS:
    print(f"\n{'='*80}")
    print(f"Testing: {model}")
    print(f"{'='*80}")
    
    results[model] = {}
    
    # Test Russian prompt
    print(f"\n📝 Russian prompt...")
    resp_ru = send_request(model, gm_ru, USER_MESSAGE)
    if resp_ru and "usage" in resp_ru:
        usage_ru = resp_ru["usage"]
        results[model]["russian"] = {
            "prompt_tokens": usage_ru.get("prompt_tokens", 0),
            "completion_tokens": usage_ru.get("completion_tokens", 0),
            "total_tokens": usage_ru.get("total_tokens", 0),
            "cost": usage_ru.get("cost", 0)
        }
        print(f"   Prompt tokens: {usage_ru.get('prompt_tokens', 0)}")
        print(f"   Completion tokens: {usage_ru.get('completion_tokens', 0)}")
        print(f"   Total tokens: {usage_ru.get('total_tokens', 0)}")
        print(f"   Cost: ${usage_ru.get('cost', 0):.6f}")
    
    # Test English prompt
    print(f"\n📝 English prompt...")
    resp_en = send_request(model, gm_en, USER_MESSAGE)
    if resp_en and "usage" in resp_en:
        usage_en = resp_en["usage"]
        results[model]["english"] = {
            "prompt_tokens": usage_en.get("prompt_tokens", 0),
            "completion_tokens": usage_en.get("completion_tokens", 0),
            "total_tokens": usage_en.get("total_tokens", 0),
            "cost": usage_en.get("cost", 0)
        }
        print(f"   Prompt tokens: {usage_en.get('prompt_tokens', 0)}")
        print(f"   Completion tokens: {usage_en.get('completion_tokens', 0)}")
        print(f"   Total tokens: {usage_en.get('total_tokens', 0)}")
        print(f"   Cost: ${usage_en.get('cost', 0):.6f}")
    
    # Calculate savings
    if "russian" in results[model] and "english" in results[model]:
        ru = results[model]["russian"]
        en = results[model]["english"]
        
        prompt_diff = ru["prompt_tokens"] - en["prompt_tokens"]
        prompt_pct = (prompt_diff / ru["prompt_tokens"] * 100) if ru["prompt_tokens"] > 0 else 0
        
        cost_diff = ru["cost"] - en["cost"]
        cost_pct = (cost_diff / ru["cost"] * 100) if ru["cost"] > 0 else 0
        
        print(f"\n💰 Savings:")
        print(f"   Prompt tokens: {prompt_diff} ({prompt_pct:.1f}% reduction)")
        print(f"   Cost per turn: ${cost_diff:.6f} ({cost_pct:.1f}% reduction)")

# Summary
print(f"\n{'='*80}")
print("📊 SUMMARY")
print(f"{'='*80}\n")

for model in MODELS:
    print(f"Model: {model}")
    if "russian" in results[model] and "english" in results[model]:
        ru = results[model]["russian"]
        en = results[model]["english"]
        
        prompt_saving = ru["prompt_tokens"] - en["prompt_tokens"]
        cost_saving = ru["cost"] - en["cost"]
        cost_saving_pct = (cost_saving / ru["cost"] * 100) if ru["cost"] > 0 else 0
        
        print(f"  Russian:  {ru['prompt_tokens']:>5} tokens, ${ru['cost']:.6f}")
        print(f"  English:  {en['prompt_tokens']:>5} tokens, ${en['cost']:.6f}")
        print(f"  Savings:  {prompt_saving:>5} tokens, ${cost_saving:.6f} ({cost_saving_pct:.1f}%)")
        print()

# Save results
with open("token_cost_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("✅ Results saved to token_cost_test_results.json")

