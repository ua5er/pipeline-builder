# pipeline.json schema

```jsonc
{
  "name": "video-ad",                       // kebab-case, used for .claude/pipelines/<name>/
  "goal": "One 30 s video ad for ...",
  "goal_type": "video ad",                  // from team-patterns.md
  "budget_mode": "standard",                // lean | standard | max
  "facts_file": "facts.md",                 // only source of claims, or null
  "consumer_dependent": true,
  "consumer_eval": {
    "who": "US women 25-45 who edit photos on their phone",
    "how_they_judge": ["stops in 1-2 s", "understands what the app does", "trusts the before/after"],
    "metrics": ["thumb-stop rate", "hold rate", "CTR", "CPA"]
  },
  "stages": [
    {
      "id": "concept",
      "name": "Concepts and hooks",
      "human_team_equivalent": "creative director with strategist",
      "owner_agent": "writer",
      "inputs": ["research/snapshot.md"],
      "outputs": [".pipeline/out/concepts.md"],
      "skill_queries": ["video ad hooks", "creative concepts paid social"],
      "skills": ["owner/repo@skill", "local:brand-voice"],
      "skills_rationale": {"owner/repo@skill": "hook formulas with examples"},
      "no_skill_reason": null,
      "max_takes": 2,
      "est_tokens": 60000,                  // per take, maker
      "external_usd": 0,                    // per take, paid APIs
      "notes": "5 concepts, one line each",
      "gate": {
        "type": "critic",                   // critic | panel | script | human
        "agent": "critic",
        "count": 1,                         // critics, or panel size
        "est_tokens": 30000,                // per critic per take
        "criteria": ["hook readable sound-off", "one clear promise", "no claim outside facts.md"],
        "pass_rule": "all criteria pass; lead picks 1-2 concepts",
        "report": ".pipeline/gates/concept.md"
      }
    }
  ],
  "agents": [
    {"name": "writer", "role": "writer", "model": "sonnet", "skills": ["owner/repo@skill"]},
    {"name": "critic", "role": "critic", "model": "opus", "skills": ["local:brand-voice"]},
    {"name": "panel", "role": "panel", "model": "haiku", "skills": []}
  ],
  "token_economy": {
    "rules": "ua5er/marketing-token-economy",
    "ledger": "tools/cost_ledger.py",
    "budget_usd": 15,
    "ask_above_usd": 2
  },
  "skill_map": [
    {"task": "video ad", "triggers": ["video ad", "ugc ad", "ролик"], "skills": ["owner/repo@skill"], "agents": ["writer", "critic"]}
  ]
}
```

Checks run by `scripts/pipeline.py check`:
- required fields; every stage has an owner in `agents`, outputs, skills or `no_skill_reason`, a gate or `no_gate_reason`;
- gates have criteria and a pass rule; a critic is never the maker; critics not on Haiku;
- consumer-dependent work has `consumer_eval` and (outside lean) a panel gate;
- the last gate is an Opus critic or a human;
- critic and panel counts meet the budget mode;
- Fable agents flagged; agents without skills flagged;
- the cost estimate is compared with `budget_usd` and `ask_above_usd`;
- `skill_map` is not empty.
