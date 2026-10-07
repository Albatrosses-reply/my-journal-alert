#!/usr/bin/env python3
"""설정 마법사. Actions → '① 설정' 실행 버튼의 입력값(환경변수)으로 alert.toml을 다시 쓴다.

추가 저널은 이름이나 ISSN으로 Crossref에서 찾아 넣는다. 찾은 결과는 실행 요약에 표로 보여 준다.
내 컴퓨터에서: REALESTATE=핵심+확장 ECONOMICS=false ... python setup.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from alert.util import Http

ROOT = Path(__file__).resolve().parent
CROSSREF_J = "https://api.crossref.org/journals"
ISSN_RE = re.compile(r"^\d{4}-?\d{3}[\dXx]$")
REALESTATE = {"핵심+확장": ["realestate_core", "realestate_ext"], "핵심만": ["realestate_core"], "안 받음": []}
GENERAL = [("ECONOMICS", "economics"), ("FINANCE", "finance"), ("MANAGEMENT", "management")]


def env_bool(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("true", "1", "yes", "y")


def split_list(s: str) -> list[str]:
    return [x.strip() for x in re.split(r"[,;\n]", s or "") if x.strip()]


def abbrev_of(title: str) -> str:
    words = [w for w in re.findall(r"[A-Za-z]+", title) if w.lower() not in ("of", "and", "the", "for", "in", "on", "&")]
    return "".join(w[0].upper() for w in words)[:8] or "J"


def resolve(query: str, http: Http) -> dict | None:
    """이름 또는 ISSN → {abbrev, name, issn}. 이름은 제목이 정확히 같은 것을 우선, 없으면 첫 결과."""
    q = query.strip()
    if ISSN_RE.match(q):
        issn = q.upper() if "-" in q else f"{q[:4]}-{q[4:]}".upper()
        d = http.get_json(f"{CROSSREF_J}/{issn}")
        items = [d["message"]] if d and d.get("message") else []
    else:
        d = http.get_json(CROSSREF_J, {"query": q, "rows": 10})
        items = ((d or {}).get("message") or {}).get("items") or []
        norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower().replace("&", "and"))  # noqa: E731
        items.sort(key=lambda it: norm(it.get("title", "")) != norm(q))
    for it in items:
        if it.get("ISSN"):
            return {"abbrev": abbrev_of(it["title"]), "name": it["title"], "issn": it["ISSN"][:2]}
    return None


def toml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def toml_list(xs: list[str]) -> str:
    return "[" + ", ".join(toml_str(x) for x in xs) + "]"


def write_config(groups, keywords, only, extra, lookback=10) -> str:
    ej = ",\n".join(f"  {{ abbrev = {toml_str(j['abbrev'])}, name = {toml_str(j['name'])}, issn = {toml_list(j['issn'])} }}" for j in extra)
    text = f"""# 내 알림 설정. Actions → '① 설정' 실행 버튼으로 바꾸면 이 파일이 자동으로 다시 쓰인다. 직접 고쳐도 된다.

# 받을 저널 묶음 (journals.toml의 groups 이름)
groups = {toml_list(groups)}

# 관심 키워드. 제목·초록에 있으면 ⭐ 표시하고 위로 올린다. 끝에 *를 붙이면 앞부분 일치 (예: hous* → housing, house)
keywords = {toml_list(keywords)}

# 이 묶음은 키워드에 맞는 논문만 보낸다 (분야가 넓은 경제·재무·경영 저널용)
keyword_only_groups = {toml_list(only)}

# 마법사에서 추가한 저널 (이름·ISSN으로 찾은 결과)
extra_journals = [{chr(10) + ej + chr(10) if extra else ""}]

# 매 실행마다 최근 며칠을 다시 조회할지. 이미 보낸 논문은 다시 보내지 않는다
lookback_days = {int(lookback)}
"""
    (ROOT / "alert.toml").write_text(text, encoding="utf-8")
    return text


def main() -> int:
    re_choice = os.environ.get("REALESTATE", "핵심+확장").strip()
    groups = list(REALESTATE.get(re_choice, REALESTATE["핵심+확장"]))
    general = [g for envname, g in GENERAL if env_bool(envname)]
    groups += general
    keywords = split_list(os.environ.get("KEYWORDS", ""))
    only = general if env_bool("KEYWORD_FILTER") and keywords else []
    http = Http(delay=0.3)
    found, failed = [], []
    for q in split_list(os.environ.get("EXTRA_JOURNALS", "")):
        j = resolve(q, http)
        if j:
            found.append((q, j))
        else:
            failed.append(q)
    extra = [j for _, j in found]
    if not groups and not extra:
        print("저널이 하나도 선택되지 않았습니다. 묶음을 하나 이상 고르거나 추가 저널을 적어 주세요.")
        return 1
    write_config(groups, keywords, only, extra)
    lines = ["## 설정 완료", "", f"- 저널 묶음: {', '.join(groups) or '없음'}",
             f"- 키워드: {', '.join(keywords) or '없음'}",
             f"- 키워드에 맞는 논문만 받는 묶음: {', '.join(only) or '없음'}", ""]
    if extra:
        lines += ["### 추가한 저널 (이름이 맞는지 확인하세요)", "", "| 입력 | 찾은 저널 | ISSN |", "|---|---|---|"]
        lines += [f"| {q} | {j['name']} | {', '.join(j['issn'])} |" for q, j in found]
    if failed:
        lines += ["", f"⚠️ 찾지 못한 저널: {', '.join(failed)} (정확한 영문 이름이나 ISSN으로 다시 실행하세요)"]
    out = "\n".join(lines)
    print(out)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(out + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
