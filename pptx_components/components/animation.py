"""Animation and transition effects for pptx_components.

Note: python-pptx does not natively support slide animations/transitions.
This module provides helper functions to simulate animation effects by:
    1. Creating duplicate shapes with staged opacity/positioning
    2. Providing preset animations (fade, slide, grow)
    3. Enabling manual multi-frame rendering for slide-show animation

For true PowerPoint animations, use the PowerPoint GUI or python-pptx-animators package.
This module is useful for procedural effect generation, testing, and visual effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


@dataclass
class AnimationConfig:
    """Configuration for an animation effect.

    Attributes:
        duration_ms: Total animation duration in milliseconds.
        frames: Number of keyframes to generate (for multi-frame export).
        easing: Easing function name ("linear", "ease_in", "ease_out", "ease_in_out").
    """

    duration_ms: int = 500
    frames: int = 10
    easing: str = "ease_in_out"

    def __post_init__(self) -> None:
        if self.duration_ms <= 0:
            raise ValueError("duration_ms must be > 0")
        if self.frames < 2:
            raise ValueError("frames must be >= 2")
        # Validate easing early so invalid configs fail fast.
        get_easer(self.easing)


def _validate_frame_index(frame: int, total_frames: int) -> int:
    """Validate a zero-based frame index against a known frame count."""
    if frame < 0 or frame >= total_frames:
        raise ValueError(f"frame must be in [0, {total_frames - 1}]; got {frame}")
    return frame


def ease_linear(t: float) -> float:
    """Linear easing: t ∈ [0, 1]."""
    return t


def ease_in(t: float) -> float:
    """Quadratic ease-in."""
    return t * t


def ease_out(t: float) -> float:
    """Quadratic ease-out."""
    return 1.0 - (1.0 - t) ** 2


def ease_in_out(t: float) -> float:
    """Quadratic ease-in-out."""
    if t < 0.5:
        return 2 * t * t
    return 1.0 - 2 * (1.0 - t) ** 2


def get_easer(easing: str) -> Callable[[float], float]:
    """Get easing function by name."""
    easers = {
        "linear": ease_linear,
        "ease_in": ease_in,
        "ease_out": ease_out,
        "ease_in_out": ease_in_out,
    }
    if easing not in easers:
        raise ValueError(f"unknown easing: {easing!r}")
    return easers[easing]


class FadeInEffect(Component):
    """Fade-in animation overlay (opacity ramp from 0 to 1).

    Renders the underlying component with opacity starting at 0 and ending at 1.
    In static PowerPoint, this renders at full opacity. For animation, use the
    config.frames property to generate keyframe layers for slide-show export.

    Args:
        child: Component to fade in.
        config: AnimationConfig with duration and easing settings.

    Example:
        >>> fade = FadeInEffect(
        ...     SectionHeader("Welcome", badge_text="Intro"),
        ...     AnimationConfig(duration_ms=1000, frames=20, easing="ease_out")
        ... )
        >>> builder.add(fade, w=8, h=0.5)
    """

    def __init__(self, child: Component, config: AnimationConfig | None = None):
        self.child = child
        self.config = config or AnimationConfig()

    @property
    def min_height(self) -> float:
        return self.child.min_height

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        # In static rendering, we render at full opacity (end state)
        # For animation, the containing system would call render_frame() repeatedly
        self.child.render(slide, x, y, width, height, theme)

    def render_frame(
        self, slide, x: float, y: float, width: float, height: float,
        frame: int, theme: Theme | None = None
    ) -> None:
        """Render a specific animation frame (0 to config.frames-1).

        Args:
            frame: Frame index, 0 to config.frames-1.
        """
        _validate_frame_index(frame, self.config.frames)
        # Note: python-pptx doesn't directly support opacity changes via API.
        # This is a placeholder for future animation systems.
        # For now, render the child as-is (end state).
        self.child.render(slide, x, y, width, height, theme)


class SlideInEffect(Component):
    """Slide-in animation from edge (position translation).

    Animates component from off-screen into final position.

    Args:
        child: Component to slide in.
        direction: "left", "right", "top", or "bottom".
        config: AnimationConfig with duration and easing settings.

    Example:
        >>> slide_in = SlideInEffect(
        ...     MetricCard("Revenue", "$5.2M", "+12%", True),
        ...     direction="left",
        ...     config=AnimationConfig(duration_ms=800, easing="ease_out")
        ... )
    """

    def __init__(
        self,
        child: Component,
        direction: str = "left",
        config: AnimationConfig | None = None,
    ):
        if direction not in ("left", "right", "top", "bottom"):
            raise ValueError(f"direction must be one of left/right/top/bottom; got {direction!r}")
        self.child = child
        self.direction = direction
        self.config = config or AnimationConfig()

    @property
    def min_height(self) -> float:
        return self.child.min_height

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        # Static render: show at final position
        self.child.render(slide, x, y, width, height, theme)

    def render_frame(
        self, slide, x: float, y: float, width: float, height: float,
        frame: int, theme: Theme | None = None
    ) -> None:
        """Render animation frame with position translation."""
        _validate_frame_index(frame, self.config.frames)
        easer = get_easer(self.config.easing)
        progress = easer(frame / (self.config.frames - 1))

        # Calculate offset
        offset_units = 2.0  # Offscreen distance
        offset = offset_units * (1.0 - progress)

        if self.direction == "left":
            render_x = x - offset
            render_y = y
        elif self.direction == "right":
            render_x = x + offset
            render_y = y
        elif self.direction == "top":
            render_x = x
            render_y = y - offset
        else:  # bottom
            render_x = x
            render_y = y + offset

        self.child.render(slide, render_x, render_y, width, height, theme)


class GrowEffect(Component):
    """Scale-up animation (size expansion from 0 to full).

    Animates component from small/center-point to full size.

    Args:
        child: Component to grow.
        config: AnimationConfig with duration and easing settings.

    Example:
        >>> grow = GrowEffect(
        ...     BarChart(
        ...         ["Jan", "Feb", "Mar"],
        ...         [[10, 12, 15]],
        ...         title="Revenue Trend"
        ...     ),
        ...     config=AnimationConfig(duration_ms=1200, easing="ease_out")
        ... )
    """

    def __init__(self, child: Component, config: AnimationConfig | None = None):
        self.child = child
        self.config = config or AnimationConfig()

    @property
    def min_height(self) -> float:
        return self.child.min_height

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        # Static render: show at full size
        self.child.render(slide, x, y, width, height, theme)

    def render_frame(
        self, slide, x: float, y: float, width: float, height: float,
        frame: int, theme: Theme | None = None
    ) -> None:
        """Render animation frame with scaling effect."""
        _validate_frame_index(frame, self.config.frames)
        easer = get_easer(self.config.easing)
        scale = easer(frame / (self.config.frames - 1))

        # Calculate scaled position (grow from center)
        center_x = x + width / 2
        center_y = y + height / 2
        scaled_w = width * scale
        scaled_h = height * scale
        scaled_x = center_x - scaled_w / 2
        scaled_y = center_y - scaled_h / 2

        self.child.render(slide, scaled_x, scaled_y, scaled_w, scaled_h, theme)


class SequenceAnimation(Component):
    """Play multiple animations in sequence.

    Args:
        animations: List of (Component, delay_ms) tuples.
        config: Overall animation duration settings.

    Example:
        >>> seq = SequenceAnimation(
        ...     [
        ...         (FadeInEffect(title), 0),
        ...         (SlideInEffect(chart, "left"), 300),
        ...         (SlideInEffect(legend, "right"), 300),
        ...     ]
        ... )
    """

    def __init__(
        self,
        animations: list[tuple[Component, int]],
        config: AnimationConfig | None = None,
    ):
        if not animations:
            raise ValueError("animations list must not be empty")
        self.animations = animations
        self.config = config or AnimationConfig()

        # Calculate total duration to cover all animations
        max_delay = max((delay for _, delay in animations), default=0)
        self.config.duration_ms = max(self.config.duration_ms, max_delay + 500)

    @property
    def min_height(self) -> float:
        # Return max height among children (they're stacked or overlaid)
        return max((comp.min_height for comp, _ in self.animations), default=1.0)

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        # Static render: show all components
        for comp, _ in self.animations:
            comp.render(slide, x, y, width, height, theme)

    def render_frame(
        self, slide, x: float, y: float, width: float, height: float,
        frame: int, theme: Theme | None = None
    ) -> None:
        """Render animation frame for sequence."""
        _validate_frame_index(frame, self.config.frames)
        # Convert frame to milliseconds
        time_ms = (frame / (self.config.frames - 1)) * self.config.duration_ms

        for comp, delay_ms in self.animations:
            if time_ms >= delay_ms:
                # Component's animation starts at delay_ms
                render_frame_fn = getattr(comp, "render_frame", None)
                if callable(render_frame_fn):
                    local_time = max(0.0, time_ms - delay_ms)
                    comp_cfg = getattr(comp, "config", None)
                    comp_duration_ms = getattr(comp_cfg, "duration_ms", self.config.duration_ms)
                    comp_frames = getattr(comp_cfg, "frames", self.config.frames)

                    if comp_duration_ms <= 0:
                        comp_duration_ms = self.config.duration_ms
                    if comp_frames < 2:
                        comp_frames = self.config.frames

                    local_progress = min(1.0, local_time / comp_duration_ms)
                    local_frame = int(local_progress * (comp_frames - 1))
                    _validate_frame_index(local_frame, comp_frames)
                    render_frame_fn(slide, x, y, width, height, local_frame, theme)
                else:
                    comp.render(slide, x, y, width, height, theme)
