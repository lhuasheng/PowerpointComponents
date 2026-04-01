from __future__ import annotations

import re

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box, set_slide_background
from pptx_components.theme import Theme


def _split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    if len(paragraph) <= max_chars:
        return [paragraph]

    # Prefer sentence boundaries, then fall back to words.
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", paragraph) if s.strip()]
    if len(sentences) <= 1:
        words = paragraph.split()
        chunks: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = word
            else:
                current = candidate
        if current:
            chunks.append(current)
        return chunks

    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def paginate_narrative(
    text: str,
    max_chars_per_page: int = 700,
    max_paragraphs_per_page: int = 3,
) -> list[str]:
    """Split long narrative text into slide-friendly pages.

    Paragraphs are preserved when possible and oversized paragraphs are
    sentence-split before word-level fallback.
    """
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return [""]

    raw_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", normalized) if p.strip()]
    paragraphs: list[str] = []
    for para in raw_paragraphs:
        paragraphs.extend(_split_long_paragraph(para, max_chars=max_chars_per_page))

    pages: list[str] = []
    current: list[str] = []
    current_chars = 0

    for para in paragraphs:
        para_len = len(para)
        would_exceed_chars = current and (current_chars + para_len + 2 > max_chars_per_page)
        would_exceed_paras = current and (len(current) >= max_paragraphs_per_page)

        if would_exceed_chars or would_exceed_paras:
            pages.append("\n\n".join(current))
            current = [para]
            current_chars = para_len
        else:
            current.append(para)
            current_chars += para_len + (2 if len(current) > 1 else 0)

    if current:
        pages.append("\n\n".join(current))
    return pages


class NarrativePage(Component):
    """Framed long-form narrative panel with page metadata and key takeaways."""

    def __init__(
        self,
        title: str,
        body: str,
        summary: str | None = None,
        key_points: list[str] | None = None,
        page: int = 1,
        total_pages: int = 1,
    ):
        self.title = title
        self.body = body
        self.summary = summary
        self.key_points = key_points or []
        self.page = page
        self.total_pages = max(1, total_pages)

    @property
    def min_height(self) -> float:
        return 2.8 if self.key_points else 2.3

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

        add_rect(slide, x, y, width, height, fill_rgb=t.SURFACE, radius=0.05)
        add_rect(slide, x, y, width, 0.05, fill_rgb=t.ACCENT)

        page_w = 1.0
        add_text_box(
            slide,
            x + width - page_w - pad,
            y + pad,
            page_w,
            0.25,
            f"Page {self.page}/{self.total_pages}",
            t.CAPTION,
            bold=True,
            color_rgb=t.TEXT_MUTED,
            alignment=PP_ALIGN.RIGHT,
            font_name="Calibri",
        )

        title_w = width - page_w - 2 * pad
        add_text_box(
            slide,
            x + pad,
            y + pad,
            max(0.5, title_w),
            0.35,
            self.title,
            t.SUBHEADING,
            bold=True,
            color_rgb=t.TEXT_PRIMARY,
            font_name="Calibri Light",
        )

        cursor_y = y + pad + 0.35
        if self.summary:
            add_text_box(
                slide,
                x + pad,
                cursor_y,
                width - 2 * pad,
                0.28,
                self.summary,
                t.CAPTION,
                color_rgb=t.TEXT_MUTED,
                font_name="Calibri",
            )
            cursor_y += 0.32

        takeaway_h = 0.0
        if self.key_points:
            takeaway_h = 0.55

        body_h = max(0.4, (y + height - pad - takeaway_h) - cursor_y)
        add_text_box(
            slide,
            x + pad,
            cursor_y,
            width - 2 * pad,
            body_h,
            self.body,
            t.BODY,
            color_rgb=t.TEXT_SECONDARY,
            font_name="Calibri",
            word_wrap=True,
        )

        if self.key_points:
            strip_y = y + height - pad - takeaway_h
            add_rect(
                slide,
                x + pad,
                strip_y,
                width - 2 * pad,
                takeaway_h,
                fill_rgb=t.SURFACE_ALT,
                radius=0.04,
            )
            points = "  |  ".join(f"- {p}" for p in self.key_points[:3])
            add_text_box(
                slide,
                x + pad + 0.12,
                strip_y + 0.06,
                width - 2 * pad - 0.24,
                takeaway_h - 0.12,
                points,
                t.CAPTION,
                bold=True,
                color_rgb=t.TEXT_PRIMARY,
                font_name="Calibri",
                word_wrap=True,
            )


