from rich.console import Console
from rich.markdown import Markdown

c = Console(force_terminal=True, color_system="truecolor")
c.print(Markdown("""
```python
def greet(name: str) -> str:
    \"\"\"Returns greeting.\"\"\"
    return f"Hello, {name}!"
```
""", code_theme="monokai"))
