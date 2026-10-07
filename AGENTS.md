# AGENTS.md — AI 코딩 에이전트용 안내 (Codex, Claude Code 등)

이 저장소는 **저널 신간 알림** 템플릿이다. GitHub Actions가 매일 고른 저널의 새 논문을 모아 사용자 저장소에 Issue로 올린다.
사용자는 대부분 **프로그래밍 경험이 없는 학생**이다. 아래 순서대로 설치를 돕고, 각 단계에서 무엇을 했는지 한국어로 짧게 알려 준다.

## 절대 규칙

1. **API 키를 직접 읽거나, 출력하거나, 파일·Issue·커밋·명령어 인자에 넣지 않는다.** 키는 사용자가 직접 `gh secret set`의 입력 프롬프트나 GitHub 웹 화면(Settings → Secrets)에 붙여 넣게 한다. 사용자가 채팅에 키를 붙여 넣으면 쓰지 말고, 노출됐으니 새로 발급받으라고 안내한다.
2. **원본 템플릿 저장소(`Albatrosses-reply/journal-alert`)에서 설정 마법사나 커밋을 실행하지 않는다.** 작업은 항상 사용자 계정에 복사한 저장소에서 한다.
3. 사용자 저장소를 삭제하거나 강제 push하지 않는다. 설정을 바꿀 때는 `① 설정` 워크플로를 다시 실행하거나 `alert.toml`을 고친다.
4. 출판사 웹페이지를 긁는 코드를 추가하지 않는다(봇 차단, 이용약관). 초록 보충은 공식 API만 쓴다.

## 설치 순서 (gh CLI 사용)

