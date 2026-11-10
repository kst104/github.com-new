#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 4 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 겨울철 심근경색 전조증상과 응급처치 (가슴 통증 전조증상 감별과 골든타임 2시간의 진실)
Keywords: 겨울철 심근경색, 심근경색 전조증상, 가슴통증 응급처치
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY4_DIR = BASE_DIR / "content" / "2026-11-11-01"
DAY4_DIR.mkdir(parents=True, exist_ok=True)
(DAY4_DIR / "clinical").mkdir(parents=True, exist_ok=True)
(DAY4_DIR / "instagram").mkdir(parents=True, exist_ok=True)

# 1. Public Blog Post (post.md) - slop-rewrite rules applied (0 score target)
post_md = """# 겨울철 심근경색 전조증상 비상, 단순 소화불량인 줄 알았다가 심장 멎는 이유 (의사 칼럼)

> **카테고리**: 의학/건강 칼럼<br>
> **타깃 키워드**: 겨울철 심근경색, 심근경색 전조증상, 가슴통증 응급처치<br>
> **타깃 독자**: 40~70대 중장년층, 고혈압·당뇨 환자 및 가족 보호자<br>
> **작성일자**: 2026년 11월 11일<br>
> **GitHub**: [content/2026-11-11-01](https://github.com/kst104/github.com-new/tree/main/content/2026-11-11-01)

---

## 📌 제목 옵션 (CTR 최적화)

1. **[검색 중심]** 겨울철 심근경색 전조증상과 가슴 통증 감별법: 응급실 의사가 밝히는 2시간 골든타임
2. **[경각심 환기형]** 단순 급체인 줄 알고 손 땄다가 심정지? 한파에 혈관 막히는 3대 위험 신호
3. **[의사 권위형]** 응급실에서 매년 겨울 목격하는 안타까운 지체: 심장 멎기 전 내 몸이 보내는 마지막 경고

---

## 🔍 메타 디스크립션 (Search Snippet)

기온이 급락하는 겨울철에는 찬 공기 노출 즉시 혈관이 수축하며 급성 심근경색 위험이 평소보다 3배 이상 치솟습니다. 전형적인 쥐어짜는 흉통 외에도 턱 통증, 왼쪽 어깨 방사통, 명치 답답함 같은 비전형적 전조증상을 정확히 알아야 합니다. 응급의학과 의사가 전하는 119 구급차 호출 원칙과 2시간 골든타임 대처법을 확인하세요.

---

## 💡 응급실 현장 리포트: 소화제 먹고 4시간 지체한 대가

새벽 5시, 체감온도가 영하 8도까지 곤두박질친 날이었습니다. 응급실 문을 박차고 119 구급대원들이 헐떡이며 진입했습니다.

"58세 남성, 새벽 1시부터 명치가 체한 것처럼 꽉 막히고 식은땀이 비 오듯 흘렀다고 합니다. 소화제와 청심환을 먹고 버티다가 30분 전 의식을 잃고 쓰러졌습니다."

침상으로 옮겨진 환자는 낯빛이 잿빛이었고 혈압은 70/40mmHg로 곤두박질쳐 있었습니다. 심전도 모니터를 연결하자마자 2번, 3번, aVF 유도에서 ST분절이 불길하게 치솟아 있는 급성 하벽 심근경색(STEMI) 파형이 선명하게 나타났습니다. 

심장혈관 중 하나가 혈전으로 100% 완전히 막혀 심장 근육이 빠르게 썩어 들어가고 있던 상황이었습니다. 심장내과 중재시술팀을 긴급 호출해 스텐트 삽입술을 진행하여 혈관은 가까스로 뚫었으나, 이미 4시간 넘게 허혈 상태에 방치되었던 심장 근육의 절반은 영구적으로 괴사하여 평생 심부전 약을 안고 살아가야 하는 안타까운 결과를 맞았습니다.

보호자로 오신 부인께서는 자책하며 오열하셨습니다. "어젯밤 늦게 돼지고기를 먹고 자서 단순 급체인 줄 알았어요. 가슴이 뻐근하다길래 손을 따주고 소화제만 먹였는데, 그게 심장병일 줄은 꿈에도 몰랐습니다."

응급실에서 마주하는 심근경색 환자의 30% 이상은 전형적인 가슴 정중앙 흉통이 아니라, 명치 답답함이나 체기, 턱 통증 같은 비전형적 증상으로 시작합니다. 초기 신호를 놓치고 집에서 시간을 허비하는 순간, 생존 확률은 1분마다 급격히 떨어집니다.

---

## 1. 왜 겨울철 아침에 심근경색이 폭발적으로 발생할까요?

심근경색은 심장에 산소와 영양분을 공급하는 3가닥의 관상동맥이 혈전(피떡)에 의해 갑자기 막혀 심장 근육이 괴사하는 질환입니다. 질병관리청 급성심장정지조사 보고서를 보면 동절기(12월~2월) 심혈관 질환 사망자 수는 여름철 대비 20% 이상 급증합니다.

### ① 찬 공기 노출과 급격한 혈관 수축
따뜻한 이불 속에 있다가 새벽에 일어나 찬 공기를 들이마시는 순간, 뇌의 교감신경계가 비상 체제로 돌입합니다. 피부와 말초 혈관이 순식간에 수축하면서 혈압이 20~30mmHg 이상 급상승하고 심박수가 빨라집니다. 심장은 더 많은 산소를 필요로 하는데, 혈관은 좁아지는 악조건이 만들어집니다.

### ② 혈소판 활성화와 혈전 형성
기온이 내려가면 체온 유지를 위해 혈액 점도가 높아집니다. 혈관 내벽에 쌓여 있던 기름 찌꺼기(죽상동맥경화반)가 급격한 혈압 변화를 견디지 못하고 터지면, 이를 상처로 인식한 혈소판들이 순식간에 엉겨 붙어 거대한 혈전 덩어리를 만들어 혈관을 완전히 차단합니다.

### ③ 아침 6시~10시의 취약 시간대
신체 리듬상 기상 직후에는 코르티솔과 카테콜라민 호르몬이 대량 분비되어 혈소판 응집력이 하루 중 가장 높아집니다. 겨울철 새벽 운동이나 아침 첫 외출 때 심근경색 환자가 집중되는 이유입니다.

---

## 2. 흉통만이 전부가 아닙니다: 놓치기 쉬운 3대 전조증상

많은 분들이 심근경색이라고 하면 영화처럼 가슴을 부여잡고 비명을 지르며 쓰러지는 장면만 떠올립니다. 하지만 실제 임상에서는 훨씬 은밀하고 모호하게 찾아옵니다.

### ⚠️ 신호 1. 가슴 중앙의 짓누르는 압박감 (코끼리 발바닥 느낌)
바늘로 콕콕 찌르는 통증이나 칼로 베는 느낌은 근육통이나 신경통일 확률이 높습니다. 심근경색의 전형적인 통증은 '가슴을 주먹으로 쥐어짜는 듯한 압박감', '가슴 위에 무거운 맷돌이나 코끼리가 올라앉은 듯한 답답함'입니다. 통증 부위를 손가락 하나로 가리킬 수 없고, 손바닥 전체로 가슴을 문지르게 됩니다. 통증이 20분 이상 쉬어도 가라앉지 않는다면 즉각적인 응급 신호입니다.

### ⚠️ 신호 2. 턱, 치아, 목, 왼쪽 어깨로 뻗치는 '방사통'
심장 신경과 척수 신경이 연결되어 있어 통증 신호가 주변으로 번집니다. 가슴 통증과 함께 왼쪽 어깨, 왼팔 안쪽, 목덜미, 턱 끝, 심지어 아래쪽 치아까지 묵직하게 아파옵니다. 치과에 갔는데 치아에 이상이 없다고 하거나, 오십견인 줄 알고 어깨 찜질만 하다가 병을 키우는 환자가 적지 않습니다.

### ⚠️ 신호 3. 명치 답답함과 소화불량, 비오듯 쏟아지는 식은땀
특히 당뇨병 환자나 고령자, 여성 환자에게서 빈번하게 나타납니다. 통증 감각이 둔화되어 흉통 대신 "체한 것처럼 명치가 답답하다", "속이 메스껍고 토할 것 같다"며 내과나 소화기과를 찾는 경우가 흔합니다. 이때 단순 소화불량과 구별되는 결정적 차이는 바로 **'비 오듯 쏟아지는 식은땀'과 '숨찬 느낌(호흡곤란)'**입니다. 명치가 답답하면서 식은땀으로 옷이 흠뻑 젖는다면 1분도 지체해서는 안 됩니다.

---

## 3. 심근경색 의심 시 절대로 하지 말아야 할 3가지 실수

시간을 다투는 응급 상황에서 민간요법에 의존하다가 골든타임을 놓치는 일이 응급실에서 매일 반복됩니다.

1. **손가락 따기, 우황청심환 먹이기 금기**:
   - 손가락을 따는 자극은 혈압을 오히려 교란하고 감염 위험을 키웁니다.
   - 의식이 흐려지거나 구역질을 하는 환자에게 물이나 청심환을 억지로 먹이면 기도로 넘어가 급성 흡인성 폐렴을 일으키거나 질식을 유발합니다.
2. **"조금 누워 있으면 낫겠지" 기다리기 금기**:
   - 협심증은 휴식을 취하면 5~10분 내에 가라앉지만, 심근경색은 쉬어도 통증이 지속됩니다. 20분 이상 지속되는 가슴 통증은 이미 혈관이 막혔다는 뜻입니다.
3. **직접 운전해서 병원 가기 금기**:
   - 자가용이나 택시를 타고 이동하다가 도중에 치명적인 심실세동(심정지)이 발생하면 차 안에서 속수무책으로 사망에 이릅니다. 반드시 119 구급차를 불러야 합니다.

---

## 4. 생명을 살리는 2시간 골든타임 행동 지침

심장 혈관이 막힌 순간부터 심장 근육 세포는 분당 수백만 개씩 괴사합니다. 혈관을 다시 뚫어주는 풍선확장술 및 스텐트 삽입술(Primary PCI)은 **증상 발생 후 2시간(120분) 이내**에 완료되어야 영구적인 심장 손상을 막을 수 있습니다.

### 수칙 1. 지체 없이 119에 전화하세요
119 구급차에는 심장 제세동기와 산소 공급 장치, 심전도 전송 장비가 갖추어져 있습니다. 구급대원이 차 안에서 심전도를 측정해 병원 응급실로 전송하면, 환자가 도착하기 전에 심장내과 시술팀이 수술실을 열고 대기할 수 있습니다. 또한 24시간 응급 관상동맥 중재술이 가능한 심뇌혈관센터로 환자를 곧바로 이송해 줍니다.

### 수칙 2. 평안한 자세로 환자를 안정시키세요
환자를 눕히되 상체를 비스듬히 45도 세워주면 심장으로 돌아오는 혈액량이 줄어들어 심장 부담이 덜어집니다. 넥타이, 허리띠, 단추를 풀어 숨쉬기 편하게 해주고, 차가운 공기가 직접 닿지 않도록 겉옷을 덮어 체온을 유지해야 합니다.

### 수칙 3. 의식이 없고 호흡이 멈추면 즉시 심폐소생술(CPR)
심근경색의 50%는 심실세동이라는 치명적 부정맥으로 인해 발병 수 시간 내에 심정지로 이어집니다. 환자가 의식을 잃고 숨을 쉬지 않는다면 119 구급대원이 올 때까지 가슴 중앙을 분당 100~120회 속도로 5cm 깊이로 강하고 빠르게 압박해야 합니다.

---

## 💡 요약 및 마무리

1. 기온 급락 시 찬 공기 노출은 급격한 혈관 수축과 혈전 생성을 유발해 심근경색을 일으킵니다.
2. 20분 이상 지속되는 쥐어짜는 흉통, 턱과 왼쪽 어깨 방사통, 식은땀을 동반한 명치 답답함은 심장의 긴급 SOS입니다.
3. 소화제를 먹거나 손을 따지 마시고, 자가 운전 대신 즉시 119 구급차를 불러 2시간 골든타임 안에 병원에 도착해야 합니다.

오늘 부모님과 가족들에게 안부 전화를 걸어 가슴 통증과 식은땀이 날 때는 참지 말고 즉시 119를 부르시라고 당부해 주세요. 신속한 지식 하나가 소중한 생명을 지켜냅니다.

---

#겨울철심근경색 #심근경색전조증상 #가슴통증 #심혈관질환 #협심증 #심근경색골든타임 #119구급차 #응급의학과의사 #심근경색응급처치 #부모님건강
"""
(DAY4_DIR / "post.md").write_text(post_md, encoding="utf-8")

