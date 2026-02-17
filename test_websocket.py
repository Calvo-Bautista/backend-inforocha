import asyncio
import websockets

async def test_ws():
    uri = "ws://127.0.0.1:8000/api/v1/ws"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            await websocket.send("Test message")
            print("Message sent")
            # Wait a bit
            await asyncio.sleep(1)
            print("Closing...")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws())
