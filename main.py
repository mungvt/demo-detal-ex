import asyncio
import json
from pprint import pprint

import websockets


# import hashlib
# import hmac
# import base64
# import datetime

# api_key = "a207900b7693435a8fa9230a38195d"
# api_secret = "7b6f39dcf660ec1c7c664f612c60410a2bd0c258416b498bf0311f94228f"


# def generate_signature(secret, message):
#     message = bytes(message, "utf-8")
#     secret = bytes(secret, "utf-8")
#     hash = hmac.new(secret, message, hashlib.sha256)
#     return hash.hexdigest()


# def get_time_stamp():
#     d = datetime.datetime.utcnow()
#     epoch = datetime.datetime(1970, 1, 1)
#     return str(int((d - epoch).total_seconds()))


# # Get open orders
# method = "GET"
# timestamp = get_time_stamp()
# path = "/live"
# signature_data = method + timestamp + path
# signature = generate_signature(api_secret, signature_data)

# ws = websockets.WebSocketApp("wss://api.delta.exchange:2096")
# ws.send(
#     json.dumps(
#         {
#             "type": "auth",
#             "payload": {
#                 "api-key": api_key,
#                 "signature": signature,
#                 "timestamp": timestamp,
#             },
#         }
#     )
# )

# To unsubscribe from all private channels, just send a 'unauth' message on the socket. This will automatically unsubscribe the connection from all authenticated channels.

# ws.send(json.dumps({"type": "unauth", "payload": {}}))


# WebSocket URL for Delta exchange
websocket_url = "wss://socket.delta.exchange"

# Define the products to subscribe to
products = ["C-BTC-26000-230623", "P-BTC-26000-230623"]

# Set up the order book dictionary to store the order book for each product
order_books = {product: {} for product in products}


async def subscribe_to_orderbook(websocket, product):
    # Create the subscription message
    subscribe_msg = {
        "type": "subscribe",
        "payload": {
            "channels": [
                {
                    "name": "l2_orderbook",
                    "symbols": ["C-BTC-26000-230623", "P-BTC-26000-230623"],
                }
            ]
        },
    }
    await websocket.send(json.dumps(subscribe_msg))


async def process_orderbook_message(message):
    product = message.get("symbol")
    if product and product in products:
        # Update the order book for the respective product
        order_books[product] = message


async def heartbeat(websocket):
    while True:
        heartbeat_msg = {"type": "enable_heartbeat"}
        await websocket.send(json.dumps(heartbeat_msg))
        await asyncio.sleep(5)  # Send heartbeat every 5 seconds


async def connect_to_delta_exchange():
    async with websockets.connect(websocket_url) as websocket:
        # Subscribe to the order book channels for each product
        for product in products:
            await subscribe_to_orderbook(websocket, product)

        # Start the heartbeat to keep the connection alive
        asyncio.create_task(heartbeat(websocket))

        # Listen for incoming messages
        while True:
            message = await websocket.recv()
            message = json.loads(message)
            if message["type"] == "l2_orderbook":
                await process_orderbook_message(message)
                pprint(order_books)


async def main():
    while True:
        try:
            print("Connection to delta exchange...")
            await connect_to_delta_exchange()
        except websockets.exceptions.ConnectionClosed:
            # Reconnect in case of connection drop
            print("Connection closed. Reconnecting...")
            await asyncio.sleep(5)  # Wait before reconnecting


if __name__ == "__main__":
    asyncio.run(main())
