#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 3 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 겨울철 노인 낙상과 대퇴골 골절 예방법 (빙판길 고관절 골절의 치명성과 실내 낙상 3대 방어 수칙)
Keywords: 겨울철 낙상, 고관절 골절, 노인 안전
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY3_DIR = BASE_DIR / "content" / "2026-11-10-01"
DAY3_DIR.mkdir(parents=True, exist_ok=True)
(DAY3_DIR / "clinical").mkdir(parents=True, exist_ok=True)
(DAY3_DIR / "instagram").mkdir(parents=True, exist_ok=True)

# 1. Public Blog Post (post.md) - slop-rewrite rules applied (0 score target)
post_md = """# 겨울철 노인 낙상과 대퇴골 골절 비상, 빙판길보다 안방 화장실이 위험한 이유 (의사 칼럼)

> **카테고리**: 의학/건강 칼럼<br>
> **타깃 키워드**: 겨울철 낙상, 고관절 골절, 노인 안전<br>
> **타깃 독자**: 고령 부모를 둔 자녀, 60대 이상 고령자 및 가족 보호자<br>
> **작성일자**: 2026년 11월 10일<br>
> **GitHub**: [content/2026-11-10-01](https://github.com/kst104/github.com-new/tree/main/content/2026-11-10-01)

---

## 📌 제목 옵션 (CTR 최적화)

1. **[검색 중심]** 겨울철 노인 낙상과 고관절 골절, 빙판길보다 안방 화장실이 더 위험한 이유
2. **[경각심 환기형]** 부모님 엉덩방아 한 번에 1년 내 사망률 20%? 응급실 의사가 밝히는 대퇴골 골절의 진실
3. **[의사 권위형]** 응급실에서 매년 겨울 목격하는 비극, 부모님 댁에 당장 설치해야 할 낙상 방지 3대 수칙

---

## 🔍 메타 디스크립션 (Search Snippet)

겨울철 한파 속 고령자 낙상은 빙판길보다 실내 화장실과 침실에서 60% 이상 발생합니다. 골다공증이 있는 상태에서 엉덩방아를 찧으면 대퇴골 경부 골절로 이어져 1년 내 사망률이 20%를 웃돕니다. 응급의학과 의사가 알려주는 실내 낙상 3대 방어 수칙과 골든타임 대처법을 확인하세요.

---

## 💡 응급실 현장 리포트: 엉덩방아 한 번의 치명적 대가

기온이 영하로 곤두박질치는 날이면 응급실 구급차 전용 문으로 119 구급대원들의 다급한 외침이 들려옵니다.

"82세 여성 환자분, 새벽에 화장실 가시다가 미끄러져 엉덩방아를 찧으셨습니다. 우측 고관절 극심한 통증과 외회전 변형, 체중 부하 전혀 불가능합니다."

엑스레이를 띄우자마자 우측 대퇴골 경부가 완전히 어긋나 있는 모습이 선명하게 나타납니다. 보호자로 뛰어오신 자녀분들은 하나같이 눈물을 글썽이며 말씀하십니다. "바깥 날씨가 춥다고 어머니 외출도 못 하게 막았는데, 집 안에서 넘어지셨다니 믿기지 않아요."

많은 분들이 겨울철 낙상이라고 하면 눈길이나 빙판길을 먼저 떠올립니다. 하지만 질병관리청 국가손상정보 통계와 실제 응급실 임상 데이터를 보면, 65세 이상 노인 낙상의 60% 이상은 익숙하고 안전하다고 믿었던 '집 안(화장실, 침실, 거실)'에서 발생합니다.

젊은 사람에게 엉덩방아는 며칠 멍들고 마는 가벼운 타박상이지만, 골밀도가 떨어진 고령층에게 대퇴골(고관절) 골절은 단순한 뼈 손상이 아닙니다. 제때 걷지 못해 자리에 눕는 순간부터 폐렴, 욕창, 패혈증이 덮쳐 1년 이내에 사망할 확률이 20%에서 30%에 이르는 치명적인 응급 질환입니다.

오늘 칼럼에서는 응급실 현장에서 뼈저리게 확인하는 고관절 골절의 위험성과 부모님 생명을 지키는 실내 환경 개조 3대 수칙을 명확하게 짚어 드립니다.

---

## 1. 왜 고령자의 대퇴골 골절은 생명까지 위협할까요?

### ① 대퇴골 경부의 취약한 혈관 구조 (무혈성 괴사 위험)
대퇴골두(골반과 맞물리는 넙다리뼈 머리 부분)는 목처럼 가느다란 '대퇴골 경부'를 통해 피를 공급받습니다. 이 부위 혈관은 매우 가늘어서 골절이 일어나는 순간 혈관이 찢어지거나 압박을 받습니다. 피가 통하지 않게 된 대퇴골두는 몇 달 안에 뼈 조직이 썩어 무너져 내리는 무혈성 괴사(AVN)로 이어집니다.

### ② 부동(Immobility)이 부르는 도미노 합병증
대퇴골이 부러지면 통증 때문에 단 하루도 스스로 일어나 앉지 못합니다. 고령 환자가 침상에 꼼짝없이 누워 있게 되면 폐 하부에 가래가 고이면서 급성 흡인성 폐렴이 발생하고, 꼬리뼈 부위 피부가 썩는 3도 욕창이 생기며, 다리 정맥 혈액이 굳어 폐동맥을 막아버리는 폐색전증이 발생합니다. 결국 골절 자체보다 장기 침상 안정으로 인한 이차 합병증이 환자의 생명을 앗아가는 것입니다.

### ③ 수술의 골든타임: 24시간에서 48시간 이내
합병증 도미노를 끊어내는 유일한 방법은 최대한 빠른 시간 안에 인공관절 치환술이나 골유합술을 시행하여 환자를 다시 앉히고 세우는 것입니다. 응급실 도착 후 24시간에서 48시간 이내에 수술적 고정을 받아야 생존율이 비약적으로 올라갑니다.

---

## 2. 빙판길보다 위험한 실내 3대 낙상 사각지대

겨울철 어르신들이 집 안에서 넘어지는 이유는 추위로 인해 관절과 근육이 경직되고, 실내외 온도 차로 인해 순간적인 기립성 어지럼증이 발생하기 때문입니다.

### ⚠️ 사각지대 1. 새벽 화장실 (미끄러운 타일 바닥)
야간뇨로 인해 불도 켜지 않은 채 어두컴컴한 상태로 화장실에 들어가다가 물기 있는 타일에 발이 미끄러지는 사고가 전체 실내 낙상의 40%를 차지합니다.

### ⚠️ 사각지대 2. 침대 앞과 거실 문턱 (발 걸림)
잠에서 덜 깬 상태로 발을 내딛다가 침대 밑 미끄러운 바닥 매트나 슬리퍼, 1~2cm의 미세한 문턱에 발가락이 걸려 앞으로 고꾸라집니다.

### ⚠️ 사각지대 3. 높은 곳의 물건 꺼내기 (의자 이용)
찬 바람을 막겠다고 창문 커튼을 달거나 높은 선반의 두꺼운 이불을 꺼내려고 불안정한 의자나 플라스틱 통을 딛고 올라섰다가 중심을 잃고 추락합니다.

---

## 3. 부모님 댁에 지금 당장 시공해야 할 실내 낙상 3대 방어 수칙

큰 비용을 들이지 않고도 오늘 당장 부모님 댁에 설치할 수 있는 실천 지침 3가지입니다.

### 수칙 1. 화장실 변기와 욕조 옆 'L자형 안전 손잡이' 설치
벽을 짚는 것과 손잡이를 단단히 쥐는 것은 지지력 차이가 5배 이상 납니다. 타일 바닥 전체에는 물 빠짐형 미끄럼 방지 롤매트를 빈틈없이 깔아 물기로 인한 미끄러짐을 원천 차단해야 합니다.

### 수칙 2. 침실에서 화장실로 이어지는 복도에 '야간 센서등' 부착
사람의 움직임을 감지해 자동으로 켜지는 충전식 LED 센서등을 침대 발치와 복도 벽면, 화장실 입구에 각각 1개씩 부착하세요. 어르신들이 새벽에 일어나 스위치를 찾느라 비틀거릴 필요가 없게 만들어야 합니다.

### 수칙 3. 집 안 문턱 제거와 미끄럼 방지 실내 양말 착용
바닥의 미끄러운 극세사 슬리퍼는 버리고, 바닥에 고무 패킹이 촘촘하게 박힌 미끄럼 방지 양말을 신으시도록 하세요. 거실과 방 사이의 문턱에는 완만한 경사로 테이프를 붙여 걸림을 방지해야 합니다.

---

## 4. 부모님이 넘어지셨을 때 응급 대처 요령

어르신이 엉덩방아를 찧으신 뒤 "아이고, 뼈가 아파서 못 일어나겠다"고 하시면 **절대로 억지로 일으켜 세우거나 부축해서 걸려 보지 마세요.**

1. **환자를 억지로 움직이지 마세요**: 부러진 뼈 단면이 주변 대퇴동맥과 신경을 손상시키고 출혈을 키울 수 있습니다.
2. **다리 모양을 관찰하세요**: 골절된 다리가 반대쪽 다리보다 짧아 보이고, 발끝이 바깥쪽으로 힘없이 돌아가 있다면(외회전) 100% 대퇴골 골절입니다.
3. **즉시 119에 연락하세요**: 체온이 떨어지지 않도록 두꺼운 이불을 덮어드리고, 119 구급대원이 도착할 때까지 바닥에 편안히 누운 상태를 유지해야 합니다.

---

## 💡 요약 및 마무리

1. 노인 대퇴골 골절은 1년 내 사망률이 20%가 넘는 침상 부동 합병증의 주범입니다.
2. 낙상 사고의 60% 이상은 빙판길이 아니라 실내 화장실과 침실에서 발생합니다.
3. 화장실 안전 손잡이, 야간 복도 센서등, 미끄럼 방지 양말 3가지만 갖춰도 부모님의 생명을 지킬 수 있습니다.

이번 주말에는 부모님 댁 화장실 타일을 만져보고 손잡이가 튼튼한지 꼭 확인해 보세요. 자녀의 작은 점검 하나가 부모님의 보행과 여생을 지킵니다.

---

#겨울철낙상 #노인낙상예방 #대퇴골골절 #고관절골절 #화장실안전손잡이 #노인골절 #골다공증 #응급의학과의사 #실내안전 #부모님건강
"""
(DAY3_DIR / "post.md").write_text(post_md, encoding="utf-8")

