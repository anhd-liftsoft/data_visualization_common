import os
import streamlit.components.v1 as components

# Get the path to the frontend folder
_COMPONENT_PATH = os.path.join(os.path.dirname(__file__), "frontend")


def streaming_chart(
    websocket_url: str,
    topic: str = "market.data@BTC",
    height: int = 500,
    candle_interval: int = 60,
):
    """
    Render a real-time candlestick chart that connects to a WebSocket.

    Args:
        websocket_url: The WebSocket URL to connect to (e.g., "wss://example.com/ws")
        topic: The topic to subscribe to (e.g., "market.data@BTC")
        height: Height of the chart in pixels
        candle_interval: Candlestick interval in seconds (default: 60 = 1 minute)
        key: Unique key for the component

    Returns:
        None
    """
    # Read the HTML template
    html_file = os.path.join(_COMPONENT_PATH, "index.html")
    css_file = os.path.join(_COMPONENT_PATH, "style.css")
    js_file = os.path.join(_COMPONENT_PATH, "main.js")
    msgpack_file = os.path.join(_COMPONENT_PATH, "msgpack.js")

    with open(html_file, "r") as f:
        html_content = f.read()

    with open(css_file, "r") as f:
        css_content = f.read()

    with open(js_file, "r") as f:
        js_content = f.read()

    with open(msgpack_file, "r") as f:
        msgpack_content = f.read()

    # Remove the ES module import/export statements since we're inlining
    # Remove import statement from main.js
    js_content = js_content.replace(
        "import { decodeMessage, encodeMessage } from './msgpack.js';", ""
    )
    # Remove export statement from msgpack.js
    msgpack_content = msgpack_content.replace(
        "export { encodeMessage, decodeMessage };", ""
    )

    # Inject configuration into the component
    config_script = f"""
    <script>
        window.STREAMING_CHART_CONFIG = {{
            websocketUrl: "{websocket_url}",
            topic: "{topic}",
            candleInterval: {candle_interval}
        }};
    </script>
    """

    # Combine all parts into a single HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script
            src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js">
        </script>
        <style>
        {css_content}
        </style>
    </head>
    <body>
        {html_content}
        {config_script}
        <script>
        // Msgpack decoder/encoder
        {msgpack_content}
        </script>
        <script>
        // Main chart script
        {js_content}
        </script>
    </body>
    </html>
    """

    components.html(full_html, height=height, scrolling=False)
