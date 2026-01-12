"""Chart creation module for data visualization.

This module provides classes for creating interactive charts using Plotly,
including candlestick charts, line plots, and bar plots with multi-row layouts.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional


class QuickChart:
    """Quick chart templates for common chart types.

    This class provides pre-configured chart templates that can be used
    to quickly create common visualizations like Kline (candlestick) charts
    with volume bars.
    """

    def create_kline_chart(
        self,
        data: pd.DataFrame,
        x: str = "open_time",
        y_open: str = "open",
        y_high: str = "high",
        y_low: str = "low",
        y_close: str = "close",
        volume: str = "volume",
        title: str = "Kline Chart",
    ) -> go.Figure:
        """Create a Kline (candlestick) chart with volume bars.

        Args:
            data: DataFrame containing OHLCV data
            x: Column name for x-axis (typically time/date)
            y_open: Column name for open prices
            y_high: Column name for high prices
            y_low: Column name for low prices
            y_close: Column name for close prices
            volume: Column name for volume data
            title: Chart title

        Returns:
            Plotly Figure object with candlestick and volume charts
        """
        chart = Chart(title)
        row1 = RowChart("Price", height=600)
        row1.add_candlestick_chart(
            data,
            x=x,
            y_open=y_open,
            y_high=y_high,
            y_low=y_low,
            y_close=y_close,
            name="Sample Candlestick"
        )
        row1.add_line_plot(
            data,
            x=x,
            y=volume,
            name="Volume"
        )
        chart.add_row(row1)

        row2 = RowChart("Volume", height=150)
        row2.add_bar_plot(
            data,
            x=x,
            y=volume,
            name="Volume"
        )
        chart.add_row(row2)
        fig = chart.create_chart()
        return fig


class Chart:
    """Main chart container that manages multiple row charts.

    This class provides a flexible way to create multi-row charts with
    shared x-axes and customizable layouts using Plotly.

    Attributes:
        title: The main title of the chart
        rows: List of RowChart objects to be displayed

    Example:
        >>> chart = Chart("My Dashboard")
        >>> row1 = chart.add_row(RowChart("Price", height=400))
        >>> row1.add_line_plot(df, x="date", y="price", name="BTC Price")
        >>> fig = chart.create_chart()
    """

    def __init__(self, title: str = "Chart") -> None:
        """Initialize a Chart with a title.

        Args:
            title: The main title for the chart (default: "Chart")
        """
        self.title = title
        self.rows: list[RowChart] = []

    def set_title(self, title: str) -> None:
        """Set or update the chart title.

        Args:
            title: New title for the chart
        """
        self.title = title

    def add_row(self, row: 'RowChart') -> 'RowChart':
        """Add a new row chart to the layout.

        Args:
            row: A RowChart instance to add to the chart

        Returns:
            The same RowChart instance for method chaining
        """
        self.rows.append(row)
        return row

    def create_chart(self) -> go.Figure:
        """Create and return the complete Plotly figure.

        This method combines all row charts into a single figure with
        shared x-axes and proper layout configuration.

        Returns:
            A Plotly Figure object ready for display or export
        """
        heights = [row.height for row in self.rows]
        row_count = len(self.rows)
        fig = make_subplots(
            rows=row_count,
            cols=1,
            shared_xaxes=True,
            row_heights=heights,
            vertical_spacing=0.1
        )
        for row_index, row in enumerate(self.rows, start=1):
            for chart in row.charts:
                fig.add_trace(chart, row=row_index, col=1)
        fig.update_layout(title=self.title)
        fig.update_layout(xaxis_rangeslider_visible=False, height=sum(heights) + 100)
        fig.update_layout({f"xaxis{row_count}": {"rangeslider": {"visible": True, "thickness": 0.03}}})
        return fig


class RowChart:
    """A single row in a multi-row chart layout.

    Each RowChart can contain multiple traces (line plots, bar charts,
    candlestick charts, etc.) that will be displayed in the same subplot.

    Attributes:
        charts: List of Plotly trace objects
        title: Title for this row
        height: Height of this row in pixels

    Example:
        >>> row = RowChart("Volume", height=200)
        >>> row.add_bar_plot(df, x="date", y="volume", name="Volume")
    """

    def __init__(self, title: str = "", height: int = 300) -> None:
        """Initialize a RowChart.

        Args:
            title: Title for this row (default: "")
            height: Height of this row in pixels (default: 300)
        """
        self.charts: list[go.Trace] = []
        self.title: str = title
        self.height: int = height

    def set_title(self, title: str) -> None:
        """Set or update the row title.

        Args:
            title: New title for this row
        """
        self.title = title

    def set_height(self, height: int) -> None:
        """Set or update the row height.

        Args:
            height: New height in pixels
        """
        self.height = height

    def add_line_plot(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        name: str,
    ) -> go.Scatter:
        """Add a line plot to this row.

        Args:
            data: DataFrame containing the data
            x: Column name for x-axis values
            y: Column name for y-axis values
            name: Name for the trace (shown in legend)

        Returns:
            The created Scatter trace object
        """
        trace = go.Scatter(x=data[x], y=data[y], mode='lines', name=name)
        self.charts.append(trace)
        return trace

    def add_bar_plot(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        name: str,
    ) -> go.Bar:
        """Add a bar chart to this row.

        Args:
            data: DataFrame containing the data
            x: Column name for x-axis values
            y: Column name for y-axis values
            name: Name for the trace (shown in legend)

        Returns:
            The created Bar trace object
        """
        trace = go.Bar(x=data[x], y=data[y], name=name)
        self.charts.append(trace)
        return trace

    def add_candlestick_chart(
        self,
        data: pd.DataFrame,
        x: str = "date",
        y_open: str = "open",
        y_high: str = "high",
        y_low: str = "low",
        y_close: str = "close",
        name: str = "Candlestick",
    ) -> go.Candlestick:
        """Add a candlestick chart to this row.

        Args:
            data: DataFrame containing OHLC data
            x: Column name for x-axis (typically time/date)
            y_open: Column name for open prices
            y_high: Column name for high prices
            y_low: Column name for low prices
            y_close: Column name for close prices
            name: Name for the trace (shown in legend)

        Returns:
            The created Candlestick trace object
        """
        trace = go.Candlestick(
            x=data[x],
            open=data[y_open],
            high=data[y_high],
            low=data[y_low],
            close=data[y_close],
            name=name,
        )
        self.charts.append(trace)
        return trace
