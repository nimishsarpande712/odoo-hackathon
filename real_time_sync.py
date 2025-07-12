# Real-time Sync
# Handles real-time updates using WebSockets or polling

import asyncio
import websockets

connected_clients = set()

async def handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # Broadcast message to all connected clients
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
    except:
        connected_clients.remove(websocket)

start_server = websockets.serve(handler, 'localhost', 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
