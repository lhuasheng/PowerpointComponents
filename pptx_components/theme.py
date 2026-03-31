from __future__ import annotations
from abc import ABC, abstractmethod


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


# ── Global theme registry ──────────────────────────────────────────────────

_active_theme: Theme = DarkTheme()


def set_theme(theme: Theme) -> None:
    global _active_theme
    _active_theme = theme


def get_theme() -> Theme:
    return _active_theme