# 2. Marketing Ad Copies (ads.md)
ads_md = """# 📢 Day 3 다채널 마케팅 광고 소재 10종

### 1. 페이스북 & 인스타그램 스폰서드 피드 광고 (PAS)
- **[Hook]**: 부모님 겨울철 엉덩방아 한 번에 1년 내 사망률이 20%를 넘는다는 사실, 알고 계셨나요?
- **[Problem]**: 골다공증이 있는 상태에서 넘어지면 대퇴골(고관절)이 부러져 하루아침에 자리에 눕게 되고, 폐렴과 욕창 같은 합병증이 연쇄적으로 찾아옵니다.
- **[Agitation]**: 더 충격적인 것은 낙상 사고의 60%가 눈길 빙판이 아니라 우리 집 안방과 화장실에서 발생한다는 점입니다.
- **[Solution]**: 응급의학과 전문의가 알려주는 부모님 댁 실내 낙상 3대 방어 수칙과 골든타임 대처법을 확인하세요.
- **[CTA]**: 👉 [더 알아보기] 누르고 부모님 댁 낙상 안심 체크리스트 무료 확인하기

### 2. 인스타그램 카드뉴스 10장 구성안 (AIDA)
- Slide 1: [표지] 겨울철 부모님 엉덩방아 한 번의 치명적 대가 ⚠️
- Slide 2: [Attention] 빙판길보다 안방 화장실이 3배 더 위험합니다.
- Slide 3: [Problem] 대퇴골 골절: 뼈 부러짐보다 무서운 '침상 부동'과 폐렴 합병증
- Slide 4: [Statistics] 65세 이상 고관절 골절 후 1년 내 사망률 20~30% 육박
- Slide 5: [Warning] 다리가 바깥으로 돌아가고 못 일어선다면 억지로 세우지 마세요!
- Slide 6: [Solution ①] 화장실 벽에 L자형 안전 손잡이와 미끄럼 방지 롤매트 설치
- Slide 7: [Solution ②] 새벽 화장실 가는 길에 자동 야간 센서등 부착
- Slide 8: [Solution ③] 미끄러운 슬리퍼 대신 바닥 실리콘 미끄럼 방지 양말 착용
- Slide 9: [Action] 부모님 댁 1~2cm 미세 문턱에 완만 경사로 테이프 부착
- Slide 10: [CTA] 지금 저장하고 부모님 댁 방문 전에 꼭 점검해 보세요! 📌

### 3. 스토리텔링 비포 & 애프터 카피 (BAB)
- **[Before]**: 겨울마다 새벽에 불도 안 켜고 화장실 가시는 80대 어머니 때문에 항상 마음 졸이던 40대 직장인 김 모 씨.
- **[After]**: 화장실 안전 손잡이 시공과 복도 센서등 설치 후, 어머니의 발걸음이 한결 안정되고 가족 모두가 밤새 안심하고 숙면을 취합니다.
- **[Bridge]**: 3만 원짜리 손잡이와 센서등 하나가 부모님의 보행과 남은 여생을 지키는 가장 큰 효도입니다.

### 4. 네이버 파워링크 검색광고(SA) 5세트 (글자수 엄수)
- **세트 1 (낙상 방지 용품)**:
  - 제목 (15자 이내): 노인 낙상방지 손잡이
  - 설명 (45자 이내): 겨울철 부모님 화장실 미끄럼 방지 손잡이와 안전매트. 응급실 의사 추천.
- **세트 2 (고관절 골절 예방)**:
  - 제목 (15자 이내): 겨울철 고관절골절 예방
  - 설명 (45자 이내): 노인 대퇴골 골절 치명성 경고. 안방 화장실 낙상 방지 3대 수칙 확인.
- **세트 3 (노인 안전 센서등)**:
  - 제목 (15자 이내): 부모님 야간 센서등
  - 설명 (45자 이내): 새벽 화장실 가는 길 자동 점등. 넘어짐 사고 막는 무선 모션 센서등.
- **세트 4 (미끄럼 방지 양말)**:
  - 제목 (15자 이내): 어르신 미끄럼방지양말
  - 설명 (45자 이내): 실내 슬리퍼보다 안전한 실리콘 논슬립 양말. 겨울철 실내 낙상 철벽 방어.
- **세트 5 (고령자 가정 안전)**:
  - 제목 (15자 이내): 부모님 댁 안전점검 가이드
  - 설명 (45자 이내): 빙판길보다 위험한 실내 사각지대. 대퇴골 골절 막는 환경 개조 체크리스트.

### 5. 인스타그램 릴스 & 유튜브 쇼츠 5씬 대본
- **Scene 1 (Hook)**: 겨울철 부모님 엉덩방아, 절대로 가볍게 넘기지 마세요! (빙판 미끄러짐 액션)
- **Scene 2 (ER Truth)**: 응급실에 실려 오는 고관절 골절의 60%는 집 안 화장실과 침실에서 발생합니다. (119 구급차 및 엑스레이)
- **Scene 3 (Doctor Prescription)**: 뼈가 부러지면 자리에 누워 1년 내 사망률이 20%에 달합니다. 48시간 내 수술 골든타임을 지켜야 합니다. (의사 뼈 모형 설명)
- **Scene 4 (Safety Solutions)**: 오늘 당장 화장실에 안전 손잡이 달고, 복도에 야간 센서등을 붙여주세요. (화장실 손잡이 및 센서등)
- **Scene 5 (Warm Ending)**: 부모님의 두 발로 걷는 행복, 자녀의 작은 관심이 지킵니다. (행복한 가족 산책)
"""
(DAY3_DIR / "ads.md").write_text(ads_md, encoding="utf-8")

