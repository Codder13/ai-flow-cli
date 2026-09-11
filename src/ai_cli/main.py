#!/usr/bin/env python3
"""ai-cli: Fast CLI wrapper around local AI harnesses for everyday queries and Unix pipelines."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional

# Optional rich for beautiful markdown rendering in terminal
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.status import Status
    from rich.table import Table

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    from ai_cli.latex_render import (
        render_mixed_markdown_with_math,
        sanitize_inline_math,
    )
except ImportError:
    # Resolve symlink to real path of main.py, then add parent of ai_cli (src) to sys.path
    real_script = os.path.realpath(__file__)
    src_dir = os.path.dirname(os.path.dirname(real_script))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    from ai_cli.latex_render import (
        render_mixed_markdown_with_math,
        sanitize_inline_math,
    )

CONFIG_DIR = Path.home() / ".config" / "ai"
CONFIG_FILE = CONFIG_DIR / "config.json"

LATEX_SYSTEM_PROMPT = (
    "Formatting instructions: For mathematical equations, display formulas, or matrices, "
    "use standard LaTeX block math ($$ ... $$ or \\[ ... \\]). For plain physical units, "
    "numbers, and measurements in text, write normal readable text without math dollar signs "
    "(e.g. ~21,196 km, 65.5 million tons, 200 km²)."
)


def build_pi_cmd(model: Optional[str], enable_tools: bool, prompt: str) -> List[str]:
    cmd = ["pi", "-p", "--no-session"]
    if not enable_tools:
        cmd.append("--no-tools")
    cmd.extend(["--append-system-prompt", LATEX_SYSTEM_PROMPT])
    if model:
        cmd.extend(["--model", model])
    cmd.append(prompt)
    return cmd


def build_omp_cmd(model: Optional[str], enable_tools: bool, prompt: str) -> List[str]:
    cmd = ["omp", "-p", "--no-session"]
    if not enable_tools:
        cmd.append("--no-tools")
    else:
        cmd.append("--auto-approve")
    cmd.extend(["--append-system-prompt", LATEX_SYSTEM_PROMPT])
    if model:
        cmd.extend(["--model", model])
    cmd.append(prompt)
    return cmd


def build_claude_cmd(model: Optional[str], enable_tools: bool, prompt: str) -> List[str]:
    cmd = ["claude", "-p", "--no-session-persistence"]
    if not enable_tools:
        cmd.extend(["--tools", ""])
    else:
        cmd.append("--dangerously-skip-permissions")
    cmd.extend(["--append-system-prompt", LATEX_SYSTEM_PROMPT])
    if model:
        cmd.extend(["--model", model])
    cmd.append(prompt)
    return cmd


def build_codex_cmd(model: Optional[str], enable_tools: bool, prompt: str) -> List[str]:
    cmd = ["codex", "exec", "--ephemeral"]
    if not enable_tools:
        cmd.extend(["--sandbox", "read-only"])
    else:
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    if model:
        cmd.extend(["-m", model])
    cmd.append(f"{LATEX_SYSTEM_PROMPT}\n\n{prompt}")
    return cmd


def build_copilot_cmd(model: Optional[str], enable_tools: bool, prompt: str) -> List[str]:
    cmd = ["copilot", "-p", f"{LATEX_SYSTEM_PROMPT}\n\n{prompt}", "--silent"]
    if enable_tools:
        cmd.append("--allow-all")
    if model:
        cmd.extend(["--model", model])
    return cmd


def build_opencode_cmd(model: Optional[str], enable_tools: bool, prompt: str) -> List[str]:
    cmd = ["opencode", "run"]
    if enable_tools:
        cmd.append("--auto")
    if model:
        cmd.extend(["-m", model])
    cmd.append(f"{LATEX_SYSTEM_PROMPT}\n\n{prompt}")
    return cmd


HARNESS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "pi": {
        "name": "pi",
        "description": "Pi coding assistant (fast, headless mode)",
        "builder": build_pi_cmd,
    },
    "omp": {
        "name": "omp",
        "description": "Oh My Pi / Hermes (autonomous agent harness)",
        "builder": build_omp_cmd,
    },
    "claude": {
        "name": "claude",
        "description": "Claude Code CLI",
        "builder": build_claude_cmd,
    },
    "codex": {
        "name": "codex",
        "description": "OpenAI Codex CLI",
        "builder": build_codex_cmd,
    },
    "copilot": {
        "name": "copilot",
        "description": "GitHub Copilot CLI",
        "builder": build_copilot_cmd,
    },
    "opencode": {
        "name": "opencode",
        "description": "OpenCode CLI assistant",
        "builder": build_opencode_cmd,
    },
}


def load_config() -> Dict[str, Any]:
    """Load configuration from ~/.config/ai/config.json."""
    if CONFIG_FILE.is_file():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to ~/.config/ai/config.json."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
            f.write("\n")
    except Exception as e:
        sys.stderr.write(f"Warning: Could not save configuration to {CONFIG_FILE}: {e}\n")


def detect_installed_harnesses() -> List[str]:
    """Return list of harness keys present in PATH."""
    installed = []
    for key in HARNESS_REGISTRY:
        if shutil.which(key):
            installed.append(key)
    return installed


def run_harness_wizard(console: Optional[Any] = None, current_harness: Optional[str] = None) -> str:
    """Interactive wizard to select and save a default harness."""
    installed = detect_installed_harnesses()
    all_keys = list(HARNESS_REGISTRY.keys())

    if console and HAS_RICH:
        table = Table(title="Select AI Harness", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Harness", style="bold")
        table.add_column("Status", width=14)
        table.add_column("Description")

        for idx, key in enumerate(all_keys, 1):
            info = HARNESS_REGISTRY[key]
            is_installed = key in installed
            status_str = "[green]✓ Installed[/green]" if is_installed else "[red]✗ Not found[/red]"
            active_marker = " [bold yellow](current)[/bold yellow]" if key == current_harness else ""
            table.add_row(str(idx), f"{key}{active_marker}", status_str, info["description"])

        console.print()
        console.print(table)
        console.print()
    else:
        print("\nSelect AI Harness:")
        for idx, key in enumerate(all_keys, 1):
            info = HARNESS_REGISTRY[key]
            is_installed = key in installed
            status = "Installed" if is_installed else "Not found"
            marker = " (current)" if key == current_harness else ""
            print(f"  [{idx}] {key}{marker} [{status}] - {info['description']}")
        print()

    # Determine default choice
    default_idx = "1"
    if current_harness and current_harness in all_keys:
        default_idx = str(all_keys.index(current_harness) + 1)
    elif installed:
        default_idx = str(all_keys.index(installed[0]) + 1)

    choices = [str(i) for i in range(1, len(all_keys) + 1)] + all_keys

    while True:
        if console and HAS_RICH:
            prompt_str = f"[bold cyan]Choose harness number or name[/bold cyan]"
            ans = Prompt.ask(prompt_str, choices=choices, default=default_idx)
        else:
            ans = input(f"Choose harness number or name [{default_idx}]: ").strip()
            if not ans:
                ans = default_idx

        chosen = None
        if ans.isdigit():
            idx = int(ans) - 1
            if 0 <= idx < len(all_keys):
                chosen = all_keys[idx]
        elif ans in all_keys:
            chosen = ans

        if chosen:
            if chosen not in installed:
                warn_msg = f"Warning: '{chosen}' binary was not found in PATH."
                if console and HAS_RICH:
                    console.print(f"[yellow]{warn_msg}[/yellow]")
                else:
                    print(warn_msg)
            cfg = load_config()
            cfg["harness"] = chosen
            save_config(cfg)
            success_msg = f"✓ Saved default harness '{chosen}' to {CONFIG_FILE}"
            if console and HAS_RICH:
                console.print(f"[green]{success_msg}[/green]\n")
            else:
                print(f"{success_msg}\n")
            return chosen


def resolve_harness(cli_harness: Optional[str], console: Optional[Any] = None) -> str:
    """Resolve which harness to use from CLI flag, env, config, or wizard."""
    if cli_harness:
        if cli_harness in HARNESS_REGISTRY:
            return cli_harness
        sys.stderr.write(
            f"Error: Unknown harness '{cli_harness}'. Supported: {', '.join(HARNESS_REGISTRY.keys())}\n"
        )
        sys.exit(1)

    # 1. Environment variable
    env_harness = os.environ.get("AI_HARNESS")
    if env_harness and env_harness in HARNESS_REGISTRY:
        return env_harness

    # 2. Config file
    cfg = load_config()
    configured_harness = cfg.get("harness")
    if configured_harness and configured_harness in HARNESS_REGISTRY:
        if shutil.which(configured_harness):
            return configured_harness
        # If configured harness is missing from PATH, notify user
        sys.stderr.write(
            f"Warning: Configured harness '{configured_harness}' not found in PATH.\n"
        )

    # 3. If TTY and not configured, launch wizard if multiple harnesses or ask user
    installed = detect_installed_harnesses()
    if sys.stdin.isatty():
        if not configured_harness:
            # Wizard on first run or when no harness configured
            return run_harness_wizard(console=console, current_harness=None)

    # 4. Fallback: first installed harness, or configured, or pi/omp
    if configured_harness:
        return configured_harness
    if installed:
        return installed[0]

    return "pi"


def print_help() -> None:
    supported_list = ", ".join(HARNESS_REGISTRY.keys())
    help_text = f"""ai - Fast terminal AI wrapper around local agent harnesses

