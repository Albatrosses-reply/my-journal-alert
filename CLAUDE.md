# CLAUDE.md

Claude Code용 안내는 AGENTS.md와 같다. 설치를 도울 때와 코드를 고칠 때 모두 아래 문서를 따른다.

@AGENTS.md

## Claude Code에서만 해당하는 것
- API 키 등록은 사용자가 프롬프트에서 직접 `! gh secret set ELSEVIER_API_KEY -R <저장소>`로 실행하게 한다. Claude가 키 값을 다루지 않는다.
- `gh auth login`도 사용자가 `! gh auth login`으로 직접 실행하게 한다.
