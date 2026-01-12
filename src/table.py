import streamlit as st
import pandas as pd
import math
from datetime import time


class TableManager:
    @st.fragment
    @staticmethod
    def render_table(df: pd.DataFrame, filters: list[dict], scope: str = "table"):
        # ==== Filters trong Expander ====
        with st.expander("Bộ lọc", expanded=False):
            vals = TableManager._render_filters(df, filters, scope)

            # Reset button bên trong expander
            if st.button("Reset tất cả bộ lọc", key=f"{scope}:reset", width='stretch'):
                # reset keys filters
                for f in filters:
                    st.session_state.pop(f"{scope}:{f['column']}", None)

                # reset keys bảng
                for k in [f"{scope}:search", f"{scope}:sort_by", f"{scope}:sort_order",
                          f"{scope}:page_size", f"{scope}:page"]:
                    st.session_state.pop(k, None)

                st.rerun(scope="fragment")

        filtered_df = TableManager._apply_filters(df, filters, vals)

        # ==== Controls search/sort ====
        col_search, _, col_sort_by, col_sort_order = st.columns([6, 3, 1, 1])
        with col_search:
            search_term = st.text_input(
                "🔍 Tìm kiếm",
                placeholder="Nhập từ khóa để tìm kiếm...",
                label_visibility="collapsed",
                key=f"{scope}:search",
            )
        with col_sort_by:
            sort_by = st.selectbox(
                "Sắp xếp theo cột",
                options=filtered_df.columns.tolist(),
                index=0,
                label_visibility="collapsed",
                key=f"{scope}:sort_by",
            )
        with col_sort_order:
            sort_order = st.selectbox(
                "Thứ tự sắp xếp",
                options=["Tăng dần", "Giảm dần"],
                index=0,
                label_visibility="collapsed",
                key=f"{scope}:sort_order",
            )

        # ---- Logic: Search ----
        if search_term:
            mask = pd.Series(False, index=filtered_df.index)
            q = str(search_term)
            for c in filtered_df.columns:
                mask |= filtered_df[c].astype(str).str.contains(q, case=False, na=False)
            filtered_df = filtered_df[mask]

        # ---- Logic: Sort ----
        ascending = (sort_order == "Tăng dần")
        if sort_by:
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending, kind="mergesort")

        # ==== Hiển thị bảng ====
        total_rows = len(filtered_df)

        if total_rows == 0:
            st.info("Không có dữ liệu phù hợp với điều kiện lọc/tìm kiếm.")
            return

        # Tính toán phân trang
        page_size = st.session_state.get(f"{scope}:page_size", 20)
        total_pages = max(1, math.ceil(total_rows / page_size))
        current_page = min(st.session_state.get(f"{scope}:page", 1), total_pages)

        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        page_df = filtered_df.iloc[start_idx:end_idx]

        # Hiển thị bảng
        st.dataframe(page_df, width='stretch')

        # ==== Pagination ====
        _, col_right = st.columns([5, 1])

        with col_right:
            st.markdown(
                f"<div style='text-align: right; font-size: 0.85em; color: gray; margin-bottom: 5px;'>"
                f"<b>{start_idx + 1}</b>-<b>{end_idx}</b> / <b>{total_rows}</b>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # Compact pagination controls
            sub_col1, sub_col2 = st.columns([1, 1])
            with sub_col1:
                st.selectbox(
                    "Rows",
                    options=[10, 20, 50, 100],
                    index=[10, 20, 50, 100].index(page_size) if page_size in [10, 20, 50, 100] else 1,
                    label_visibility="collapsed",
                    key=f"{scope}:page_size",
                )
            with sub_col2:
                st.number_input(
                    "Page",
                    min_value=1,
                    max_value=total_pages,
                    step=1,
                    value=current_page,
                    label_visibility="collapsed",
                    key=f"{scope}:page",
                )

    @staticmethod
    def _render_filters(df: pd.DataFrame, filters: list[dict], scope: str) -> dict:
        """
        Render các filter widgets trong grid layout 4 cột.

        Args:
            filters: List of dictionary describe filter. Each filter has keys:
                - 'key' (required): Unique key for filter.
                - 'type' (required): Filter type ('multiselect', 'selectbox',
                'range', 'daterange', 'timerange').
                - 'label' (optional): Label to display. Default is key.
            scope: Namespace to avoid session_state conflict between pages.
                Example: 'trades', 'overview'.

        Returns:
            Dictionary with key is filter key and value is current value of filter.
        """
        values = {}

        # Tạo grid layout: 4 filters mỗi hàng
        num_filters = len(filters)
        num_cols = 4

        for i in range(0, num_filters, num_cols):
            cols = st.columns(num_cols)
            batch = filters[i:i + num_cols]

            for idx, f in enumerate(batch):
                col = f['column']
                key = f"{scope}:{col}"
                label = f.get("label", col)
                type = f["type"]

                with cols[idx]:
                    if type == "multiselect":
                        options = df[col].dropna().unique().tolist()
                        values[col] = st.multiselect(label, options, key=key)

                    elif type == "selectbox":
                        options = ["All"] + df[col].dropna().unique().tolist()
                        values[col] = st.selectbox(label, options, key=key)

                    elif type == "range":
                        fmin = float(df[col].min())
                        fmax = float(df[col].max())
                        values[col] = st.slider(
                            label,
                            min_value=fmin,
                            max_value=fmax,
                            value=(fmin, fmax),
                            key=key
                        )

                    elif type == "daterange":
                        datemin = df[col].min().date()
                        datemax = df[col].max().date()
                        values[col] = st.date_input(label, value=(datemin, datemax), key=key)

                    elif type == "timerange":
                        default_start = f.get("default_start", time(0, 0))
                        default_end = f.get("default_end", time(23, 59))
                        st.write(f"{label}")
                        col1, col2 = st.columns(2)
                        with col1:
                            start_time = st.time_input(
                                "Từ",
                                value=default_start,
                                key=f"{key}_start",
                                step=60
                            )
                        with col2:
                            end_time = st.time_input(
                                "Đến",
                                value=default_end,
                                key=f"{key}_end",
                                step=60
                            )
                        values[col] = (start_time, end_time)

                    else:
                        st.warning(f"Unknown filter type: {type}")

        return values

    @staticmethod
    def _apply_filters(df: pd.DataFrame, filters: list[dict], values: dict) -> pd.DataFrame:
        """
        Apply filters to DataFrame and return filtered data.

        Args:
            df: DataFrame cần lọc.
            filters: List of dictionary describe filter. Each filter has keys:
                - 'key' (required): Key of filter, must match with key in values.
                - 'type' (required): Filter type ('multiselect', 'selectbox',
                'range', 'daterange', 'timerange', 'text', 'checkbox').
                - 'column' (optional): Column name in DataFrame. Default is key.
                - 'all_value' (optional): Value representing "all" (skip filter).
            values: Dictionary containing current filter values, returned from
                render_filters().

        Returns:
            DataFrame after applying filters.

        Note:
            - With 'timerange', supports time range across midnight
            (e.g., 22:00 - 06:00).
            - With 'text', case-insensitive search.
            - With 'multiselect/selectbox', if value is 'all_value' then
            filter will be skipped.
        """
        mask = pd.Series(True, index=df.index)
        for f in filters:
            col = f["column"]
            type = f["type"]
            value = values.get(col)

            if type in ("multiselect", "selectbox"):
                # Skip filtering if value is the "all_value" (e.g., "All")
                all_val = f.get("all_value")
                if value == all_val:
                    continue

                if isinstance(value, list) and len(value) > 0:
                    mask &= df[col].isin(value)
                elif value is not None:
                    mask &= df[col].eq(value)

            elif type == "range":
                lo, hi = value
                mask &= df[col].between(lo, hi)

            elif type == "text":
                if value and value.strip():
                    mask &= df[col].astype(str).str.contains(value.strip(), case=False, na=False)

            elif type == "checkbox":
                if value is True:
                    mask &= df[col].astype(bool)

            elif type == "daterange":
                start, end = value
                mask &= df[col].dt.date.between(start, end)

            elif type == "timerange":
                start_time, end_time = value
                col_time = df[col].dt.time
                if start_time <= end_time:
                    mask &= (col_time >= start_time) & (col_time <= end_time)
                else:
                    mask &= (col_time >= start_time) | (col_time <= end_time)

        return df[mask]
