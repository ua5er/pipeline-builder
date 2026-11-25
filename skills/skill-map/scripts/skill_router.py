#!/usr/bin/env python3
"""UserPromptSubmit hook: when a prompt matches a task in .claude/skill-map.json, remind the
agent which skills (and pipeline) to use. Prints nothing when nothing matches, so it costs
no tokens on unrelated prompts. Standard library only; never fails the prompt."""
import json, os, re, sys
from pathlib import Path


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return
    prompt = (ev.get("prompt") or "").lower()
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ev.get("cwd") or ".")
    f = root / ".claude" / "skill-map.json"
    if not prompt or not f.exists():
        return
    try:
        entries = json.loads(f.read_text()).get("entries", [])
    except Exception:
        return
    hits = []
    for e in entries:
        trig = [t.lower() for t in e.get("triggers", []) + [e.get("task", "")] if t]
        if any(re.search(r"(?<!\w)" + re.escape(t), prompt) for t in trig):
            hits.append(e)
    if not hits:
        return
    lines = ["Skill map match (from .claude/skill-map.json). Load these skills before the work and pass them by name to subagents:"]
    for e in hits[:3]:
        extra = f"; pipeline .claude/pipelines/{e['pipeline']}/PIPELINE.md" if e.get("pipeline") else ""
        ag = f"; agents {', '.join(e['agents'])}" if e.get("agents") else ""
        lines.append(f"- {e['task']}: {', '.join(e.get('skills', []))}{extra}{ag}")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "\n".join(lines)}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
