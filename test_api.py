"""
Simple test script for PlexMem API.
Tests basic functionality without Telegram.
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"


async def test_api():
    """Test basic API flow."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 80)
        print("Testing PlexMem API")
        print("=" * 80)
        
        # 1. Health check
        print("\n1. Health check...")
        response = await client.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 2. Create session
        print("\n2. Creating session...")
        response = await client.post(
            f"{BASE_URL}/sessions",
            json={
                "platform_id": "test_user_123",
                "platform_type": "console",
                "session_type": "game"
            }
        )
        print(f"Status: {response.status_code}")
        session_data = response.json()
        print(f"Response: {session_data}")
        
        session_id = session_data["session_id"]
        
        # 3. Send first message
        print("\n3. Sending first message...")
        response = await client.post(
            f"{BASE_URL}/sessions/{session_id}/messages",
            json={
                "session_id": session_id,
                "message": "Привет! Я просыпаюсь в незнакомом месте. Что я вижу?"
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            message_data = response.json()
            print(f"Turn: {message_data['turn_number']}")
            print(f"Reply: {message_data['reply'][:200]}...")
            print(f"Quants requested: {message_data['quants_requested']}")
        else:
            print(f"Error: {response.text}")
        
        # 4. Send second message
        print("\n4. Sending second message...")
        response = await client.post(
            f"{BASE_URL}/sessions/{session_id}/messages",
            json={
                "session_id": session_id,
                "message": "Я осматриваюсь вокруг и иду к ближайшему строению."
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            message_data = response.json()
            print(f"Turn: {message_data['turn_number']}")
            print(f"Reply: {message_data['reply'][:200]}...")
            print(f"Quants used: {message_data['quants_used']}")
            print(f"Quants requested: {message_data['quants_requested']}")
        else:
            print(f"Error: {response.text}")
        
        # 5. Get session info
        print("\n5. Getting session info...")
        response = await client.get(f"{BASE_URL}/sessions/{session_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # 6. Get quants
        print("\n6. Getting quants...")
        response = await client.get(f"{BASE_URL}/sessions/{session_id}/quants")
        print(f"Status: {response.status_code}")
        quants_data = response.json()
        print(f"Total quants: {quants_data['total']}")
        if quants_data['quants']:
            print("First quant:")
            print(json.dumps(quants_data['quants'][0], indent=2, ensure_ascii=False))
        
        # 7. Get history
        print("\n7. Getting history...")
        response = await client.get(f"{BASE_URL}/sessions/{session_id}/history")
        print(f"Status: {response.status_code}")
        history_data = response.json()
        print(f"Total turns: {history_data['total']}")
        
        print("\n" + "=" * 80)
        print("Test completed!")
        print("=" * 80)


if __name__ == "__main__":
    print("Make sure the API server is running (python run_api.py)")
    print("Press Enter to start test...")
    input()
    
    asyncio.run(test_api())

