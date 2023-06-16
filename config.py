import os
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 3333))
    LIMIT_ORDERS = int(os.environ.get("LIMIT_ORDERS", 10))
    BASE_URL = f"http://{HOST}:{PORT}"


class BackendConfig:
    RETRY_DELAY = int(os.environ.get("RETRY_DELAY", 10))
    WEBSOCKET_URL = os.environ.get("WEBSOCKET_URL", "wss://socket.delta.exchange")
    PRODUCTS = os.environ.get("PRODUCTS", "C-BTC-26000-230623, P-BTC-26000-230623").split(",")
    HEARTBEAT_TIME = int(os.environ.get("HEARTBEAT_TIME", 3))
    DATA_DIR = os.environ.get("DATA_DIR", "./data/")