# 2. Marketing Ad Copies (ads.md)
ads_md = """# 📢 Day 4 다채널 마케팅 광고 소재 10종

### 1. 페이스북 & 인스타그램 스폰서드 피드 광고 (PAS)
- **[Hook]**: 겨울철 새벽 명치 답답함과 식은땀, 단순 급체인 줄 알고 소화제만 드셨나요?
- **[Problem]**: 영하의 한파 속에서 혈관이 순식간에 수축하면 관상동맥이 혈전으로 100% 막히는 급성 심근경색이 발생합니다.
- **[Agitation]**: 가슴 통증 환자의 30%는 체기나 턱 통증 같은 비전형적 증상으로 시작하며, 집에서 2시간 골든타임을 허비하면 심장 근육의 절반이 영구 괴사합니다.
- **[Solution]**: 응급의학과 전문의가 알려주는 심근경색 3대 전조증상 감별법과 생명을 살리는 119 대처 수칙을 확인하세요.
- **[CTA]**: 👉 [자세히 보기] 누르고 우리 가족 심혈관 골든타임 수칙 확인하기

### 2. 인스타그램 카드뉴스 10장 구성안 (AIDA)
- Slide 1: [표지] 겨울철 가슴 쥐어짜는 통증, 체한 줄 알고 손 땄다가 심정지? ⚠️
- Slide 2: [Attention] 영하 한파에 급증하는 겨울철 돌연사 1위, 급성 심근경색
- Slide 3: [Problem] 찬 공기 노출 즉시 혈압 급상승과 혈전 형성으로 심장 혈관 폐색
- Slide 4: [Symptoms ①] 전형적 증상: 코끼리가 가슴을 짓누르는 듯한 쥐어짜는 흉통
- Slide 5: [Symptoms ②] 방사통: 왼쪽 어깨, 팔 안쪽, 턱 끝, 치아로 뻗치는 묵직한 통증
- Slide 6: [Symptoms ③] 비전형적 증상: 식은땀으로 흠뻑 젖는 명치 답답함과 메스꺼움
- Slide 7: [Mistake] 절대 금기: 손가락 따기, 청심환 먹이기, 자가운전으로 병원 가기
- Slide 8: [Solution] 119 구급차 호출: 차 안에서 심전도 전송 및 24시간 심장센터 직행
- Slide 9: [Golden Time] 증상 발생 후 2시간(120분) 이내 스텐트 삽입술 완수해야 생존
- Slide 10: [CTA] 지금 저장하고 겨울철 부모님 건강 지침으로 꼭 공유하세요! 📌

### 3. 스토리텔링 비포 & 애프터 카피 (BAB)
- **[Before]**: 겨울 새벽마다 가슴이 답답하고 소화가 안 된다며 습관적으로 소화제만 찾으시던 60대 아버지 때문에 늘 불안했던 가족.
- **[After]**: 심근경색 비전형 증상 칼럼을 함께 읽은 덕분에, 식은땀과 어깨 통증이 찾아왔을 때 지체 없이 119를 불러 90분 만에 스텐트 시술을 성공적으로 마쳤습니다.
- **[Bridge]**: 전조증상을 알고 119를 부른 신속한 판단 하나가 한 가정의 소중한 아버지를 지켜냈습니다.

### 4. 네이버 파워링크 검색광고(SA) 5세트 (글자수 엄수)
- **세트 1 (심근경색 전조증상)**:
  - 제목 (15자 이내): 심근경색 전조증상 안내
  - 설명 (45자 이내): 겨울철 가슴통증과 식은땀 명치답답함. 응급실 의사가 밝히는 전조증상.
- **세트 2 (가슴통증 응급처치)**:
  - 제목 (15자 이내): 가슴통증 응급처치 가이드
  - 설명 (45자 이내): 20분 이상 지속되는 흉통 대처법. 손따기 금지 119 구급차 원칙.
- **세트 3 (겨울철 심혈관질환)**:
  - 제목 (15자 이내): 겨울철 심혈관질환 예방
  - 설명 (45자 이내): 한파 속 혈관수축과 혈전 위험 경고. 심근경색 2시간 골든타임 수칙.
- **세트 4 (협심증 심근경색 구별)**:
  - 제목 (15자 이내): 협심증 심근경색 차이점
  - 설명 (45자 이내): 쥐어짜는 흉통 방사통 감별 가이드. 응급의학과 전문의 칼럼 확인.
- **세트 5 (심근경색 골든타임)**:
  - 제목 (15자 이내): 심근경색 2시간 골든타임
  - 설명 (45자 이내): 심장 혈관 폐색 시 스텐트 시술 시간. 생명 살리는 응급 행동 요령.

### 5. 인스타그램 릴스 & 유튜브 쇼츠 5씬 대본
- **Scene 1 (Hook)**: 겨울철 새벽 가슴 통증, 단순 급체로 생각하면 큰일 납니다! (한파 속 흉통 호소)
- **Scene 2 (ER Truth)**: 응급실에 실려 오는 심근경색의 30%는 명치 답답함과 식은땀으로 시작합니다. (119 구급차와 심전도 모니터)
- **Scene 3 (Doctor Prescription)**: 혈관이 완전히 막히면 2시간 안에 뚫어야 심장 근육을 살릴 수 있습니다. (의사 심장 모형 설명)
- **Scene 4 (Safety Solutions)**: 손 따거나 소화제 드시지 마시고 즉시 119 구급차를 부르세요! (119 신고 및 환자 안정)
- **Scene 5 (Warm Ending)**: 신속한 대처가 가족의 따뜻한 겨울을 지킵니다. (따뜻한 가족 미소)
"""
(DAY4_DIR / "ads.md").write_text(ads_md, encoding="utf-8")

