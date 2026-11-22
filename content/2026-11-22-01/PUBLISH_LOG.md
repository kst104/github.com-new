# Day 15 발행·업로드 기록 (2026-11-22)

## 네이버 블로그

| 구분 | 카테고리 | 제목 | URL | 공개 |
| :--- | :--- | :--- | :--- | :--- |
| 대중용 | 의학·건강 (categoryNo=10) | "크림을 발라도 다음 날 또 당겨요"... 겨울 피부에 빠진 건 물이 아니라 기름입니다 | https://blog.naver.com/kst104/224486927034 | 전체공개 |
| 전문가용 | 임상·전문가 칼럼 (categoryNo=11) | [임상 리뷰] 한랭기 피부 장벽 손상과 보습 요법의 근거: 각질층 지질 조성, 3분 법칙의 근거 수준, 세라마이드 보충의 임상 적용 | https://blog.naver.com/kst104/224486929870 | 전체공개 |

- 제휴: 네이버 쇼핑 커넥트 들꽃잠 배 찜질팩 온열 팥 멀티형 32,300원 `https://naver.me/Faeu91oI`, 크리에이터샵 `https://cshop.naver.com/geongtae_shop`, 공정위 고지 문구를 두 글 모두에 포함.
- 링크 방식: 스마트에디터 본문에서 `span.se-link[data-href]`로 들어갔고, 모바일 `m.blog.naver.com`에서 `<a href ... target="_blank">`로 렌더되어 파란 밑줄 링크로 노출되는 것을 확인했다(색 rgb(96,140,186), text-decoration underline).
- 표: 대중용 3개, 임상 6개가 `<table>`로 변환되어 발행됨(`engine/md_tables.py`).
- 태그: 대중용 6개(겨울철피부건조·보습제바르는법·세라마이드크림·3분법칙·피부장벽·겨울피부관리), 임상 4개(임상리뷰·피부장벽·세라마이드·보습요법).
- 저자 표기: 두 글 모두 `저자: 겅태(의학과 경제학에 관심많은)` 한 줄로 시작, 실명 0건.
- 중복 발행: 이번 회차는 두 글 모두 발행 직후 오류 화면 없이 글 보기로 넘어갔고, 카테고리 목록에서 새 글 1건씩만 확인되어 중복 사본이 생기지 않았다.

## 유튜브 쇼츠

| 항목 | 값 |
| :--- | :--- |
| 채널 | 잘못된 의료 정보 바로잡기(잘.의.정.바) `UCHhMXW0nECx7N3wFo9TfJAg`, @promokorea |
| URL | https://youtube.com/shorts/gI6g5CRjDwg |
| 제목 | 크림을 발라도 당기는 이유, 겨울 피부에 빠진 건 물이 아닙니다 |
| 공개 상태 | 공개, 아동용 아님, 2026-11-22 게시 |
| 길이 | 0:53 (파일 52.24초) |
| 설명란 | 블로그·크리에이터샵·쇼핑 커넥트 링크, 공정위 고지, #Shorts 해시태그 포함. 실명·@ 멘션 없음 |
| 검증 | 게시 후 `youtube.com/shorts/gI6g5CRjDwg`에서 재생 확인, 저작권 검사 "발견된 문제 없음" |

## 산출물

- 원고: `post.md`, `naver_post.html`, `naver_post_publish.html`, `clinical/clinical_column.md`, `clinical/clinical_column.html`, `clinical/clinical_column_naver.html`, `ads.md`, `instagram/card_news_caption.md`
- 영상: `downloads/Day15_겨울피부건조_보습3분법칙_칠판드로잉_쇼츠.mp4` (1080x1920, 52.24초), `downloads/Day15_겨울피부건조_미리보기.gif`, `downloads/Day15_scene_1~3.png`
- 검증 캡처: `downloads/네이버블로그_day15_모바일_쇼핑커넥트링크.png`, `downloads/네이버블로그_day15_임상칼럼_모바일_쇼핑커넥트링크.png`, `downloads/Day15_유튜브_쇼츠_게시_확인.png`
- 듀얼 뷰어: `downloads/Day15_콘텐츠_이원화_듀얼뷰어.html`, `widgets/dual-content-viewer` Day 15 탭
- 생성 스크립트: `generate_day15.py`, `generate_day15_shorts.py`, `publish_prep_day15.py`, `update_widget_day15.py`
