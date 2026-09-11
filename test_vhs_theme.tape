Output test_vhs_theme.gif

Set FontSize 15
Set FontFamily "CaskaydiaMono Nerd Font"
Set LineHeight 1.3
Set Width 1200
Set Height 700
Set Padding 20
Set Theme "Catppuccin Mocha"
Set WindowBar "Colorful"
Set BorderRadius 8

Type "NO_COLOR= python3 -c '
from rich.console import Console
from rich.markdown import Markdown
from rich.theme import Theme

theme = Theme({
    \"markdown.h1\": \"bold #ffb68f\",
    \"markdown.h2\": \"bold #ffb68f\",
    \"markdown.h3\": \"bold #ffb68f\",
    \"markdown.item.bullet\": \"#ffb68f\",
    \"markdown.item.number\": \"#ffb68f\",
    \"markdown.block_quote\": \"italic #ffb68f\",
    \"markdown.code\": \"bold #ffb68f on #271e19\",
})
c = Console(theme=theme, force_terminal=True, color_system=\"truecolor\", no_color=False)
md = \"\"\"
## Ordered List
1. First step
2. Second step

## Code Block
\`\`\`python
def greet(name: str) -> str:
    \"\"\"Returns a greeting message.\"\"\"
    return f\"Hello, {name}!\"

if __name__ == \"__main__\":
    print(greet(\"World\"))
\`\`\`

## Table
| Feature | Syntax | Status |
| :--- | :--- | :--- |
| Headers | \`# ... ######\` | Supported |
| Tables | \`| col |\` | Supported |
| Code Blocks | \`\`\`\` \`\`\`lang \`\`\`\` | Supported |
\"\"\"
c.print(Markdown(md, code_theme=\"monokai\"))
'"
Enter
Sleep 3s
