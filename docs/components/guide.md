# Components Guide

This section contains practical notes for using the component system effectively.

## Public vs Internal Imports

Most components are available from top-level imports:

```python
import pptx_components as pc
```

Some components may be imported directly from module paths when not re-exported:

```python
from pptx_components.components.timeline import Timeline
from pptx_components.components.comparison import ComparisonPanel
```

## Minimal Slide Pattern

```python
from pptx import Presentation
import pptx_components as pc

prs = Presentation()
pc.set_theme(pc.DarkTheme())

builder = pc.SlideBuilder(prs)
builder.add(pc.SectionHeader("Status"))
builder.skip(0.1)
builder.add_row(
    pc.MetricCard("Revenue", "$1.2M", delta="+18%", delta_positive=True),
    pc.MetricCard("Users", "24,370", delta="+7%", delta_positive=True),
    pc.MetricCard("Churn", "3.2%", delta="+0.4pp", delta_positive=False),
    h=1.5,
)

prs.save("example.pptx")
```
