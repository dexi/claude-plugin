"""The Dexi plugin's Claude Code hooks (hooks/dexi_hooks.py), run as Claude
Code runs them: JSON on stdin, JSON (or nothing) on stdout, exit 0 always."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parents[1]
SCRIPT = HOOKS / "dexi_hooks.py"
sys.path.insert(0, str(HOOKS))

import dexi_hooks  # noqa: E402

DEXI_CREATE = "mcp__plugin_dexi_dexi__create_note"


def run(event, payload, *, env=None, raw_stdin=None):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), event],
        input=raw_stdin if raw_stdin is not None else json.dumps(payload),
        capture_output=True, text=True, timeout=20,
        env={**{k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_PLUGIN_")}, **(env or {})},
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def transcript(tmp_path, tool_names, name="t.jsonl"):
    path = tmp_path / name
    lines = [json.dumps({"type": "user", "message": {"content": "hi"}})]
    for tool in tool_names:
        lines.append(json.dumps({
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": "…"},
                                    {"type": "tool_use", "id": "x", "name": tool, "input": {}}]},
        }))
    lines.append("not json \"tool_use\"")  # corrupt line survives
    path.write_text("\n".join(lines) + "\n")
    return str(path)


def stop_payload(tmp_path, tools, **extra):
    return {
        "session_id": "abc-123",
        "transcript_path": transcript(tmp_path, tools),
        "cwd": str(tmp_path),
        "hook_event_name": "Stop",
        "stop_hook_active": False,
        "background_tasks": [],
        "session_crons": [],
        **extra,
    }


def checkpoints_env(tmp_path, every=5):
    return {
        "CLAUDE_PLUGIN_OPTION_CHECKPOINTS": "true",
        "CLAUDE_PLUGIN_OPTION_CHECKPOINT_EVERY": str(every),
        "CLAUDE_PLUGIN_DATA": str(tmp_path / "data"),
    }


# --- project tag ------------------------------------------------------------------


@pytest.mark.parametrize("name,tag", [
    ("dexi", "#dexi"),
    ("my-Project.v2", "#my_project_v2"),   # Dexi hashtags stop at '-' and '.'
    ("__x__", "#x"),
    ("2026", None),                       # HASHTAG_RE needs a letter or '_'
    ("---", None),
])
def test_project_tag_is_parseable_by_dexi(name, tag):
    assert dexi_hooks.project_tag(name) == tag


# --- SessionStart -------------------------------------------------------------------


def test_session_start_injects_memory_protocol(tmp_path):
    proj = tmp_path / "atlas-api"
    proj.mkdir()
    out = run("session-start", {"cwd": str(proj), "source": "startup"})
    spec = out["hookSpecificOutput"]
    assert spec["hookEventName"] == "SessionStart"
    ctx = spec["additionalContext"]
    assert "Current project: atlas-api" in ctx
    assert "#memory and #atlas_api" in ctx
    for tool in ("semantic_search", "create_note", "update_note"):
        assert tool in ctx


def test_session_start_uses_git_toplevel(tmp_path):
    repo = tmp_path / "repo-root"
    sub = repo / "src" / "deep"
    sub.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    out = run("session-start", {"cwd": str(sub)})
    assert "Current project: repo-root" in out["hookSpecificOutput"]["additionalContext"]


def test_session_start_can_be_turned_off(tmp_path):
    assert run("session-start", {"cwd": str(tmp_path)},
               env={"CLAUDE_PLUGIN_OPTION_RECALL": "false"}) is None


# --- Stop checkpoints ----------------------------------------------------------------


def test_checkpoints_are_off_by_default(tmp_path):
    payload = stop_payload(tmp_path, ["Bash"] * 50)
    assert run("stop", payload, env={"CLAUDE_PLUGIN_DATA": str(tmp_path / "d")}) is None


def test_checkpoint_fires_once_per_stretch(tmp_path):
    env = checkpoints_env(tmp_path)
    payload = stop_payload(tmp_path, ["Bash"] * 6)
    out = run("stop", payload, env=env)
    spec = out["hookSpecificOutput"]
    assert spec["hookEventName"] == "Stop"
    assert "6 tool calls since anything was saved" in spec["additionalContext"]
    # Same transcript at the next stop: already nudged for this stretch
    assert run("stop", payload, env=env) is None
    # Another full stretch of work later → one more nudge
    payload["transcript_path"] = transcript(tmp_path, ["Bash"] * 11, name="t2.jsonl")
    assert run("stop", payload, env=env) is not None


def test_recent_dexi_write_resets_the_count(tmp_path):
    env = checkpoints_env(tmp_path)
    tools = ["Bash"] * 10 + [DEXI_CREATE] + ["Read"] * 3
    assert run("stop", stop_payload(tmp_path, tools), env=env) is None


def test_user_added_server_name_counts_as_a_write(tmp_path):
    env = checkpoints_env(tmp_path)
    tools = ["Bash"] * 10 + ["mcp__dexi__update_note"]
    assert run("stop", stop_payload(tmp_path, tools), env=env) is None


def test_below_threshold_is_quiet(tmp_path):
    env = checkpoints_env(tmp_path, every=20)
    assert run("stop", stop_payload(tmp_path, ["Bash"] * 19), env=env) is None


@pytest.mark.parametrize("extra", [
    {"stop_hook_active": True},
    {"background_tasks": [{"id": "t", "type": "shell", "status": "running"}]},
    {"session_crons": [{"id": "c", "schedule": "0 9 * * *", "recurring": True}]},
])
def test_never_nudges_while_continuing_or_paused(tmp_path, extra):
    env = checkpoints_env(tmp_path)
    assert run("stop", stop_payload(tmp_path, ["Bash"] * 50, **extra), env=env) is None


def test_interval_has_a_floor(tmp_path):
    env = checkpoints_env(tmp_path, every=1)
    assert run("stop", stop_payload(tmp_path, ["Bash"] * 4), env=env) is None


def test_no_data_dir_means_no_nudge(tmp_path):
    # Without somewhere to remember the nudge it would repeat every turn
    env = {"CLAUDE_PLUGIN_OPTION_CHECKPOINTS": "true", "CLAUDE_PLUGIN_OPTION_CHECKPOINT_EVERY": "5"}
    assert run("stop", stop_payload(tmp_path, ["Bash"] * 50), env=env) is None


# --- robustness -------------------------------------------------------------------------


@pytest.mark.parametrize("stdin", ["", "not json", "[1, 2]"])
def test_bad_input_is_silent(stdin):
    for event in ("session-start", "stop"):
        assert run(event, None, raw_stdin=stdin) is None


def test_missing_transcript_is_silent(tmp_path):
    payload = stop_payload(tmp_path, [])
    payload["transcript_path"] = str(tmp_path / "gone.jsonl")
    assert run("stop", payload, env=checkpoints_env(tmp_path)) is None


def test_unknown_event_is_silent():
    assert run("bogus", {}) is None


def test_hooks_json_points_at_the_script():
    config = json.loads((HOOKS / "hooks.json").read_text())
    commands = [h["command"] for groups in config["hooks"].values()
                for g in groups for h in g["hooks"]]
    assert any("dexi_hooks.py\" session-start" in c for c in commands)
    assert any("dexi_hooks.py\" stop" in c for c in commands)
    assert all("${CLAUDE_PLUGIN_ROOT}" in c and c.endswith("|| true") for c in commands)