class NarrativeTwoColumnPage(Component):
    """Long-form narrative layout with a right-side evidence or takeaway rail."""

    def __init__(
        self,
        title: str,
        body: str,
        sidebar_title: str = "Key Points",
        sidebar_points: list[str] | None = None,
        sidebar_note: str | None = None,
        summary: str | None = None,
        page: int = 1,
        total_pages: int = 1,
    ):
        self.title = title
        self.body = body
        self.sidebar_title = sidebar_title
        self.sidebar_points = sidebar_points or []
        self.sidebar_note = sidebar_note
        self.summary = summary
        self.page = page
        self.total_pages = max(1, total_pages)

    @property
    def min_height(self) -> float:
        return 2.6

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

        add_rect(slide, x, y, width, height, fill_rgb=t.SURFACE, radius=0.05)
        add_rect(slide, x, y, width, 0.05, fill_rgb=t.ACCENT)

        page_w = 1.0
        add_text_box(
            slide,
            x + width - page_w - pad,
            y + pad,
            page_w,
            0.25,
            f"Page {self.page}/{self.total_pages}",
            t.CAPTION,
            bold=True,
            color_rgb=t.TEXT_MUTED,
            alignment=PP_ALIGN.RIGHT,
            font_name="Calibri",
        )

        title_w = width - page_w - 2 * pad
        add_text_box(
            slide,
            x + pad,
            y + pad,
            max(0.5, title_w),
            0.35,
            self.title,
            t.SUBHEADING,
            bold=True,
            color_rgb=t.TEXT_PRIMARY,
            font_name="Calibri Light",
        )

        cursor_y = y + pad + 0.35
        if self.summary:
            add_text_box(
                slide,
                x + pad,
                cursor_y,
                width - 2 * pad,
                0.28,
                self.summary,
                t.CAPTION,
                color_rgb=t.TEXT_MUTED,
                font_name="Calibri",
            )
            cursor_y += 0.32

        content_h = y + height - pad - cursor_y
        left_w = width * 0.68
        right_w = width - left_w - pad

        add_rect(
            slide,
            x + pad,
            cursor_y,
            left_w - pad,
            content_h,
            fill_rgb=t.BG,
            radius=0.03,
        )
        add_text_box(
            slide,
            x + pad + 0.14,
            cursor_y + 0.12,
            left_w - pad - 0.28,
            content_h - 0.24,
            self.body,
            t.BODY,
            color_rgb=t.TEXT_SECONDARY,
            font_name="Calibri",
            word_wrap=True,
        )

        rail_x = x + left_w + 0.02
        add_rect(
            slide,
            rail_x,
            cursor_y,
            right_w - pad,
            content_h,
            fill_rgb=t.SURFACE_ALT,
            radius=0.03,
        )
        add_text_box(
            slide,
            rail_x + 0.12,
            cursor_y + 0.1,
            right_w - pad - 0.24,
            0.25,
            self.sidebar_title,
            t.CAPTION,
            bold=True,
            color_rgb=t.TEXT_PRIMARY,
            font_name="Calibri",
        )

        if self.sidebar_points:
            points_text = "\n".join(f"- {p}" for p in self.sidebar_points[:6])
            add_text_box(
                slide,
                rail_x + 0.12,
                cursor_y + 0.34,
                right_w - pad - 0.24,
                content_h * 0.66,
                points_text,
                t.CAPTION,
                color_rgb=t.TEXT_SECONDARY,
                font_name="Calibri",
                word_wrap=True,
            )

        if self.sidebar_note:
            add_text_box(
                slide,
                rail_x + 0.12,
                cursor_y + content_h - 0.7,
                right_w - pad - 0.24,
                0.58,
                self.sidebar_note,
                t.CAPTION,
                bold=True,
                color_rgb=t.ACCENT,
                font_name="Calibri",
                word_wrap=True,
            )


class LongNarrativeBlock(Component):
    """Auto-paginated narrative component for long-form slide storytelling.

    Use `paginate_narrative(...)` if you want to pre-generate all pages, or pass
    `page` to render one page at a time.
    """

    def __init__(
        self,
        title: str,
        text: str,
        page: int = 1,
        summary: str | None = None,
        key_points: list[str] | None = None,
        max_chars_per_page: int = 700,
        max_paragraphs_per_page: int = 3,
    ):
        self.title = title
        self.summary = summary
        self.key_points = key_points or []
        self.pages = paginate_narrative(
            text,
            max_chars_per_page=max_chars_per_page,
            max_paragraphs_per_page=max_paragraphs_per_page,
        )
        if page < 1 or page > len(self.pages):
            raise ValueError(f"page must be in [1, {len(self.pages)}]")
        self.page = page

    @property
    def total_pages(self) -> int:
        return len(self.pages)

    @property
    def min_height(self) -> float:
        return 2.8 if self.key_points else 2.3

    def render(
        self,
        slide,
        x: float,
        y: float,
        width: float,
        height: float,
        theme: Theme | None = None,
    ) -> None:
        content = self.pages[self.page - 1]
        if self.page < self.total_pages:
            content = f"{content}\n\n(continued on next slide)"

        NarrativePage(
            title=self.title,
            body=content,
            summary=self.summary,
            key_points=self.key_points,
            page=self.page,
            total_pages=self.total_pages,
        ).render(slide, x, y, width, height, theme=theme)


def build_narrative_slides(
    prs,
    title: str,
    text: str,
    summary: str | None = None,
    key_points: list[str] | None = None,
    sidebar_title: str | None = None,
    sidebar_points: list[str] | None = None,
    sidebar_note: str | None = None,
    max_chars_per_page: int = 700,
    max_paragraphs_per_page: int = 3,
    theme: Theme | None = None,
) -> list:
    """Generate one slide per narrative page and return created slide objects."""
    t = _resolve(theme)
    pages = paginate_narrative(
        text,
        max_chars_per_page=max_chars_per_page,
        max_paragraphs_per_page=max_paragraphs_per_page,
    )

    created = []
    for idx, body in enumerate(pages, start=1):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        set_slide_background(slide, t.BG)

        if idx < len(pages):
            body = f"{body}\n\n(continued on next slide)"

        if sidebar_title or sidebar_points or sidebar_note:
            component = NarrativeTwoColumnPage(
                title=title,
                body=body,
                sidebar_title=sidebar_title or "Key Points",
                sidebar_points=sidebar_points,
                sidebar_note=sidebar_note,
                summary=summary,
                page=idx,
                total_pages=len(pages),
            )
        else:
            component = NarrativePage(
                title=title,
                body=body,
                summary=summary,
                key_points=key_points,
                page=idx,
                total_pages=len(pages),
            )

        component.render(
            slide,
            x=t.MARGIN,
            y=t.MARGIN,
            width=t.SLIDE_W - 2 * t.MARGIN,
            height=t.SLIDE_H - 2 * t.MARGIN,
            theme=t,
        )
        created.append(slide)

    return created