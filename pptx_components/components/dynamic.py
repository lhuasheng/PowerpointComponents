from __future__ import annotations

import json
from dataclasses import dataclass, field

from pptx_components.base import Component, _resolve
from pptx_components.theme import Theme


@dataclass
class ComponentSpec:
    """Declarative specification for a single rendered component."""
    type: str
    props: dict = field(default_factory=dict)
    height: float | None = None


COMPONENT_REGISTRY: dict[str, type[Component]] = {}


def register_component(name: str, cls: type[Component]) -> None:
    """Add a component class to the registry under ``name``."""
    COMPONENT_REGISTRY[name] = cls


def render_specs(
    slide,
    specs: list[ComponentSpec],
    x: float,
    y: float,
    width: float,
    height: float,
    theme: Theme | None = None,
    gap: float = 0.1,
) -> None:
    """Render a list of ComponentSpec objects stacked vertically.

    Components are laid out from top to bottom.  If a spec supplies an explicit
    ``height`` it is used (subject to component.min_height); otherwise
    ``component.min_height`` is used.  Rendering stops when the available height
    is exhausted.
    """
    cursor_y = y
    remaining = height

    for spec in specs:
        if remaining <= 0:
            break

        cls = COMPONENT_REGISTRY.get(spec.type)
        if cls is None:
            continue

        try:
            component = cls(**spec.props)
        except Exception:
            continue

        if spec.height is not None:
            comp_h = max(spec.height, component.min_height)
        else:
            comp_h = component.min_height

        comp_h = min(comp_h, remaining)
        if comp_h <= 0:
            continue

        try:
            component.render(slide, x, cursor_y, width, comp_h, theme)
        except Exception:
            pass

        cursor_y += comp_h + gap
        remaining -= comp_h + gap


# ── Component schema (used as context for the AI) ─────────────────────────────
# Each entry describes the constructor signature that must be satisfied.
# Keep prop descriptions concise; the AI parses this at call time.