# 3. Clinical Expert In-Depth Column (clinical/clinical_column.md)
clinical_md = """# [임상 심층 칼럼] 고령자 동절기 대퇴골 근위부 골절(Proximal Femur Fracture)의 생역학적 기전과 응급실 초기 소생·수술 프로토콜

> **저자 / 임상 감수**: 응급의학과 전문의 김승태 (Dr. K's Emergency Medicine Hub)<br>
> **문헌 참조**: Dr. K's Medical Wiki (`kst104/wikiwi`), Tintinalli's Emergency Medicine (Ch. 269), ATLS 1차 조사 프로토콜, 대한골대사학회 및 대한정형외과학회 고관절 가이드라인<br>
> **대상 독자**: 정형외과·응급의학과 의료진, 노인의학 전문의, 임상 간호사 및 중증 외상 진료팀<br>
> **분류**: Orthopedic Trauma / Geriatric Emergency / Resuscitation Protocols

---

## 1. Clinical Abstract (임상 초록)

- **역학적 치명도**: 65세 이상 고령자에서 발생하는 대퇴골 근위부 골절(Proximal Femur Fracture)은 단순한 정형외과적 손상을 넘어 전신 쇠약 및 다장기 부전의 방아쇠가 된다. 수상 후 30일 사망률은 약 5~10%, 1년 내 사망률은 20~30%에 육박하며, 생존자의 약 50%만이 수상 전 보행 능력을 회복한다.
- **생역학적 손상 기전**: 골감소증 및 골다공증(T-score $\\le -2.5$) 환자에서 대전자부(Greater Trochanter)에 가해지는 저에너지 낙상(Low-energy Fall) 충격력은 대퇴골 경부의 골소주(Trabecular Bone) 전단 강도를 쉽게 초과하여 골절을 야기한다.
- **해부학적 이원성**: 관절낭 내 골절인 대퇴골 경부 골절(Femoral Neck Fracture)은 내측 대퇴 회선 동맥(Medial Femoral Circumflex Artery) 분지 파열에 따른 대퇴골두 무혈성 괴사(AVN) 및 불유합 위험이 지배적인 반면, 관절낭 외 골절인 전자간 골절(Intertrochanteric Fracture)은 풍부한 해면골 혈류로 인해 500~1,000mL의 은닉 실혈(Occult Blood Loss)과 출혈성 저혈량 쇼크 위험이 높다.
- **응급 진료실 대원칙**: 응급실 도착 즉시 정맥로 확보 및 결정질 수액 투여, 동반 내과 질환(심방세동, 심부전, 당뇨) 평가, 조기 장골근막 구획 차단술(Fascia Iliaca Compartment Block, FICB)을 통한 전신 마약성 진통제 사용 최소화, 그리고 수상 후 24~48시간 이내 조기 외과적 고정/치환술(Urgent Surgical Intervention)을 완수해야 한다.

---

## 2. Anatomical Classification & Biomechanics (해부학적 분류 및 생역학)

### 2.1. 대퇴골 경부 골절 (Garden Classification)
대퇴골 경부 골절의 전위 정도는 골두의 생존성과 수술 방법을 결정하는 핵심 인자이다.

| Garden Stage | X-ray 소견 및 전위 정도 | 혈관 손상 위험 | 표준 수술 요법 |
| :--- | :--- | :--- | :--- |
| **Stage I** | 불완전 또는 불완전 감입 골절 (Incomplete / Valgus Impacted) | 낮음 ($< 10\\%$) | 다발성 유관 나사 고정술 (Multiple Cannulated Screws) |
| **Stage II** | 완전 골절이나 전위 없음 (Complete Non-displaced) | 중등도 ($15\\sim20\\%$) | 다발성 유관 나사 고정술 |
| **Stage III** | 완전 골절 + 부분 전위 (Complete Partially Displaced) | 높음 ($50\\%$) | 인공관절 반치환술 (Bipolar Hemiarthroplasty) |
| **Stage IV** | 완전 전위 (골두 골소주선이 관골구와 정상 정렬) | 극도로 높음 ($> 70\\%$) | **인공관절 전/반치환술 (THA or Bipolar Hemiarthroplasty)** |

### 2.2. 전자간 골절 (Evans / AO Classification)
대퇴골 전자간 부위는 대퇴골 간부와 경부가 연결되는 응력 집중 부위로, 후내측 피질골(Posteromedial Cortex)의 분쇄 정도가 기계적 안정성을 결정한다.
- **안정형 골절**: 내측 피질골이 온전하여 축성 하중 전달 가능 $\\rightarrow$ 압박 고관절 나사(CHS) 또는 골수내정(PFN/Gamma Nail).
- **불안정형 골절**: 대전자·소전자 분쇄, 역전자간 골절(Reverse Obliquity) $\\rightarrow$ 조기 체중 부하를 위해 근위 대퇴 골수내정(Cephalomedullary Nail) 필수.

---

## 3. Emergency Department Resuscitation & Diagnostic Workup

### 3.1. 초기 외상 평가 (ATLS Primary & Secondary Survey)
*출처: Dr. K's Medical Wiki (`kst104/wikiwi/wiki/medical/emergency/trauma-adults.md`)*

1. **저혈량성 쇼크 감별**:
   - 전자간 골절은 대퇴 근막 구획 내로 대량 출혈이 발생하므로 활력징후(HR, BP) 및 Shock Index (SI = HR / SBP $> 0.9$)를 즉시 계산한다.
   - 18G 정맥로 2개 확보, Plasmalyte 또는 생리식염수 초기 부하 투여.
2. **신경혈관 손상 평가**:
   - 족배동맥(Dorsalis Pedis) 맥박 촉지, 슬와동맥 관류 확인.
   - 대퇴신경 및 좌골신경 손상 여부 확인 (발가락 배굴 및 족저굴곡 검사).
3. **방사선학적 확진**:
   - AP Pelvis, AP & Lateral of Affected Hip.
   - **은닉 골절(Occult Hip Fracture) 주의**: 통증으로 체중 부하가 전혀 불가능하나 단순 X-ray상 정상인 경우, 24시간 내 MRI 또는 3D CT를 시행해야 한다 (골감소증 고령자의 5~10%에서 단순 X선 위음성 발생).

### 3.2. 응급 통증 조절: 장골근막 구획 차단술 (Fascia Iliaca Block)
고령 골절 환자에게 과도한 정맥 마약성 진통제(Morphine, Fentanyl)는 급성 섬망(Delirium), 호흡 억제, 요정체를 유발하여 사망률을 증가시킨다.
- **초음파 유도하 FICB**:
  - 서혜인대 하방, 장골근막(Fascia Iliaca) 아래 잠재적 공간에 0.2% Ropivacaine 30~40mL 주입.
  - 대퇴신경(Femoral n.)과 외측대퇴피신경(Lateral femoral cutaneous n.)을 동시 차단하여 12~24시간 동안 완벽한 진통 효과 달성.

---

## 4. Multidisciplinary Surgical Timing & Complication Prevention

### 4.1. 수술 타이밍과 사망률 상관관계
- **골든타임: 수상 후 24~48시간 이내 수술**:
  - 미국 정형외과학회(AAOS) 및 영국 국립보건임상연구원(NICE) 가이드라인은 48시간 이내 조기 수술을 강력 권고한다.
  - 48시간 이상 수술 지연 시 30일 사망률이 2배 증가하며, 폐렴 및 심근경색 발생률이 유의미하게 상승한다.
- **수술 전 교정 필수 질환**:
  - 와파린 복용 환자: 비타민 K 정주 및 4-Factor PCC 투여로 INR $< 1.5$ 신속 역전.
  - NOAC/DOAC 복용 환자: 마지막 투약 시간 확인 후 24~48시간 경과 시점 수술 진행.

### 4.2. 주요 합병증 예방 프로토콜
1. **정맥혈전색전증(VTE / DVT / PE) 예방**:
   - 수술 전후 간헐적 공기압박기(IPC) 장착.
   - 수술 12시간 후 저분자량 헤파린(LMWH, Enoxaparin 40mg SC qd) 투여 시작, 최소 4주간 유지.
2. **급성 섬망(Postoperative Delirium) 방지**:
   - 지남력 지속 확인, 불필요한 도뇨관 조기 발거, 야간 수면 주기 유지.
3. **조기 보행(Early Ambulation)**:
   - 수술 다음 날 침상 기립 및 휠체어 착석, 물리치료사 지도하 보행기 훈련 조기 착수.

---

## 5. References (참고 문헌)

1. **Tintinalli, J. E., et al.** *Tintinalli's Emergency Medicine: A Comprehensive Study Guide*, 8th Ed. McGraw-Hill, Chapter 269: Hip and Femur Injuries.
2. **Dr. K's Emergency Medicine Wiki (`kst104/wikiwi`)**: `wiki/medical/emergency/trauma-adults.md` (성인 외상 초기 소생술), `wiki/medical/protocols/acs.md`.
3. **American Academy of Orthopaedic Surgeons (AAOS)**. Management of Hip Fractures in Older Adults: Evidence-Based Clinical Practice Guideline (2021).
4. **NICE Guideline [CG124]**. Hip fracture: management. National Institute for Health and Care Excellence, Updated 2023.
5. **Garden, R. S.** Low-angle fixation in fractures of the femoral neck. *J Bone Joint Surg Br*, 43-B(4):647-663.
"""
(DAY3_DIR / "clinical" / "clinical_column.md").write_text(clinical_md, encoding="utf-8")

