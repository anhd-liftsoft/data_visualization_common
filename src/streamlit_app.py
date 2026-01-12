"""Streamlit application module for interactive data visualization.

This module provides a high-level DataVisualizationApp class that combines
tables, charts, and streaming visualizations in a Streamlit web application.
"""

import streamlit as st
import pandas as pd
from typing import Any

from .streaming_chart import streaming_chart
from .table import TableManager
from .exporter import Exporter


class DataVisualizationApp:
    """Main application class for building data visualization dashboards.

    This class provides a convenient API for creating Streamlit applications
    that display tables with advanced filtering, static Plotly charts, and
    real-time streaming charts powered by WebSocket connections.

    Attributes:
        title: The application title displayed at the top
        tables: List of table configurations to render
        figures: List of Plotly figures to display
        streaming_charts: List of streaming chart configurations

    Example:
        >>> app = DataVisualizationApp("My Dashboard")
        >>> app.add_table(df, filters=[...], title="Sales Data")
        >>> app.add_figure(fig)
        >>> app.run()
    """

    def __init__(self, title: str = "Data Visualization App") -> None:
        """Initialize the application.

        Args:
            title: Application title (default: "Data Visualization App")
        """
        self.title = title
        self.tables: list[dict] = []
        self.figures: list = []
        self.streaming_charts: list[dict] = []

    def run(self) -> None:
        """Run the Streamlit application.

        This method configures the page layout, displays all added components
        (tables, charts, streaming charts), and provides an export button.
        """
        st.set_page_config(layout="wide")
        st.title(self.title)

        for idx, table in enumerate(self.tables):
            self.show_table(table, scope=f"table_{idx}")

        for fig in self.figures:
            self.show_chart(fig)

        for chart_config in self.streaming_charts:
            streaming_chart(
                websocket_url=chart_config.get("websocket_url", ""),
                topic=chart_config.get("topic", "market.data@BTC"),
                height=chart_config.get("height", 500),
                candle_interval=chart_config.get("candle_interval", 60),
            )

        if st.button("Export Data", width='content'):
            is_done = Exporter.export_to_markdown(
                df_list=[table["dataframe"] for table in self.tables],
                fig_list=self.figures,
                name_path="exported_data"
            )
            if is_done:
                st.success("Data exported successfully!")
            else:
                st.error("Failed to export data.")

    def add_table(self, df: pd.DataFrame, filters: list = [], title: str = "") -> None:
        """Add a table with filters to the application.

        Args:
            df: DataFrame to display
            filters: List of filter configurations (see TableManager documentation)
            title: Title to display above the table

        Example:
            >>> filters = [
            ...     {"column": "category", "type": "multiselect", "label": "Category"},
            ...     {"column": "price", "type": "range", "label": "Price Range"}
            ... ]
            >>> app.add_table(df, filters=filters, title="Products")
        """
        self.tables.append({
            "dataframe": df,
            "filters": filters,
            "title": title
        })

    @st.fragment
    def show_table(self, table_config: dict, scope: str) -> None:
        """Render a single table with its filters.

        Args:
            table_config: Dictionary containing "dataframe", "filters", and "title"
            scope: Unique scope identifier to avoid session_state conflicts
        """
        st.markdown("---")
        st.subheader(table_config.get("title", ""))
        TableManager.render_table(
            table_config.get("dataframe", pd.DataFrame()),
            table_config.get("filters", []),
            scope=scope
        )

    def show_chart(self, fig: Any) -> None:
        """Display a Plotly figure.

        Args:
            fig: Plotly Figure object to display
        """
        st.markdown("---")
        st.plotly_chart(fig)

    def add_figure(self, fig: Any) -> None:
        """Add a Plotly figure to the application.

        Args:
            fig: Plotly Figure object to add

        Example:
            >>> from plotly import graph_objects as go
            >>> fig = go.Figure(data=[go.Bar(x=[1, 2, 3], y=[4, 5, 6])])
            >>> app.add_figure(fig)
        """
        self.figures.append(fig)

    def add_streaming_chart(
        self,
        websocket_url: str,
        topic: str = "market.data@BTC",
        height: int = 500,
        candle_interval: int = 60,
        key: str = None,
    ):
        """
        Add a real-time candlestick chart that connects to a WebSocket.

        Args:
            websocket_url: The WebSocket URL to connect to (e.g., "wss://example.com/ws")
            topic: The topic to subscribe to (e.g., "market.data@BTC")
            height: Height of the chart in pixels
            candle_interval: Candlestick interval in seconds (default: 60 = 1 minute)
            key: Unique key for the component
        """
        self.streaming_charts.append({
            "websocket_url": websocket_url,
            "topic": topic,
            "height": height,
            "candle_interval": candle_interval,
            "key": key,
        })
