import pandas as pd

from src.chart import Chart, RowChart
from src.streamlit_app import DataVisualizationApp


app = DataVisualizationApp("Combined Chart and Table Example")

# Prepare sample data
df = pd.read_csv("btc_data.csv")
df["open_time"] = pd.to_datetime(df["open_time"], unit="us")
df["close_time"] = pd.to_datetime(df["close_time"], unit="us")
df["ma"] = df["close"].rolling(window=20).mean()

# Build chart using the common Chart API from src/chart.py
chart = Chart("Example Combined Chart")

row1 = RowChart("Line Series", height=150)
row1.add_line_plot(df, x="open_time", y="open", name="Open Price")
chart.add_row(row1)

row2 = RowChart("Candlestick", height=450)
row2.add_candlestick_chart(
    df,
    x="open_time",
    y_open="open",
    y_high="high",
    y_low="low",
    y_close="close",
    name="Sample Candlestick"
)
row2.add_line_plot(df, x="open_time", y="ma", name="20-period MA")
chart.add_row(row2)

chart_figure = chart.create_chart()
app.add_figure(chart_figure)

# Add table with filters
filter_configs = [
    {"column": "open_time", "type": "timerange", "label": "Open Time Range"},
    {"column": "open", "type": "range", "label": "Open Price Range"},
    {"column": "high", "type": "range", "label": "High Price Range"},
    {"column": "low", "type": "range", "label": "Low Price Range"},
    {"column": "close", "type": "range", "label": "Close Price Range"},
    {"column": "volume", "type": "range", "label": "Volume Range"},
]

app.add_table(
    df,
    filters=filter_configs,
    title="BTC Market Data Table"
)

# Add a real-time streaming chart
streaming_chart_config = {
    "websocket_url": "ws://localhost:8009/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWI"
                     "iOiIxIiwidG9waWNzIjpbIm1hcmtldC5kYXRhQEJUQyIsInVzZXIudHJhZGVAMSJdLCJzY29wZXMiOlsidHJh"
                     "ZGU6cmVhZCJdLCJleHAiOjIxMjY3MTI3MTR9.E03drQ5OFn6GhSgoR3QAezUkfQjlZOpBAeZj6KKoWi8",
    "topic": "market.data@BTC",
    "height": 500,
    "candle_interval": 60,
}
app.add_streaming_chart(**streaming_chart_config)

app.run()
