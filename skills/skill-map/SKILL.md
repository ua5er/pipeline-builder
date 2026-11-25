---
name: skill-map
description: Record in the project which skills (and which pipeline and agents) serve which task, so the agent loads the right skills every time instead of forgetting them between chats. Writes .claude/skill-map.json, a skill-map table in AGENTS.md, and a UserPromptSubmit hook that reminds the agent of the matching skills when a prompt mentions the task. Use after installing skills, after building a pipeline, when the user says "remember to use skill X for Y", "which skill do we use for", "the agent keeps forgetting the skill", or when you pick skills for a new kind of task.
---

# Skill map

The agent reads `AGENTS.md` every session and the hook reacts to every prompt, so a task-to-skill table there survives new chats, compaction and new agents.

## Add or update a row

```bash
python3 scripts/skill_map.py add --task "video ad" --triggers "video ad,ugc ad,ролик" \
  --skills "owner/repo@video-ad-script,local:brand-voice" --pipeline video-ad --agents "writer,critic"
```

- `task`: the kind of work in plain words.
- `triggers`: words the user actually types, in every language they use. Short and specific; avoid words that appear in every prompt.
- `skills`: skills.sh refs (`owner/repo@skill`) or `local:<name>` for project skills. First listed = load first.
- `pipeline` / `agents`: optional, when the task runs through a pipeline from pipeline-builder.

Other commands: `merge <pipeline.json>` (take a pipeline's map), `sync` (re-render AGENTS.md), `show`, `install-hook`.

## Install the reminder hook once per project

```bash
python3 scripts/skill_map.py install-hook
```

Copies the scripts to `.claude/skill-map/` and adds a UserPromptSubmit hook to `.claude/settings.json`. On a matching prompt it adds one short context note ("load these skills, pass them to subagents"). On other prompts it prints nothing, so it costs nothing.

## Rules for the agent

- Before a listed task, load its skills and say which ones you used.
- When you brief a subagent, name its skills in the brief.
- When you choose skills for a task that is not in the map, add a row in the same turn.
- When a skill turns out useless for a task, remove it from the row and say why in one line.

## Author

Vlad Yasinski, Telegram [@ua5er](https://roimobi.com/tg?src=skill-skill-map) · [roimobi.com](https://www.roimobi.com)