COMPONENT_SCHEMA: dict[str, dict] = {
    "TitleBlock": {
        "description": "Large slide title with optional subtitle. Use for the main heading of a slide.",
        "typical_height": 1.2,
        "props": {
            "title": {"type": "str", "required": True, "description": "Primary heading text"},
            "subtitle": {"type": "str | null", "required": False, "description": "Secondary line below title"},
        },
    },
    "SectionHeader": {
        "description": "Section divider with a prominent label. Use between major slide sections.",
        "typical_height": 0.8,
        "props": {
            "title": {"type": "str", "required": True},
            "subtitle": {"type": "str | null", "required": False},
        },
    },
    "TextCard": {
        "description": "Narrative text panel with optional title and accent bar. Good for explanatory copy.",
        "typical_height": 1.5,
        "props": {
            "body": {"type": "str", "required": True, "description": "Main body text"},
            "title": {"type": "str | null", "required": False},
            "style": {"type": "str", "required": False, "default": "default",
                      "description": "\"default\" | \"muted\" | \"accent\""},
        },
    },
    "CalloutBox": {
        "description": "Highlighted callout panel for important notes, warnings, or statuses.",
        "typical_height": 0.8,
        "props": {
            "text": {"type": "str", "required": True},
            "style": {"type": "str", "required": False, "default": "info",
                      "description": "\"info\" | \"warning\" | \"success\" | \"error\""},
        },
    },
    "QuoteBlock": {
        "description": "Styled pull-quote with optional attribution.",
        "typical_height": 1.2,
        "props": {
            "text": {"type": "str", "required": True},
            "author": {"type": "str | null", "required": False},
        },
    },
    "MetricCard": {
        "description": "Single KPI card showing a label, a large value, and an optional delta.",
        "typical_height": 1.0,
        "props": {
            "label": {"type": "str", "required": True},
            "value": {"type": "str", "required": True, "description": "Display value, e.g. \"$2.1M\" or \"94%\""},
            "delta": {"type": "str | null", "required": False, "description": "Change indicator, e.g. \"+12%\""},
            "delta_positive": {"type": "bool | null", "required": False, "description": "True=green, False=red, null=neutral"},
        },
    },
    "KPIGrid": {
        "description": "Grid of KPI cards. Each metric is a 4-element list [label, value, delta, delta_positive].",
        "typical_height": 1.5,
        "props": {
            "metrics": {
                "type": "list[list]",
                "required": True,
                "description": "List of [label: str, value: str, delta: str|null, delta_positive: bool|null]",
            },
            "cols": {"type": "int", "required": False, "default": 3},
        },
    },
    "BarChart": {
        "description": "Vertical bar chart. Use for comparing values across categories.",
        "typical_height": 3.0,
        "props": {
            "categories": {"type": "list[str]", "required": True, "description": "X-axis labels"},
            "series": {"type": "dict[str, list[float]]", "required": True,
                       "description": "Mapping of series name to list of values, one per category"},
            "title": {"type": "str | null", "required": False},
        },
    },
    "LineChart": {
        "description": "Line chart. Use for trends over time.",
        "typical_height": 3.0,
        "props": {
            "categories": {"type": "list[str]", "required": True},
            "series": {"type": "dict[str, list[float]]", "required": True,
                       "description": "Mapping of series name to list of values"},
            "title": {"type": "str | null", "required": False},
        },
    },
    "PieChart": {
        "description": "Pie chart. Use for showing proportional composition (up to ~6 slices).",
        "typical_height": 3.0,
        "props": {
            "categories": {"type": "list[str]", "required": True, "description": "Slice labels"},
            "values": {"type": "list[float]", "required": True},
            "title": {"type": "str | null", "required": False},
        },
    },
    "DonutChart": {
        "description": "Donut chart with optional center label. Good for showing a dominant metric.",
        "typical_height": 3.0,
        "props": {
            "categories": {"type": "list[str]", "required": True},
            "values": {"type": "list[float]", "required": True},
            "center_label": {"type": "str | null", "required": False},
            "title": {"type": "str | null", "required": False},
        },
    },
    "ListBlock": {
        "description": "Bulleted or numbered list of items.",
        "typical_height": 1.5,
        "props": {
            "items": {"type": "list[str]", "required": True},
            "style": {"type": "str", "required": False, "default": "bullet",
                      "description": "\"bullet\" | \"numbered\" | \"check\""},
            "title": {"type": "str | null", "required": False},
        },
    },
    "ProgressBar": {
        "description": "Single labelled progress bar showing a value against a max.",
        "typical_height": 0.5,
        "props": {
            "label": {"type": "str", "required": True},
            "value": {"type": "float", "required": True},
            "max_value": {"type": "float", "required": False, "default": 100},
            "show_pct": {"type": "bool", "required": False, "default": True},
        },
    },
    "StepFlow": {
        "description": "Horizontal stepper showing a sequence of steps with a current active step.",
        "typical_height": 1.2,
        "props": {
            "steps": {"type": "list[str]", "required": True},
            "current": {"type": "int", "required": False, "default": 0,
                        "description": "0-based index of the active step"},
            "title": {"type": "str | null", "required": False},
        },
    },
    "FeatureGrid": {
        "description": "Grid of feature cards with icon, title, and description. Each feature is a 3-element list.",
        "typical_height": 2.5,
        "props": {
            "features": {
                "type": "list[list[str]]",
                "required": True,
                "description": "List of [icon_char: str, title: str, description: str] — use a single emoji or letter for icon",
            },
            "columns": {"type": "int", "required": False, "default": 3},
            "title": {"type": "str | null", "required": False},
        },
    },
    "FlowchartDiagram": {
        "description": "Top-down flowchart with auto-layout. Nodes can be process, decision, terminal, or data types.",
        "typical_height": 4.0,
        "props": {
            "nodes": {
                "type": "list[dict]",
                "required": True,
                "description": "List of {\"id\": str, \"label\": str, \"type\": \"process\"|\"decision\"|\"terminal\"|\"data\"}",
            },
            "edges": {
                "type": "list[dict]",
                "required": True,
                "description": "List of {\"from\": str, \"to\": str, \"label\": str (optional)}",
            },
        },
    },
    "DataTable": {
        "description": "Tabular data with header row and striped body rows.",
        "typical_height": 2.5,
        "props": {
            "headers": {"type": "list[str]", "required": True},
            "rows": {"type": "list[list]", "required": True,
                     "description": "Each row is a list of values (str or number)"},
            "title": {"type": "str | null", "required": False},
        },
    },
}

