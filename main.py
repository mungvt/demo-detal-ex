import asyncio
import json
import os

import websockets
import pandas as pd

# WebSocket URL for Delta exchange
websocket_url = "wss://socket.delta.exchange"

# Define the products to subscribe to
products = ["C-BTC-26000-230623", "P-BTC-26000-230623"]

# Set up the order book dictionary to store the order book for each product
order_books = {product: {"buy": {}, "sell": {}} for product in products}


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
        new_buy, new_sell = {}, {}
        for price in message["buy"]:
            new_buy.update({price["limit_price"]: price["size"]})
        for price in message["sell"]:
            new_buy.update({price["limit_price"]: price["size"]})
        order_books[product]["buy"].update(new_buy)
        order_books[product]["sell"].update(new_sell)


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
                os.makedirs("./data/", exist_ok=True)
                for product, order_book in order_books.items():
                    buy_df = convert_to_order_book(order_book["buy"])
                    sell_df = convert_to_order_book(order_book["sell"])
                    buy_df.to_csv(f"./data/{product}_buy.csv", index=False)
                    sell_df.to_csv(f"./data/{product}_sell.csv", index=False)


def convert_to_order_book(orders: dict):
    prices = list(orders.keys())
    sizes = list(orders.values())
    df = pd.DataFrame(data={'price': prices, 'size': sizes})
    df["price"] = df["price"].astype(float)
    df["size"] = df["size"].astype(float)
    return df.sort_values('price', ascending=False)


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
