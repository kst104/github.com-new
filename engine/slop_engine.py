# -*- coding: utf-8 -*-
"""
slop-rewrite Engine for Content Automation
GitHub AgriciDaniel/anti-slop 및 Claude slop-rewrite 스킬 기반
AI 특유의 상투어구, 엠대시, 형식적 서론/결론, 불렛 도배를 제거하고 
현직 전문의의 자연스럽고 신뢰감 있는 실제 어조로 정밀 교정하는 엔진.
"""

import os
import sys
import re
import json
from pathlib import Path

# 상위 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 한국어 및 영어 AI 상투어 패턴 사전
KOREAN_THROAT_CLEARING = [
    r"현대\s*사회에서\b",
    r"급변하는\s*(디지털\s*)?(사회|환경|시대)속에서\b",
    r"많은\s*분들이\s*(관심을\s*가지|고민하|궁금해하)는\b",
    r"오늘\s*(포스팅|글)에서는\b.*(알아보겠습니다|살펴보겠습니다|소개해\s*드립니다)",
    r"이번\s*(글|시간)에서는\b.*(다뤄보겠습니다|알아보겠습니다)",
    r"자,\s*(그럼\s*)?이제\b.*(알아볼까요|시작해볼까요)",
]

KOREAN_FILLER_TRANSITIONS = [
    r"\b더\s*나아가\b",
    r"\b뿐만\s*아니라\b",
    r"\b이와\s*더불어\b",
    r"\b특히\s*주목할\s*만한\s*점은\b",
    r"\b그렇다면\s*과연\b",
    r"\b결론적으로\s*말하자면\b",
    r"\b일석이조의\s*효과\b",
    r"\b눈길을\s*끕니다\b",
    r"\b주목할\s*만합니다\b",
    r"\b기대할\s*수\s*있습니다\b",
]

KOREAN_HOLLOW_CONCLUSIONS = [
    r"건강한\s*내일을\s*위해\s*지금\s*바로\s*실천해보세요[!.]?",
    r"오늘\s*글이\s*도움이\s*되셨다면\s*(공감과\s*댓글|이웃\s*추가).*",
    r"작은\s*실천이\s*모여\s*큰\s*변화를\s*만듭니다[!.]?",
    r"여러분의\s*건강한\s*삶을\s*응원합니다[!.]?",
]

ENGLISH_AI_BUZZWORDS = [
    r"\bdelve\b",
    r"\btapestry\b",
    r"\btestament\b",
    r"\bunderscore(s|d)?\b",
    r"\bmoreover\b",
    r"\bfurthermore\b",
    r"\bpivotal\s*moment\b",
    r"\bin\s*today'?s\s*fast-paced\b",
    r"\bat\s*the\s*end\s*of\s*the\s*day\b",
    r"\bgame-changer\b",
    r"\bnot\s*only\b.*\bbut\s*also\b",
    r"\bseamlessly\b",
    r"\brobust\b",
]

VAGUE_ATTRIBUTIONS = [
    r"전문가들에\s*따르면",
    r"많은\s*연구에\s*따르면",
    r"연구에\s*따르면",
    r"통계에\s*따르면",
    r"학계에서는",
]

