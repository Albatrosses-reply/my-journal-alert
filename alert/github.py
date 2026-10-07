"""GitHub Issue 게시. Actions의 GITHUB_TOKEN을 쓴다. 토큰이 없으면(내 컴퓨터에서 시험할 때) 파일로 저장만 한다."""
from __future__ import annotations

import json
import logging
import os
import urllib.request

log = logging.getLogger("alert")
API = "https://api.github.com"


def _call(method: str, path: str, token: str, body: dict) -> dict:
    req = urllib.request.Request(f"{API}{path}", data=json.dumps(body).encode("utf-8"), method=method, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def post(title: str, chunks: list[str], preview_path=None) -> str:
    token, repo = os.environ.get("GITHUB_TOKEN", ""), os.environ.get("GITHUB_REPOSITORY", "")
    if not (token and repo):
        if preview_path:
            preview_path.write_text(f"# {title}\n\n" + "\n\n<!-- 댓글 -->\n\n".join(chunks), encoding="utf-8")
            log.info(f"GITHUB_TOKEN 없음: {preview_path}에 저장")
        return ""
    issue = _call("POST", f"/repos/{repo}/issues", token, {"title": title, "body": chunks[0]})
    for c in chunks[1:]:
        _call("POST", f"/repos/{repo}/issues/{issue['number']}/comments", token, {"body": c})
    return issue.get("html_url", "")
