# ai-cli

> **Lightweight, fast terminal AI wrapper around modern coding harnesses with Rich markdown and math rendering.**

Wraps fast headless AI harnesses (`pi`, `omp`, `claude`, `codex`, `copilot`, `opencode`) for everyday queries and Unix pipelines.

---

## ⚡ Features

- 🚀 **Multi-Harness Support** — seamlessly autodetect and use `pi`, `omp`, `claude`, `codex`, `copilot`, or `opencode`.
- 🧙 **Interactive Setup Wizard** — run `ai --wizard` to inspect detected harnesses and choose your default.
- 🎨 **Rich Terminal Markdown & LaTeX** — renders clean markdown, tables, syntax highlighting, and math formulas in the terminal.
- 💬 **No Quotes Required** — run `ai what is the biggest object on earth` directly.
- 🚰 **Pure Unix Pipelines** — stdin context injection and clean raw text output when piped.
- 🛠️ **Tools On Demand** — pass `--tools` when agentic filesystem/system actions are needed.

---

## 📦 Installation

### 1. Recommended: Install via `mise`
```bash
mise use -g pipx:ai-flow-cli
# or via python backend:
mise use -g pip:ai-flow-cli
```

### 2. Install via PyPI (`pip` / `pipx` / `uv`)
```bash
# Standard pip install:
pip install --user ai-flow-cli

# Isolated global CLI with pipx:
pipx install ai-flow-cli

# Fast install with uv:
uv tool install ai-flow-cli
```

### 3. One-Line Script Install
```bash
curl -sSL https://raw.githubusercontent.com/Codder13/ai-cli/main/install.sh | bash
```

---

## 🛠️ Usage

### 1. Initial Setup & Harness Selection Wizard
Run the interactive wizard to detect installed harnesses and set your preferred default:
```bash
ai --wizard
```
If no config exists yet, `ai` automatically prompts the wizard on first run when interactive, or picks the first detected harness (`pi` -> `omp` -> `claude` -> ...).

### 2. Direct Questions (Fast Headless Mode)
No quotes needed:
```bash
ai explain what is eBPF in 3 bullet points
```

### 3. Switching Harnesses on the Fly
Use `--harness` or `-H` to override your default for a single query:
```bash
ai -H claude explain why rust ownership works this way
ai -H omp write a bash script to backup my dotfiles
```

### 4. Enable Tools for Agentic Actions
By default, queries run without tool side-effects for speed and safety. Pass `--tools` or `-t` to enable filesystem and command execution:
```bash
ai --tools check git status and run tests
```

### 5. Unix Pipelines & Input Redirection
When piped, `ai` preserves standard Unix conventions:
```bash
git diff | ai explain these changes
cat error.log | ai "what caused this panic?"
curl -s https://example.com | ai summarize this page
```

Output is automatically raw and unformatted when redirected to a pipe or file:
```bash
ai "generate a python regex for uuid4" > regex.txt
```

---

## ⚙️ Configuration

Settings are stored in `~/.config/ai/config.json`:
```json
{
  "harness": "pi"
}
```

You can change it anytime via:
```bash
ai --wizard
```

---

## 📄 License

MIT
