# Agent roster and model routing

Smallest roster that covers the stages. One agent may own several stages. Names are kebab-case.

| Role | Typical model | Does | Never does |
|---|---|---|---|
| main thread (lead) | the user's session model | brief, approach pick, hooks, art direction, final call | volume work |
| researcher | Sonnet + scripts | collect and tag sources, competitor libraries, data pulls | final claims |
| writer / builder | Sonnet | copy, HTML/Figma builds, code, edits from critic notes | judge its own work |
| producer (external) | script wrapper | image, voice, video, copy variants on external models, logged in the ledger | more than max_takes per asset |
| file-ops | Haiku or a script | renames, resizes, exports, contact sheets, specs checks | judgment |
| critic | Opus | independent sign-off per gate: scores criteria, quotes evidence, PASS/FAIL with ranked fixes | make the thing it judges |
| panel | cheap model (personas) or a typed model (distributions) | simulate consumers on the real artefact | predict CTR |
| fact-checker | Sonnet or script | every number and claim against the facts file | add new facts |

## How many critics
- lean: 1 critic, only on the final.
- standard: 1 critic on each key gate (concept, near-final) and the final gate on Opus.
- max: 2 independent critics on key gates (different briefs: one for craft, one for the audience and the brief), reconcile by the lead.
A critic must not share context with the maker: give it the brief, the criteria and the output files only.

## How many virtual users
- Qualitative: 5 personas standard, 10 in max.
- Typed: 30 standard, 200 to 1000 in max when a distribution matters (ads, onboarding).

## Token rules for every agent
- English prompts, 150 to 350 words, inputs as file paths, explicit output path, 6-line reply.
- Data in files; read ranges, not whole folders. Contact sheets instead of many screenshots.
- Max takes per stage; stop and report on repeated gate failure.
- Paid external calls quoted first and logged.
- Fable or the most expensive tier only when the user picks it.
