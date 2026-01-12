"""Data export module for converting visualizations to various formats.

This module provides utilities for exporting DataFrames and Plotly figures
to different file formats, including Markdown with embedded images.
"""

import os
from typing import Optional

import pandas as pd
from plotly import graph_objects as go


class Exporter:
    """Utility class for exporting data visualizations."""

    @staticmethod
    def export_to_markdown(
        df_list: list[pd.DataFrame],
        fig_list: list[go.Figure],
        name_path: str
    ) -> bool:
        """Export DataFrames and figures to a Markdown file with images.

        Args:
            df_list: List of DataFrames to export as markdown tables
            fig_list: List of Plotly figures to export as PNG images
            name_path: Directory name and base filename for exports
                      (e.g., "exported_data" creates folder "exported_data"
                      with file "exported_data/exported_data_markdown.md")

        Returns:
            True if export was successful, False otherwise

        Example:
            >>> dfs = [df1, df2]
            >>> figs = [fig1, fig2]
            >>> success = Exporter.export_to_markdown(dfs, figs, "my_report")
        """
        # Tạo folder nếu chưa tồn tại
        if not os.path.exists(name_path):
            os.makedirs(name_path)

        md_filename = f"{name_path}/{name_path}_markdown.md"
        md_imagename = f"{name_path}/{name_path}_image.png"
        try:
            # Save figure as image
            for i, fig in enumerate(fig_list):
                md_imagename = f"{name_path}/{name_path}_image{i}.png"
                fig.write_image(md_imagename)

            with open(md_filename, "w") as f:
                for df in df_list:
                    f.write(df.to_markdown(index=False))
                    f.write("\n\n")
                for i in range(len(fig_list)):
                    imagepath = f"{name_path}_image{i}.png"
                    f.write(f"![Chart]({imagepath})\n")

        except Exception as e:
            print(f"Error exporting to Markdown: {e}")
            return False

        return True
