from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Mapping


class Theme(ABC):
    # ── Typography scale (points) ──────────────────────────────────────────
    DISPLAY: int = 40
    HEADING: int = 28
    SUBHEADING: int = 20
    BODY: int = 14
    CAPTION: int = 11

    # ── Spacing constants (inches) ─────────────────────────────────────────
    XS: float = 0.1
    SM: float = 0.2
    MD: float = 0.3
    LG: float = 0.5
    XL: float = 0.8

    # ── Slide geometry (inches) ────────────────────────────────────────────
    SLIDE_W: float = 13.333
    SLIDE_H: float = 7.5
    MARGIN: float = 0.5

    # ── Surface colors — (R, G, B) tuples ─────────────────────────────────
    @property
    @abstractmethod
    def BG(self) -> tuple[int, int, int]: ...

    @property
    @abstractmethod
    def SURFACE(self) -> tuple[int, int, int]: ...

    @property
    @abstractmethod
    def SURFACE_ALT(self) -> tuple[int, int, int]: ...

    # ── Text colors ────────────────────────────────────────────────────────
    @property
    @abstractmethod
    def TEXT_PRIMARY(self) -> tuple[int, int, int]: ...

    @property
    @abstractmethod
    def TEXT_SECONDARY(self) -> tuple[int, int, int]: ...

    @property
    @abstractmethod
    def TEXT_MUTED(self) -> tuple[int, int, int]: ...

    # ── Accent colors ──────────────────────────────────────────────────────
    @property
    @abstractmethod
    def ACCENT(self) -> tuple[int, int, int]: ...

    @property
    @abstractmethod
    def ACCENT_SOFT(self) -> tuple[int, int, int]: ...

    # ── Semantic color pairs: {"style": (fill_rgb, text_rgb)} ─────────────
    @property
    @abstractmethod
    def CALLOUT(self) -> dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]]: ...

    # ── Delta / trend colors ───────────────────────────────────────────────
    @property
    @abstractmethod
    def POSITIVE(self) -> tuple[int, int, int]: ...

    @property
    @abstractmethod
    def NEGATIVE(self) -> tuple[int, int, int]: ...


class DarkTheme(Theme):
    """Slate-navy dark theme — executive dashboard aesthetic."""

    @property
    def BG(self): return (15, 23, 42)           # slate-950

    @property
    def SURFACE(self): return (30, 41, 59)       # slate-800

    @property
    def SURFACE_ALT(self): return (51, 65, 85)   # slate-700

    @property
    def TEXT_PRIMARY(self): return (248, 250, 252)   # slate-50

    @property
    def TEXT_SECONDARY(self): return (203, 213, 225) # slate-300

    @property
    def TEXT_MUTED(self): return (148, 163, 184)     # slate-400

    @property
    def ACCENT(self): return (59, 130, 246)          # blue-500

    @property
    def ACCENT_SOFT(self): return (37, 99, 235)      # blue-600

    @property
    def CALLOUT(self):
        return {
            "info":    ((37, 99, 235),   (248, 250, 252)),   # blue fill, white text
            "warning": ((180, 83, 9),    (255, 251, 235)),   # amber fill, cream text
            "success": ((21, 128, 61),   (240, 253, 244)),   # green fill, green-50 text
            "error":   ((185, 28, 28),   (255, 241, 242)),   # red fill, red-50 text
        }

    @property
    def POSITIVE(self): return (34, 197, 94)     # green-500

    @property
    def NEGATIVE(self): return (239, 68, 68)     # red-500


class LightTheme(Theme):
    """White/light-gray minimal theme — modern consulting aesthetic."""

    @property
    def BG(self): return (255, 255, 255)

    @property
    def SURFACE(self): return (248, 250, 252)    # slate-50

    @property
    def SURFACE_ALT(self): return (241, 245, 249) # slate-100

    @property
    def TEXT_PRIMARY(self): return (15, 23, 42)   # slate-950

    @property
    def TEXT_SECONDARY(self): return (51, 65, 85)  # slate-700

    @property
    def TEXT_MUTED(self): return (100, 116, 139)   # slate-500

    @property
    def ACCENT(self): return (37, 99, 235)          # blue-600

    @property
    def ACCENT_SOFT(self): return (147, 197, 253)   # blue-300

    @property
    def CALLOUT(self):
        return {
            "info":    ((219, 234, 254), (30, 64, 175)),   # blue-100 fill, blue-800 text
            "warning": ((254, 243, 199), (146, 64, 14)),   # amber-100 fill, amber-800 text
            "success": ((220, 252, 231), (22, 101, 52)),   # green-100 fill, green-800 text
            "error":   ((254, 226, 226), (153, 27, 27)),   # red-100 fill, red-800 text
        }

    @property
    def POSITIVE(self): return (22, 163, 74)     # green-600

    @property
    def NEGATIVE(self): return (220, 38, 38)     # red-600