def scan_text_for_slop(text: str) -> dict:
    """
    텍스트를 스캔하여 AI 슬롭(상투어, 엠대시, 군더더기, 잔여 마크업)을 감지하고
    구체적 결함 보고서(findings report)를 반환합니다.
    """
    findings = []
    
    # 1. 엠대시 (Em-dash U+2014) 및 엔대시 (En-dash U+2013) 검사 (Layer 0)
    dashes = list(re.finditer(r"[—–]", text))
    if dashes:
        findings.append({
            "id": f"SLOP-{len(findings)+1:03d}",
            "severity": "LOW",
            "confidence": "high",
            "type": "em_dash_residue",
            "count": len(dashes),
            "description": f"AI 특유의 엠대시/엔대시 {len(dashes)}개 발견 (마침표, 쉼표, 콜론 또는 괄호로 교체 권장)"
        })

    # 2. 서론 군더더기 (Throat-clearing) 검사 (Layer 1)
    for pat in KOREAN_THROAT_CLEARING:
        for m in re.finditer(pat, text):
            findings.append({
                "id": f"SLOP-{len(findings)+1:03d}",
                "severity": "MEDIUM",
                "confidence": "high",
                "type": "throat_clearing",
                "quote": m.group(0),
                "description": f"상투적 AI 도입부 패턴 발견: '{m.group(0)}' (즉각적인 구체적 팩트/임상 상황으로 교체 권장)"
            })

    # 3. 상투적 접속사 및 필러 검사 (Layer 1)
    for pat in KOREAN_FILLER_TRANSITIONS:
        for m in re.finditer(pat, text):
            findings.append({
                "id": f"SLOP-{len(findings)+1:03d}",
                "severity": "LOW",
                "confidence": "medium",
                "type": "filler_transition",
                "quote": m.group(0),
                "description": f"기계적 접속사/필러 발견: '{m.group(0)}' (문장 간소화 또는 삭제 권장)"
            })

    # 4. 공허한 결론 문구 검사 (Layer 1)
    for pat in KOREAN_HOLLOW_CONCLUSIONS:
        for m in re.finditer(pat, text):
            findings.append({
                "id": f"SLOP-{len(findings)+1:03d}",
                "severity": "MEDIUM",
                "confidence": "high",
                "type": "hollow_conclusion",
                "quote": m.group(0),
                "description": f"공허한 맺음말 발견: '{m.group(0)}' (구체적 행동 지침으로 교체 권장)"
            })

    # 5. 영문 AI 버즈워드 검사 (Layer 1)
    for pat in ENGLISH_AI_BUZZWORDS:
        for m in re.finditer(pat, text, re.IGNORECASE):
            findings.append({
                "id": f"SLOP-{len(findings)+1:03d}",
                "severity": "LOW",
                "confidence": "high",
                "type": "english_buzzword",
                "quote": m.group(0),
                "description": f"영문 AI 버즈워드 발견: '{m.group(0)}'"
            })

    # 6. 모호한 인용 (Vague Attribution) 검사
    for pat in VAGUE_ATTRIBUTIONS:
        for m in re.finditer(pat, text):
            findings.append({
                "id": f"SLOP-{len(findings)+1:03d}",
                "severity": "MEDIUM",
                "confidence": "medium",
                "type": "vague_attribution",
                "quote": m.group(0),
                "description": f"출처 불분명 인용: '{m.group(0)}' (구체적인 학회/교과서명 명시 필요)"
            })

    # 7. 불렛-볼드 과다 도배 검사 (Bullet & Bold Soup)
    lines = text.split("\n")
    bullet_bold_count = sum(1 for line in lines if re.match(r"^\s*[-*]\s*\*\*.*?\*\*:", line))
    if bullet_bold_count > 6:
        findings.append({
            "id": f"SLOP-{len(findings)+1:03d}",
            "severity": "LOW",
            "confidence": "medium",
            "type": "bullet_bold_soup",
            "count": bullet_bold_count,
            "description": f"반복적 불렛-볼드 패턴 과다 ({bullet_bold_count}행) (자연스러운 서술형 줄글과 혼합 권장)"
        })

    # 종합 슬롭 지수 계산 (0 = 완전 무결, 100 = 극심한 AI 티)
    slop_score = min(100, len(findings) * 8)
    
    return {
        "slop_score": slop_score,
        "clean": len(findings) == 0,
        "finding_count": len(findings),
        "findings": findings
    }


