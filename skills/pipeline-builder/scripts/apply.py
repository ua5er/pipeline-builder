#!/usr/bin/env python3
"""Apply a checked pipeline.json to a project: install skills, write subagents, record the skill map.

  python3 apply.py .pipeline/pipeline.json --root . [--dry-run] [--no-install] [--agent claude-code]

Steps
1. `pipeline.py check` must pass (no errors).
2. Install every remote skill ref (owner/repo@skill) at project level with the Vercel skills CLI.
   Refs starting with `local:` are skills already in the project and are not installed.
3. Write `.claude/agents/<name>.md` for each agent: model, tools, the skills it must load, its gates.
4. Copy pipeline.json and PIPELINE.md to `.claude/pipelines/<name>/`.
5. Merge the skill map into `.claude/skill-map.json` and AGENTS.md, register the reminder hook.
6. Make sure the token economy rules are present (installs ua5er/marketing-token-economy if not).
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLI = ["npx", "-y", "skills@latest"]
SKILL_MAP = None
for cand in (HERE.parent.parent / "skill-map" / "scripts" / "skill_map.py", HERE / "skill_map.py"):
    if cand.exists():
        SKILL_MAP = cand
        break

MODEL_ID = {"opus": "opus", "sonnet": "sonnet", "haiku": "haiku"}


def run(cmd, dry, cwd):
    print("$", " ".join(cmd))
    if dry:
        return 0
    return subprocess.run(cmd, cwd=cwd).returncode


def agent_md(a, p):
    stages = [s for s in p["stages"] if s["owner_agent"] == a["name"]]
    gates = [s for s in p["stages"] if (s.get("gate") or {}).get("agent") == a["name"]]
    fam = next((k for k in MODEL_ID if k in a.get("model", "").lower()), "sonnet")
    tools = a.get("tools") or (["Read", "Grep", "Glob", "Write"] if a.get("role") in ("critic", "panel") else ["Read", "Grep", "Glob", "Write", "Edit", "Bash"])
    L = ["---", f"name: {a['name']}", f"description: {a.get('description') or a.get('role','') + ' for the ' + p['name'] + ' pipeline'}",
         f"model: {MODEL_ID[fam]}", f"tools: {', '.join(tools)}", "---", "",
         f"You are the {a.get('role', a['name'])} in the `{p['name']}` pipeline. Goal of the pipeline: {p['goal']}", "",
         "Read `.claude/pipelines/%s/PIPELINE.md` first. Work in English. Keep the chat reply to 6 lines: what you did, output paths, open issues." % p["name"], ""]
    if a.get("skills"):
        L += ["## Skills you must load before working", ""] + [f"- `{s}`" for s in a["skills"]] + [
            "", "Load each with the Skill tool if installed, otherwise run `npx skills use <ref>` and follow it. Say in your reply which skills you used.", ""]
    if stages:
        L += ["## Your stages", ""]
        for s in stages:
            L += [f"### {s['name']}", f"- Inputs: {', '.join(s.get('inputs', [])) or '-'}", f"- Outputs: {', '.join(s.get('outputs', []))}",
                  f"- Max takes: {s.get('max_takes', 1)}"]
            if s.get("notes"):
                L.append(f"- Notes: {s['notes']}")
            g = s.get("gate")
            if g:
                L.append(f"- Your work is checked by {g.get('agent', g['type'])} against: " + "; ".join(g.get("criteria", [])))
            L.append("")
    if gates:
        L += ["## Gates you run", "", "You judge other agents' output. You did not make it; be strict and specific. Score each criterion, quote the evidence, and return PASS or FAIL with the fixes ranked.", ""]
        for s in gates:
            g = s["gate"]
            L += [f"### Gate after: {s['name']}", f"- Read: {', '.join(s.get('outputs', []))}", "- Criteria:"] + [f"  - {c}" for c in g.get("criteria", [])] + [
                f"- Pass rule: {g.get('pass_rule')}", f"- Write the verdict to `{g.get('report', '.pipeline/gates/' + s['id'] + '.md')}`", ""]
        if a.get("role") == "panel":
            ce = p.get("consumer_eval") or {}
            L += ["## Virtual users", "", f"Simulate the people who will judge the result: {ce.get('who', '')}.",
                  "Give each persona a name, context and job-to-be-done; answer as them, not as a marketer. Report the distribution, not only the mean, and quote the 3 most common objections.", ""]
    L += ["## Token rules", "", "- Data stays in files; read only the ranges you need.", "- No more takes than the stage allows; stop and report if the gate keeps failing.",
          "- Paid external calls: one cost line first, log them in the ledger.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pipeline")
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-install", action="store_true")
    ap.add_argument("--agent", default="claude-code", help="agent id for `skills add -a`")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    ppath = Path(a.pipeline).resolve()
    if subprocess.run([sys.executable, str(HERE / "pipeline.py"), "render", str(ppath)]).returncode:
        sys.exit("pipeline.py check failed; fix the errors first")
    p = json.loads(ppath.read_text())

    refs = sorted({s for st in p["stages"] for s in st.get("skills", [])} | {s for ag in p["agents"] for s in ag.get("skills", [])})
    te_rules = (p.get("token_economy") or {}).get("rules", "")
    if "marketing-token-economy" in te_rules and not any((root / d / "marketing-token-economy").exists() for d in (".claude/skills", ".agents/skills")):
        refs.append("ua5er/marketing-token-economy@marketing-token-economy")
    if not a.no_install:
        for r in refs:
            if r.startswith("local:") or "@" not in r:
                continue
            src, skill = r.split("@", 1)
            run(CLI + ["add", src, "-s", skill, "-a", a.agent, "-y"], a.dry_run, root)

    pdir = root / ".claude" / "pipelines" / p["name"]
    adir = root / ".claude" / "agents"
    if not a.dry_run:
        pdir.mkdir(parents=True, exist_ok=True)
        adir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ppath, pdir / "pipeline.json")
        shutil.copy2(ppath.parent / "PIPELINE.md", pdir / "PIPELINE.md")
        for ag in p["agents"]:
            (adir / f"{ag['name']}.md").write_text(agent_md(ag, p))
    print(f"agents: {', '.join(x['name'] for x in p['agents'])} -> {adir}")

    if SKILL_MAP:
        run([sys.executable, str(SKILL_MAP), "merge", str(pdir / "pipeline.json" if not a.dry_run else ppath), "--root", str(root)], a.dry_run, root)
        run([sys.executable, str(SKILL_MAP), "install-hook", "--root", str(root)], a.dry_run, root)
    else:
        print("skill-map skill not found next to pipeline-builder; install ua5er/pipeline-builder@skill-map to keep the map")
    print(f"done: .claude/pipelines/{p['name']}/PIPELINE.md")


if __name__ == "__main__":
    main()
