"""GitHub Issue 본문(마크다운). 본문 한도(65,536자)를 넘으면 여러 조각으로 나눠 첫 조각은 본문, 나머지는 댓글로 올린다."""
from __future__ import annotations

from .collect import Paper

LIMIT = 60000


def _md(s: str) -> str:
    return (s or "").replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ").strip()


def paper_md(p: Paper) -> str:
    star = "⭐ " if p.score else ""
    lines = [f"- {star}**[{_md(p.title)}](https://doi.org/{p.doi})**  ",
             f"  {_md(p.authors_str) or '저자 미상'} · {p.pub_date or '날짜 미상'}"]
    if p.abstract:
        src = f" ({p.abstract_src})" if p.abstract_src not in ("", "Crossref", "OpenAlex") else ""
        lines.append(f"  <details><summary>초록{src}</summary>\n\n  {_md(p.abstract)}\n\n  </details>")
    else:
        lines.append("  _초록 없음_")
    return "\n".join(lines)


def title(day: str, papers: list[Paper]) -> str:
    stars = sum(1 for p in papers if p.score)
    return f"📚 논문 알림 {day} · {len(papers)}편" + (f" (⭐ {stars})" if stars else "")


def body_chunks(day: str, papers: list[Paper], order: list[tuple[str, str]], mention: str = "", notes: list[str] | None = None) -> list[str]:
    head = [f"@{mention}" if mention else "", f"**{day} 새 논문 {len(papers)}편** · ⭐ 키워드 {sum(1 for p in papers if p.score)}편 · "
            f"초록 없음 {sum(1 for p in papers if not p.abstract)}편", ""]
    units: list[str] = []  # 나눌 수 있는 단위: 묶음 제목, 저널 제목, 논문 하나
    for g, label in order:
        ps = [p for p in papers if p.group == g]
        if not ps:
            continue
        units.append(f"## {label} ({len(ps)})")
        by_j: dict[str, list[Paper]] = {}
        for p in ps:
            by_j.setdefault(f"{p.journal} ({p.abbrev})", []).append(p)
        for jname, jps in by_j.items():
            jps.sort(key=lambda p: (p.score, p.pub_date), reverse=True)  # ⭐ 먼저, 그다음 최신순
            units.append(f"### {jname} · {len(jps)}편")
            units += [paper_md(p) for p in jps]
    tail = ["", "---", "<sub>제목을 누르면 DOI 페이지로 갑니다. 초록 출처가 따로 적힌 것은 Crossref 밖에서 보충한 것입니다."
            + ("<br>" + " · ".join(notes) if notes else "") + "</sub>"]
    chunks, cur = [], "\n".join(head)
    for u in units:
        if len(cur) + len(u) + 2 > LIMIT:
            chunks.append(cur)
            cur = "_(이어서)_"
        cur += "\n\n" + u  # 빈 줄로 띄워야 <details> 다음 항목이 깨지지 않는다
    chunks.append(cur + "\n".join(tail))
    return chunks
