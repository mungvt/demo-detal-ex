import asyncio
import json
import os
import logging
import websockets
import pandas as pd
from config import BackendConfig


def logging_basic_config(filename=None):
    log_format = '%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    if filename is not None:
        logging.basicConfig(level=logging.INFO, format=log_format, filename=filename)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)


logging_basic_config()

# WebSocket URL for Delta exchange
websocket_url = BackendConfig.WEBSOCKET_URL

# Define the products to subscribe to
products = BackendConfig.PRODUCTS

# Set up the order book dictionary to store the order book for each product
order_books = {product: {"buy": {}, "sell": {}} for product in products}


async def subscribe_to_orderbook():
    # Create the subscription message
    subscribe_msg = {
        "type": "subscribe",
        "payload": {
            "channels": [
                {
                    "name": "l2_orderbook",
                    "symbols": products,
                }
            ]
        },
    }
    await websocket.send(json.dumps(subscribe_msg))


async def unsubscribe_to_orderbook():
    # Create the subscription message
    subscribe_msg = {
        "type": "unsubscribe",
        "payload": {
            "channels": [
                {
                    "name": "l2_orderbook",
                    "symbols": products,
                }
            ]
        }
    }
    await websocket.send(json.dumps(subscribe_msg))
    await websocket.close()


async def process_orderbook_message(message):
    product = message.get("symbol")
    # Update the order book for the respective product
    new_buy, new_sell = {}, {}
    for price in message["buy"]:
        new_buy.update({price["limit_price"]: price["size"]})
    for price in message["sell"]:
        new_sell.update({price["limit_price"]: price["size"]})
    order_books[product]["buy"].update(new_buy)
    order_books[product]["sell"].update(new_sell)


async def heartbeat():
    while True:
        heartbeat_msg = {"type": "enable_heartbeat"}
        await websocket.send(json.dumps(heartbeat_msg))
        await asyncio.sleep(BackendConfig.HEARTBEAT_TIME)  # Send heartbeat every 5 seconds


async def connect_to_delta_exchange():
    global websocket
    websocket = await websockets.connect(websocket_url)
    # Subscribe to the order book channels for products
    await subscribe_to_orderbook()

    # Start the heartbeat to keep the connection alive
    asyncio.create_task(heartbeat())

    # Listen for incoming messages
    while True:
        message = await websocket.recv()
        message = json.loads(message)
        if message["type"] == "l2_orderbook":
            logging.info(
                f'New messages for product {message.get("symbol")} at timestamp: {message.get("timestamp")}')
            product = message.get("symbol")
            if product and product in products:
                await process_orderbook_message(message)
                for product, order_book in order_books.items():
                    update_order_books(product, order_book)
        elif message["type"] == "heartbeat":
            logging.info(f'Healthy check:{message}')
        else:
            logging.info(message)


def update_order_books(product, order_book):
    os.makedirs(BackendConfig.DATA_DIR, exist_ok=True)
    buy_df = convert_to_order_book(order_book["buy"])
    sell_df = convert_to_order_book(order_book["sell"])
    buy_df.to_csv(f"{BackendConfig.DATA_DIR}{product}_BUY.csv", index=False)
    sell_df.to_csv(f"{BackendConfig.DATA_DIR}{product}_SELL.csv", index=False)


def convert_to_order_book(orders: dict):
    prices = list(orders.keys())
    sizes = list(orders.values())
    df = pd.DataFrame(data={'price': prices, 'size': sizes})
    df["price"] = df["price"].astype(float)
    df["size"] = df["size"].astype(float)
    return df.sort_values('price', ascending=False)


async def track_order_books():
    while True:
        try:
            logging.info(f"Connection to delta exchange: {websocket_url}...")
            await connect_to_delta_exchange()
        except websockets.ConnectionClosed:
            # Reconnect in case of connection drop
            logging.info("Connection closed. Reconnecting...")
            await asyncio.sleep(BackendConfig.RETRY_DELAY)  # Wait before reconnecting