_COMPONENT_SCHEMA_JSON = json.dumps(COMPONENT_SCHEMA, indent=2)


_INSTRUCTION_TEXT = """\
You are a PowerPoint slide layout engine. Given a content brief, you select the \
best components from the available schema and return a JSON array of component \
specifications that will fill the slide.

## Rules
1. Return ONLY a valid JSON array — no prose, no markdown fences, no explanation.
2. Each element: {"type": "<ComponentName>", "props": {...}, "height": <float>}
3. "type" must exactly match a key in the component schema.
4. "props" must satisfy the schema: all required props present, types correct.
5. Heights are in inches. The slide height budget is given in the user message; \
   keep the sum of heights + 0.1 gaps below that budget.
6. KPIGrid "metrics" is a list of lists: [[label, value, delta, delta_positive], ...] \
   where delta and delta_positive may be null.
7. FeatureGrid "features" is a list of lists: [[icon_char, title, description], ...].
8. Choose visualizations that best represent the content: use charts for numbers, \
   lists for bullet points, flowcharts for processes, KPI grids for multiple metrics.
9. Always start with a TitleBlock if the content has a clear headline.
10. Do not exceed 4–5 components per slide for readability.
"""


def generate_slide(
    content: str,
    slide,
    model: str = "claude-opus-4-7",
    x: float = 0.5,
    y: float = 0.5,
    width: float = 12.33,
    height: float = 6.5,
    theme: Theme | None = None,
    api_key: str | None = None,
) -> list[ComponentSpec]:
    """Design and render a slide from natural language content using Claude.

    Sends ``content`` to Claude along with the component schema.  Claude picks
    the appropriate components and returns a JSON array of specs, which are then
    rendered onto ``slide`` via :func:`render_specs`.

    Args:
        content: Natural language description of the slide content.
        slide: A python-pptx slide object to render onto.
        model: Anthropic model ID to use.
        x: Left edge of the render area (inches).
        y: Top edge of the render area (inches).
        width: Width of the render area (inches).
        height: Height budget (inches).
        theme: Optional theme override.
        api_key: Anthropic API key.  Defaults to the ``ANTHROPIC_API_KEY``
            environment variable.

    Returns:
        The list of :class:`ComponentSpec` objects that were rendered.

    Raises:
        ImportError: If the ``anthropic`` package is not installed.
        ValueError: If Claude returns an unparseable response.
    """
    try:
        import anthropic
    except ImportError as exc:
        raise ImportError(
            "The 'anthropic' package is required for generate_slide(). "
            "Install it with: pip install anthropic"
        ) from exc

    client = anthropic.Anthropic(api_key=api_key)

    user_message = (
        f"Slide height budget: {height:.1f} inches\n"
        f"Slide width: {width:.1f} inches\n\n"
        f"Content:\n{content}"
    )

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": _INSTRUCTION_TEXT,
            },
            {
                "type": "text",
                "text": f"## Available Component Schema\n{_COMPONENT_SCHEMA_JSON}",
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    # Extract text from the response (skip thinking blocks if present)
    raw_text = ""
    for block in response.content:
        if getattr(block, "type", None) == "text":
            raw_text = block.text.strip()
            break

    try:
        spec_dicts = json.loads(raw_text)
        if not isinstance(spec_dicts, list):
            raise ValueError("Expected a JSON array at top level.")
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Claude returned non-JSON content:\n{raw_text}"
        ) from exc

    specs: list[ComponentSpec] = []
    for item in spec_dicts:
        comp_type = item.get("type", "")
        props = item.get("props", {})
        comp_height = item.get("height")
        if comp_type not in COMPONENT_REGISTRY:
            continue
        if not isinstance(props, dict):
            continue
        specs.append(ComponentSpec(type=comp_type, props=props, height=comp_height))

    render_specs(slide, specs, x, y, width, height, theme)
    return specs