Usage:
  ai <prompt>                      Ask question / prompt
  ai "multi word prompt"           Ask question
  echo "data" | ai <prompt>        Pipe stdin context into prompt
  ai --help, -h                    Show this help
  ai --wizard                      Interactive harness setup wizard
  ai --harness <name> <prompt>     Use specific harness ({supported_list})
  ai --raw <prompt>                Print plain text without markdown styling
  ai --tools <prompt>              Run with tool execution enabled
  ai --model <name> <prompt>       Specify model override

Features:
  - Supports multiple harnesses: {supported_list}
  - Auto-detection and interactive first-run wizard
  - Persistent harness preference in ~/.config/ai/config.json
  - Rich terminal markdown rendering with code syntax highlighting
  - Pure PDF/LaTeX math rendering in supported terminals (Kitty graphics)
  - Clean Unicode unit conversion (e.g. ~21,196 km, ~200 km²)
  - Unix pipeline friendly (clean stdout passthrough when piped)

Examples:
  ai what is the biggest object on earth
  ai --wizard
  ai --harness claude "review recent commit"
  ai show me the quadratic formula
  git diff | ai review these changes
  cat server.log | ai find error root cause
"""
    print(help_text)


def main() -> None:
    args = sys.argv[1:]

    console = Console() if HAS_RICH else None

    # Check for wizard flag first
    if any(arg in ("--wizard", "--setup") for arg in args):
        cfg = load_config()
        run_harness_wizard(console=console, current_harness=cfg.get("harness"))
        sys.exit(0)

    if not args and sys.stdin.isatty():
        print_help()
        sys.exit(0)

    # Check for help flag
    if any(arg in ("-h", "--help") for arg in args):
        print_help()
        sys.exit(0)

    # Parse our custom options
    raw_mode = False
    enable_tools = False
    model_override = None
    cli_harness = None
    prompt_words = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--raw":
            raw_mode = True
            i += 1
        elif arg == "--tools":
            enable_tools = True
            i += 1
        elif arg in ("-H", "--harness"):
            if i + 1 < len(args):
                cli_harness = args[i + 1]
                i += 2
            else:
                prompt_words.append(arg)
                i += 1
        elif arg.startswith("--harness="):
            cli_harness = arg.split("=", 1)[1]
            i += 1
        elif arg in ("-m", "--model"):
            if i + 1 < len(args):
                model_override = args[i + 1]
                i += 2
            else:
                prompt_words.append(arg)
                i += 1
        elif arg.startswith("--model="):
            model_override = arg.split("=", 1)[1]
            i += 1
        else:
            prompt_words.append(arg)
            i += 1

    harness_name = resolve_harness(cli_harness, console=console)

    if not shutil.which(harness_name):
        sys.stderr.write(f"Error: Harness '{harness_name}' executable not found in PATH.\n")
        sys.stderr.write(f"Please install '{harness_name}' or run 'ai --wizard' to switch.\n")
        sys.exit(1)

    prompt = " ".join(prompt_words).strip()

    # Handle piped stdin
    stdin_content = ""
    if not sys.stdin.isatty():
        try:
            stdin_content = sys.stdin.read().strip()
        except Exception:
            pass

    if stdin_content:
        if prompt:
            prompt = f"{stdin_content}\n\n{prompt}"
        else:
            prompt = stdin_content

    if not prompt:
        print_help()
        sys.exit(1)

    builder = HARNESS_REGISTRY[harness_name]["builder"]
    cmd = builder(model_override, enable_tools, prompt)

    # Terminal output checking
    is_interactive_terminal = sys.stdout.isatty() and not raw_mode and HAS_RICH

    if is_interactive_terminal and console:
        # Show clean spinner on stderr while harness processes
        status = console.status(
            f"[bold blue]Thinking ({harness_name})...[/bold blue]", spinner="dots"
        )
        status.start()
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout_data, stderr_data = proc.communicate()
        finally:
            status.stop()

        if proc.returncode != 0:
            if stderr_data:
                sys.stderr.write(stderr_data)
            sys.exit(proc.returncode)

        if stdout_data:
            render_mixed_markdown_with_math(stdout_data.strip(), console)
        elif stderr_data:
            sys.stderr.write(stderr_data)
    else:
        # Piped stdout or raw mode or no rich: direct output
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout_data, stderr_data = proc.communicate()
        if proc.returncode != 0:
            if stderr_data:
                sys.stderr.write(stderr_data)
            sys.exit(proc.returncode)

        if stdout_data:
            clean_output = sanitize_inline_math(stdout_data)
            sys.stdout.write(clean_output)
            sys.stdout.flush()
        elif stderr_data:
            sys.stderr.write(stderr_data)


if __name__ == "__main__":
    main()
