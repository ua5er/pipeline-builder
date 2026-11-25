#!/usr/bin/env python3
"""Validate a pipeline.json, estimate its token cost, and render PIPELINE.md.

  python3 pipeline.py check  .pipeline/pipeline.json
  python3 pipeline.py render .pipeline/pipeline.json          # writes PIPELINE.md next to it
  python3 pipeline.py cost   .pipeline/pipeline.json

Schema: see references/pipeline-schema.md. Standard library only.
"""
import json, sys
from pathlib import Path

# USD per 1M tokens (input, output). Edit when provider prices change.
PRICES = {
    "haiku": (1.0, 5.0),
    "sonnet": (2.0, 10.0),
    "opus": (4.0, 20.0),
    "fable": (10.0, 50.0),
    "script": (0.0, 0.0),
    "external": (0.0, 0.0),
}
IN_SHARE = 0.8  # agent work is input-heavy (files, context); output share 0.2
BUDGET_RUNS = {"lean": 1, "standard": 1, "max": 1}
CRITIC_MIN = {"lean": 1, "standard": 1, "max": 2}
PANEL_MIN = {"lean": 0, "standard": 30, "max": 200}


def fam(model):
    m = (model or "").lower()
    for k in PRICES:
        if k in m:
            return k
    return "opus"


def usd(model, tokens):
    i, o = PRICES[fam(model)]
    return tokens / 1e6 * (IN_SHARE * i + (1 - IN_SHARE) * o)


def stage_cost(st, agents, worst=False):
    """Expected cost = one take; worst = every take used. Panel est_tokens is for the whole panel."""
    model = agents.get(st.get("owner_agent"), {}).get("model", st.get("model", "sonnet"))
    takes = max(1, int(st.get("max_takes", 1))) if worst else 1
    total = usd(model, st.get("est_tokens", 0)) * takes
    g = st.get("gate") or {}
    gm = agents.get(g.get("agent"), {}).get("model", g.get("model", "opus"))
    n = 1 if g.get("type") == "panel" else max(1, int(g.get("count", 1)))
    total += usd(gm, g.get("est_tokens", 0)) * n * takes
    return total + float(st.get("external_usd", 0)) * takes


def check(p):
    errs, warns = [], []
    agents = {a["name"]: a for a in p.get("agents", [])}
    mode = p.get("budget_mode", "standard")
    for k in ("name", "goal", "goal_type", "stages", "agents", "token_economy", "skill_map"):
        if k not in p:
            errs.append(f"missing top-level field: {k}")
    if p.get("consumer_dependent") and not p.get("consumer_eval"):
        errs.append("consumer_dependent is true but consumer_eval is empty")
    stages = p.get("stages", [])
    if not stages:
        errs.append("no stages")
    has_panel = False
    for i, st in enumerate(stages):
        sid = st.get("id", f"#{i}")
        if st.get("owner_agent") not in agents:
            errs.append(f"{sid}: owner_agent {st.get('owner_agent')!r} not in agents")
        if not st.get("outputs"):
            errs.append(f"{sid}: no outputs (every stage writes files)")
        if not st.get("skills") and not st.get("no_skill_reason"):
            warns.append(f"{sid}: no skills and no no_skill_reason")
        g = st.get("gate")
        if not g:
            if not st.get("no_gate_reason"):
                warns.append(f"{sid}: no gate and no no_gate_reason")
            continue
        if g.get("type") not in ("critic", "panel", "script", "human"):
            errs.append(f"{sid}: gate.type must be critic|panel|script|human")
        if g.get("type") == "critic":
            ga = agents.get(g.get("agent"), {})
            if g.get("agent") == st.get("owner_agent"):
                errs.append(f"{sid}: critic is the same agent as the maker")
            if fam(ga.get("model")) in ("haiku",):
                warns.append(f"{sid}: critic on Haiku; judgment gates belong on Opus or Sonnet")
            if int(g.get("count", 1)) < CRITIC_MIN[mode]:
                warns.append(f"{sid}: {mode} mode expects at least {CRITIC_MIN[mode]} critic(s)")
        if g.get("type") == "panel":
            has_panel = True
            if int(g.get("count", 0)) < PANEL_MIN[mode]:
                warns.append(f"{sid}: panel of {g.get('count')} is below {PANEL_MIN[mode]} for {mode} mode")
        if not g.get("criteria"):
            errs.append(f"{sid}: gate has no criteria")
        if not g.get("pass_rule"):
            errs.append(f"{sid}: gate has no pass_rule")
    if p.get("consumer_dependent") and not has_panel and mode != "lean":
        warns.append("consumer-dependent result without any panel gate (virtual users)")
    if stages:
        last = stages[-1].get("gate") or {}
        la = agents.get(last.get("agent"), {})
        if last.get("type") not in ("critic", "human") or (last.get("type") == "critic" and fam(la.get("model")) != "opus"):
            warns.append("final gate should be an Opus critic or a human: downgrade the work, never the final gate")
    for a in p.get("agents", []):
        if fam(a.get("model")) == "fable":
            warns.append(f"agent {a['name']}: Fable is reserved for when the user picks it")
        if not a.get("skills") and a.get("role") not in ("file-ops",):
            warns.append(f"agent {a['name']}: no skills assigned")
    te = p.get("token_economy", {})
    if not te.get("rules"):
        errs.append("token_economy.rules missing (install ua5er/marketing-token-economy or name your rules file)")
    total = sum(stage_cost(s, agents) for s in stages)
    worst = sum(stage_cost(s, agents, True) for s in stages)
    cap = float(te.get("budget_usd", 0) or 0)
    if cap and total > cap:
        warns.append(f"expected ${total:.2f} is above budget_usd ${cap:.2f}")
    elif cap and worst > cap:
        warns.append(f"worst case ${worst:.2f} (all takes used) is above budget_usd ${cap:.2f}; stop at the cap")
    if total > float(te.get("ask_above_usd", 2)):
        warns.append(f"expected ${total:.2f} is above ask_above_usd; quote it to the user before running")
    if not p.get("skill_map"):
        errs.append("skill_map empty: record which skills serve which task")
    p["_worst"] = worst
    return errs, warns, total