def clean_and_rewrite_deterministic(text: str) -> tuple[str, list[str]]:
    """
    결정론적(Deterministic) 규칙 기반 1차 슬롭 제거 및 정제
    외부 API 호출 없이도 엠대시, 잔여 표기, 상투적 필러를 즉시 교정합니다.
    """
    applied_fixes = []
    cleaned = text

    # 1. 엠대시 및 엔대시 제거 (House Rule: Never write em dash or en dash)
    # 문맥에 맞게 대체: 단어 사이 엠대시는 쉼표나 괄호, 문장 연결은 쉼표/마침표로 교체
    if "—" in cleaned or "–" in cleaned:
        cleaned = re.sub(r"\s*[—–]\s*", ", ", cleaned)
        # 혹시 끝부분에 남은 쉼표 정리
        cleaned = re.sub(r",\s*\n", ".\n", cleaned)
        applied_fixes.append("엠대시(—) 및 엔대시(–) ➔ 쉼표/마침표 자연스러운 문장 구조로 교체")

    # 2. 공허한 서론 패턴 정돈
    for pat in KOREAN_THROAT_CLEARING:
        match = re.search(pat, cleaned)
        if match:
            # 상투적 문장이 포함된 전체 문장을 축약하거나 보다 직관적인 표현으로 정돈
            cleaned = re.sub(pat, "실제 임상 현장에서", cleaned)
            applied_fixes.append(f"상투적 서론구('{match.group(0)}') ➔ 직관적 현장 서술로 교체")

    # 3. 과도한 접속사 및 필러 완화
    replacements = [
        (r"\b더\s*나아가,?\s*", "또한 "),
        (r"\b뿐만\s*아니라,?\s*", "동시에 "),
        (r"\b이와\s*더불어,?\s*", "함께 "),
        (r"\b특히\s*주목할\s*만한\s*점은,?\s*", "주의할 점은 "),
        (r"\b그렇다면\s*과연,?\s*", "실제로 "),
        (r"\b결론적으로\s*말하자면,?\s*", "요약하자면 "),
        (r"\b일석이조의?\s*효과\b", "두 가지 이점"),
        (r"\b눈길을\s*끕니다\.?\b", "중요합니다."),
        (r"\b주목할\s*만합니다\.?\b", "눈여겨보아야 합니다."),
        (r"\b기대할\s*수\s*있습니다\.?\b", "도움이 됩니다."),
    ]
    for pattern, rep in replacements:
        if re.search(pattern, cleaned):
            cleaned = re.sub(pattern, rep, cleaned)
            applied_fixes.append(f"기계적 접속사 패턴 정돈: {rep.strip()}")

    # 4. 공허한 맺음말 상투어 제거
    for pat in KOREAN_HOLLOW_CONCLUSIONS:
        match = re.search(pat, cleaned)
        if match:
            cleaned = re.sub(pat, "이상 징후가 있을 때는 지체 없이 전문의 진료를 받으시길 권합니다.", cleaned)
            applied_fixes.append("공허한 마무리 응원구 ➔ 전문의 의학적 행동 권고로 교체")

    # 5. 불필요한 연속 빈 줄 정리
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned, applied_fixes


def generate_slop_rewrite_prompt(original_text: str, findings: list) -> str:
    """Claude / GPT용 slop-rewrite 전문 교정 프롬프트 생성"""
    findings_str = "\n".join([f"- [{f['severity']}] {f['description']}" for f in findings])
    
    return f"""
당신은 GitHub의 `slop-rewrite` 전문 에디터입니다.
아래의 [검토된 결함 목록]을 바탕으로, 원문의 핵심 의학 정보와 데이터는 100% 보존하면서 AI 특유의 상투어와 어색함을 완벽히 제거한 '탈(脫)AI 의사 칼럼'으로 다시 작성하십시오.

[절대 방화벽 규칙]
1. 원문에 없는 새로운 사실, 통계, 약제명, 수치를 절대 지어내지 마십시오 (No hallucination).
2. 엠대시(—)나 엔대시(–)는 일체 쓰지 마십시오. 마침표, 쉼표, 콜론으로 문장을 나누십시오.
3. "현대 사회에서", "알아보겠습니다", "더 나아가", "뿐만 아니라", "일석이조" 같은 상투어를 전면 삭제하십시오.
4. 모든 문장마다 볼드체(- **항목**: 설명)를 도배하지 말고, 자연스러운 진료실 설명조 줄글로 풀어서 서술하십시오.
5. 응급실 전문의(닥터 김승태)의 담백하고 신뢰감 있는 실제 현장 목소리를 완벽히 구현하십시오.

[검토된 결함 목록]
{findings_str if findings_str else "- 전반적인 AI 번역투 및 상투어구 정돈 필요"}

[교정 대상 원문]
{original_text}

오직 교정된 최종 완성 원고 본문만 출력하십시오. 부연 설명이나 사족은 생략하십시오.
"""


