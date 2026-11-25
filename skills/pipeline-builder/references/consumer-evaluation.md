# Is the result judged by consumers, and how

## Decide consumer_dependent
True when a person outside the team decides whether the result worked: ads, landing pages, websites, posts, emails, app screens, onboarding, paywalls, product names, articles meant to rank and convert.
False for internal tools, data pipelines, refactors, reports for one stakeholder (then the stakeholder is the final gate, not a panel).

## How consumers judge (write the ones that apply into consumer_eval.how_they_judge)
First 1 to 3 seconds: do I stop, what is it, is it for me, do I trust it.
Next 10 to 30 seconds: what do I gain, what does it cost me (money, effort, risk), what is the proof, what do I do next.
Later: did it keep its promise (retention, refunds, reviews, returning visits).
Format-specific: video (hook, hold, sound-off readability), ads (thumb-stop, clarity of offer, native feel), pages (message match, one CTA, load speed), articles (answers the query fast, depth, credibility), app screens (effort, clarity of next step, price fairness).

## Real metrics after launch (consumer_eval.metrics)
Ads: thumb-stop rate, hold rate, CTR, CPA, ROAS. Pages: conversion rate of the primary action, bounce, scroll depth. Content: impressions, clicks, time on page, saves, comments. Apps: step completion, trial start, paywall conversion, D1/D7 retention. Email: open, click, conversion, unsubscribe.

## Virtual-user panels
Where: where the consumer first meets the result. Usually twice in standard mode: on concepts (cheap, catches wrong angles early) and on the near-final (catches clarity and trust issues). In lean mode skip panels; in max add one after the final edit.

Two kinds:
1. Qualitative personas, 5 to 10. Each has a name, context, job-to-be-done, objections and taste. They react in their own words. Run on a cheap model or a cheap external vision model for images. Output: the three most common objections and what each persona would do next.
2. Typed panel, 30 to 1000 answers. A structured model answers fixed yes/no/score questions per synthetic person from a cohort built to match the audience. Code computes the scores and thresholds. Output: distributions and gaps between variants.

Rules:
- Freeze the questionnaire across runs; regenerate personas every run.
- Show the real artefact (screenshot, frame, page text), not a description of it.
- Compare variants and report gaps; never present a panel score as a CTR or conversion forecast.
- A pass rule names numbers, e.g. "at least 4 of 5 personas state WHAT and GAIN correctly; clarity mean >= 4.0/5; no persona flags it as a scam".
- If scores stay flat across runs while you change the creative, the inputs are the problem (missing proof, placeholder facts), not the creative.
- Max 3 panel rounds per asset, then the lead decides.

## Critics are not panels
A critic is an expert reviewer (creative director, editor, QA lead) checking craft, claims and the brief. A panel is the audience. Consumer-dependent work needs both: the critic first (cheap fixes), the panel second (audience truth), and the final call by the strongest model or the human.
