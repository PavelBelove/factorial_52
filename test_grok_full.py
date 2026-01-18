import httpx
import json
import os

api_key = os.popen("grep OPENROUTER_API_KEY .env | cut -d= -f2").read().strip()

# Полный системный промпт как в реальном запросе
system_prompt = """# Роль: Гейм-мастер (ГМ)

Ты - опытный гейм-мастер текстовой RPG в стиле фэнтези-исекай.

**ВАЖНО: Отвечай на русском языке, без использования англицизмов.** Используй естественную русскую речь.

Отвечай ТОЛЬКО в формате JSON:
{
  "reply": "текст для игрока",
  "quants": ["Character", "Inventory", "квант1", "квант2"]
}
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Привет! Готов начать игру?"}
]

# Тест 1: Без reasoning
print("=== ТЕСТ 1: Grok БЕЗ reasoning ===")
try:
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "x-ai/grok-4.1-fast",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.8,
            "reasoning": {"enabled": False}
        },
        timeout=30.0
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Content: {data['choices'][0]['message']['content'][:200]}")
    else:
        print(f"Error: {response.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n=== ТЕСТ 2: Grok С reasoning ===")
try:
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "x-ai/grok-4.1-fast",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.8
        },
        timeout=30.0
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Content: {data['choices'][0]['message']['content'][:200]}")
    else:
        print(f"Error: {response.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")
