# Day 16 발행·업로드 기록 (2026-11-23)

## 네이버 블로그

| 구분 | 카테고리 | 제목 | URL | 공개 |
| :--- | :--- | :--- | :--- | :--- |
| 대중용 | 의학·건강 (categoryNo=10) | "뜨거운 물로 씻을수록 다음 날 더 가려워요"... 겨울 샤워가 피부를 망치는 세 가지 | https://blog.naver.com/kst104/224487897690 | 전체공개 |
| 전문가용 | 임상·전문가 칼럼 (categoryNo=11) | 한랭기 세정 습관과 표피 장벽: 계면활성제·표면산도·물리적 각질제거의 병태생리와 근거 기반 세정 처방 | https://blog.naver.com/kst104/224487915036 | 전체공개 |

- 제휴: 네이버 쇼핑 커넥트 들꽃잠 배 찜질팩 온열 팥 멀티형 32,300원 `https://naver.me/Faeu91oI`, 크리에이터샵 `https://cshop.naver.com/geongtae_shop`, 공정위 고지 문구를 두 글 모두에 포함.
- 링크 방식: 스마트에디터 본문에서 각 링크 문단을 선택해 「링크 입력」으로 `span.se-link[data-href]`를 만들었고, m.blog.naver.com에서 `<a href ... target="_blank">`로 렌더되는 것을 DOM에서 확인했다.
- 태그: 대중용 6개(겨울철샤워습관·뜨거운물피부자극·약산성클렌저·때밀이·피부장벽·손습진), 임상 3개(임상리뷰·피부장벽·계면활성제).
- 저자 표기: 두 글 모두 `저자: 겅태(의학과 경제학에 관심많은)` 한 줄로 시작, 실명 0건.
- 중복 발행: 두 글 모두 발행 버튼 후 오류 화면이 떴지만 RSS(`rss.blog.naver.com/kst104.xml`) 확인 결과 새 글 1건씩만 게시되어 재발행하지 않았다.
- **임상 칼럼 게시본은 요약판**이다. 스마트에디터가 호출당 1,450자까지만 입력을 받고, 긴 원고를 여러 번 붙여 넣으면 문단 순서가 뒤섞여, 8개 절·부록으로 정리한 약 6,000자 버전을 올렸다. 저장소 원고(`clinical/clinical_column.md`, 11,091자, 표 4개)는 전체판이며 GitHub·위젯에는 전체판이 들어간다.

## 유튜브 쇼츠

| 항목 | 값 |
| :--- | :--- |
| 채널 | 잘못된 의료 정보 바로잡기(잘.의.정.바) `UCHhMXW0nECx7N3wFo9TfJAg`, @promokorea |
| URL | https://youtube.com/shorts/HulnC4Skkro |
| 제목 | 뜨거운 물로 씻을수록 더 가려운 이유, 겨울 샤워의 함정 |
| 공개 상태 | 공개, 아동용 아님, 2026-11-23 게시 |
| 길이 | 0:59 (파일 59.11초) |
| 설명란 | 블로그·크리에이터샵·쇼핑 커넥트 링크, 공정위 고지, #Shorts 해시태그 포함. 실명·@ 멘션 없음 |

## 산출물

- 원고: `post.md`, `naver_post.html`, `naver_post_publish.html`, `body-public.txt`, `clinical/clinical_column.md`, `clinical/clinical_column.html`, `clinical/clinical_column_naver.html`, `body-clinical.txt`, `ads.md`, `instagram/card_news_caption.md`, `slop_report.json`(전 원고 0점)
- 영상: `downloads/Day16_겨울샤워습관_피부장벽_칠판드로잉_쇼츠.mp4` (1080x1920, 59.11초), `downloads/Day16_겨울샤워습관_미리보기.gif`, `downloads/Day16_scene_1~3.png`
- 아트: `assets/chalkboard/day16/scene1~5.png`(칠판 분필화, 글자 없음)
- 듀얼 뷰어: `downloads/Day16_콘텐츠_이원화_듀얼뷰어.html`, `widgets/dual-content-viewer` Day 16 탭
- 생성 스크립트: `generate_day16.py`, `generate_day16_shorts.py`, `publish_prep_day16.py`

## 반영한 외부 검수 의견

- 지피티 겅태 11-22 21:05 검수 메일: 카드뉴스 첫 화면을 시간 기준('꼭 3분 안에') 대신 "씻고 물기를 가볍게 닦은 뒤 피부가 아직 촉촉할 때 보습"으로 바꾸라는 의견을 대중용 본문 3분 법칙 절, 카드뉴스 카드 1 연출 메모, 쇼츠 5씬 내레이션에 반영했다.
- 같은 메일의 일리윤 세라마이드 아토 집중크림 75mL(6,900원+배송 2,500원) 후보는 수수료·공식 이미지 사용권 미확인으로 전시·제휴를 보류했고, 제휴는 지시대로 들꽃잠 찜질팩 단일 유지다.
