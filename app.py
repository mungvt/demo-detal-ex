import uvicorn
import asyncio
import logging
import shutil
from fastapi import FastAPI
import pandas as pd

from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from logic import unsubscribe_to_orderbook, track_order_books
from ultils import get_all_file_paths
from config import AppConfig, BackendConfig

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with the specific origin(s) of your HTML UI
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    # Load the index.html file
    with open("index.html", "r") as file:
        html_content = file.read()
    # Replace the hard-coded URL with the dynamic base URL
    updated_html = html_content.replace("{{base_url}}", AppConfig.BASE_URL)
    return HTMLResponse(content=updated_html, media_type="text/html")


@app.get("/styles.css")
async def load_index_html():
    return FileResponse("styles.css")


@app.get('/subscribe')
async def subscribe():
    asyncio.create_task(track_order_books())
    return {"message": "Subscribed to WebSocket."}


@app.get('/unsubscribe')
async def unsubscribe():
    shutil.rmtree(BackendConfig.DATA_DIR)
    asyncio.create_task(unsubscribe_to_orderbook())
    return {"message": "Unsubscribed from WebSocket."}


@app.get('/refresh_order_books')
async def refresh_order_books():
    dfs = []
    order_book_files = get_all_file_paths(BackendConfig.DATA_DIR)
    for filepath in order_book_files:
        dfs.append(pd.read_csv(filepath))
    if dfs:
        order_book_df = pd.concat(dfs, axis=1)
        order_book_df = order_book_df.fillna('_')
        order_book_df = order_book_df.head(AppConfig.LIMIT_ORDERS)
        return order_book_df.values.tolist()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logging.info(AppConfig.HOST)
    uvicorn.run(app, host=AppConfig.HOST, port=AppConfig.PORT)
