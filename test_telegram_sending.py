#!/usr/bin/env python3
"""
Test Telegram Bot API sending speed.
Tests how fast we can send messages to Telegram.
"""
import asyncio
import httpx
import time
from datetime import datetime

TELEGRAM_BOT_TOKEN = "6906529039:AAFjvfMroCz5VwTEQMSExKOVFrJ_rT4xXQY"
CHAT_ID = 677134292  # Your Telegram user ID

async def send_message(message: str, timeout: float = 30.0):
    """Send message via Telegram Bot API and measure time."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    send_time = time.time()
    send_timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                json={
                    "chat_id": CHAT_ID,
                    "text": message
                }
            )
            
            receive_time = time.time()
            receive_timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            duration = (receive_time - send_time) * 1000  # milliseconds
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "send_time": send_timestamp,
                    "receive_time": receive_timestamp,
                    "duration_ms": duration,
                    "status_code": response.status_code
                }
            else:
                return {
                    "status": "error",
                    "send_time": send_timestamp,
                    "receive_time": receive_timestamp,
                    "duration_ms": duration,
                    "status_code": response.status_code,
                    "error": response.text
                }
    
    except asyncio.TimeoutError:
        receive_time = time.time()
        duration = (receive_time - send_time) * 1000
        return {
            "status": "timeout",
            "send_time": send_timestamp,
            "duration_ms": duration,
            "timeout": timeout
        }
    
    except Exception as e:
        receive_time = time.time()
        duration = (receive_time - send_time) * 1000
        return {
            "status": "exception",
            "send_time": send_timestamp,
            "duration_ms": duration,
            "error": str(e)
        }


async def main():
    """Main test function."""
    print("="*70)
    print("🧪 ТЕСТ ОТПРАВКИ СООБЩЕНИЙ В TELEGRAM")
    print("="*70)
    print(f"\n📱 Chat ID: {CHAT_ID}")
    print(f"📤 Количество сообщений: 12")
    print(f"⏱️  Интервал: 5 секунд")
    print(f"⏱️  Таймаут на сообщение: 30 секунд\n")
    print("="*70)
    
    # Send initial notification
    print("\n📣 Отправка уведомления о начале теста...")
    await send_message("🧪 НАЧИНАЮ ТЕСТ ОТПРАВКИ\n\nБуду отправлять 12 тестовых сообщений с интервалом 5 секунд.")
    await asyncio.sleep(2)
    
    results = []
    
    # Send test messages
    for i in range(1, 13):
        print(f"\n{'─'*70}")
        print(f"📤 Сообщение #{i}/12")
        
        message = f"Тест #{i} - время отправки: {datetime.now().strftime('%H:%M:%S')}"
        print(f"   Текст: {message}")
        
        result = await send_message(message)
        results.append(result)
        
        # Print result
        if result["status"] == "success":
            print(f"   ✅ Отправлено успешно")
            print(f"   ⏱️  {result['send_time']} → {result['receive_time']}")
            print(f"   ⏱️  Задержка: {result['duration_ms']:.0f} мс")
        elif result["status"] == "timeout":
            print(f"   ⏱️  ТАЙМАУТ после {result['timeout']} секунд")
        elif result["status"] == "error":
            print(f"   ❌ Ошибка: HTTP {result['status_code']}")
        else:
            print(f"   ❌ Исключение: {result.get('error', 'Unknown')}")
        
        # Wait before next message (except for the last one)
        if i < 12:
            print(f"   ⏸️  Пауза 5 секунд...")
            await asyncio.sleep(5)
    
    # Print summary
    print(f"\n{'='*70}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("="*70)
    
    successful = [r for r in results if r["status"] == "success"]
    timeouts = [r for r in results if r["status"] == "timeout"]
    errors = [r for r in results if r["status"] in ["error", "exception"]]
    
    print(f"\n✅ Успешно отправлено: {len(successful)}/12")
    print(f"⏱️  Таймауты: {len(timeouts)}")
    print(f"❌ Ошибки: {len(errors)}")
    
    if successful:
        durations = [r["duration_ms"] for r in successful]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        print(f"\n⏱️  Статистика по времени отправки:")
        print(f"   Средняя задержка: {avg_duration:.0f} мс")
        print(f"   Минимальная: {min_duration:.0f} мс")
        print(f"   Максимальная: {max_duration:.0f} мс")
        
        print(f"\n📋 Детали по каждому сообщению:")
        for i, r in enumerate(successful, 1):
            msg_num = results.index(r) + 1
            print(f"   #{msg_num:2d}: {r['send_time']} → {r['receive_time']} = {r['duration_ms']:6.0f} мс")
    
    if timeouts:
        print(f"\n⏱️  Сообщения с таймаутом:")
        for r in timeouts:
            msg_num = results.index(r) + 1
            print(f"   #{msg_num:2d}: таймаут после {r['timeout']} сек")
    
    if errors:
        print(f"\n❌ Ошибки:")
        for r in errors:
            msg_num = results.index(r) + 1
            error_msg = r.get('error', f"HTTP {r.get('status_code', 'Unknown')}")
            print(f"   #{msg_num:2d}: {error_msg}")
    
    # Send final summary
    print(f"\n{'='*70}")
    print("📤 Отправка итогового сообщения...")
    
    summary = f"🧪 ТЕСТ ЗАВЕРШЁН\n\n"
    summary += f"✅ Успешно: {len(successful)}/12\n"
    if successful:
        summary += f"⏱️ Средняя задержка: {avg_duration:.0f} мс\n"
        summary += f"⏱️ Мин/Макс: {min_duration:.0f}/{max_duration:.0f} мс\n"
    if timeouts:
        summary += f"\n⏱️ Таймауты: {len(timeouts)}\n"
    if errors:
        summary += f"❌ Ошибки: {len(errors)}\n"
    
    summary += f"\n{'✅' if len(successful) == 12 else '⚠️'} Telegram API работает {'стабильно' if len(successful) >= 11 else 'нестабильно'}"
    
    await send_message(summary)
    
    print("\n✅ ТЕСТ ЗАВЕРШЁН\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Тест прерван пользователем")

