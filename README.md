# Delta Exchange Order Book WebSocket Client

This is an asynchronous WebSocket client that connects to the Delta exchange and subscribes to order book channels for specific products. It processes incoming order book messages, updates the order book data, and saves the buy and sell order book data as CSV files.

## Prerequisites

- Python 3.7 or higher
- `websockets` library (`pip install websockets`)
- `pandas` library (`pip install pandas`)

## Usage

1. Update the `websocket_url` variable with the WebSocket URL for the Delta exchange.
2. Define the products to subscribe to in the `products` list.
3. Install dependencies: `pip3 install -r requirements.txt`
4. Run the script `python3 main.py`.

The script will establish a connection to the Delta exchange WebSocket server and start subscribing to the order book channels for the specified products. It will continuously listen for incoming messages and update the order book data accordingly. The buy and sell order book data will be saved as separate CSV files in the `./data/` directory.

## Configuration

You can modify the script to suit your needs:

- Update the WebSocket URL to connect to a different exchange or server.
- Modify the list of products to subscribe to.
- Customize the output directory for saving the order book CSV files.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This code is licensed under the [MIT License](LICENSE).
