from __future__ import annotations

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class GroupedTable(Component):
    """Table with group headers, sub-rows, and optional group footers.

    Organizes hierarchical data into collapsible groups and rows. Useful for:
        - Regional/departmental breakdowns with totals
        - Category hierarchies (Product > SKU > Variant)
        - Org charts with team members
        - Budget hierarchies (Program > Project > Line Item)

    Layout:
        - Group header row (bold, colored background)
        - Data rows (indented, lighter background)
        - Optional group footer row (summary, subtle color)
        - Column headers at top

    Data Structure:
        groups: List of {
            "header": "Group Name" or ("Group Name", value1, value2, ...),
            "rows": [
                ("Item 1", val1, val2, ...),
                ("Item 2", val1, val2, ...),
            ],
            "footer": ("Total", val1, val2, ...) or None,
        }

    Args:
        columns: List of column header strings (e.g. ["Region", "Q1", "Q2", "Q3"]).
        groups: List of group dicts as described above.
        title: Optional table title.
        column_widths: List of width fractions; auto-calculated if None.
        show_dividers: Whether to show group separators. Default: True.

    Example:
        >>> table = GroupedTable(
        ...     columns=["Region", "2025", "2026", "+/- YoY"],
        ...     groups=[
        ...         {
        ...             "header": "NORTH AMERICA",
        ...             "rows": [
        ...                 ("USA", "$500M", "$620M", "+24%"),
        ...                 ("Canada", "$80M", "$95M", "+19%"),
        ...             ],
        ...             "footer": ("SubtotalNA", "$580M", "$715M", "+23%"),
        ...         },
        ...         {
        ...             "header": "EMEA",
        ...             "rows": [
        ...                 ("UK", "$200M", "$245M", "+22%"),
        ...                 ("France", "$150M", "$180M", "+20%"),
        ...             ],
        ...             "footer": ("SubtotalEMEA", "$350M", "$425M", "+21%"),
        ...         },
        ...     ],
        ...     title="Regional Revenue Review",
        ... )
    """

    TITLE_H = 0.35
    HEADER_H = 0.32
    ROW_H = 0.28
    FOOTER_H = 0.28

    def __init__(
        self,
        columns: list[str],
        groups: list[dict],
        title: str | None = None,
        column_widths: list[float] | None = None,
        show_dividers: bool = True,
    ):
        if not columns:
            raise ValueError("columns list must not be empty")
        if not groups:
            raise ValueError("groups list must not be empty")

        self.columns = columns
        self.groups = groups
        self.title = title
        self.show_dividers = show_dividers

        # Auto-calculate column widths if not provided
        if column_widths is None:
            self.column_widths = [1.0 / len(columns)] * len(columns)
        else:
            if len(column_widths) != len(columns):
                raise ValueError(f"column_widths length mismatch: {len(column_widths)} vs {len(columns)}")
            total = sum(column_widths)
            self.column_widths = [w / total for w in column_widths]

    @property
    def min_height(self) -> float:
        h = (self.TITLE_H if self.title else 0.0) + self.HEADER_H
        for group in self.groups:
            h += self.ROW_H  # Group header
            h += len(group.get("rows", [])) * self.ROW_H
            if group.get("footer"):
                h += self.FOOTER_H
            if self.show_dividers:
                h += 0.1  # Divider space
        return h

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        cursor_y = y

        # Title
        if self.title:
            add_text_box(
                slide, x, cursor_y, width, self.TITLE_H,
                self.title, 24, bold=True,
                color_rgb=t.TEXT_PRIMARY,
                alignment=PP_ALIGN.CENTER
            )
            cursor_y += self.TITLE_H

        # Column headers (fixed row)
        col_x = x
        for i, (col_name, col_width) in enumerate(zip(self.columns, self.column_widths)):
            col_w = width * col_width
            add_rect(slide, col_x, cursor_y, col_w, self.HEADER_H, fill_rgb=t.ACCENT)
            add_text_box(
                slide, col_x + 0.05, cursor_y + 0.02, col_w - 0.1, self.HEADER_H - 0.04,
                col_name, 11, bold=True,
                color_rgb=(255, 255, 255),
                alignment=PP_ALIGN.CENTER
            )
            col_x += col_w

        cursor_y += self.HEADER_H

        # Group rows
        for group_idx, group in enumerate(self.groups):
            # Group header row
            group_header = group.get("header", "")
            col_x = x
            for col_idx, col_width in enumerate(self.column_widths):
                col_w = width * col_width
                add_rect(slide, col_x, cursor_y, col_w, self.ROW_H, fill_rgb=t.SURFACE_ALT)

                # Get text for this column
                if col_idx == 0:
                    cell_text = (group_header if isinstance(group_header, str) else group_header[0])
                else:
                    if isinstance(group_header, tuple) and col_idx < len(group_header):
                        cell_text = str(group_header[col_idx])
                    else:
                        cell_text = ""

                add_text_box(
                    slide, col_x + 0.05, cursor_y + 0.02, col_w - 0.1, self.ROW_H - 0.04,
                    cell_text, 11, bold=True,
                    color_rgb=t.TEXT_PRIMARY,
                    alignment=PP_ALIGN.LEFT
                )
                col_x += col_w

            cursor_y += self.ROW_H

            # Data rows
            for row_data in group.get("rows", []):
                col_x = x
                for col_idx, col_width in enumerate(self.column_widths):
                    col_w = width * col_width
                    add_rect(slide, col_x, cursor_y, col_w, self.ROW_H, fill_rgb=t.SURFACE)

                    # Get cell text
                    cell_text = str(row_data[col_idx]) if col_idx < len(row_data) else ""
                    indent = "    " if col_idx == 0 else ""

                    add_text_box(
                        slide, col_x + 0.05, cursor_y + 0.02, col_w - 0.1, self.ROW_H - 0.04,
                        indent + cell_text, 10,
                        color_rgb=t.TEXT_PRIMARY,
                        alignment=PP_ALIGN.LEFT
                    )
                    col_x += col_w

                cursor_y += self.ROW_H

            # Footer row
            if group.get("footer"):
                footer_data = group["footer"]
                col_x = x
                for col_idx, col_width in enumerate(self.column_widths):
                    col_w = width * col_width
                    add_rect(slide, col_x, cursor_y, col_w, self.FOOTER_H, fill_rgb=t.SURFACE_ALT)

                    # Get footer cell text
                    cell_text = str(footer_data[col_idx]) if col_idx < len(footer_data) else ""

                    add_text_box(
                        slide, col_x + 0.05, cursor_y + 0.02, col_w - 0.1, self.FOOTER_H - 0.04,
                        cell_text, 10, bold=True,
                        color_rgb=t.TEXT_MUTED,
                        alignment=PP_ALIGN.LEFT
                    )
                    col_x += col_w

                cursor_y += self.FOOTER_H

            # Divider
            if self.show_dividers and group_idx < len(self.groups) - 1:
                cursor_y += 0.1
