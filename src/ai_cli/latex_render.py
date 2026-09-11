"""
LaTeX math post-processing and rendering helpers.
Converts LaTeX formulas and notation to readable Unicode/terminal text
matching Oh My Pi (omp) native rendering.
"""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.theme import Theme
except ImportError:
    pass

try:
    import pylatexenc.latex2text

    HAS_PYLATEXENC = True
except ImportError:
    HAS_PYLATEXENC = False

LATEX_THEME = Theme({
    "markdown.h1": "bold #ffb68f",
    "markdown.h2": "bold #ffb68f",
    "markdown.h3": "bold #ffb68f",
    "markdown.h4": "bold #ffb68f",
    "markdown.hr": "#52443d",
    "markdown.item.bullet": "#ffb68f",
    "markdown.item.number": "#ffb68f",
    "markdown.block_quote": "italic #d7c2b9",
    "markdown.link": "underline #ffb68f",
    "markdown.code": "bold #ffb68f on #271e19",
})

# Path to the bundled JS math engine
OMP_MATH_SCRIPT = Path(__file__).resolve().parent / "omp_math.mjs"

# Common unit patterns emitted by models in LaTeX math mode:
UNITS_RE = re.compile(
    r"\$(?:\\sim\s*)?([0-9.,]+(?:\s*[a-zA-Z%]+|\s*\\text\{[a-zA-Z%]+\})?)\$"
)
TEXT_MACRO_RE = re.compile(r"\\text\{([^}]+)\}")
SIM_RE = re.compile(r"\\sim\s*")
TIMES_RE = re.compile(r"\\times\s*")
EXPONENT_RE = re.compile(r"\^\{?([0-9+-]+)\}?")
DISPLAY_MATH_RE = re.compile(r"(\$\$(?:\\.|[^\$])+\$\$|\\\[(?:\\.|[^\]])+\\\])")


def render_math_with_omp(text: str) -> str:
    """
    Renders LaTeX math notation in text using omp's bundled parser logic.
    Executes via bun or node if available. Returns original text on error.
    """
    if not OMP_MATH_SCRIPT.exists():
        return text

    js_runtime = shutil.which("bun") or shutil.which("node")
    if not js_runtime:
        return text

    try:
        proc = subprocess.run(
            [js_runtime, str(OMP_MATH_SCRIPT)],
            input=text,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout
    except Exception:
        pass

    return text


def sanitize_inline_math(text: str) -> str:
    """
    Normalizes simple inline math units and symbols so they don't break
    standard terminal output or markdown rendering.
    """
    # Fix unit measurements: $\sim 21{,}196\text{ km}$ -> ~21,196 km
    text = TEXT_MACRO_RE.sub(r"\1", text)
    text = SIM_RE.sub("~", text)
    text = TIMES_RE.sub("×", text)
    text = re.sub(r"\{,\}", ",", text)

    # Exponents: m^3 -> m³, x^2 -> x²
    superscripts = {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
        "+": "⁺",
        "-": "⁻",
    }

    def _replace_exp(match: re.Match) -> str:
        exp_str = match.group(1)
        if all(c in superscripts for c in exp_str):
            return "".join(superscripts[c] for c in exp_str)
        return match.group(0)

    text = EXPONENT_RE.sub(_replace_exp, text)

    # Remove remaining standalone $ if they are wrapping simple numbers/units
    text = re.sub(r"\$([0-9.,~×\s\w]+)\$", r"\1", text)

    return text


def render_mixed_markdown_with_math(text: str, console: Console) -> None:
    """
    Renders text by converting LaTeX math (display blocks and inline) to
    beautiful Unicode text using omp's exact renderer (or pylatexenc fallback),
    then prints rich markdown to the terminal with colorful theme.
    """
    # Try omp native renderer first
    omp_rendered = render_math_with_omp(text)
    if omp_rendered != text:
        console.print(Markdown(omp_rendered, code_theme="monokai"))
        return

    if HAS_PYLATEXENC:
        l2t = pylatexenc.latex2text.LatexNodes2Text(math_mode="text")

        def _convert_display_math(m: re.Match) -> str:
            raw = m.group(0).strip()
            inner = raw
            if inner.startswith("$$") and inner.endswith("$$"):
                inner = inner[2:-2].strip()
            elif inner.startswith("\\[") and inner.endswith("\\]"):
                inner = inner[2:-2].strip()
            try:
                converted = l2t.latex_to_text(inner).strip()
                if converted:
                    return "\n\n" + converted + "\n\n"
            except Exception:
                pass
            return raw

        text = DISPLAY_MATH_RE.sub(_convert_display_math, text)

    text = sanitize_inline_math(text)
    console.print(Markdown(text, code_theme="monokai"))