def apply_slop_rewrite(text: str, provider: str = None) -> tuple[str, dict]:
    """
    통합 슬롭 리라이트 실행기:
    1) 스캔 ➔ 2) 결정론적 1차 정제 ➔ 3) (API 가용 시) Claude/GPT 기반 심층 교정 ➔ 4) 재스캔 검증
    """
    initial_scan = scan_text_for_slop(text)
    
    # 1단계: 결정론적 정제
    cleaned_text, fixes = clean_and_rewrite_deterministic(text)
    
    # 2단계: API 가용 시 심층 LLM 리라이트 (선택적)
    from engine.config import ANTHROPIC_API_KEY, OPENAI_API_KEY
    final_text = cleaned_text
    
    if provider == "claude" and (ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")):
        try:
            from engine.claude_engine import call_claude
            prompt = generate_slop_rewrite_prompt(cleaned_text, initial_scan["findings"])
            system_prompt = "당신은 세계 최고의 테크니컬/메디컬 라이팅 에디터이자 slop-rewrite 집행자입니다."
            llm_cleaned = call_claude(system_prompt, prompt)
            if llm_cleaned and len(llm_cleaned) > len(cleaned_text) * 0.5:
                final_text = llm_cleaned
                fixes.append("Claude 3.5 Sonnet 기반 slop-rewrite 심층 인간화 패스 완료")
        except Exception as e:
            fixes.append(f"Claude 심층 리라이트 폴백: {e}")
            
    elif provider == "openai" and (OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")):
        try:
            from engine.openai_engine import call_openai
            prompt = generate_slop_rewrite_prompt(cleaned_text, initial_scan["findings"])
            system_prompt = "당신은 세계 최고의 테크니컬/메디컬 라이팅 에디터이자 slop-rewrite 집행자입니다."
            llm_cleaned = call_openai(system_prompt, prompt)
            if llm_cleaned and len(llm_cleaned) > len(cleaned_text) * 0.5:
                final_text = llm_cleaned
                fixes.append("GPT-4o 기반 slop-rewrite 심층 인간화 패스 완료")
        except Exception as e:
            fixes.append(f"OpenAI 심층 리라이트 폴백: {e}")

    # 최종 사후 스캔 검증
    final_scan = scan_text_for_slop(final_text)

    report = {
        "initial_score": initial_scan["slop_score"],
        "final_score": final_scan["slop_score"],
        "initial_findings": initial_scan["findings"],
        "final_findings": final_scan["findings"],
        "fixes_applied": fixes,
        "clean": final_scan["clean"]
    }
    
    return final_text, report


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])
        if target_path.exists():
            content = target_path.read_text(encoding="utf-8")
            print(f"📄 대상 파일: {target_path}")
            cleaned, rep = apply_slop_rewrite(content)
            print(f"📊 슬롭 지수: {rep['initial_score']} ➔ {rep['final_score']}")
            print(f"🛠️ 적용된 교정: {len(rep['fixes_applied'])}건")
            for fix in rep['fixes_applied']:
                print(f"  - {fix}")
            if "--save" in sys.argv:
                target_path.write_text(cleaned, encoding="utf-8")
                print(f"✅ 저장 완료: {target_path}")
        else:
            print(f"파일을 찾을 수 없습니다: {target_path}")