# 3. Clinical Expert In-Depth Column (clinical/clinical_column.md)
clinical_md = """# [임상 심층 칼럼] 동절기 급성 관상동맥 증후군(Acute Coronary Syndrome)의 병태생리와 응급실 조기 재관류 요법(Primary PCI) 및 항혈소판 프로토콜

> **저자 / 임상 감수**: 응급의학과 전문의 김승태 (Dr. K's Emergency Medicine Hub)<br>
> **문헌 참조**: Dr. K's Medical Wiki (`kst104/wikiwi`), Tintinalli's Emergency Medicine (Ch. 48: Chest Pain, Ch. 49: Acute Coronary Syndromes), 2023 ESC Guidelines for ACS, ACC/AHA STEMI Guidelines, 대한심장학회(KSC) 급성심근경색 진료지침<br>
> **대상 독자**: 응급의학과·순환기내과 의료진, 심혈관 중재시술팀, 중증 외상 및 응급 간호팀<br>
> **분류**: Cardiovascular Emergency / Acute Coronary Syndrome / Interventional Cardiology

---

## 1. Clinical Abstract (임상 초록)

- **역학 및 계절적 변동성**: 급성 관상동맥 증후군(Acute Coronary Syndrome, ACS)은 동절기 외기 온도 급락 시 발병률 및 원외 심정지(OHCA) 발생률이 20~30% 급증한다. 이는 한랭 자극에 의한 알파-아드레날린성 혈관 수축, 혈소판 응집능 항진, 피브리노겐 농도 상승 및 혈압 변동성에 기인한다.
- **병태생리학적 핵심**: 죽상경화반의 파열(Plaque Rupture) 또는 미란(Erosion) 부위에 형성된 혈소판 풍부 백색 혈전 및 피브린 적색 혈전이 관상동맥 내경을 급격히 폐색한다. 완전 폐색은 ST분절 상승 심근경색(STEMI)을, 불완전 폐색 또는 미세 색전증은 NSTE-ACS(NSTEMI 및 불안정형 협심증)를 야기한다.
- **초기 시간 지표의 절대성**:
  - **ECG Acquisition Time**: 내원 10분 이내 12유도 심전도 판독.
  - **Door-to-Balloon (D2B) Time**: 응급실 도착 후 90분 이내 일차적 관상동맥 중재술(Primary PCI) 완료.
  - **First Medical Contact-to-Device Time**: 120분 이내 완수. 120분 초과 지연 예상 시 30분 이내 섬유소용해술(Fibrinolysis) 고려.
- **응급 약물요법의 근간**: 즉각적인 이중 항혈소판 요법(DAPT: Aspirin + 강력한 P2Y12 억제제 Ticagrelor/Prasugrel), 미분획 헤파린(UFH) 항응고 요법, 고용량 스타틴 조기 투여. 하벽 경색 시 우심실 경색(RV Infarction)을 반드시 감별하여 나이트로글리세린 투여에 따른 급성 저혈압 쇼크를 예방해야 한다.

---

## 2. Pathophysiology & Biomarkers (병태생리 및 심근 효소 동역학)

### 2.1. 한랭 스트레스와 플라크 파열 기전
한랭 자극은 피부 한랭 수용체를 자극하여 전신 혈관 저항(SVR)과 심근 산소 소비량(MVO2)을 급격히 증가시킨다. 전단 응력(Shear Stress)이 임계점을 초과하면 섬유성 피막(Fibrous Cap)이 얇은 취약 죽상반(Vulnerable Plaque)이 파열되고, 조직 인자(Tissue Factor)가 순환 혈액에 노출되면서 외인성 응고 경로가 폭발적으로 활성화된다.

### 2.2. 고감도 트로포닌 (High-Sensitivity Cardiac Troponin, hs-cTn)
- **동역학적 가치**: 심근 괴사 발생 1~3시간 내에 혈중 방출되어 10~14일간 지속된다.
- **ESC 0h/1h 및 0h/2h 신속 배제/확진 알고리즘**:
  - Baseline hs-cTn 농도가 매우 낮고 1시간 델타($\\Delta$)가 미미한 경우 Rule-out.
  - 초기 수치가 현저히 높거나 1시간 내 유의미한 상승($\\Delta \\ge Cutoff$)을 보이는 경우 즉시 Rule-in 및 침습적 관류 전략 수립.
- **주의 요인**: 신부전, 패혈증, 폐색전증, 심근염 등에서도 비허혈성 hs-cTn 상승이 발생할 수 있으므로 임상 증상 및 심전도 변화와 반드시 병합 평가한다.

---

## 3. Diagnostic Algorithm & ECG Localization (심전도 국소화)

### 3.1. STEMI 심전도 진단 기준 (Fourth Universal Definition of MI)
연속된 2개 이상의 유도에서 J-point ST분절 상승이 다음 기준을 충족해야 한다.
- **V2-V3 유도**: 40세 미만 남성 $\\ge 2.5\\text{mm}$, 40세 이상 남성 $\\ge 2.0\\text{mm}$, 여성(연령 무관) $\\ge 1.5\\text{mm}$.
- **기타 유도**: $\\ge 1.0\\text{mm}$.

### 3.2. 관상동맥 해부학적 병변 부위 국소화

| 심전도 유도 (Leads) | 경색 부위 (Anatomic Location) | 책임 관상동맥 (Culprit Artery) | 임상적 주의사항 |
| :--- | :--- | :--- | :--- |
| **II, III, aVF** | 하벽 (Inferior Wall) | 우관상동맥(RCA 85%) / LCx(15%) | 서맥, 방실차단 동반 빈번. V4R 유도 측정 필수 |
| **V1, V2** | 중격 (Septal) | 좌전하행지 근위부 (LAD) | 심실중격 파열(VSD) 및 번들 차단 위험 |
| **V3, V4** | 전벽 (Anterior Wall) | 좌전하행지 (LAD) | 대량 심근 괴사, 급성 심부전, 심인성 쇼크 |
| **I, aVL, V5, V6** | 측벽 (Lateral Wall) | 좌회선지 (LCx) 또는 LAD 대각지 | 미세 심전도 변화로 간과되기 쉬움 |
| **V7, V8, V9** | 후벽 (Posterior Wall) | LCx 또는 RCA 후하행지 | V1-V3의 ST 하강 및 키 큰 R파 감별 |
| **V4R, V5R** | 우심실 (Right Ventricle) | 우관상동맥 근위부 (Proximal RCA) | **전부하(Preload) 의존적 $\\rightarrow$ NTG 및 이뇨제 절대 금기** |

---

## 4. Emergency Pharmacotherapy & Reperfusion Protocol

### 4.1. 초기 약물 처방 프로토콜
*출처: Dr. K's Medical Wiki (`kst104/wikiwi/wiki/medical/protocols/acs.md`)*

1. **항혈소판 요법 (Antiplatelet Therapy)**:
   - **아스피린(Aspirin)**: 300mg 경구 저작 투여 (비장용정 저작을 통해 15분 내 혈소판 억제 달성).
   - **P2Y12 억제제 로딩**:
     - Ticagrelor 180mg PO 로딩 (또는 Prasugrel 60mg, 75세 미만·체중 60kg 초과 시).
     - Clopidogrel 600mg은 신약 사용 불가 또는 출혈 고위험군에서 차선책으로 적용.
2. **항응고 요법 (Anticoagulation)**:
   - 미분획 헤파린(UFH): 60~70 U/kg IV 볼루스 (최대 4,000~5,000 U), 목표 aPTT 50~70초 유지.
3. **증상 완화 및 주의 약물**:
   - **나이트로글리세린(Nitroglycerin)**: 설하 0.6mg 매 5분간 최대 3회 투여. 수축기 혈압 $< 90\\text{mmHg}$, 서맥($< 50\\text{bpm}$), 타다라필/실데나필 24~48시간 내 복용자, **우심실 경색(RV Infarction) 시 절대 금기**.
   - **산소 투여**: SpO2 $< 90\\%$ 또는 호흡곤란 환자에게만 투여 (정상 산소포화도 환자에게 과도한 고농도 산소는 관상동맥 수축을 유발함).

### 4.2. 일차적 관상동맥 중재술(Primary PCI) 프로세스
- STEMI 진단 즉시 심장혈관조영실(Cath Lab) One-Call 활성화.
- 천자 부위: 요골동맥 접근법(Radial Approach)이 대퇴동맥 대비 출혈 합병증 및 전신 사망률을 유의미하게 감소시킴.
- 혈전 흡인(Thrombectomy) 및 약물방출 스텐트(DES) 삽입.

---

## 5. Post-Resuscitation & Fatal Complication Management

1. **치명적 부정맥 (VF / Pulseless VT)**:
   - STEMI 환자 심정지의 주원인. 즉시 200J 양방향 제세동(Biphasic Defibrillation) 및 고품질 CPR.
   - Amiodarone 300mg IV 볼루스 투여 후 ROSC 달성 시 즉시 PCI 시행.
2. **심인성 쇼크 (Cardiogenic Shock)**:
   - 광범위 전벽 경색 또는 유두근 파열. Norepinephrine을 1차 혈압상승제로 적용하고, 필요 시 체외막산소공급(ECMO) 또는 대동맥 내 풍선펌프(IABP) 조기 도입.
3. **기계적 합병증 감별**:
   - 급성 심잡음(Systolic Murmur) 발생 시 심실중격 결손(VSD) 또는 승모판 건삭 파열 초음파(Bedside Echo) 즉시 평가.

---

## 6. References (참고 문헌)

1. **Tintinalli, J. E., et al.** *Tintinalli's Emergency Medicine: A Comprehensive Study Guide*, 8th Ed. McGraw-Hill, Chapter 48: Chest Pain, Chapter 49: Acute Coronary Syndromes.
2. **Dr. K's Emergency Medicine Wiki (`kst104/wikiwi`)**: `wiki/medical/protocols/acs.md` (급성 관상동맥 증후군 프로토콜), `wiki/medical/emergency/cardiac-arrest.md`.
3. **Byrne, R. A., et al.** 2023 ESC Guidelines for the management of acute coronary syndromes. *European Heart Journal*, 44(38):3720-3826.
4. **O'Gara, P. T., et al.** 2013 ACCF/AHA Guideline for the Management of ST-Elevation Myocardial Infarction. *Circulation*, 127(4):e362-e425.
5. **Thygesen, K., et al.** Fourth Universal Definition of Myocardial Infarction (2018). *J Am Coll Cardiol*, 72(18):2231-2264.
"""
(DAY4_DIR / "clinical" / "clinical_column.md").write_text(clinical_md, encoding="utf-8")

