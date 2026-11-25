---
name: pipeline-builder
description: Turn one goal prompt into a production pipeline for AI agents, the way a human team would run it. Maps the stages and review gates a real team uses, decides whether consumers judge the result and how, picks a skill for every stage from the Vercel skills directory (skills.sh, `npx skills find`), creates the subagents that run those skills, places critics and virtual-user panels, adds token-economy limits, and writes a skill map into the project so the agent never forgets which skill serves which task. Use when the user says "build a pipeline", "set up agents for", "how should agents make", "pipeline for a website generator / video ad / landing page / article series / app screen", "which skills do I need for", or gives a goal and wants the best possible result from a chain of agents.
---

# Pipeline builder

One prompt in, a working pipeline out: `PIPELINE.md` + `pipeline.json`, installed skills, `.claude/agents/*.md`, a skill map in `AGENTS.md`, and a hook that reminds the agent of the right skills.

Principle: **downgrade the work, never the final gate.** The strongest model decides and signs off; cheaper models, scripts and external models do the volume. Quality comes from the gates, not from running everything on the top model.

## Step 0. Brief and budget (main thread)

1. Rewrite the goal as a short English brief: goal, deliverable, audience, constraints, what "done" looks like, facts source, cost cap. If the user wrote in another language, translate it yourself.
2. Pick a budget mode and say it in one line:
   - `lean`: one critic, no panel, max 2 takes. For internal or throwaway work.
   - `standard` (default): one critic per key gate, one virtual-user panel before the final, max 3 takes.
   - `max`: two independent critics on key gates, panels before and after the final edit, larger panels. Only when the user asks for the best possible result and accepts the cost.
3. Token economy is on by default. If the project has no rules, `apply.py` installs `ua5er/marketing-token-economy`. If the TokenEconomizer plugin is available, recommend enabling it for long coding pipelines.
4. Facts: if the result makes claims (numbers, cases, prices), name one facts file as the only source. Agents never invent facts.

## Step 1. Model the human team

Read `references/team-patterns.md` and find the closest goal type (or combine two). Write down how a strong human team would do it: roles, stages in order, hand-offs, and the review points where a lead, an editor, QA, legal or a client signs off. Keep the review points. They become your gates.

## Step 2. Does a consumer judge the result?

Read `references/consumer-evaluation.md`. Decide `consumer_dependent` (true for ads, landing pages, posts, apps, onboarding, emails, most content; false for internal tooling, data pipelines, refactors).
If true, write `consumer_eval`: who the consumers are, how they judge in the first seconds and later (clarity, trust, "is this for me", effort, price, taste), and which real metrics prove it after launch. This decides where panels go and what they score.

## Step 3. Find a skill for every stage

For each stage write 1 to 3 search queries (task words, not tool names) into `skill_queries`, then:

```bash
python3 scripts/find_skills.py --from-pipeline .pipeline/pipeline.json --vet 3 --out .pipeline/skills.json
```

Read the vetted `SKILL.md` texts in `.pipeline/skills.json`, not just the names. Choose per stage by: does it do this exact job, is it specific (not a generic "marketing" skill), does it bring scripts or checklists, installs as a weak tiebreak. Prefer skills already in the project (`local:<name>`). Reject skills that only restate common sense. If nothing fits, write `no_skill_reason` and give the stage a checklist in `notes`. Record the choice and one-line reason in `skills_rationale`.

## Step 4. Agents, critics, panels

Read `references/agent-roster.md`. Build the smallest roster that covers the stages:
- The main thread keeps strategy, the approach pick, art direction and the final call.
- Makers: builder or writer on Sonnet; mechanical work on Haiku or a script; drafts of images, voice, video or copy variants on external models through one wrapper with a ledger.
- Critics: a separate agent, never the maker, on Opus for judgment gates. One per key gate in `standard`, two independent ones in `max`. They read files and return PASS or FAIL with ranked fixes.
- Virtual users (panel): only when `consumer_dependent`. Place them where the consumer first meets the result (concept, then near-final). Size by stake: 5 to 10 rich personas on a cheap model for qualitative objections; 30 to 1000 typed answers on a structured model when you need a distribution. Fresh personas each run, frozen questionnaire, score gaps between variants, never predict CTR.
- Script gates for anything a script can check: sizes, lint, links, facts, word counts, contrast, banned phrases.
Every gate has criteria and a pass rule, and every stage has `max_takes`. If a gate fails `max_takes` times, stop and ask the human.

## Step 5. Write and check the pipeline

Write `.pipeline/pipeline.json` per `references/pipeline-schema.md` (copy `assets/pipeline.template.json`). Then:

```bash
python3 scripts/pipeline.py check .pipeline/pipeline.json
python3 scripts/pipeline.py render .pipeline/pipeline.json   # PIPELINE.md + cost estimate
```

Fix every ERROR. Read the WARNs and fix or justify them. Quote the estimated cost to the user in one line; above `ask_above_usd` wait for a yes.

## Step 6. Apply to the project

```bash
python3 scripts/apply.py .pipeline/pipeline.json --root . --dry-run   # show what will be installed and written
python3 scripts/apply.py .pipeline/pipeline.json --root .
```

This installs the skills at project level (`npx skills add <repo> -s <skill> -a claude-code -y`), writes `.claude/agents/*.md` (each lists the skills it must load and the gates it runs), copies the pipeline to `.claude/pipelines/<name>/`, merges the skill map into `.claude/skill-map.json` and `AGENTS.md`, and registers the `skill_router.py` hook (UserPromptSubmit) that injects the matching skills when a prompt mentions the task.

## Step 7. Pilot, then run

Run the pipeline on one item first. Show the human the first real output (visuals always) before a batch. After the pilot, update gates, takes and the cost estimate from what actually happened, then run the batch. End every run with one line: `Tokens: Claude <n> ($x) · External <units> ($y) · Total $z`, and a HANDOFF.md if the work continues in another chat.

## Output to the user

Six lines at most: the pipeline name and stage count, the skills chosen (with one reason each for the non-obvious ones), the gates (critics and panel sizes), the estimated cost, what was installed or written, and the first command to run the pilot.

## Rules that came from real failures

- Agents ignore skills unless the brief names them and the agent must say which ones it used. `apply.py` writes both into every agent file.
- Visuals: no default "AI look" (dark background with purple glow, glass cards). Give the human two art directions and show work before publishing.
- Claims only from the facts file. A critic checks every number against it.
- Check finished results, never started jobs: one research workflow re-ran three times this way and burned about 100M tokens.
- No large fan-outs by default. Pilot 1 to 2 items, cap spend, quote paid batches.
- Score gaps between variants, not absolute predictions. A panel cannot fix missing real facts: if scores stay flat across runs, the problem is the inputs.

## Author

Vlad Yasinski, Telegram [@ua5er](https://roimobi.com/tg?src=skill-pipeline-builder) · [roimobi.com](https://www.roimobi.com)
