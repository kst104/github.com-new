# 🚀 Content Automation Engine (GitHub × Notion × Claude / ChatGPT)

> **기획부터 SEO 블로그 포스팅, 다채널 광고 카피 10종 생성, Git 영구 아카이빙까지 완전 자동화**  
> 김승태 님을 위한 서버리스 무비용 콘텐츠 마케팅 엔진

---

## 🌟 핵심 특징

- 🤖 **듀얼 AI 엔진 지원**: Anthropic **Claude 3.5 Sonnet** 및 OpenAI **GPT-4o** 완벽 지원 (환경변수나 CLI 옵션으로 손쉽게 전환)
- 📝 **네이버 & 구글 SEO 최적화**: C-Rank & D.I.A+ 알고리즘 기준의 고품질 2,000자 전문 블로그 원고 자동 생성
- 📢 **다채널 광고 카피 10종 동시 생성**:
  - 페이스북/인스타그램 스폰서드 카피 (PAS 공식)
  - 인스타그램 카드뉴스 10장 구성안 (AIDA 공식)
  - 비포&애프터 스토리텔링 카피 (BAB 공식)
  - **네이버 파워링크 검색광고(SA) 5세트** (제목 15자 / 설명 45자 규격 엄수)
  - 숏폼 릴스/쇼츠 60초 대본
- ⚡ **100% 무료 서버리스 (월 0원)**: GitHub Actions 매시간/정기 스케줄러 활용
- 📓 **노션 양방향 동기화**: 노션 DB에서 '생성요청' 상태 감지 ➔ 생성 후 노션 페이지에 본문 입력 및 상태 '초안완료' 변경
- 💬 **Claude Project & Claude Code 전용 프롬프트 수록**: API 연동 없이 Claude 웹/데스크톱에서도 동일한 퀄리티로 즉시 활용 가능

---

## 🛠 아키텍처 흐름도

```
[1. 기획]              [2. 감지 및 오케스트레이션]          [3. 고품질 생성]               [4. 저장 및 배포]
+--------------+      +---------------------------+      +----------------------+      +----------------------+
|    Notion    | ---> |      GitHub Actions       | ---> | Anthropic Claude 3.5 | ---> | 1. Git Commit (MD)   |
| (아이디어/DB)|      | (매일 아침 9시 / 수동 실행) |      |         또는         |      | 2. Notion 본문 삽입 |
|  상태: 생성요청|      |  python run_pipeline.py   |      |    OpenAI GPT-4o     |      | 3. 블로그/SNS 발행  |
+--------------+      +---------------------------+      +----------------------+      +----------------------+
```

---

## 📂 프로젝트 구조

```
content-automation-engine/
├── workflows/
│   └── content_engine.yml          # GitHub Actions 서버리스 자동화 워크플로우 템플릿
├── engine/
│   ├── config.py                   # 환경변수 및 모델 설정
│   ├── claude_engine.py            # Anthropic Claude 3.5 Sonnet 파이프라인
│   ├── openai_engine.py            # OpenAI GPT-4o 파이프라인
│   ├── notion_engine.py            # 노션 API 연동 및 상태/본문 업데이트
│   └── run_pipeline.py             # 통합 마스터 실행 스크립트
├── prompts/
│   ├── claude_blog_prompt.md       # Claude 최적화 XML 구조 블로그 프롬프트
│   ├── claude_ad_prompt.md         # Claude 최적화 마케팅 카피 프롬프트
│   ├── openai_blog_prompt.md       # OpenAI 프롬프트
│   └── openai_ad_prompt.md         # OpenAI 광고 프롬프트
├── posts/                          # 생성된 블로그 마크다운 영구 보관소
├── ads/                            # 생성된 광고 카피 마크다운 영구 보관소
├── claude_project_instructions.md  # Claude 웹/앱 Project용 커스텀 지침
├── requirements.txt
└── README.md
```

---

## 🚀 빠른 시작 가이드

### 1. 로컬 환경에서 실행

```bash
# 레포지토리 클론 및 이동
git clone https://github.com/kst104/github.com-new.git content-automation-engine
cd content-automation-engine

# 의존성 패키지 설치
pip install -r requirements.txt

# .env 파일 생성 (필요한 키 입력)
cat << 'EOF' > .env
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_db_id
EOF

# Claude를 이용한 단일 실행 (키워드 지정)
python engine/run_pipeline.py --provider claude --topic "겨울철 당뇨 혈당 관리" --keyword "당뇨 인슐린 주사"

# 테스트 모의 실행 (API 키 없이 전체 파이프라인 테스트)
python engine/run_pipeline.py --dry-run
```

### 2. GitHub Actions 자동화 설정 (클라우드 무인 운영)

1. 리포지토리의 **Settings** ➔ **Secrets and variables** ➔ **Actions**로 이동합니다.
2. **New repository secret**을 클릭하고 다음 시크릿을 등록합니다:
   - `ANTHROPIC_API_KEY`: Anthropic 콘솔에서 발급받은 API 키
   - `OPENAI_API_KEY`: OpenAI 콘솔에서 발급받은 API 키 (선택)
   - `NOTION_API_KEY`: 노션 통합(Integration) 토큰 (선택)
   - `NOTION_DATABASE_ID`: 연동할 노션 데이터베이스 ID (선택)
3. 상단 **Actions** 탭 ➔ **Content Automation Engine** 워크플로우 ➔ **Run workflow** 버튼을 누르면 즉시 실행됩니다!

---

## 💡 Claude 사용자(웹/앱)를 위한 꿀팁

API 연결 없이 **Claude.ai**에서 바로 글을 뽑아내고 싶으시다면:
1. `claude_project_instructions.md` 파일을 엽니다.
2. 1번에 적힌 **Claude Project 시스템 지침**을 복사하여 Claude.ai의 Project 지침에 넣습니다.
3. 채팅창에 `주제: ... / 키워드: ...`만 입력하시면 가이드 규격 그대로 블로그와 광고 카피가 출력됩니다!
