# 블로그·마케팅·쇼츠 작업 허브

김승태 님의 블로그 원고, 다채널 광고 소재, 쇼츠 대본을 **한곳에서 관리하고 여러 기기에서 같이 손보는** 저장소입니다.

```
 [맥미니]  localhost:8787 ─┐                        ┌─ 노션 '📋 콘텐츠 보드' (상태 보기·아이디어 입력)
 [노트북]  localhost:8787 ─┼── 깃허브 (이 저장소) ───┤
 [다른 PC] localhost:8787 ─┘    자동 동기화          └─ Claude (claude.ai 프로젝트 / Claude Code)
```

- **로컬 작업 허브**: 콘텐츠 목록, 칸반 보드, 마크다운 편집기(미리보기), 영상 미리보기
- **자동 깃허브 동기화**: 2분마다 다른 기기 변경을 받고, 내 변경을 올립니다
- **노션 연동**: 허브에서 상태를 바꾸면 노션 보드에도 반영 (토큰 설정 시)
- **Claude 연동**: 요청문 복사 버튼, `CLAUDE.md` 작업 규칙, 엔진 자동 생성(선택)

설치할 프로그램은 없습니다. 맥에 기본으로 있는 `git`과 `python3`만 씁니다.

---

## 1. 켜기

### 맥
폴더에서 **`start.command`를 더블클릭**하세요. 브라우저에 http://localhost:8787 이 열립니다.
터미널 창을 닫으면 허브도 꺼집니다.

> 처음 더블클릭할 때 "확인되지 않은 개발자" 경고가 나오면: 파일을 **우클릭 → 열기 → 열기**.

로그인할 때마다 자동으로 켜 두고 싶으면 (선택):
```bash
bash scripts/autostart_mac.sh        # 켜기
bash scripts/autostart_mac.sh off    # 끄기
```

### 다른 기기 추가
```bash
git clone https://github.com/kst104/github.com-new.git 블로그.마케팅.쇼츠
```
받은 폴더에서 맥은 `start.command`, 윈도우는 `start.bat`, 리눅스는 `./start.sh`.

### 깃허브에 올리기(push) 권한
받기(pull)는 로그인 없이 되지만, 올리기는 기기마다 한 번 로그인해야 합니다.
```bash
brew install gh        # gh 가 없을 때
gh auth login          # 브라우저로 승인
gh auth setup-git
```
허브 오른쪽 위 동기화 표시가 **빨간색 · "깃허브 로그인이 필요해요"** 이면 이 단계가 빠진 것입니다.

---

## 2. 쓰는 법

1. **+ 새 콘텐츠** → 주제, 키워드, 카테고리, 채널 입력 → `content/날짜-번호/` 폴더와 양식 3개(post·ads·shorts)가 생깁니다.
2. **Claude 요청문 복사** → claude.ai의 '블로그.마케팅 자동화' 프로젝트에 붙여넣기 → 결과를 블로그/광고 소재/쇼츠 대본 탭에 붙여넣고 **⌘S**.
3. 상태를 `아이디어 → 생성요청 → 작성중 → 검토 → 발행완료`로 옮깁니다 (보드 탭에서 끌어다 놓기 가능).
4. 저장한 내용은 다음 동기화 때 깃허브로 올라가고, 다른 기기 허브에 자동으로 나타납니다. 급하면 **지금 동기화**.

