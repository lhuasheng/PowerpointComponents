from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class CodeBlock(Component):
    """Monospace code display inspired by shadcn/ui's and MUI's CodeBlock patterns.

    Args:
        code: The code text to display (newlines preserved).
        language: Optional language badge shown in a header bar.
        show_line_numbers: Prefix each line with its 1-based line number.
    """

    HEADER_H = 0.30
    LINE_H = 0.22
    PAD = 0.14

    def __init__(
        self,
        code: str,
        language: str | None = None,
        show_line_numbers: bool = False,
    ):
        if not code:
            raise ValueError("code must not be empty")
        self.code = code
        self.language = language
        self.show_line_numbers = show_line_numbers
        self._lines = code.splitlines() or [""]

    @property
    def min_height(self) -> float:
        header = self.HEADER_H if self.language else 0.0
        return header + len(self._lines) * self.LINE_H + 2 * self.PAD

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

        # Outer background
        add_rect(slide, x, y, width, height, fill_rgb=t.SURFACE, radius=0.04)

        cursor_y = y + self.PAD

        if self.language:
            # Header bar with language badge
            add_rect(slide, x, y, width, self.HEADER_H, fill_rgb=t.SURFACE_ALT, radius=0.04)
            badge_w = max(0.65, min(1.6, 0.55 + len(self.language) * 0.075))
            add_rect(
                slide,
                x + self.PAD,
                y + (self.HEADER_H - 0.18) / 2,
                badge_w,
                0.18,
                fill_rgb=t.ACCENT,
                radius=0.09,
            )
            add_text_box(
                slide,
                x + self.PAD,
                y + (self.HEADER_H - 0.18) / 2,
                badge_w,
                0.18,
                self.language,
                t.CAPTION,
                bold=True,
                color_rgb=(255, 255, 255),
                alignment=PP_ALIGN.CENTER,
                font_name="Consolas",
            )
            cursor_y = y + self.HEADER_H + self.PAD

        ln_w = 0.30 if self.show_line_numbers else 0.0
        ln_gap = 0.08 if self.show_line_numbers else 0.0
        code_x = x + self.PAD + ln_w + ln_gap
        code_w = max(0.1, width - self.PAD - (code_x - x))

        for i, line in enumerate(self._lines):
            if self.show_line_numbers:
                add_text_box(
                    slide,
                    x + self.PAD,
                    cursor_y,
                    ln_w,
                    self.LINE_H,
                    str(i + 1),
                    t.CAPTION,
                    color_rgb=t.TEXT_MUTED,
                    alignment=PP_ALIGN.RIGHT,
                    font_name="Consolas",
                    word_wrap=False,
                )
            add_text_box(
                slide,
                code_x,
                cursor_y,
                code_w,
                self.LINE_H,
                line,
                t.CAPTION,
                color_rgb=t.TEXT_SECONDARY,
                font_name="Consolas",
                word_wrap=False,
            )
            cursor_y += self.LINE_H
