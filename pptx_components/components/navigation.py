from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class TabsPanel(Component):
    """Static tabs-style panel inspired by React Tabs components.

    This is intentionally non-interactive for slides: one active tab is rendered
    with its associated body text while inactive tabs remain as headers.

    Args:
        tabs: Ordered tab labels.
        active_index: Which tab appears selected.
        content: Optional body text to show for the active tab.
        title: Optional heading above tabs.
        variant: "pill" | "line"
    """

    TITLE_H = 0.35
    HEADER_H = 0.45
    BODY_MIN_H = 0.8

    def __init__(
        self,
        tabs: list[str],
        active_index: int = 0,
        content: str | None = None,
        title: str | None = None,
        variant: str = "pill",
    ):
        if not tabs:
            raise ValueError("tabs must contain at least one item")
        if variant not in ("pill", "line"):
            raise ValueError(f"variant must be 'pill' or 'line'; got {variant!r}")
        if active_index < 0 or active_index >= len(tabs):
            raise ValueError("active_index out of range for tabs list")

        self.tabs = tabs
        self.active_index = active_index
        self.content = content
        self.title = title
        self.variant = variant

    @property
    def min_height(self) -> float:
        title_h = self.TITLE_H if self.title else 0.0
        return title_h + self.HEADER_H + self.BODY_MIN_H

    def render(
        self,
        slide,
        x: float,
        y: float,
        width: float,
        height: float,
        theme: Theme | None = None,
    ) -> None:
        t = _resolve(theme)
        pad = t.SM

        cursor_y = y
        if self.title:
            add_text_box(
                slide,
                x,
                cursor_y,
                width,
                self.TITLE_H,
                self.title,
                t.SUBHEADING,
                bold=True,
                color_rgb=t.TEXT_PRIMARY,
                font_name="Calibri Light",
            )
            cursor_y += self.TITLE_H

        tab_area_h = self.HEADER_H
        body_y = cursor_y + tab_area_h
        body_h = max(0.0, y + height - body_y)

        tab_w = width / len(self.tabs)
        for idx, label in enumerate(self.tabs):
            tab_x = x + idx * tab_w
            is_active = idx == self.active_index

            if self.variant == "pill":
                fill = t.ACCENT if is_active else t.SURFACE_ALT
                text_color = t.BG if is_active else t.TEXT_SECONDARY
                add_rect(
                    slide,
                    tab_x + 0.02,
                    cursor_y + 0.02,
                    max(0.0, tab_w - 0.04),
                    max(0.0, tab_area_h - 0.04),
                    fill_rgb=fill,
                    radius=0.06,
                )
            else:
                fill = None
                text_color = t.TEXT_PRIMARY if is_active else t.TEXT_MUTED
                if is_active:
                    add_rect(
                        slide,
                        tab_x + 0.06,
                        cursor_y + tab_area_h - 0.05,
                        max(0.0, tab_w - 0.12),
                        0.03,
                        fill_rgb=t.ACCENT,
                        radius=0.01,
                    )

            if fill is None:
                pass

            add_text_box(
                slide,
                tab_x,
                cursor_y,
                tab_w,
                tab_area_h,
                label,
                t.BODY,
                bold=is_active,
                color_rgb=text_color,
                font_name="Calibri",
                alignment=PP_ALIGN.CENTER,
            )

        add_rect(slide, x, body_y, width, body_h, fill_rgb=t.SURFACE, radius=0.05)

        body_text = self.content or ""
        if body_text:
            add_text_box(
                slide,
                x + pad,
                body_y + pad,
                max(0.0, width - 2 * pad),
                max(0.0, body_h - 2 * pad),
                body_text,
                t.BODY,
                color_rgb=t.TEXT_SECONDARY,
                font_name="Calibri",
                word_wrap=True,
            )


