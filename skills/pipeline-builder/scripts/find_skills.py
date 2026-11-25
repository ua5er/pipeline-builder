#!/usr/bin/env python3
"""Search the Vercel skills directory (skills.sh) for each pipeline stage and rank candidates.

Uses the official CLI (`npx skills find <query>`) for keyword search and the skills.sh
semantic search endpoint as a second source, merges both, and ranks by relevance and
installs. With --vet it fetches each finalist's SKILL.md through `npx skills use` (no
install) so an agent can read what the skill actually does before choosing it.

Standard library only.

  python3 find_skills.py --query "storyboard for video ads" --query "ugc hook writing" --out .pipeline/skills.json
  python3 find_skills.py --from-pipeline .pipeline/pipeline.json --vet 3 --out .pipeline/skills.json
"""
import argparse, json, math, os, re, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
LINE = re.compile(r"^([\w.-]+/[\w.-]+)@([\w.:-]+)\s+([\d.,]+)([KkMm]?)\s+installs?")
CLI = ["npx", "-y", "skills@latest"]


def _num(n, suf):
    v = float(n.replace(",", ""))
    return int(v * {"k": 1e3, "m": 1e6}.get(suf.lower(), 1))


def cli_find(query, timeout=120):
    env = dict(os.environ, NO_COLOR="1", FORCE_COLOR="0", CI="1")
    try:
        p = subprocess.run(CLI + ["find", query], capture_output=True, text=True, timeout=timeout, env=env)
    except Exception as e:  # npx missing or offline
        print(f"[find] cli failed for {query!r}: {e}", file=sys.stderr)
        return []
    out = []
    for raw in (p.stdout + p.stderr).splitlines():
        m = LINE.match(ANSI.sub("", raw).strip())
        if m:
            out.append({"source": m.group(1), "skill": m.group(2), "installs": _num(m.group(3), m.group(4)), "via": "cli"})
    return out


def api_find(query, limit=10, timeout=30):
    url = "https://skills.sh/api/search?" + urllib.parse.urlencode({"q": query, "limit": limit})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pipeline-builder"}), timeout=timeout) as r:
            data = json.load(r)
    except Exception as e:
        print(f"[find] api failed for {query!r}: {e}", file=sys.stderr)
        return []
    return [{"source": s.get("source"), "skill": s.get("skillId") or s.get("name"), "installs": int(s.get("installs") or 0), "via": "api"}
            for s in data.get("skills", []) if s.get("source")]


def score(c, rank, query):
    words = {w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2}
    name = (c["skill"] + " " + c["source"]).lower()
    overlap = sum(1 for w in words if w in name)
    # keyword CLI hits are usually more on-topic than the semantic endpoint; installs are a weak tiebreak
    return round(3.0 / (1 + rank) + 1.5 * overlap + (1.0 if c["via"] == "cli" else 0) + math.log10(1 + c["installs"]) * 0.7, 3)


def vet(ref, timeout=90):
    env = dict(os.environ, NO_COLOR="1", CI="1")
    try:
        p = subprocess.run(CLI + ["use", ref], capture_output=True, text=True, timeout=timeout, env=env)
    except Exception as e:
        return {"ok": False, "error": str(e)}
    txt = ANSI.sub("", p.stdout)
    m = re.search(r"<SKILL\.md>(.*?)</SKILL\.md>", txt, re.S)
    body = (m.group(1) if m else txt).strip()
    desc = re.search(r"^description:\s*\"?(.+?)\"?\s*$", body, re.M)
    return {
        "ok": bool(m),
        "description": desc.group(1)[:400] if desc else "",
        "chars": len(body),
        "mentions_scripts": bool(re.search(r"scripts?/|\.py\b|\.mjs\b|\.sh\b", body)),
        "skill_md": body[:6000],
    }


def search(queries, limit, vet_n):
    results = {}
    for q in queries:
        merged = {}
        for src in (cli_find(q), api_find(q, limit)):
            for i, c in enumerate(src):
                ref = f"{c['source']}@{c['skill']}"
                s = score(c, i, q)
                if ref not in merged or merged[ref]["score"] < s:
                    merged[ref] = {"ref": ref, **c, "score": s, "url": f"https://skills.sh/{c['source']}/{c['skill']}"}
        ranked = sorted(merged.values(), key=lambda x: -x["score"])[:limit]
        for c in ranked[:vet_n]:
            c["vet"] = vet(c["ref"])
        results[q] = ranked
        print(f"[find] {q!r}: {len(ranked)} candidates" + (f", vetted {min(vet_n, len(ranked))}" if vet_n else ""), file=sys.stderr)
    return results


def queries_from_pipeline(path):
    p = json.loads(Path(path).read_text())
    qs = []
    for st in p.get("stages", []):
        qs += st.get("skill_queries", [])
    return list(dict.fromkeys(qs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", action="append", default=[])
    ap.add_argument("--from-pipeline")
    ap.add_argument("--limit", type=int, default=6)
    ap.add_argument("--vet", type=int, default=0, help="fetch SKILL.md for the top N per query")
    ap.add_argument("--out")
    a = ap.parse_args()
    qs = a.query + (queries_from_pipeline(a.from_pipeline) if a.from_pipeline else [])
    if not qs:
        ap.error("give --query or --from-pipeline")
    res = search(qs, a.limit, a.vet)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, indent=2, ensure_ascii=False))
        print(a.out)
    else:
        for q, cs in res.items():
            print(f"\n## {q}")
            for c in cs:
                d = c.get("vet", {}).get("description", "")
                print(f"- {c['ref']}  ({c['installs']} installs, score {c['score']})" + (f"\n    {d[:160]}" if d else ""))


if __name__ == "__main__":
    main()
