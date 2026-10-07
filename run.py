#!/usr/bin/env python3
"""매일 실행: 수집 → 이미 보낸 논문 제외 → 초록 보충 → 키워드 ⭐ → GitHub Issue 게시 → data/seen.json 갱신.

  python run.py              # GitHub Actions에서 (GITHUB_TOKEN 있으면 Issue 게시)
  python run.py --dry-run    # 내 컴퓨터에서 시험: data/preview.md에 저장, seen.json은 그대로
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from alert import abstracts, config, github, render
from alert.collect import Collector, score

ROOT = Path(__file__).resolve().parent
SEEN = ROOT / "data" / "seen.json"
KEEP_DAYS = 120
log = logging.getLogger("alert")


def load_seen() -> dict:
    try:
        return json.loads(SEEN.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_seen(seen: dict, today: str) -> None:
    cut = (date.fromisoformat(today) - timedelta(days=KEEP_DAYS)).isoformat()
    seen = {k: v for k, v in seen.items() if v >= cut}
    SEEN.parent.mkdir(exist_ok=True)
    SEEN.write_text(json.dumps(dict(sorted(seen.items())), indent=0, ensure_ascii=False) + "\n", encoding="utf-8")


def summary(text: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--days", type=int, help="조회 기간(일). 기본은 alert.toml의 lookback_days")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    cfg = config.load()
    js = config.journals(cfg)
    if not js:
        log.error("저널이 하나도 없습니다. Actions → '① 설정'을 먼저 실행하세요.")
        return 1
    today = date.today().isoformat()
    since = date.today() - timedelta(days=args.days or int(cfg.get("lookback_days", 10)))
    log.info(f"저널 {len(js)}종, {since} 이후 수집")
    col = Collector()
    papers = col.collect_all(js, since)
    seen = load_seen()
    new = [p for p in papers if p.doi not in seen]
    log.info(f"수집 {len(papers)}편 · 새 논문 {len(new)}편" + (f" · 소스 오류 {', '.join(col.errors)}" if col.errors else ""))

    stats = abstracts.fill(new) if new else {}
    kws = cfg.get("keywords", [])
    only = set(cfg.get("keyword_only_groups", []))
    for p in new:
        p.score = score(p, kws)
    shown = [p for p in new if p.group not in only or p.score]
    for p in new:
        seen[p.doi] = today  # 키워드에 안 맞아 뺀 논문도 다시 보지 않는다

    notes = []
    if col.errors:
        notes.append("일부 소스 조회 실패: " + ", ".join(col.errors[:10]))
    if not os.environ.get("ELSEVIER_API_KEY"):
        notes.append("Elsevier 키 없음(Elsevier 저널 초록이 비어 있을 수 있음)")
    url = ""
    if shown:
        chunks = render.body_chunks(today, shown, config.group_order(cfg), os.environ.get("GITHUB_REPOSITORY_OWNER", ""), notes)
        url = github.post(render.title(today, shown), chunks, ROOT / "data" / "preview.md" if args.dry_run or not os.environ.get("GITHUB_TOKEN") else None)
    else:
        log.info("보낼 새 논문 없음 → Issue를 만들지 않음")
    if not args.dry_run:
        save_seen(seen, today)
    summary(f"### {today}\n- 저널 {len(js)}종 · 수집 {len(papers)}편 · 새 논문 {len(new)}편 · 게시 {len(shown)}편\n"
            f"- 초록 보충: {stats}\n" + (f"- Issue: {url}\n" if url else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