class StepFlow(Component):
    """Horizontal stepper inspired by UI libraries such as Ant Design Steps.

    Args:
        steps: Ordered step labels.
        current: Active step index.
        statuses: Optional explicit status list per step:
            "done" | "current" | "pending" | "error".
            If omitted, status is inferred from `current`.
        title: Optional heading above the stepper.
        show_numbers: Show step numbers for non-completed states.
    """

    TITLE_H = 0.35
    TRACK_H = 0.48
    LABEL_H = 0.42

    def __init__(
        self,
        steps: list[str],
        current: int = 0,
        statuses: list[str] | None = None,
        title: str | None = None,
        show_numbers: bool = True,
    ):
        if not steps:
            raise ValueError("steps must contain at least one item")
        if current < 0 or current >= len(steps):
            raise ValueError("current out of range for steps list")

        allowed = {"done", "current", "pending", "error"}
        if statuses is not None:
            if len(statuses) != len(steps):
                raise ValueError("statuses length must match steps length")
            bad = [s for s in statuses if s not in allowed]
            if bad:
                raise ValueError(f"invalid statuses found: {bad!r}")

        self.steps = steps
        self.current = current
        self.statuses = statuses
        self.title = title
        self.show_numbers = show_numbers

    @property
    def min_height(self) -> float:
        title_h = self.TITLE_H if self.title else 0.0
        return title_h + self.TRACK_H + self.LABEL_H + 0.1

    def _status_for(self, idx: int) -> str:
        if self.statuses is not None:
            return self.statuses[idx]
        if idx < self.current:
            return "done"
        if idx == self.current:
            return "current"
        return "pending"

    def render(
        self,
        slide,
        x: float,
        y: float,
        width: float,
        height: float,
        theme: Theme | None = None,
    ) -> None:
        t = _resolve(theme)

        cursor_y = y
        if self.title:
            add_text_box(
                slide,
                x,
                cursor_y,
                width,
                self.TITLE_H,
                self.title,
                t.SUBHEADING,
                bold=True,
                color_rgb=t.TEXT_PRIMARY,
                font_name="Calibri Light",
            )
            cursor_y += self.TITLE_H

        n = len(self.steps)
        if n == 1:
            centers = [x + width / 2]
        else:
            span = width - 0.4
            left = x + 0.2
            centers = [left + i * (span / (n - 1)) for i in range(n)]

        line_y = cursor_y + self.TRACK_H * 0.46
        node_d = min(0.28, max(0.2, width / (n * 8.0)))

        for i in range(n - 1):
            s0 = self._status_for(i)
            color = t.ACCENT_SOFT if s0 in ("done", "current") else t.SURFACE_ALT
            add_rect(
                slide,
                centers[i] + node_d / 2,
                line_y - 0.015,
                max(0.0, centers[i + 1] - centers[i] - node_d),
                0.03,
                fill_rgb=color,
                radius=0.01,
            )

        for idx, label in enumerate(self.steps):
            status = self._status_for(idx)
            if status == "done":
                fill = t.POSITIVE
                text = "✓"
                text_color = t.BG
                label_color = t.TEXT_SECONDARY
            elif status == "current":
                fill = t.ACCENT
                text = str(idx + 1) if self.show_numbers else ""
                text_color = t.BG
                label_color = t.TEXT_PRIMARY
            elif status == "error":
                fill = t.NEGATIVE
                text = "!"
                text_color = t.BG
                label_color = t.NEGATIVE
            else:
                fill = t.SURFACE_ALT
                text = str(idx + 1) if self.show_numbers else ""
                text_color = t.TEXT_MUTED
                label_color = t.TEXT_MUTED

            node_x = centers[idx] - node_d / 2
            node_y = line_y - node_d / 2
            add_rect(slide, node_x, node_y, node_d, node_d, fill_rgb=fill, radius=node_d / 2)

            if text:
                add_text_box(
                    slide,
                    node_x,
                    node_y + 0.01,
                    node_d,
                    node_d - 0.02,
                    text,
                    t.CAPTION,
                    bold=True,
                    color_rgb=text_color,
                    alignment=PP_ALIGN.CENTER,
                    font_name="Calibri",
                )

            label_top = cursor_y + self.TRACK_H + 0.02
            add_text_box(
                slide,
                centers[idx] - 0.7,
                label_top,
                1.4,
                self.LABEL_H,
                label,
                t.CAPTION,
                bold=(status == "current"),
                color_rgb=label_color,
                alignment=PP_ALIGN.CENTER,
                font_name="Calibri",
                word_wrap=True,
            )
