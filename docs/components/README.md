# Components Documentation

This folder contains GitHub-friendly docs for all presentation components in this repository.

## Navigation

- [Visual Gallery](./visual_gallery.md)
- [Component Reference](./REFERENCE.md)
- [Composition Patterns](./PATTERNS.md)
- [Module Catalog](./modules/index.md)

## Public vs Internal Imports

Most components are available from top-level `pptx_components` imports:

```python
import pptx_components as pc
```

A few components currently exist in the codebase but are not re-exported at the package root. Import those from module paths directly:

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

b = pc.SlideBuilder(prs)
b.add(pc.SectionHeader("Status"))
b.skip(0.1)
b.add_row(
    pc.MetricCard("Revenue", "$1.2M", delta="+18%", delta_positive=True),
    pc.MetricCard("Users", "24,370", delta="+7%", delta_positive=True),
    pc.MetricCard("Churn", "3.2%", delta="+0.4pp", delta_positive=False),
    h=1.5,
)

prs.save("example.pptx")
```
