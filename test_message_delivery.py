#!/usr/bin/env python3
"""
Test script to measure message delivery time.
Sends test messages to the bot and logs delivery time.
"""
import asyncio
import httpx
import time
from datetime import datetime
import sys

API_BASE_URL = "http://localhost:8000"
TELEGRAM_BOT_TOKEN = "6906529039:AAFjvfMro2v03KKK1bAKp5GyIHE2RbpbNRc"
USER_ID = 677134292  # Your Telegram user ID

async def send_telegram_message(chat_id: int, text: str):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                url,
                json={"chat_id": chat_id, "text": text}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return False


async def get_or_create_session(user_id: int) -> int:
    """Get active session or create new one."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Try to get existing session
            response = await client.get(
                f"{API_BASE_URL}/sessions/user/{user_id}",
                params={"platform_type": "telegram"}
            )
            if response.status_code == 200:
                data = response.json()
                session_id = data["session_id"]
                print(f"✓ Found existing session: {session_id}")
                return session_id
        except Exception:
            pass
        
        # Create new session
        response = await client.post(
            f"{API_BASE_URL}/sessions",
            json={
                "platform_id": str(user_id),
                "platform_type": "telegram",
                "session_type": "game"
            }
        )
        if response.status_code == 200:
            data = response.json()
            session_id = data["session_id"]
            print(f"✓ Created new session: {session_id}")
            return session_id
        else:
            raise Exception(f"Failed to create session: {response.text}")


async def send_test_message(session_id: int, message_num: int):
    """Send a test message and measure response time."""
    message = f"Тестовое сообщение #{message_num} от {datetime.now().strftime('%H:%M:%S')}"
    
    print(f"\n{'='*60}")
    print(f"📤 Отправка сообщения #{message_num}")
    print(f"   Текст: {message}")
    
    send_time = time.time()
    send_timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"   ⏱️  Время отправки: {send_timestamp}")
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/sessions/{session_id}/messages",
                json={
                    "session_id": session_id,
                    "message": message
                }
            )
            
            receive_time = time.time()
            receive_timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            duration = receive_time - send_time
            
            if response.status_code == 200:
                data = response.json()
                reply_length = len(data["reply"])
                
                print(f"   ✅ Получен ответ от API")
                print(f"   ⏱️  Время получения: {receive_timestamp}")
                print(f"   ⏱️  Задержка API: {duration:.2f} сек")
                print(f"   📝 Длина ответа: {reply_length} символов")
                print(f"   🎲 Ход: {data['turn_number']}")
                
                return {
                    "message_num": message_num,
                    "send_time": send_timestamp,
                    "receive_time": receive_timestamp,
                    "duration": duration,
                    "reply_length": reply_length,
                    "turn_number": data["turn_number"],
                    "status": "success"
                }
            else:
                print(f"   ❌ Ошибка API: {response.status_code}")
                print(f"   {response.text}")
                return {
                    "message_num": message_num,
                    "send_time": send_timestamp,
                    "duration": duration,
                    "status": "error",
                    "error": response.text
                }
    
    except Exception as e:
        receive_time = time.time()
        duration = receive_time - send_time
        receive_timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        print(f"   ❌ Исключение: {e}")
        print(f"   ⏱️  Время падения: {receive_timestamp}")
        print(f"   ⏱️  Прошло: {duration:.2f} сек")
        
        return {
            "message_num": message_num,
            "send_time": send_timestamp,
            "receive_time": receive_timestamp,
            "duration": duration,
            "status": "exception",
            "error": str(e)
        }


async def main():
    """Main test function."""
    print("🧪 Тест доставки сообщений\n")
    print(f"User ID: {USER_ID}")
    print(f"API: {API_BASE_URL}")
    print(f"Количество сообщений: 12")
    print(f"Интервал: 5 секунд\n")
    
    # Get or create session
    try:
        session_id = await get_or_create_session(USER_ID)
    except Exception as e:
        print(f"❌ Не удалось получить сессию: {e}")
        return
    
    # Notify user via Telegram
    await send_telegram_message(
        USER_ID,
        "🧪 Начинаю тест доставки сообщений. Буду отправлять 12 тестовых сообщений с интервалом 5 секунд."
    )
    
    results = []
    
    # Send test messages
    for i in range(1, 13):
        result = await send_test_message(session_id, i)
        results.append(result)
        
        # Wait before next message (except for the last one)
        if i < 12:
            await asyncio.sleep(5)
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА\n")
    
    successful = [r for r in results if r["status"] == "success"]
    errors = [r for r in results if r["status"] != "success"]
    
    print(f"✅ Успешно: {len(successful)}")
    print(f"❌ Ошибок: {len(errors)}\n")
    
    if successful:
        durations = [r["duration"] for r in successful]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        print(f"⏱️  Средняя задержка: {avg_duration:.2f} сек")
        print(f"⏱️  Минимальная: {min_duration:.2f} сек")
        print(f"⏱️  Максимальная: {max_duration:.2f} сек\n")
        
        print("Детали по каждому сообщению:")
        for r in successful:
            print(f"  #{r['message_num']:2d}: {r['send_time']} → {r['receive_time']} = {r['duration']:5.2f}с (ход {r['turn_number']})")
    
    if errors:
        print("\n❌ Ошибки:")
        for r in errors:
            print(f"  #{r['message_num']:2d}: {r['status']} - {r.get('error', 'Unknown')}")
    
    # Send summary via Telegram
    summary = f"🧪 Тест завершен!\n\n"
    summary += f"✅ Успешно: {len(successful)}/12\n"
    if successful:
        summary += f"⏱️ Средняя задержка: {avg_duration:.1f}с\n"
        summary += f"⏱️ Мин/Макс: {min_duration:.1f}с / {max_duration:.1f}с"
    
    await send_telegram_message(USER_ID, summary)
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Тест прерван пользователем")
        sys.exit(0)

