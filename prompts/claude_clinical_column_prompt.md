# 🩺 닥터 K 임상 심층 의학 칼럼 (전문가용) 프롬프트 가이드

이 프롬프트는 일반 대중용 요약본과 차별화하여, **의사·의료진·임상 연구자 및 고관여 독자**를 대상으로 하는 3,500~4,500자 이상의 고밀도 학술·임상 심층 칼럼을 생성할 때 사용합니다.

---

## 🏛️ 지식베이스 참조 (Dr. K's Medical Wiki)
- **핵심 레퍼런스**: `kst104/wikiwi` (승태의 의학 위키, Dr. K's Wiki, `localhost:8090`)
- **주요 교과서 및 프로토콜**:
  - Tintinalli's Emergency Medicine (7th/8th Ed)
  - Harrison's Principles of Internal Medicine
  - KSH (대한고혈압학회), AHA/ACC, ESC 최신 임상 가이드라인
  - ACS 프로토콜 (`wiki/medical/protocols/acs.md`): STEMI/NSTEMI, D2B, DAPT, UFH
  - 대동맥 박리 프로토콜 (`wiki/medical/emergency/aortic-dissection.md`): Stanford Type A/B, SBP <120, HR <60
  - 패혈증/쇼크 프로토콜 (`wiki/medical/emergency/sepsis.md`): Sepsis-3, MAP ≥65mmHg

---

## 📝 칼럼 표준 구조 (8단계 고정 스키마)

### 1. Clinical Abstract (임상 초록 / Key Takeaways)
- 역학 통계, 치명도, 핵심 임상 결론 3~4개 불릿 정리.
- 의학 용어(한/영 병기: 예: 아침 혈압 급상승 [Morning BP Surge, MBPS]).

### 2. Pathophysiology & Hemodynamics (병태생리 및 혈류역학적 기전)
- 한랭 자극 및 기상 시 신경내분비계(HPA 축, 교감신경계) 활성화 기전.
- 카테콜아민 분비, $\alpha$-아드레날린 수용체 매개 전신 혈관 저항(SVR) 급증.
- 혈류역학적 전단 응력(Shear Stress), 죽상경화반 파열(Plaque Rupture), 혈소판 응집 촉진 기전 서술.

### 3. Clinical Manifestations & Red Flags (임상 발현 및 위험 징후)
- 전형적 흉통/신경학적 결손 vs 고령·당뇨 환자의 비전형적 무통성 발현(Atypical Equivalents).
- 응급 진료실 즉각 배제 대상(Immediate Red Flags).

### 4. Differential Diagnosis (응급 감별진단 알고리즘)
- 급성 관상동맥 증후군 (STEMI vs NSTEMI vs UA)
- 급성 대동맥 증후군 (AAS, Stanford Type A vs B)
- 급성 뇌혈관 질환 (Ischemic Stroke vs ICH)
- 고혈압성 응급(Hypertensive Emergency: End-organ damage 동반) vs 절박(Urgency)

### 5. Diagnostic Workup & Risk Stratification (진단 검사 및 위험도 층화)
- 12-lead ECG: 10분 이내 획득, 연속 변화 추적.
- 심근 효소 검사: High-sensitivity Troponin (0/1hr or 0/2hr 알고리즘), CK-MB.
- 영상의학 검사: Non-contrast Brain CT, Chest CT Angiography (Stanford 분별).
- 임상 위험 점수: GRACE Score, TIMI Risk Score 계산 및 침습적 중재 시기 결정.

### 6. Emergency Management & Pharmacotherapy (응급 처치 및 정밀 약물 요법)
- 목표 혈압 및 감압 속도: 초기 1시간 이내 MAP 20~25% 감량 상한선 준수 (뇌관류압 보존).
- 정주형 혈압 강하제: Nicardipine IV (5mg/h 시작, 2.5mg/h 증량, max 15mg/h), Labetalol IV bolus/infusion.
- 허혈성 심질환 로딩 프로토콜: Aspirin 300mg + Ticagrelor 180mg (DAPT), UFH 60-70 IU/kg IV.
- 재관류 목표 시간: Door-to-Balloon (D2B) ≤ 90분, Door-to-Needle (tPA) ≤ 60분 (4.5시간 윈도우).

### 7. Outpatient Risk Management & Clinical Guidelines (외래 관리 및 예방 지침)
- 가정 혈압 모니터링 프로토콜 (Morning/Evening 평균치, 135/85mmHg 기준).
- 24시간 활동 혈압 모니터링(ABPM) 상 Non-dipper / Riser 패턴의 심혈관 위험도.
- 장기 작용형 항고혈압제(CCB, ARB) 복약 스케줄 최적화 (Bedtime dosing 전략 등).

### 8. References & Textbook Citations (참고 문헌)
- Tintinalli's Emergency Medicine, Harrison's Internal Medicine.
- AHA/ACC/ESC Guidelines for Management of Arterial Hypertension / ACS.
- Dr. K's Emergency Medicine Wiki (`kst104/wikiwi`).
