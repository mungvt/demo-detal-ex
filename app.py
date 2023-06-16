# from flask import Flask
# from flask_cors import CORS
# from main import main, unsubscribe_to_orderbook
#
# app = Flask(__name__)
# CORS(app)
#
#
# @app.route('/subscribe')
# async def subscribe():
#     await main()
#     return "Main function started."
#
#
# @app.route('/unsubscribe')
# async def unsubscribe():
#     products = ["C-BTC-26000-230623", "P-BTC-26000-230623"]
#     websocket_url = "wss://socket.delta.exchange"
#
#     await unsubscribe_to_orderbook(websocket_url, products)
#     return "Main function started."
#
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

import uvicorn
import asyncio
import csv
import json
import logging
import websockets
from fastapi import FastAPI
import pandas as pd

from main import unsubscribe_to_orderbook, main
from fastapi.middleware.cors import CORSMiddleware

from ultils import get_all_file_paths

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with the specific origin(s) of your HTML UI
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get('/subscribe')
async def subscribe():
    asyncio.create_task(main())
    return {"message": "Subscribed to WebSocket."}


@app.get('/unsubscribe')
async def unsubscribe():
    asyncio.create_task(unsubscribe_to_orderbook())
    return {"message": "Unsubscribed from WebSocket."}


@app.get('/refresh_order_books')
async def refresh_order_books():
    dfs = []
    order_book_files = get_all_file_paths('./data/')
    for filepath in order_book_files:
        dfs.append(pd.read_csv(filepath))
    if dfs:
        order_book_df = pd.concat(dfs, axis=1)
        order_book_df = order_book_df.fillna('_')
        order_book_df = order_book_df.head(10)
        return order_book_df.values.tolist()
    return ['_']*8


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)
