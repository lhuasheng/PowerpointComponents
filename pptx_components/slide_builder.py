from __future__ import annotations

from pptx import Presentation

from pptx_components.base import Component, set_slide_background, _resolve
from pptx_components.layout import Row
from pptx_components.theme import Theme, get_theme


class SlideBuilder:
    """Clean API for composing a single slide from components.

    Tracks a vertical cursor so callers can `add()` components sequentially
    without manually computing y-offsets.
    """

    def __init__(self, prs: Presentation, theme: Theme | None = None):
        self.theme = _resolve(theme)
        # Use blank slide layout (index 6)
        blank_layout = prs.slide_layouts[6]
        self.slide = prs.slides.add_slide(blank_layout)
        set_slide_background(self.slide, self.theme.BG)
        self.cursor_y: float = self.theme.MARGIN

    # ── Internal ───────────────────────────────────────────────────────────

    def _content_width(self) -> float:
        return self.theme.SLIDE_W - 2 * self.theme.MARGIN

    # ── Public API ─────────────────────────────────────────────────────────

    def add(self, component: Component,
            x: float | None = None,
            y: float | None = None,
            w: float | None = None,
            h: float | None = None) -> "SlideBuilder":
        """Render a component on the slide.

        Defaults:
          x = theme.MARGIN
          w = SLIDE_W - 2*MARGIN
          h = component.min_height
          y = cursor_y (auto-advances after render)

        Passing an explicit y overrides the cursor for this call only
        (cursor is NOT advanced when y is explicitly provided).
        """
        t = self.theme
        resolved_x = x if x is not None else t.MARGIN
        resolved_w = w if w is not None else self._content_width()
        resolved_h = h if h is not None else component.min_height_for(t)

        explicit_y = y is not None
        resolved_y = y if explicit_y else self.cursor_y

        component.render(self.slide, resolved_x, resolved_y, resolved_w, resolved_h, theme=t)

        if not explicit_y:
            self.cursor_y += resolved_h + t.SM

        return self  # fluent API

    def add_full(self, component: Component,
                 h: float | None = None) -> "SlideBuilder":
        """Add a component spanning the full content width at the current cursor."""
        return self.add(component, h=h)

    def add_row(self, *components: Component,
                h: float | None = None,
                gap: float | None = None,
                weights: list[float] | None = None) -> "SlideBuilder":
        """Wrap components in a Row and add at the current cursor."""
        row = Row(*components, gap=gap, weights=weights)
        return self.add(row, h=h)

    def skip(self, height: float) -> "SlideBuilder":
        """Advance the cursor by a fixed amount (manual spacing)."""
        self.cursor_y += height
        return self

    def set_cursor(self, y: float) -> "SlideBuilder":
        """Manually position the cursor."""
        self.cursor_y = y
        return self
