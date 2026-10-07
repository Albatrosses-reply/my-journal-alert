"""설정 읽기: alert.toml(내 설정) + journals.toml(저널 묶음)."""
from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(root: Path = ROOT) -> dict:
    with open(root / "alert.toml", "rb") as f:
        cfg = tomllib.load(f)
    with open(root / "journals.toml", "rb") as f:
        cfg["catalog"] = tomllib.load(f).get("groups", {})
    return cfg


def journals(cfg: dict) -> list[dict]:
    """고른 묶음의 저널 + 추가 저널. 각 저널에 group·group_label을 붙이고 ISSN 중복은 하나만."""
    out, seen = [], set()
    for g in cfg.get("groups", []):
        grp = cfg["catalog"].get(g)
        if not grp:
            continue
        for j in grp.get("journals", []):
            out.append({**j, "group": g, "group_label": grp.get("label", g)})
    for j in cfg.get("extra_journals", []):
        out.append({**j, "group": "extra", "group_label": "추가 저널"})
    uniq = []
    for j in out:
        if j.get("issn") and j["issn"][0] not in seen:
            seen.add(j["issn"][0])
            uniq.append(j)
    return uniq


def group_order(cfg: dict) -> list[tuple[str, str]]:
    order = [(g, cfg["catalog"][g].get("label", g)) for g in cfg.get("groups", []) if g in cfg["catalog"]]
    if cfg.get("extra_journals"):
        order.append(("extra", "추가 저널"))
    return order
