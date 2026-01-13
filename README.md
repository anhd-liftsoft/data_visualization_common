# Data Visualization Library

A comprehensive Python library for creating interactive data visualizations with Plotly and Streamlit. This library provides an easy-to-use API for building dashboards with advanced table filtering, multi-row charts, and real-time streaming data visualization.

## 🌟 Features

- **📊 Interactive Charts**: Create multi-row Plotly charts with candlesticks, line plots, and bar charts
- **📋 Advanced Tables**: Feature-rich tables with multiple filter types (multiselect, range, date, time)
- **⚡ Real-time Streaming**: WebSocket-powered live candlestick charts
- **📤 Export Capabilities**: Export data and visualizations to Markdown with embedded images
- **🎨 Streamlit Integration**: Ready-to-use Streamlit app components for rapid dashboard development

## 📦 Installation

### For Development

```bash
pip install -e .
```

### From Source

```bash
git clone <repository-url>
cd data_visualization
pip install -r requirements.txt
```

## 🚀 Quick Start

### Creating a Simple Chart

```python
from data_visualization import Chart, RowChart
import pandas as pd

# Load your data
df = pd.read_csv("btc_data.csv")

# Create a chart with multiple rows
chart = Chart("Bitcoin Price Analysis")

# Add a candlestick chart row
price_row = chart.add_row(RowChart("Price", height=600))
price_row.add_candlestick_chart(
    df,
    x="open_time",
    y_open="open",
    y_high="high",
    y_low="low",
    y_close="close",
    name="BTC/USD"
)

# Add a volume bar chart row
volume_row = chart.add_row(RowChart("Volume", height=200))
volume_row.add_bar_plot(df, x="open_time", y="volume", name="Volume")

# Generate and display the figure
fig = chart.create_chart()
fig.show()
```

### Building a Streamlit Dashboard

```python
from data_visualization import DataVisualizationApp
import pandas as pd

# Initialize the app
app = DataVisualizationApp("My Trading Dashboard")

# Add a table with filters
df = pd.read_csv("trades.csv")
filters = [
    {"column": "symbol", "type": "multiselect", "label": "Symbol"},
    {"column": "price", "type": "range", "label": "Price Range"},
    {"column": "timestamp", "type": "daterange", "label": "Date Range"}
]
app.add_table(df, filters=filters, title="Recent Trades")

# Add a chart
from data_visualization import Chart, RowChart
chart = Chart("Price Chart")
row = chart.add_row(RowChart("Price", height=400))
row.add_line_plot(df, x="timestamp", y="price", name="Price")
app.add_figure(chart.create_chart())

# Add a streaming chart
app.add_streaming_chart(
    websocket_url="wss://stream.example.com",
    topic="market.data@BTC",
    height=500,
    candle_interval=60
)

# Run the app
app.run()
```

## 📚 API Documentation

### Chart Module

#### `Chart`
Main container for multi-row chart layouts.

**Methods:**
- `__init__(title: str = "Chart")`: Initialize with a title
- `add_row(row: RowChart) -> RowChart`: Add a new row to the chart
- `create_chart() -> go.Figure`: Generate the Plotly figure

#### `RowChart`
Individual row in a chart layout.

**Methods:**
- `__init__(title: str = "", height: int = 300)`: Initialize a row
- `add_line_plot(data, x, y, name) -> go.Scatter`: Add a line plot
- `add_bar_plot(data, x, y, name) -> go.Bar`: Add a bar chart
- `add_candlestick_chart(data, x, y_open, y_high, y_low, y_close, name) -> go.Candlestick`: Add candlestick chart

#### `QuickChart`
Pre-configured chart templates.

**Methods:**
- `create_kline_chart(data, ...) -> go.Figure`: Create a Kline chart with volume

### Table Module

#### `TableManager`
Advanced table rendering with filtering capabilities.

**Methods:**
- `render_table(df, filters, scope)`: Render an interactive table

**Filter Types:**
- `multiselect`: Multiple choice selection
- `selectbox`: Single choice selection
- `range`: Numeric range slider
- `daterange`: Date range picker
- `timerange`: Time range picker (supports cross-midnight ranges)

**Filter Configuration Example:**
```python
filters = [
    {
        "column": "category",
        "type": "multiselect",
        "label": "Product Category"
    },
    {
        "column": "price",
        "type": "range",
        "label": "Price Range"
    },
    {
        "column": "date",
        "type": "daterange",
        "label": "Date Range"
    }
]
```

### Exporter Module

#### `Exporter`
Export data and visualizations.

**Methods:**
- `export_to_markdown(df_list, fig_list, name_path) -> bool`: Export to Markdown with images

### Streamlit App Module

#### `DataVisualizationApp`
High-level Streamlit application builder.

**Methods:**
- `__init__(title: str)`: Initialize the app
- `add_table(df, filters, title)`: Add a table with filters
- `add_figure(fig)`: Add a Plotly figure
- `add_streaming_chart(websocket_url, topic, height, candle_interval)`: Add real-time chart
- `run()`: Start the Streamlit app

### Streaming Chart Module

#### `streaming_chart`
Real-time candlestick chart component.

**Parameters:**
- `websocket_url`: WebSocket endpoint URL
- `topic`: Data topic to subscribe to
- `height`: Chart height in pixels (default: 500)
- `candle_interval`: Candle interval in seconds (default: 60)

## 📂 Project Structure

```
data_visualization/
├── src/
│   ├── __init__.py           # Package exports
│   ├── chart.py              # Chart creation classes
│   ├── table.py              # Table manager with filters
│   ├── exporter.py           # Export utilities
│   ├── streamlit_app.py      # Streamlit app wrapper
│   ├── data_processor.py     # Data processing utilities (placeholder)
│   └── streaming_chart/      # Real-time chart component
│       ├── __init__.py
│       └── frontend/
│           ├── index.html
│           ├── main.js
│           ├── msgpack.js
│           └── style.css
├── btc_data.csv              # Sample data
├── example.py                # Usage examples
├── requirements.txt          # Dependencies
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## 🔧 Requirements

- Python 3.8+
- pandas
- plotly
- streamlit
- kaleido (for image export)
- tabulate (for markdown export)

## 📖 Examples

See [example.py](example.py) for complete working examples.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
