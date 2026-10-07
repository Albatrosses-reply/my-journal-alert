# 📚 저널 신간 알림 (journal-alert)

부동산·경제·재무·경영 주요 저널에 새 논문이 나오면 **매일 아침 GitHub 알림 메일**로 받아 보는 도구입니다.
내 컴퓨터에 아무것도 설치하지 않습니다. GitHub가 대신 매일 실행합니다.

- 매일 한국시간 05:30에 고른 저널의 새 논문을 모아 내 저장소에 **Issue** 하나로 올립니다.
- Issue가 올라오면 GitHub가 가입 메일로 알림을 보냅니다. 별도 메일 설정은 필요 없습니다.
- 관심 키워드가 들어간 논문은 ⭐로 표시하고 위로 올립니다.
- 초록이 없는 논문은 출판사 API·Semantic Scholar로 보충합니다(키를 넣은 경우).

---

## AI 도우미로 설치하기 (Claude Code · Codex)

터미널에서 Claude Code나 Codex를 쓸 수 있으면, 아래 문장을 **그대로 붙여 넣으세요.** AI가 [AGENTS.md](AGENTS.md)의 순서대로 저장소 만들기, 설정, 첫 알림 확인까지 진행하고, 필요한 것(저장소 이름, 관심 분야, 키워드)을 하나씩 물어봅니다.

```
https://raw.githubusercontent.com/Albatrosses-reply/journal-alert/main/AGENTS.md 를 읽고,
그 안내대로 내 GitHub 계정에 저널 신간 알림을 설치해 줘.
나는 프로그래밍을 잘 모르니까 단계마다 쉽게 설명하고, 정할 것은 하나씩 물어봐 줘.
```

