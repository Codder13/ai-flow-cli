#!/usr/bin/env python3
"""ai-cli: Fast CLI wrapper around omp for everyday queries and Unix pipelines."""

import os
import shutil
import subprocess
import sys

# Optional rich for beautiful markdown rendering in terminal
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.status import Status

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


def get_terminal_session_key() -> str:
    """Get unique key identifying current terminal session / tab."""
    ppid = os.getppid()

    # 1. Parent process TTY from /proc/<ppid>/fd
    for fd in (0, 1, 2):
        try:
            target = os.readlink(f"/proc/{ppid}/fd/{fd}")
            if target.startswith("/dev/"):
                clean = target[5:].replace("/", "_")
                return f"tty_{clean}"
        except Exception:
            pass

    # 2. File descriptor TTY of current process
    for fd in (0, 1, 2):
        try:
            name = os.ttyname(fd)
            if name.startswith("/dev/"):
                clean = name[5:].replace("/", "_")
                return f"tty_{clean}"
        except Exception:
            pass

    # 3. Terminal multiplexer / emulator environment variables
    for var in (
        "HERDR_PANE_ID",
        "TMUX_PANE",
        "KITTY_WINDOW_ID",
        "WEZTERM_PANE",
        "WINDOWID",
        "TERM_SESSION_ID",
    ):
        val = os.environ.get(var)
        if val:
            clean = "".join(c if c.isalnum() or c in "-_" else "_" for c in val)
            return f"{var.lower()}_{clean}"

    # 4. Fallback to parent session ID or PPID
    try:
        sid = os.getsid(ppid)
        return f"sid_{sid}"
    except Exception:
        return f"ppid_{ppid}"


def get_terminal_session_dir(harness_name: str) -> str:
    """Return directory where session files for current terminal tab are kept."""
    key = get_terminal_session_key()
    base_dir = os.path.expanduser("~/.cache/ai/sessions")
    session_dir = os.path.join(base_dir, harness_name, key)
    os.makedirs(session_dir, exist_ok=True)
    return session_dir


def clear_terminal_session() -> None:
    """Clear session history for current terminal tab across all harnesses."""
    key = get_terminal_session_key()
    base_dir = os.path.expanduser("~/.cache/ai/sessions")
    if os.path.isdir(base_dir):
        for entry in os.listdir(base_dir):
            harness_path = os.path.join(base_dir, entry)
            if os.path.isdir(harness_path):
                target = os.path.join(harness_path, key)
                if os.path.exists(target):
                    shutil.rmtree(target, ignore_errors=True)


def has_existing_session(session_dir: str) -> bool:
    """Check if session directory contains any saved session files."""
    if not os.path.exists(session_dir):
        return False
    try:
        return any(
            f.endswith(".jsonl") or f.endswith(".json")
            for f in os.listdir(session_dir)
        )
    except OSError:
        return False


def build_harness_session_args(
    harness: str,
    session_dir: str,
    resume: bool = True,
    no_session: bool = False,
) -> list[str]:
    """Harness-agnostic session argument builder."""
    if no_session:
        if harness in ("pi", "omp"):
            return ["--no-session"]
        return []

    if harness in ("pi", "omp"):
        args = ["--session-dir", session_dir]
        if resume and has_existing_session(session_dir):
            args.append("-c")
        return args
    elif harness == "claude":
        args = []
        if resume:
            args.append("-c")
        return args
    elif harness == "codex":
        return []

    # Default fallback
    args = ["--session-dir", session_dir]
    if resume and has_existing_session(session_dir):
        args.append("-c")
    return args