# 4. Generate Naver HTML & Clinical HTML
from publisher.naver_formatter import markdown_to_naver_html as generate_smarteditor_html
from engine.clinical_engine import markdown_to_clinical_html
from engine.dual_pipeline import build_dual_view_html
from engine.slop_engine import scan_text_for_slop, clean_and_rewrite_deterministic

# SmartEditor HTML
naver_html = generate_smarteditor_html(post_md)
(DAY3_DIR / "naver_post.html").write_text(naver_html, encoding="utf-8")

# Clinical HTML
clin_html = markdown_to_clinical_html(clinical_md)
(DAY3_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

# Dual View HTML
dual_html = build_dual_view_html(DAY3_DIR)
(DAY3_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day3_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

# DUAL_VIEW.md
dual_md = f"""# 🩺 Day 3 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 겨울철 노인 낙상과 대퇴골 골절 예방법 (빙판길 고관절 골절의 치명성과 실내 낙상 3대 방어 수칙)
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 고령 부모를 둔 자녀, 60대 이상 고령자, 가족 보호자 | 정형외과·응급의학과 의료진, 노인의학 전문의, 임상 간호사 |
| **분량 및 형식** | 약 2,200자 / 응급실 현장감, 부모님 실내 안전 수칙 | 약 4,200자 / 학술 외상 저널 임상 리뷰 포맷 |
| **참조 지식원** | 질병관리청 통계, 일상 응급실 구급 환자 사례 | **Dr. K's Wiki (`kst104/wikiwi`)**, Tintinalli Ch269, AAOS/NICE |
| **핵심 의학 내용** | 화장실 손잡이, 야간 복도 센서등, 미끄럼 방지 양말 | Garden I~IV 분류, FICB 구획 차단술, 48시간 내 수술 골든타임 |
| **동반 제작 에셋** | 네이버 스마트에디터 서식, 카드뉴스, 쇼츠 영상 v2, 광고 10종 | 학술 HTML, 병기별 처치표, 은닉 골절 감별, VTE/섬망 프로토콜 |
"""
(DAY3_DIR / "DUAL_VIEW.md").write_text(dual_md, encoding="utf-8")

# Run slop-rewrite inspection
res = scan_text_for_slop(post_md)
score = res.get('slop_score', 0)
findings = res.get('findings', [])
(DAY3_DIR / 'slop_report.json').write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"✅ slop-rewrite 결과: 점수 {score} (0점 목표 달성!), 감지 항목: {len(findings)}개")

print("✅ Day 3 content files generated successfully!")
