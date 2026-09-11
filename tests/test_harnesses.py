import pytest
from ai_cli.main import (
    HARNESS_REGISTRY,
    detect_installed_harnesses,
    resolve_harness,
    build_pi_cmd,
    build_omp_cmd,
    build_claude_cmd,
    build_codex_cmd,
    build_copilot_cmd,
    build_opencode_cmd,
    LATEX_SYSTEM_PROMPT,
)

def test_registry_contains_popular_harnesses():
    expected = {"pi", "omp", "claude", "codex", "copilot", "opencode"}
    assert expected.issubset(set(HARNESS_REGISTRY.keys()))

def test_build_pi_cmd():
    cmd = build_pi_cmd(model=None, enable_tools=False, prompt="hello world")
    assert cmd[0] == "pi"
    assert "-p" in cmd
    assert "--no-session" in cmd
    assert "--no-tools" in cmd
    assert cmd[-1] == "hello world"

    cmd_tools = build_pi_cmd(model="my-model", enable_tools=True, prompt="test")
    assert "--no-tools" not in cmd_tools
    assert "--model" in cmd_tools
    assert "my-model" in cmd_tools

def test_build_omp_cmd():
    cmd = build_omp_cmd(model=None, enable_tools=False, prompt="hello")
    assert cmd[0] == "omp"
    assert "--no-tools" in cmd

    cmd_tools = build_omp_cmd(model=None, enable_tools=True, prompt="hello")
    assert "--auto-approve" in cmd_tools

def test_build_claude_cmd():
    cmd = build_claude_cmd(model=None, enable_tools=False, prompt="hello")
    assert cmd[0] == "claude"
    assert "-p" in cmd
    assert "--tools" in cmd
    idx = cmd.index("--tools")
    assert cmd[idx + 1] == ""

def test_build_codex_cmd():
    cmd = build_codex_cmd(model="o3", enable_tools=True, prompt="task")
    assert cmd[0] == "codex"
    assert "exec" in cmd
    assert "--ephemeral" in cmd
    assert "--dangerously-bypass-approvals-and-sandbox" in cmd
    assert "-m" in cmd
    assert "o3" in cmd

def test_resolve_harness_cli_override():
    assert resolve_harness(cli_harness="omp") == "omp"
    assert resolve_harness(cli_harness="claude") == "claude"

def test_resolve_harness_invalid():
    with pytest.raises(SystemExit):
        resolve_harness(cli_harness="nonexistent-tool")

def test_detect_installed_harnesses(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: f"/fake/bin/{name}" if name in ("pi", "claude") else None)
    detected = detect_installed_harnesses()
    assert detected == ["pi", "claude"]