class CorporateBlueTheme(Theme):
    """Conservative enterprise theme with cool blue accents."""

    @property
    def BG(self): return (238, 244, 252)

    @property
    def SURFACE(self): return (255, 255, 255)

    @property
    def SURFACE_ALT(self): return (226, 236, 248)

    @property
    def TEXT_PRIMARY(self): return (17, 38, 70)

    @property
    def TEXT_SECONDARY(self): return (42, 76, 123)

    @property
    def TEXT_MUTED(self): return (84, 114, 153)

    @property
    def ACCENT(self): return (24, 86, 187)

    @property
    def ACCENT_SOFT(self): return (116, 168, 241)

    @property
    def CALLOUT(self):
        return {
            "info": ((214, 232, 255), (19, 72, 157)),
            "warning": ((255, 238, 204), (128, 78, 15)),
            "success": ((220, 245, 232), (24, 110, 56)),
            "error": ((255, 228, 228), (150, 32, 32)),
        }

    @property
    def POSITIVE(self): return (34, 156, 93)

    @property
    def NEGATIVE(self): return (216, 66, 66)


class EditorialWarmTheme(Theme):
    """Warm editorial palette for narrative and strategy decks."""

    @property
    def BG(self): return (251, 247, 238)

    @property
    def SURFACE(self): return (255, 252, 246)

    @property
    def SURFACE_ALT(self): return (245, 235, 220)

    @property
    def TEXT_PRIMARY(self): return (49, 33, 21)

    @property
    def TEXT_SECONDARY(self): return (102, 70, 45)

    @property
    def TEXT_MUTED(self): return (142, 112, 87)

    @property
    def ACCENT(self): return (186, 104, 41)

    @property
    def ACCENT_SOFT(self): return (233, 170, 116)

    @property
    def CALLOUT(self):
        return {
            "info": ((237, 223, 207), (90, 60, 36)),
            "warning": ((255, 233, 194), (132, 78, 15)),
            "success": ((221, 240, 221), (36, 103, 52)),
            "error": ((252, 225, 218), (149, 42, 42)),
        }

    @property
    def POSITIVE(self): return (42, 138, 72)

    @property
    def NEGATIVE(self): return (200, 68, 64)


class HighContrastTheme(Theme):
    """Accessibility-first theme with strong contrast boundaries."""

    @property
    def BG(self): return (255, 255, 255)

    @property
    def SURFACE(self): return (245, 245, 245)

    @property
    def SURFACE_ALT(self): return (224, 224, 224)

    @property
    def TEXT_PRIMARY(self): return (0, 0, 0)

    @property
    def TEXT_SECONDARY(self): return (33, 33, 33)

    @property
    def TEXT_MUTED(self): return (70, 70, 70)

    @property
    def ACCENT(self): return (0, 92, 197)

    @property
    def ACCENT_SOFT(self): return (122, 176, 244)

    @property
    def CALLOUT(self):
        return {
            "info": ((222, 236, 255), (0, 57, 128)),
            "warning": ((255, 236, 204), (102, 61, 0)),
            "success": ((215, 242, 215), (15, 84, 35)),
            "error": ((255, 224, 224), (120, 20, 20)),
        }

    @property
    def POSITIVE(self): return (20, 120, 55)

    @property
    def NEGATIVE(self): return (185, 32, 32)


class BrandTheme(Theme):
    """Parameterized brand theme for custom accent-driven palettes."""

    def __init__(
        self,
        *,
        bg: tuple[int, int, int] = (249, 250, 252),
        surface: tuple[int, int, int] = (255, 255, 255),
        surface_alt: tuple[int, int, int] = (234, 238, 245),
        text_primary: tuple[int, int, int] = (21, 31, 52),
        text_secondary: tuple[int, int, int] = (57, 76, 111),
        text_muted: tuple[int, int, int] = (96, 118, 150),
        accent: tuple[int, int, int] = (12, 119, 170),
        accent_soft: tuple[int, int, int] = (133, 201, 232),
        positive: tuple[int, int, int] = (27, 140, 79),
        negative: tuple[int, int, int] = (210, 66, 66),
        callout: dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]] | None = None,
    ):
        self._bg = bg
        self._surface = surface
        self._surface_alt = surface_alt
        self._text_primary = text_primary
        self._text_secondary = text_secondary
        self._text_muted = text_muted
        self._accent = accent
        self._accent_soft = accent_soft
        self._positive = positive
        self._negative = negative
        self._callout = callout or {
            "info": ((221, 241, 250), (24, 84, 115)),
            "warning": ((255, 237, 204), (122, 77, 20)),
            "success": ((221, 244, 230), (26, 105, 56)),
            "error": ((252, 226, 226), (140, 33, 33)),
        }

    @property
    def BG(self): return self._bg

    @property
    def SURFACE(self): return self._surface

    @property
    def SURFACE_ALT(self): return self._surface_alt

    @property
    def TEXT_PRIMARY(self): return self._text_primary

    @property
    def TEXT_SECONDARY(self): return self._text_secondary

    @property
    def TEXT_MUTED(self): return self._text_muted

    @property
    def ACCENT(self): return self._accent

    @property
    def ACCENT_SOFT(self): return self._accent_soft

    @property
    def CALLOUT(self): return self._callout

    @property
    def POSITIVE(self): return self._positive

    @property
    def NEGATIVE(self): return self._negative


