#!/usr/bin/env python3
"""Keep a project's "which skill for which task" map in files the agent always reads.

Writes three things in the project root:
  .claude/skill-map.json        machine-readable map (merged, never clobbered)
  AGENTS.md  skill-map block    human-readable table between markers (CLAUDE.md gets @AGENTS.md if missing)
  .claude/settings.json hook    UserPromptSubmit hook that reminds the agent of the right skills (install-hook)

  python3 skill_map.py add --task "video ad" --triggers "video ad,ролик,ugc" --skills "a/b@storyboard,local:brand-voice" [--pipeline video-ad]
  python3 skill_map.py merge path/to/pipeline.json     # take skill_map entries from a pipeline
  python3 skill_map.py sync                            # re-render the AGENTS.md block from the json
  python3 skill_map.py install-hook                    # copy skill_router.py into .claude/hooks and register it
  python3 skill_map.py show

Run from the project root (or pass --root). Standard library only.
"""
import argparse, json, shutil, sys
from pathlib import Path

START, END = "<!-- skill-map:start -->", "<!-- skill-map:end -->"


def load(root):
    f = root / ".claude" / "skill-map.json"
    return json.loads(f.read_text()) if f.exists() else {"version": 1, "entries": []}


def save(root, data):
    f = root / ".claude" / "skill-map.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def upsert(data, e):
    e = {"task": e["task"].strip(), "triggers": [t.strip() for t in e.get("triggers", []) if t.strip()],
         "skills": [s.strip() for s in e.get("skills", []) if s.strip()], **({"pipeline": e["pipeline"]} if e.get("pipeline") else {}),
         **({"agents": e["agents"]} if e.get("agents") else {})}
    for i, x in enumerate(data["entries"]):
        if x["task"].lower() == e["task"].lower():
            x["triggers"] = list(dict.fromkeys(x.get("triggers", []) + e["triggers"]))
            x["skills"] = list(dict.fromkeys(e["skills"] + x.get("skills", [])))
            for k in ("pipeline", "agents"):
                if e.get(k):
                    x[k] = e[k]
            return
    data["entries"].append(e)


def block(data):
    L = [START, "## Skill map (read before you start a task)", "",
         "Before working on a task below, load the listed skills (Skill tool or `npx skills use <ref>`) and pass them by name to any subagent. "
         "If a task is not listed and you pick skills for it, add a row with `python3 .claude/skill-map/skill_map.py add ...`.", "",
         "| Task | Triggers | Skills | Pipeline / agents |", "|---|---|---|---|"]
    for e in data["entries"]:
        pa = " · ".join(x for x in [f"`.claude/pipelines/{e['pipeline']}/PIPELINE.md`" if e.get("pipeline") else "", ", ".join(e.get("agents", []))] if x)
        L.append(f"| {e['task']} | {', '.join(e['triggers'])} | {', '.join('`'+s+'`' for s in e['skills'])} | {pa or '-'} |")
    return "\n".join(L + [END])


def sync(root, data):
    agents = root / "AGENTS.md"
    txt = agents.read_text() if agents.exists() else ""
    b = block(data)
    if START in txt and END in txt:
        txt = txt[: txt.index(START)] + b + txt[txt.index(END) + len(END):]
    else:
        txt = (txt.rstrip() + "\n\n" if txt.strip() else "") + b + "\n"
    agents.write_text(txt)
    claude = root / "CLAUDE.md"
    ct = claude.read_text() if claude.exists() else ""
    if "@AGENTS.md" not in ct and START not in ct:
        claude.write_text("@AGENTS.md\n" + ("\n" + ct if ct else ""))
    # keep a copy of the tools in the project so agents can update the map later
    tools = root / ".claude" / "skill-map"
    tools.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parent
    for name in ("skill_map.py", "skill_router.py"):
        if (here / name).exists() and (here / name).resolve() != (tools / name).resolve():
            shutil.copy2(here / name, tools / name)


def install_hook(root):
    sync(root, load(root))
    s = root / ".claude" / "settings.json"
    cfg = json.loads(s.read_text()) if s.exists() else {}
    cmd = 'python3 "$CLAUDE_PROJECT_DIR/.claude/skill-map/skill_router.py"'
    hooks = cfg.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])
    if not any(cmd in h.get("command", "") for grp in hooks for h in grp.get("hooks", [])):
        hooks.append({"hooks": [{"type": "command", "command": cmd, "timeout": 5}]})
    s.write_text(json.dumps(cfg, indent=2) + "\n")
    print(f"hook registered in {s}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["add", "merge", "sync", "install-hook", "show"])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--root", default=".")
    ap.add_argument("--task"); ap.add_argument("--triggers", default=""); ap.add_argument("--skills", default="")
    ap.add_argument("--pipeline"); ap.add_argument("--agents", default="")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    data = load(root)
    if a.cmd == "add":
        if not a.task or not a.skills:
            ap.error("add needs --task and --skills")
        upsert(data, {"task": a.task, "triggers": a.triggers.split(","), "skills": a.skills.split(","), "pipeline": a.pipeline,
                      "agents": [x for x in a.agents.split(",") if x]})
    elif a.cmd == "merge":
        p = json.loads(Path(a.path).read_text())
        for e in p.get("skill_map", []):
            upsert(data, {**e, "pipeline": e.get("pipeline") or p.get("name")})
    elif a.cmd == "install-hook":
        return install_hook(root)
    elif a.cmd == "show":
        return print(block(data))
    save(root, data)
    sync(root, data)
    print(f"{len(data['entries'])} entries -> .claude/skill-map.json, AGENTS.md")


if __name__ == "__main__":
    main()