def render(p, total):
    agents = {a["name"]: a for a in p["agents"]}
    L = [f"# Pipeline: {p['name']}", "", f"**Goal:** {p['goal']}  ", f"**Type:** {p['goal_type']} · **Budget mode:** {p.get('budget_mode','standard')} · **Estimated cost:** ${total:.2f} expected, ${p.get('_worst', total):.2f} if every take is used (Claude tokens + external APIs)", ""]
    ce = p.get("consumer_eval") or {}
    if p.get("consumer_dependent"):
        L += ["## How consumers judge the result", "", f"Who: {ce.get('who','')}", ""]
        L += [f"- {x}" for x in ce.get("how_they_judge", [])]
        if ce.get("metrics"):
            L += ["", "Real metrics after launch: " + ", ".join(ce["metrics"])]
        L.append("")
    L += ["## Stages", "", "| # | Stage | Human team equivalent | Owner (model) | Skills | Gate |", "|---|---|---|---|---|---|"]
    for i, st in enumerate(p["stages"], 1):
        a = agents.get(st["owner_agent"], {})
        g = st.get("gate") or {}
        gate = f"{g.get('type')} x{g.get('count',1)} ({g.get('agent','')})" if g else "none"
        L.append(f"| {i} | {st['name']} | {st.get('human_team_equivalent','')} | {st['owner_agent']} ({a.get('model','')}) | {', '.join(st.get('skills', [])) or '-'} | {gate} |")
    L += ["", "## Gates", ""]
    for st in p["stages"]:
        g = st.get("gate")
        if g:
            L += [f"**{st['name']}** · {g['type']} x{g.get('count',1)} · pass: {g.get('pass_rule','')}"]
            L += [f"- {c}" for c in g.get("criteria", [])] + [""]
    L += ["## Agents", "", "| Agent | Role | Model | Skills |", "|---|---|---|---|"]
    for a in p["agents"]:
        L.append(f"| {a['name']} | {a.get('role','')} | {a.get('model','')} | {', '.join(a.get('skills', [])) or '-'} |")
    te = p.get("token_economy", {})
    L += ["", "## Token economy", "", f"- Rules: {te.get('rules')}", f"- Budget: ${te.get('budget_usd','n/a')}, ask above ${te.get('ask_above_usd', 2)}",
          f"- Ledger: {te.get('ledger', 'tools/cost_ledger.py')}", "- Max takes per asset as set per stage; draft cheap, approve, render once.", ""]
    L += ["## Skill map", "", "| Task | Triggers | Skills |", "|---|---|---|"]
    for m in p.get("skill_map", []):
        L.append(f"| {m['task']} | {', '.join(m.get('triggers', []))} | {', '.join(m.get('skills', []))} |")
    return "\n".join(L) + "\n"


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("check", "render", "cost"):
        print(__doc__)
        sys.exit(2)
    path = Path(sys.argv[2])
    p = json.loads(path.read_text())
    errs, warns, total = check(p)
    if sys.argv[1] == "cost":
        agents = {a["name"]: a for a in p.get("agents", [])}
        for st in p.get("stages", []):
            print(f"{st.get('id')}: ${stage_cost(st, agents):.3f} expected, ${stage_cost(st, agents, True):.3f} worst")
        print(f"total: ${total:.2f} expected, ${p['_worst']:.2f} worst")
        return
    for e in errs:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    print(f"estimated cost ${total:.2f} expected, ${p['_worst']:.2f} worst; {len(errs)} errors, {len(warns)} warnings")
    if sys.argv[1] == "render":
        out = path.parent / "PIPELINE.md"
        out.write_text(render(p, total))
        print(out)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