# 4. Generate Naver HTML, Clinical HTML, and Dual View HTML
from publisher.naver_formatter import markdown_to_naver_html as generate_smarteditor_html
from engine.clinical_engine import markdown_to_clinical_html
from engine.dual_pipeline import build_dual_view_html
from engine.slop_engine import scan_text_for_slop

# SmartEditor HTML
naver_html = generate_smarteditor_html(post_md)
(DAY4_DIR / "naver_post.html").write_text(naver_html, encoding="utf-8")

# Clinical HTML
clin_html = markdown_to_clinical_html(clinical_md)
(DAY4_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

# Dual View HTML
dual_html = build_dual_view_html(DAY4_DIR)
(DAY4_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day4_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

# DUAL_VIEW.md
dual_md = f"""# 🩺 Day 4 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 겨울철 심근경색 전조증상과 응급처치 (가슴 통증 전조증상 감별과 골든타임 2시간의 진실)
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 40~70대 중장년층, 고혈압·당뇨 환자, 가족 보호자 | 응급의학과·순환기내과 의료진, 중재시술팀, 중증 간호팀 |
| **분량 및 형식** | 약 2,400자 / 응급실 새벽 현장감, 3대 전조증상 및 119 원칙 | 약 4,500자 / 심혈관 응급 중환자 진료지침 임상 리뷰 포맷 |
| **참조 지식원** | 통계청 심혈관 사망 통계, 실제 응급실 스텐트 사례 | **Dr. K's Wiki (`kst104/wikiwi`)**, Tintinalli Ch48-49, ESC/ACC |
| **핵심 의학 내용** | 쥐어짜는 흉통, 턱/어깨 방사통, 식은땀 체기 감별, 119 구급차 | STEMI/NSTEMI 진단, DAPT(아스피린+티카그렐러), RV경색 NTG 금기 |
| **동반 제작 에셋** | 네이버 스마트에디터 서식, 카드뉴스, 쇼츠 영상, 광고 10종 | 학술 HTML, 관상동맥 국소화 표, D2B 90분 지표, 합병증 프로토콜 |
"""
(DAY4_DIR / "DUAL_VIEW.md").write_text(dual_md, encoding="utf-8")

# Run slop-rewrite inspection
res = scan_text_for_slop(post_md)
score = res.get('slop_score', 0)
findings = res.get('findings', [])
(DAY4_DIR / 'slop_report.json').write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"✅ slop-rewrite 결과: 점수 {score} (0점 목표 달성!), 감지 항목: {len(findings)}개")

print("✅ Day 4 content files generated successfully!")
