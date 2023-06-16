import os
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    HOST = os.environ.get("HOST") or "0.0.0.0"
    PORT = int(os.environ.get("PORT")) or 8000
    LIMIT_ORDERS = int(os.environ.get("LIMIT_ORDERS")) or 10
    BASE_URL = f"http://{HOST}:{PORT}"


class BackendConfig:
    RETRY_DELAY = int(os.environ.get("RETRY_DELAY")) or 10
    WEBSOCKET_URL = os.environ.get("WEBSOCKET_URL") or "wss://socket.delta.exchange"
    PRODUCTS = os.environ.get("PRODUCTS").split(",") or ["C-BTC-26000-230623", "P-BTC-26000-230623"]
    HEARTBEAT_TIME = int(os.environ.get("HEARTBEAT_TIME")) or 3
    DATA_DIR = os.environ.get("DATA_DIR") or "./data/"
