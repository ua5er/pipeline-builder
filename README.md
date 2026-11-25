# Pipeline Builder

One prompt in, a production pipeline of AI agents out.

You give a goal: "a site generator", "one 30-second video ad", "a series of SEO articles". The skill plans it the way a strong human team would: which stages, who reviews what, and whether real consumers judge the result and how. Then it picks a skill for every stage from the [Vercel skills directory](https://skills.sh) (`npx skills find`), creates the subagents that run those skills, puts critics and virtual-user panels where a team would put reviews, adds token-economy limits, and writes a skill map into your project so the agent never forgets which skill to use.

Two skills:

| Skill | What it does |
|---|---|
| [`pipeline-builder`](skills/pipeline-builder/SKILL.md) | Goal → team stages → consumer evaluation → skills per stage (searched and read before choosing) → agents, critics, panels → `pipeline.json`, `PIPELINE.md`, cost estimate → installs skills and writes `.claude/agents/*.md` |
| [`skill-map`](skills/skill-map/SKILL.md) | Keeps "which skill for which task" in `.claude/skill-map.json` and an `AGENTS.md` table, plus a prompt hook that reminds the agent of the matching skills. Works on its own too |

## Install

```bash
npx skills add ua5er/pipeline-builder
```

Then ask your agent: *"Build a pipeline for one 30-second video ad for our app"*.

## What you get in the project

```
.claude/pipelines/<name>/PIPELINE.md   stages, gates, agents, cost, skill map
.claude/pipelines/<name>/pipeline.json the same, machine-readable
.claude/agents/<agent>.md              one file per agent: model, skills it must load, stages, gates
.claude/skills/...                     the chosen skills, installed at project level
.claude/skill-map.json + AGENTS.md     task → skills table the agent reads every session
.claude/settings.json                  UserPromptSubmit hook: matching prompt → "load these skills"
```

## How it decides

1. **Human team first.** [`team-patterns.md`](skills/pipeline-builder/references/team-patterns.md) covers websites and site generators, video ads, static ad batches, landing pages, SEO articles, social posts, app screens, brand identity, research reports, software features and email sequences. Each review point in a real team becomes a gate.
2. **Consumers.** If people outside the team decide whether it worked (ads, pages, posts, apps), the pipeline records who they are, how they judge in the first seconds and later, and which real metrics prove it after launch ([`consumer-evaluation.md`](skills/pipeline-builder/references/consumer-evaluation.md)).
3. **Skills from the open directory.** `find_skills.py` searches skills.sh through the official CLI and the semantic search endpoint, ranks candidates, and fetches their `SKILL.md` with `npx skills use` (no install) so the agent reads what a skill does before choosing it.
4. **Agents, critics, panels.** Makers on mid-tier models, mechanical work on the cheapest model or a script, an independent critic on the strongest model for every key gate, and virtual users (5 to 10 personas, or 30 to 1000 typed answers) where the consumer first meets the result. Every stage has a takes limit.
5. **Token economy by default.** Budget modes `lean`, `standard`, `max`; an expected and worst-case cost before anything runs; [ua5er/marketing-token-economy](https://github.com/ua5er/marketing-token-economy) rules installed if the project has none. Principle: downgrade the work, never the final gate.

## Example

[`examples/video-ad`](examples/video-ad/PIPELINE.md): one 30-second vertical ad for a subscription photo app. 7 stages, 7 agents, 12 skills from skills.sh, two 30-person panels, an Opus critic on the script and the final, a human approval on the AI shots. Expected cost about $9, worst case about $23.

## Scripts (standard library Python, no dependencies)

```bash
python3 skills/pipeline-builder/scripts/find_skills.py --query "video ad hooks" --vet 2
python3 skills/pipeline-builder/scripts/pipeline.py check|render|cost .pipeline/pipeline.json
python3 skills/pipeline-builder/scripts/apply.py .pipeline/pipeline.json --root . --dry-run
python3 skills/skill-map/scripts/skill_map.py add --task "..." --triggers "..." --skills "..."
```

Skills you install from the directory run with your agent's permissions. Read them first; the `--vet` step exists for that.

## Author

Vlad Yasinski, growth and AI marketing systems for apps. Telegram [@ua5er](https://roimobi.com/tg?src=gh-pipeline-builder) · [roimobi.com](https://www.roimobi.com) · [LinkedIn](https://www.linkedin.com/in/vlad-yasinski-ua5er/)

MIT licence.