def print_help() -> None:
    help_text = """ai - Fast terminal AI powered by pi/omp

Usage:
  ai <prompt>                      Ask question / prompt (continues terminal session)
  ai "multi word prompt"           Ask question
  echo "data" | ai <prompt>        Pipe stdin context into prompt
  ai --new <prompt>                Start fresh session in this terminal
  ai --no-session <prompt>         Run ephemerally without persisting session
  ai --clear                       Clear conversation history for this terminal
  ai --help, -h                    Show this help
  ai --raw <prompt>                Print plain text without markdown styling
  ai --tools <prompt>              Run with tool execution enabled
  ai --model <name> <prompt>       Specify model
  ai --harness <name> <prompt>     Specify harness (pi, omp, etc.)

Features:
  - Persistent conversation memory per terminal tab / session
  - Harness-agnostic session storage
  - Rich terminal markdown rendering with code syntax highlighting
  - Pure PDF/LaTeX math rendering in supported terminals (Kitty graphics)
  - Clean Unicode unit conversion (e.g. ~21,196 km, ~200 km²)
  - Unix pipeline friendly (clean stdout passthrough when piped)

Examples:
  ai what is the biggest object on earth
  ai what was my previous question
  ai --clear
  git diff | ai review these changes
  cat server.log | ai find error root cause
"""
    print(help_text)


def main() -> None:
    args = sys.argv[1:]

    if not args and sys.stdin.isatty():
        print_help()
        sys.exit(0)

    # Check for help flag
    if any(arg in ("-h", "--help") for arg in args):
        print_help()
        sys.exit(0)

    # Check for session clear command
    if any(arg == "--clear" for arg in args):
        clear_terminal_session()
        print("Session cleared for this terminal.")
        sys.exit(0)

    # Parse our custom options
    raw_mode = False
    enable_tools = False
    new_session = False
    no_session = False
    harness_override = None
    model_override = None
    pass_through_args = []
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
        elif arg == "--new":
            new_session = True
            i += 1
        elif arg == "--no-session":
            no_session = True
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
        elif arg == "--harness":
            if i + 1 < len(args):
                harness_override = args[i + 1]
                i += 2
            else:
                prompt_words.append(arg)
                i += 1
        elif arg.startswith("--harness="):
            harness_override = arg.split("=", 1)[1]
            i += 1
        else:
            prompt_words.append(arg)
            i += 1
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

    # Select harness (respecting override, environment variable, then pi / omp)
    harness = harness_override or os.environ.get("AI_HARNESS")
    if not harness:
        harness = "pi" if shutil.which("pi") else "omp"

    if not shutil.which(harness):
        sys.stderr.write(f"Error: '{harness}' executable not found in PATH.\n")
        sys.stderr.write("Please install or ensure the harness is available in your PATH.\n")
        sys.exit(1)

    # Manage session directory
    session_dir = get_terminal_session_dir(harness)
    if new_session and os.path.exists(session_dir):
        shutil.rmtree(session_dir, ignore_errors=True)
        os.makedirs(session_dir, exist_ok=True)

    # Build harness command
    cmd = [harness, "-p"]
    session_args = build_harness_session_args(
        harness=harness,
        session_dir=session_dir,
        resume=not new_session,
        no_session=no_session,
    )
    cmd.extend(session_args)

    if not enable_tools:
        if harness in ("pi", "omp"):
            cmd.append("--no-tools")
    else:
        if harness in ("pi", "omp"):
            cmd.append("--auto-approve")
    # Prompt convention: use normal LaTeX display math ($$ ... $$) for equations,
    # but use normal units (~21,196 km) in conversational text.
    if harness in ("pi", "omp"):
        cmd.extend(
            [
                "--append-system-prompt",
                "Formatting instructions: For mathematical equations, display formulas, or matrices, use standard LaTeX block math ($$ ... $$ or \\[ ... \\]). For plain physical units, numbers, and measurements in text, write normal readable text without math dollar signs (e.g. ~21,196 km, 65.5 million tons, 200 km²).",
            ]
        )

    if model_override:
        cmd.extend(["--model", model_override])

    if pass_through_args:
        cmd.extend(pass_through_args)
    cmd.append(prompt)

    # Terminal output checking
    is_interactive_terminal = sys.stdout.isatty() and not raw_mode and HAS_RICH

    console = Console() if HAS_RICH else None

    if is_interactive_terminal and console:
        # Show clean spinner on stderr while omp processes
        status = console.status("[bold blue]Thinking...[/bold blue]", spinner="dots")
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