### 7070 의학서적 근거·주석·검수
직접 만든 의학서적 위키(http://localhost:7070, 의학서적 카테고리: Braunwald's 8판 · Harrison's 17판 · Tintinalli's 7판)를 근거로 씁니다.

1. 검색은 두 단계로 연결돼요.
   - **7070 자체 검색** (`/api/search`) — 한글 검색 가능(위키가 영어로 번역), 문단 단위 결과. 기본으로 이것을 씁니다.
   - **허브 예비 색인** — 7070 자체 검색이 꺼져 있거나 오류일 때 자동 전환 (영어 검색어). 7070을 켜 둔 채 허브를 처음 켜면 몇 분 동안 자동으로 만들어요 (이 기기에만 저장 `hub/.medref.sqlite`).
   - 7070 위키는 Hermes가 색인을 다시 만드는 동안(`mywiki.db`를 지우고 새로 만듦, 약 25분) 자체 검색이 500 오류를 냅니다. 그때도 예비 색인으로 계속 찾을 수 있어요.
2. 블로그 탭 오른쪽 **7070 근거** → 검색 (예: `당뇨 케톤산증`, `diabetic ketoacidosis`). 결과 위에 어떤 방법으로 찾았는지 표시돼요.
   - **주석 삽입**: 커서 위치에 `[^m1]`, 글 끝 '각주'에 책·장·발췌·원문 링크(누르면 7070의 그 문장으로 이동)
   - **근거 묶음에 추가**: `evidence.json`에 저장 → **Claude 요청문 복사**에 근거 목록과 주석 규칙이 같이 들어감
   - 검색 결과가 없으면 **7070에 없음** 이라고 알려 주고 `⚠️[7070 없음]` 표시를 넣을 수 있음
3. **검수** 탭: ✅ 7070 주석 · 🌐 인터넷 출처 · ⚠️ 7070 없음 · 🕒 최신 확인 개수와 해당 줄 목록. 남은 표시가 있으면 '발행완료'로 바꿀 때 한 번 더 확인합니다.
4. 터미널/Claude Code: `python3 hub/medref.py search "sepsis" --book tintinalli`

> 7070 서적은 2008년 전후 판이에요. 치료·약물·목표 수치는 `⚠️[최신 확인]`으로 표시하고 최신 가이드라인을 같이 확인하세요.
> 저장소가 공개(public)이면 각주의 원서 발췌도 공개됩니다. 발췌는 220자 이내로 잘리지만, 비공개 전환을 권해요.

### 동기화 규칙
| 상황 | 결과 |
|---|---|
| 서로 다른 파일을 고침 | 자동으로 합쳐짐 |
| 열어둔 파일이 다른 기기에서 바뀜 | 저장할 때 알려줌 (덮어쓰기 / 내 내용 복사 후 최신 열기) |
| 두 기기가 같은 파일을 동시에 고침 | 자동 동기화가 멈추고 **충돌 정리하기** 버튼이 나타남 → 다른 기기 버전을 받고, 내 버전은 `post.충돌-기기이름.md` 사본으로 남김. 아무것도 지워지지 않음 |
| 50MB 넘는 파일 | 그 기기에서만 동기화 제외 (깃허브 한도 100MB) |

---

## 3. 노션 연결

- 노션 **🚀 블로그 & 마케팅 콘텐츠 자동화 허브** 페이지 안에 **📋 콘텐츠 보드** 데이터베이스가 있습니다. 허브의 콘텐츠와 같은 항목·상태를 씁니다.
- 지금도 Claude(노션 커넥터 연결된 대화)에게 "콘텐츠 보드 업데이트해 줘"라고 하면 반영할 수 있습니다.
- **허브에서 바꿀 때마다 자동 반영**하려면 (선택):
  1. https://www.notion.so/profile/integrations 에서 통합(Internal) 생성 → 토큰 복사
  2. 노션 '📋 콘텐츠 보드' 페이지 오른쪽 위 `⋯` → **연결** → 방금 만든 통합 추가
  3. `.env.example`을 복사해 `.env`로 저장하고 `NOTION_API_KEY=` 에 토큰 입력
  4. 허브를 껐다 켜면 상세 화면에 **노션 반영** 버튼이 생기고, 상태 변경 시 자동 반영됩니다.

`.env`는 `.gitignore`에 들어 있어 깃허브에 올라가지 않습니다. 기기마다 따로 만들어야 합니다.

---

## 4. Claude 연결

- **claude.ai 프로젝트**: 허브의 *Claude 요청문 복사* 버튼이 주제·키워드·채널을 프로젝트 지침 형식으로 만들어 줍니다.
- **Claude Code / Claude 데스크톱**: 이 폴더에서 작업하면 `CLAUDE.md`의 규칙(폴더 구조, 상태 값, 파워링크 글자 수 등)을 따릅니다. 예: "content/2026-11-09-02 원고 써줘".
- **엔진 자동 생성 (선택, API 키 필요)**:
  ```bash
  pip install -r requirements.txt
  python3 engine/run_pipeline.py --provider claude --topic "주제" --keyword "키워드"
  python3 engine/run_pipeline.py          # 노션 보드에서 '생성요청' 항목을 찾아 생성 → 상태 '검토'
  ```
  결과는 `content/<허브ID>/post.md`, `ads.md`에 저장됩니다. 실제 API 키로는 아직 시험해 보지 않았습니다.

### GitHub Actions 상태 (중요)
`workflows/content_engine.yml`은 **아직 동작하지 않습니다.** GitHub Actions는 `.github/workflows/` 폴더의 파일만 실행하기 때문입니다.
켜려면 파일을 `.github/workflows/`로 옮기고 저장소 Settings → Secrets에 `ANTHROPIC_API_KEY`, `NOTION_API_KEY`, `NOTION_DATABASE_ID`를 등록하세요.
(켜면 매일 09시에 '생성요청' 항목을 처리합니다. 대기 항목이 없으면 아무것도 만들지 않습니다.)

---

## 폴더 구조
```
content/<YYYY-MM-DD-NN>/   콘텐츠 1건 (meta.json, post.md, ads.md, shorts.md, 미디어)
templates/                 새 콘텐츠 양식
hub/                       로컬 작업 허브 (server.py, static/index.html, config.json)
engine/, prompts/          API 자동 생성 엔진 (선택)
workflows/                 GitHub Actions 템플릿 (아직 꺼져 있음)
start.command / start.bat / start.sh
CLAUDE.md                  Claude 작업 규칙
claude_project_instructions.md   claude.ai 프로젝트 지침 원본
```

> 이 저장소는 현재 **공개(public)** 입니다. 발행 전 원고를 숨기고 싶으면 Settings → General → Danger Zone → *Change visibility* 에서 비공개로 바꿀 수 있습니다.