- 미리 필요한 것: GitHub 계정, [GitHub CLI](https://cli.github.com) (`gh`). 없으면 AI가 설치 방법을 알려 줍니다.
- **API 키는 AI에게 채팅으로 보내지 마세요.** AI가 알려 주는 명령(`gh secret set …`)을 직접 실행해 입력 칸에 붙여 넣으면 됩니다. Claude Code에서는 명령 앞에 `!`를 붙여 실행합니다.
- 터미널 없이 ChatGPT·Claude 웹 채팅만 쓴다면, 이 README 주소를 주고 "웹 화면으로 설치하는 법을 단계별로 알려 줘"라고 하면 됩니다. 아래 안내와 같은 순서입니다.
- 이 저장소를 내려받아 그 폴더에서 AI를 열면 `AGENTS.md`(Codex)·`CLAUDE.md`(Claude Code)를 자동으로 읽습니다. 기능을 고치거나 저널을 더하는 것도 그렇게 부탁하면 됩니다.

---

## 설치 (10분)

### 1. GitHub 가입
[github.com](https://github.com)에서 가입합니다. 알림은 가입한 메일로 옵니다.

### 2. 내 저장소로 복사
이 페이지 위쪽의 초록색 **Use this template** → **Create a new repository**를 누릅니다.
- Repository name: 아무 이름 (예: `my-journal-alert`)
- Public / Private: 어느 쪽이든 됩니다 (Private은 월 2,000분 무료 한도가 있지만 하루 2~3분이라 충분합니다)
- **Create repository**

### 3. 설정 마법사 실행
복사한 **내 저장소**에서:
1. 위쪽 메뉴 **Actions** 탭을 누릅니다. "workflows aren't being run" 같은 안내가 나오면 **I understand my workflows, go ahead and enable them**을 누릅니다.
2. 왼쪽 목록에서 **① 설정**을 누릅니다.
3. 오른쪽 **Run workflow** 버튼을 누르면 입력 칸이 나옵니다.

| 칸 | 설명 |
|---|---|
| 부동산 저널 | 핵심+확장 / 핵심만 / 안 받음 |
| 경제학·재무·경영 | 체크하면 그 분야 주요 저널도 받습니다 |
| 키워드에 맞는 논문만 받기 | 체크하면 경제·재무·경영 저널은 키워드가 들어간 논문만 옵니다 (권장) |
| 관심 키워드 | 쉼표로 구분, 영어. 끝에 `*`를 붙이면 앞부분 일치 (`rent*` → rent, rental, rents) |
| 추가 저널 | 목록에 없는 저널을 **영문 이름이나 ISSN**으로 적으면 자동으로 찾아 넣습니다 |

4. 초록색 **Run workflow**를 누릅니다. 1분쯤 뒤 설정이 저장되고 **첫 알림이 바로 실행**됩니다.
5. 실행 결과(초록색 체크)를 눌러 보면 어떤 저널이 들어갔는지 요약이 보입니다. 추가 저널 이름이 맞는지 여기서 확인하세요.

### 4. 첫 알림 확인
몇 분 뒤 내 저장소의 **Issues** 탭에 `📚 논문 알림 …`이 생기고, 가입 메일로 알림이 옵니다.
메일이 안 오면 GitHub 오른쪽 위 프로필 → **Settings → Notifications**에서 이메일 알림이 켜져 있는지 확인하세요.
휴대폰 **GitHub 앱**을 설치하면 앱 알림으로도 받을 수 있습니다.

이제 끝입니다. 매일 아침 새 Issue가 올라옵니다.

---

## 초록이 빈 논문을 줄이려면 (선택, 권장)

출판사마다 초록 공개 방식이 달라서, 키 없이 쓰면 일부 저널은 초록이 비어 옵니다.

| 출판사 | 저널 예 | 키 없이 | 해결 |
|---|---|---|---|
| Elsevier | JUE, RSUE, JHE, Land Use Policy, Cities | 초록 거의 없음 | **Elsevier 키** |
| Taylor & Francis | Housing Studies, HPD, JRER, JPR | 초록 없음 | Semantic Scholar 키 (일부만 채워짐) |
| Wiley, SAGE, Springer 등 | REE, Urban Studies 등 | 대부분 있음 | 필요 없음 |

**키 받기**
- **Elsevier**: [dev.elsevier.com](https://dev.elsevier.com) → I want an API key → 학교 메일로 가입 → Create API Key. 키는 **반드시 본인이 직접** 받으세요(다른 사람과 공유하면 약관 위반입니다).
- **Semantic Scholar**: [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api) → Request an API key. 승인까지 며칠 걸릴 수 있습니다.

**키 넣기** (내 저장소에서)
**Settings → Secrets and variables → Actions → New repository secret**
- Name: `ELSEVIER_API_KEY`, Secret: 받은 키 → **Add secret**
- Name: `S2_API_KEY`, Secret: 받은 키 → **Add secret**

키는 GitHub에 암호화되어 저장되고 실행 기록에도 나오지 않습니다. **키를 설정 파일이나 Issue에 적지 마세요.**

---

## 자주 하는 일

- **지금 바로 받아 보기**: Actions → **② 논문 알림 (매일)** → Run workflow
- **설정 바꾸기**: Actions → **① 설정** → Run workflow를 다시 실행 (이전 설정을 덮어씁니다)
- **직접 고치기**: `alert.toml`(내 설정), `journals.toml`(저널 묶음)을 GitHub 웹에서 연필 아이콘으로 고쳐도 됩니다
- **잠시 멈추기**: Actions → ② 논문 알림 → 오른쪽 `···` → Disable workflow

## 저널 묶음

| 묶음 | 저널 |
|---|---|
| 부동산 핵심 | Real Estate Economics, J. Real Estate Finance and Economics, J. Urban Economics, Regional Science and Urban Economics, J. Housing Economics, J. Real Estate Research |
| 부동산 확장 | Housing Studies, Housing Policy Debate, Urban Studies, J. Property Research, J. European Real Estate Research, J. Real Estate Literature, Land Use Policy, Cities |
| 경제학 | AER, Econometrica, JPE, QJE, REStud, AEJ: Policy, AEJ: Applied, REStat, J. Public Economics, J. Monetary Economics |
| 재무 | JF, JFE, RFS, JFQA, Review of Finance |
| 경영·경영정보 | Management Science, ISR, MISQ, Organization Science, SMJ |

Land Use Policy와 Cities는 논문 수가 많습니다(합쳐서 주 30편 안팎). 많다고 느끼면 '핵심만'을 고르고 필요한 저널만 추가 저널로 넣으세요.

## 동작 방식

```
매일 05:30 (GitHub Actions)
  ① Crossref + OpenAlex에서 최근 10일 신간 수집 (표지·정정문·학회 공지는 제외)
  ② 이미 보낸 논문(data/seen.json) 제외
  ③ 초록 보충: Elsevier API → Semantic Scholar
  ④ 키워드 ⭐ 표시, '키워드만' 묶음은 맞는 논문만
  ⑤ Issue 게시 (@내계정 멘션 → 알림 메일)
```

- 출판사 웹페이지를 긁지 않습니다. 공식 API만 씁니다.
- 신간은 OpenAlex·Semantic Scholar 반영이 며칠 늦어 초록이 빌 수 있습니다.
- GitHub는 60일 동안 저장소 활동이 없으면 예약 실행을 멈춥니다. 이 도구는 매일 `data/seen.json`을 저장하므로 보통 멈추지 않지만, 멈췄다면 Actions 탭에서 다시 켜면 됩니다.

## 내 컴퓨터에서 시험하기 (개발용)
Python 3.11 이상, 외부 패키지 없음.
```bash
python run.py --dry-run          # data/preview.md에 결과 저장 (Issue 게시 안 함)
python -m unittest discover -s tests
```

## 라이선스
MIT. 논문 서지·초록의 권리는 각 출판사에 있으며, Crossref·OpenAlex·Elsevier·Semantic Scholar 각 서비스의 이용 조건을 따릅니다.