사용자가 터미널과 [GitHub CLI](https://cli.github.com)를 쓸 수 있으면 아래대로 진행한다. 쓸 수 없으면 README.md의 웹 화면 안내를 한 단계씩 읽어 주며 돕는다.

### 0. 준비 확인
```bash
gh --version          # 없으면 설치 안내: macOS `brew install gh`, Windows `winget install --id GitHub.cli`
gh auth status        # 로그인 안 돼 있으면 사용자가 직접 `gh auth login` (브라우저 인증)
```
`gh auth login`은 사용자가 직접 실행하게 한다(브라우저에서 코드 입력이 필요하다).

### 1. 템플릿에서 내 저장소 만들기
저장소 이름은 사용자에게 묻는다(기본 `my-journal-alert`). 공개/비공개도 묻는다(기본 비공개).
```bash
OWNER=$(gh api user -q .login)
gh repo create "$OWNER/my-journal-alert" --template Albatrosses-reply/journal-alert --private
```
만든 뒤 10초쯤 기다렸다가 `gh workflow list -R "$OWNER/my-journal-alert"`로 `① 설정`, `② 논문 알림 (매일)`이 보이는지 확인한다.

### 2. 설정 값 묻기
사용자에게 아래를 **하나씩** 묻는다. 모르면 기본값을 쓴다.

| 입력 이름 | 값 | 기본값 |
|---|---|---|
| `realestate` | `핵심+확장` / `핵심만` / `안 받음` (정확히 이 문자열) | `핵심+확장` |
| `economics` | `true` / `false` (경제학 주요 저널 10종) | `false` |
| `finance` | `true` / `false` (재무 주요 저널 5종) | `false` |
| `management` | `true` / `false` (경영·경영정보 5종) | `false` |
| `keyword_filter` | `true` / `false` (경제·재무·경영 저널은 키워드 맞는 논문만) | `true` |
| `keywords` | 쉼표 구분 영어. 끝 `*`는 앞부분 일치 | `housing, rent*, mortgage*, house price*, real estate, zoning` |
| `extra_journals` | 쉼표 구분, 영문 저널명 또는 ISSN | 빈 문자열 |

사용자가 한국어로 관심 주제를 말하면 영어 키워드로 바꿔 제안하고 확인받는다(예: "재개발" → `redevelopment, urban renewal, gentrification`).
저널 묶음 구성은 `journals.toml`에 있다. 사용자가 원하는 저널이 이미 묶음에 있는지 먼저 확인한다.

### 3. 설정 마법사 실행
```bash
R="$OWNER/my-journal-alert"
gh workflow run setup.yml -R "$R" \
  -f realestate="핵심+확장" -f economics=false -f finance=false -f management=false \
  -f keyword_filter=true -f keywords="housing, rent*, mortgage*" -f extra_journals=""
sleep 15
gh run watch "$(gh run list -R "$R" -w setup.yml -L 1 --json databaseId -q '.[0].databaseId')" -R "$R" --exit-status
gh run view "$(gh run list -R "$R" -w setup.yml -L 1 --json databaseId -q '.[0].databaseId')" -R "$R" --log | grep -A20 "설정 완료"
```
로그의 **추가한 저널** 표를 사용자에게 보여 주고 이름이 맞는지 확인받는다. "찾지 못한 저널"이 있으면 정확한 영문명이나 ISSN을 다시 받아 3단계를 반복한다.
설정 마법사는 끝나면 첫 알림(`daily.yml`)을 자동으로 실행한다.

### 4. API 키 (선택, 권장)
키가 없어도 동작한다. 없으면 Elsevier·Taylor & Francis 저널 초록이 비어 온다. 사용자에게 키를 받을지 묻고, 받는다면:
- Elsevier: https://dev.elsevier.com → I want an API key → 학교 메일로 가입 → Create API Key
- Semantic Scholar: https://www.semanticscholar.org/product/api → Request an API key (승인에 며칠)

키 등록은 **사용자가 직접** 실행한다. 아래 명령은 키를 묻는 프롬프트를 띄우므로 키가 화면·기록에 남지 않는다.
```bash
gh secret set ELSEVIER_API_KEY -R "$R"   # 프롬프트에 사용자가 붙여 넣기
gh secret set S2_API_KEY -R "$R"
```
Claude Code에서는 사용자에게 `! gh secret set ELSEVIER_API_KEY -R <저장소>`처럼 `!`를 붙여 직접 실행하도록 안내한다. Codex에서는 사용자가 자기 터미널에서 실행하게 한다.
등록 확인은 `gh secret list -R "$R"`(이름만 보인다).

### 5. 첫 알림 확인
```bash
gh run watch "$(gh run list -R "$R" -w daily.yml -L 1 --json databaseId -q '.[0].databaseId')" -R "$R" --exit-status
gh issue list -R "$R"
```
Issue `📚 논문 알림 …`이 보이면 성공이다. 키를 4단계에서 넣었다면 초록을 채우기 위해 한 번 더 돌린다:
`gh workflow run daily.yml -R "$R" -f days=10` (이미 보낸 논문은 다시 오지 않으므로, 채워진 초록은 다음 날부터 반영된다는 점도 알려 준다).

마지막으로 사용자에게 알려 줄 것:
- 매일 한국시간 05:30에 Issue가 올라오고, GitHub 가입 메일로 알림이 간다. 안 오면 GitHub Settings → Notifications에서 Email을 켠다.
- 설정을 바꾸려면 3단계를 다시 실행한다.
- 저장소 주소: `https://github.com/$R/issues`

## 문제 해결

| 증상 | 확인·조치 |
|---|---|
| `gh workflow run` 이 404 | 저장소를 막 만들었으면 10~20초 뒤 다시. `gh workflow list`로 이름 확인 |
| 설정 실행이 `저널이 하나도 선택되지 않았습니다` | realestate=`안 받음`이고 다른 묶음·추가 저널도 없음. 하나 이상 고르게 한다 |
| daily 실행은 성공인데 Issue가 없음 | 로그에 `보낼 새 논문 없음`이면 정상(이미 보낸 논문뿐). `-f days=30`으로 범위를 넓혀 시험 |
| 초록 없음이 많음 | 4단계 키 등록 여부를 `gh secret list`로 확인. 신간은 며칠 뒤 채워지기도 한다 |
| `HTTP 429`, `할당량 소진` 로그 | OpenAlex·Semantic Scholar 일시 제한. 다음 날 자동으로 풀린다 |
| 예약 실행이 멈춤 | 60일 무활동 시 GitHub가 끔. Actions 탭에서 다시 켜거나 `gh workflow enable daily.yml -R "$R"` |
| Actions 권한 오류(`Resource not accessible by integration`) | Settings → Actions → General → Workflow permissions를 **Read and write**로 |

## 코드 구조 (수정 요청을 받았을 때)

```
run.py               매일 실행 진입점: 수집 → seen 제외 → 초록 보충 → 키워드 → Issue
setup.py             설정 마법사: 환경변수(워크플로 입력) → alert.toml, 추가 저널은 Crossref로 이름·ISSN 해석
alert/collect.py     Crossref ∪ OpenAlex 수집, 비논문 제외 규칙(EXCLUDE), 키워드 점수
alert/abstracts.py   초록 보충: Elsevier API(10.1016/) → Semantic Scholar batch
alert/render.py      Issue 마크다운, 60,000자 넘으면 댓글로 나눔
alert/github.py      Issue 게시(GITHUB_TOKEN), 토큰 없으면 data/preview.md
alert/config.py      alert.toml + journals.toml 읽기
journals.toml        저널 묶음(그룹별 abbrev, name, issn). 첫 ISSN만 조회에 쓴다
alert.toml           사용자 설정(마법사가 덮어씀)
data/seen.json       이미 보낸 DOI → 날짜 (120일 보관, 워크플로가 커밋)
.github/workflows/   setup.yml(① 설정), daily.yml(② 매일 05:30 KST)
```

- 표준 라이브러리만 쓴다(외부 패키지 추가 금지). Python 3.11+.
- 고친 뒤 반드시 `python -m unittest discover -s tests`를 돌린다. 네트워크 시험은 `python run.py --dry-run --days 3`(Issue를 올리지 않고 `data/preview.md`에 저장, seen.json 변경 없음).
- 저널을 추가할 때 ISSN은 `https://api.crossref.org/journals/<ISSN>`으로 실제 저널명과 맞는지 확인한다.
- 워크플로 입력값은 `env:`로만 스크립트에 넘긴다(`run:` 줄에 `${{ inputs.* }}`를 직접 넣지 않는다, 명령 주입 방지).
- 사용자 문서·로그·Issue 문구는 한국어로 쓴다.