ThemePatch = dict[str, object]

PATCHABLE_THEME_KEYS = {
    "DISPLAY", "HEADING", "SUBHEADING", "BODY", "CAPTION",
    "XS", "SM", "MD", "LG", "XL",
    "SLIDE_W", "SLIDE_H", "MARGIN",
    "BG", "SURFACE", "SURFACE_ALT",
    "TEXT_PRIMARY", "TEXT_SECONDARY", "TEXT_MUTED",
    "ACCENT", "ACCENT_SOFT", "CALLOUT", "POSITIVE", "NEGATIVE",
}


class PatchedTheme(Theme):
    """Theme wrapper that applies token-level overrides on top of a base theme."""

    def __init__(self, base: Theme, patch: Mapping[str, object]):
        unknown = [k for k in patch if k not in PATCHABLE_THEME_KEYS]
        if unknown:
            raise ValueError(f"Unknown theme patch key(s): {', '.join(sorted(unknown))}")

        self._base = base
        self._patch = dict(patch)

        # CALLOUT supports partial patching per style (info/warning/success/error).
        if isinstance(self._patch.get("CALLOUT"), dict):
            merged = dict(base.CALLOUT)
            merged.update(self._patch["CALLOUT"])
            self._patch["CALLOUT"] = merged

    def _value(self, key: str):
        return self._patch.get(key, getattr(self._base, key))

    @property
    def DISPLAY(self): return self._value("DISPLAY")

    @property
    def HEADING(self): return self._value("HEADING")

    @property
    def SUBHEADING(self): return self._value("SUBHEADING")

    @property
    def BODY(self): return self._value("BODY")

    @property
    def CAPTION(self): return self._value("CAPTION")

    @property
    def XS(self): return self._value("XS")

    @property
    def SM(self): return self._value("SM")

    @property
    def MD(self): return self._value("MD")

    @property
    def LG(self): return self._value("LG")

    @property
    def XL(self): return self._value("XL")

    @property
    def SLIDE_W(self): return self._value("SLIDE_W")

    @property
    def SLIDE_H(self): return self._value("SLIDE_H")

    @property
    def MARGIN(self): return self._value("MARGIN")

    @property
    def BG(self): return self._value("BG")

    @property
    def SURFACE(self): return self._value("SURFACE")

    @property
    def SURFACE_ALT(self): return self._value("SURFACE_ALT")

    @property
    def TEXT_PRIMARY(self): return self._value("TEXT_PRIMARY")

    @property
    def TEXT_SECONDARY(self): return self._value("TEXT_SECONDARY")

    @property
    def TEXT_MUTED(self): return self._value("TEXT_MUTED")

    @property
    def ACCENT(self): return self._value("ACCENT")

    @property
    def ACCENT_SOFT(self): return self._value("ACCENT_SOFT")

    @property
    def CALLOUT(self): return self._value("CALLOUT")

    @property
    def POSITIVE(self): return self._value("POSITIVE")

    @property
    def NEGATIVE(self): return self._value("NEGATIVE")


def apply_theme_patch(base: Theme, patch: Mapping[str, object] | None = None) -> Theme:
    """Return `base` when patch is empty, else a PatchedTheme wrapper."""
    if not patch:
        return base
    return PatchedTheme(base, patch)


# ── Global theme registry ──────────────────────────────────────────────────

_active_theme: Theme = DarkTheme()


def set_theme(theme: Theme) -> None:
    """Set the active global theme.

    Warning: not safe for concurrent use. For concurrent/async contexts, pass theme=
    explicitly to SlideBuilder and component render() calls instead of using the global.
    """
    global _active_theme
    _active_theme = theme


def get_theme() -> Theme:
    return _active_theme
