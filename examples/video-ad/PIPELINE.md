# Pipeline: video-ad

**Goal:** One 30-second vertical video ad for a subscription photo-editing app, ready to launch as a Meta and TikTok test  
**Type:** video ad · **Budget mode:** standard · **Estimated cost:** $9.03 expected, $23.48 if every take is used (Claude tokens + external APIs)

## How consumers judge the result

Who: US adults 25-45 who edit photos on their phone and scroll Reels or TikTok with sound off

- stops scrolling in the first 1-2 seconds
- understands what the app does without sound
- believes the before/after is real
- sees what they gain and that it is quick
- knows the next step (download, free trial)

Real metrics after launch: thumb-stop rate (3 s views / impressions), hold rate to 15 s, CTR, cost per trial

## Stages

| # | Stage | Human team equivalent | Owner (model) | Skills | Gate |
|---|---|---|---|---|---|
| 1 | Competitor and audience research | strategist with a researcher | researcher (sonnet) | ua5er/user-acquisition-skills@competitor-creative-parser, agricidaniel/claude-ads@ads-competitor | script x1 () |
| 2 | Concepts and hooks | creative director with strategist | writer (sonnet) | ua5er/user-acquisition-skills@market-to-creative-brief, mbfinotti/advertising-skills@ad-hook-analyzer | panel x30 (panel) |
| 3 | Script, shot list and on-screen text | scriptwriter, reviewed by the creative director and a claims check | writer (sonnet) | mbfinotti/advertising-skills@ugc-ad-scripts, gooseworks-ai/goose-skills@write-video-ad-script | critic x1 (critic) |
| 4 | Storyboard with first-frame prompts | storyboard artist | writer (sonnet) | 101-skills/superpowers@storyboard-creation | none |
| 5 | Asset production: AI shots, screen recordings, voice | producer with a motion designer | producer (sonnet) | 101-skills/superpowers@ai-video-generation | human x1 () |
| 6 | Edit, motion, captions, sound | editor and sound designer | builder (sonnet) | heygen-com/hyperframes@hyperframes | panel x30 (panel) |
| 7 | Platform specs QA | ad ops QA | file-ops (haiku) | - | critic x1 (critic) |

## Gates

**Competitor and audience research** · script x1 · pass: script exits 0
- at least 40 ads tagged
- every ad has hook type, format and claim fields

**Concepts and hooks** · panel x30 · pass: lead picks the 2 concepts with the largest gap over the rest; drop any concept under 50% WHAT
- states WHAT the app does
- states the GAIN
- would keep watching

**Script, shot list and on-screen text** · critic x1 · pass: all criteria pass
- hook works sound-off in 2 s
- one promise, proven on screen
- every claim is in facts.md
- 30 s or less at natural pace
- platform policy safe (no before/after body claims)

**Asset production: AI shots, screen recordings, voice** · human x1 · pass: owner approves the contact sheet
- shots match the storyboard
- no AI artefacts on hands, faces or text
- the app UI is real

**Edit, motion, captions, sound** · panel x30 · pass: at least 70% state WHAT and GAIN; first-frame stop beats the concept-stage baseline
- WHAT and GAIN stated after watching
- stop rate on the first frame
- trust in the result

**Platform specs QA** · critic x1 · pass: PASS from the Opus critic, then the owner sees the final before launch
- final cut matches the approved script
- specs file is all green
- no claim outside facts.md
- the ad would pass a creative director's review

## Agents

| Agent | Role | Model | Skills |
|---|---|---|---|
| researcher | researcher | sonnet | ua5er/user-acquisition-skills@competitor-creative-parser, agricidaniel/claude-ads@ads-competitor |
| writer | writer | sonnet | ua5er/user-acquisition-skills@market-to-creative-brief, mbfinotti/advertising-skills@ad-hook-analyzer, mbfinotti/advertising-skills@ugc-ad-scripts, gooseworks-ai/goose-skills@write-video-ad-script, 101-skills/superpowers@storyboard-creation |
| producer | producer | sonnet | 101-skills/superpowers@ai-video-generation |
| builder | builder | sonnet | heygen-com/hyperframes@hyperframes |
| file-ops | file-ops | haiku | - |
| critic | critic | opus | agricidaniel/claude-ads@ads-creative |
| panel | panel | haiku | ua5er/user-acquisition-skills@synthetic-audience-panel, ua5er/user-acquisition-skills@creative-preflight-panel |

## Token economy

- Rules: ua5er/marketing-token-economy
- Budget: $25, ask above $2
- Ledger: tools/cost_ledger.py
- Max takes per asset as set per stage; draft cheap, approve, render once.

## Skill map

| Task | Triggers | Skills |
|---|---|---|
| video ad | video ad, ugc ad, reel ad, tiktok ad, ролик, видеореклам | mbfinotti/advertising-skills@ugc-ad-scripts, mbfinotti/advertising-skills@ad-hook-analyzer, heygen-com/hyperframes@hyperframes |
| competitor ad research | competitor ads, ad library, конкурент | ua5er/user-acquisition-skills@competitor-creative-parser |
| ad audience test | panel, audience test, виртуальн, панел | ua5er/user-acquisition-skills@synthetic-audience-panel, ua5er/user-acquisition-skills@creative-preflight-panel |
