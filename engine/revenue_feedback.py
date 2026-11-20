#!/usr/bin/env python3
"""월간 수익 되먹임 · 계절성 상품 선택 엔진.

매월 말 정산한 유입·클릭·플랫폼 수익·광고비를 입력하면
1) 다음 달 재투자 광고 예산(되먹임 비율, 기본 50%)
2) ROAS·유입당 수익·클릭당 수익 같은 효율 지표
3) 검색광고 vs 콘텐츠 부스팅 예산 배분(ROAS 기반 동적 조정)
4) 다음 달 계절성 대표 상품(쿠팡파트너스 1종 + 네이버 쇼핑 커넥트 1종)
을 계산해 JSON과 Markdown 리포트로 출력한다.

실행 예시
---------
    # 11월 초기 정산 시뮬레이션(내장 샘플) → 12월 예산·상품 산출
    python3 engine/revenue_feedback.py simulate --month 2026-11

    # 실제 정산 JSON으로 실행
    python3 engine/revenue_feedback.py settle --input data/settlements/2026-11_sample.json

    # 상품 스코어만 확인
    python3 engine/revenue_feedback.py score --month 2026-12

    # 단위 테스트
    python3 -m unittest engine.test_revenue_feedback -v
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CATALOG = BASE_DIR / "data" / "seasonal_products.json"
DEFAULT_OUT_DIR = BASE_DIR.parent / "reports" / "revenue_feedback"

# ---------------------------------------------------------------------------
# 기본 가정값
# ---------------------------------------------------------------------------

#: 수익을 채널에 나눠 붙이는 기본 비율.
#: 검색 유입 글에서 결제가 일어나고, 쇼츠는 직접 결제보다 발견·재방문에 기여한다는
#: 전제다. 매달 실제 전환 데이터가 쌓이면 settlement JSON의 attribution으로 덮어쓴다.
DEFAULT_ATTRIBUTION = {"search": 0.7, "content": 0.3}

#: 광고 이력이 전혀 없는 첫 달의 기본 배분(검색 60 : 부스팅 40).
DEFAULT_COLD_START_SPLIT = {"search": 0.6, "content": 0.4}

CHANNELS = ("search", "content")
CHANNEL_LABELS = {"search": "검색광고(파워링크)", "content": "콘텐츠 부스팅(쇼츠·릴스)"}

SEASONS: dict[str, dict[str, Any]] = {
    "winter": {"months": [11, 12, 1, 2], "label": "한파·난방·호흡기/보습"},
    "spring": {"months": [3, 4, 5], "label": "환절기·알레르기/미세먼지"},
    "summer": {"months": [6, 7, 8], "label": "냉방·제습·수분/자외선"},
    "autumn": {"months": [9, 10], "label": "환절기·면역/관절"},
}
ADJACENT_SEASONS = {
    "winter": {"autumn", "spring"},
    "spring": {"winter", "summer"},
    "summer": {"spring", "autumn"},
    "autumn": {"summer", "winter"},
}

#: 상품 점수 가중치. 계절 적합도와 실제 수요를 먼저 보고, 수익성과 데이터 신뢰도로
#: 순위를 다듬는다. 추정 데이터만으로 기존 상품을 갈아치우지 않도록 신뢰도에도
#: 가중치를 둔다.
SEASON_WEIGHT = 0.36
DEMAND_WEIGHT = 0.27
ECONOMICS_WEIGHT = 0.27
CONFIDENCE_WEIGHT = 0.10


# ---------------------------------------------------------------------------
# 데이터 구조
# ---------------------------------------------------------------------------


@dataclass
class Guardrails:
    """광고 집행 안전선. 승태 님과 상의해 바꾸는 값이다."""

    feedback_rate: float = 0.5
    min_monthly_budget: int = 30_000       # 파워링크 지면이 실제로 잡히는 최소 집행액
    seed_budget: int = 50_000              # 수익이 붙기 전 초기 시드 예산
    seed_max_months: int = 3               # 시드 예산을 쓸 수 있는 개월 수
    max_monthly_budget: int = 300_000      # 월 광고비 절대 상한
    min_channel_share: float = 0.30        # 한 채널 몰빵 방지
    max_channel_share: float = 0.70
    budget_unit: int = 1_000               # 광고 집행 단위(원)
    prior_spend: int = 50_000              # ROAS 스무딩용 사전 집행액
    switch_margin: float = 0.08            # 상품 교체에 필요한 점수 차

    def validate(self) -> None:
        if not 0 < self.feedback_rate <= 1:
            raise ValueError("feedback_rate는 0보다 크고 1 이하여야 합니다.")
        if not 0 < self.min_channel_share <= self.max_channel_share < 1:
            raise ValueError("채널 최소/최대 비중 설정이 잘못되었습니다.")
        if self.max_monthly_budget < self.min_monthly_budget:
            raise ValueError("월 상한이 최소 집행액보다 작습니다.")


@dataclass
class MonthlySettlement:
    """한 달 정산 입력."""

    month: str                              # "2026-11"
    program_month: int = 1                  # 프로그램 시작 후 몇 번째 달인지
    naver_blog_views: int = 0
    naver_blog_visitors: int = 0
    youtube_shorts_views: int = 0
    coupang_clicks: int = 0
    coupang_revenue: int = 0
    naver_connect_clicks: int = 0
    naver_connect_revenue: int = 0
    other_revenue: int = 0
    ad_spend: dict[str, int] = field(default_factory=lambda: {"search": 0, "content": 0})
    feedback_rate: float | None = None
    attribution: dict[str, float] | None = None
    current_products: dict[str, str] = field(default_factory=dict)
    collection_status: str = "actual"       # actual | sample
    note: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "MonthlySettlement":
        allowed = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        unknown = set(raw) - allowed
        if unknown:
            raise ValueError(f"알 수 없는 정산 항목: {', '.join(sorted(unknown))}")
        data = dict(raw)
        spend = data.get("ad_spend") or {}
        data["ad_spend"] = {
            "search": int(spend.get("search", 0)),
            "content": int(spend.get("content", 0)),
        }
        settlement = cls(**data)
        settlement.validate()
        return settlement

    def validate(self) -> None:
        if not self.month or len(self.month) != 7 or self.month[4] != "-":
            raise ValueError("month는 'YYYY-MM' 형식이어야 합니다.")
        int_fields = (
            "naver_blog_views",
            "naver_blog_visitors",
            "youtube_shorts_views",
            "coupang_clicks",
            "coupang_revenue",
            "naver_connect_clicks",
            "naver_connect_revenue",
            "other_revenue",
        )
        for name in int_fields:
            if getattr(self, name) < 0:
                raise ValueError(f"{name}은 0 이상이어야 합니다.")
        for channel, value in self.ad_spend.items():
            if value < 0:
                raise ValueError(f"ad_spend.{channel}는 0 이상이어야 합니다.")
        if self.program_month < 1:
            raise ValueError("program_month는 1 이상이어야 합니다.")

    # 파생 값 -------------------------------------------------------------
    @property
    def gross_revenue(self) -> int:
        return self.coupang_revenue + self.naver_connect_revenue + self.other_revenue

    @property
    def total_ad_spend(self) -> int:
        return sum(self.ad_spend.get(c, 0) for c in CHANNELS)

    @property
    def total_reach(self) -> int:
        """유입 총량: 블로그 방문자 + 쇼츠 조회수."""
        return self.naver_blog_visitors + self.youtube_shorts_views

    @property
    def total_clicks(self) -> int:
        return self.coupang_clicks + self.naver_connect_clicks


@dataclass
class ProductCandidate:
    name: str
    platform: str                    # coupang | naver
    price: int
    commission_rate: float
    monthly_search_volume: int
    review_count: int
    rating: float
    seasons: list[str]
    tags: list[str] = field(default_factory=list)
    verified: bool = False
    source: str = ""

    @property
    def commission_per_sale(self) -> int:
        return int(round(self.price * self.commission_rate))


# ---------------------------------------------------------------------------
# 계산 도우미
# ---------------------------------------------------------------------------


def fmt_won(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"{int(round(value)):,}원"


def fmt_pct(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.{digits}f}%"


def safe_div(numerator: float, denominator: float) -> float | None:
    return None if not denominator else numerator / denominator


def next_month(month: str) -> str:
    year, mon = (int(part) for part in month.split("-"))
    return f"{year + 1}-01" if mon == 12 else f"{year}-{mon + 1:02d}"


def month_number(month: str) -> int:
    return int(month.split("-")[1])


def season_for_month(month: str) -> str:
    mon = month_number(month)
    for name, meta in SEASONS.items():
        if mon in meta["months"]:
            return name
    return "winter"


def round_to_unit(value: float, unit: int) -> int:
    if value <= 0:
        return 0
    return int(math.floor(value / unit + 0.5) * unit)


# ---------------------------------------------------------------------------
# 예산 배분
# ---------------------------------------------------------------------------


def _clamp_shares(raw: dict[str, float], min_share: float, max_share: float) -> dict[str, float]:
    """두 채널 기준 비중을 [min, max] 안으로 조정하고 합을 1로 맞춘다."""
    total = sum(raw.values())
    if total <= 0:
        return {c: 1 / len(raw) for c in raw}
    shares = {c: v / total for c, v in raw.items()}
    # 두 채널이므로 한쪽을 clamp하면 다른 쪽은 1 - 값이다.
    first = CHANNELS[0]
    shares[first] = min(max(shares[first], min_share), max_share)
    shares[CHANNELS[1]] = 1 - shares[first]
    return shares


def allocate_budget(
    total_budget: int,
    revenue_by_channel: dict[str, float],
    spend_by_channel: dict[str, int],
    guardrails: Guardrails,
    cold_start_split: dict[str, float] | None = None,
) -> dict[str, Any]:
    """되먹임 예산을 검색광고와 콘텐츠 부스팅에 나눈다.

    - 광고 이력이 없으면 콜드스타트 기본 배분(검색 60 : 부스팅 40)
    - 이력이 있으면 채널별 ROAS를 사전 집행액으로 스무딩한 뒤 가중 배분
    - 직전 ROAS가 1.0 미만인 채널은 최소 비중까지만 준다(손실 확대 방지)
    """
    cold_start_split = cold_start_split or DEFAULT_COLD_START_SPLIT
    total_spend = sum(spend_by_channel.get(c, 0) for c in CHANNELS)
    revenue_total = sum(revenue_by_channel.get(c, 0) for c in CHANNELS)

    if total_budget <= 0:
        return {
            "total_budget": 0,
            "by_channel": {c: 0 for c in CHANNELS},
            "share": {c: 0.0 for c in CHANNELS},
            "channel_roas": {c: (None if not spend_by_channel.get(c) else
                                 revenue_by_channel.get(c, 0) / spend_by_channel[c])
                             for c in CHANNELS},
            "basis": "이번 달 재투자 예산이 0원이라 배분하지 않았습니다.",
            "cold_start": total_spend == 0,
            "penalized": [],
        }

    channel_roas: dict[str, float | None] = {}
    for channel in CHANNELS:
        spend = spend_by_channel.get(channel, 0)
        channel_roas[channel] = None if not spend else revenue_by_channel.get(channel, 0) / spend

    if total_spend <= 0:
        shares = _clamp_shares(dict(cold_start_split), guardrails.min_channel_share,
                               guardrails.max_channel_share)
        basis = (
            "광고 집행 이력이 없는 첫 달이라 콜드스타트 기본 배분"
            f"(검색 {shares['search'] * 100:.0f} : 부스팅 {shares['content'] * 100:.0f})을 적용했습니다."
        )
        cold_start = True
        penalized: list[str] = []
    else:
        blended_roas = revenue_total / total_spend
        prior = guardrails.prior_spend
        smoothed: dict[str, float] = {}
        for channel in CHANNELS:
            spend = spend_by_channel.get(channel, 0)
            revenue = revenue_by_channel.get(channel, 0)
            # 집행이 적은 채널의 ROAS가 우연히 튀는 것을 막는 베이지안 스무딩
            smoothed[channel] = (revenue + prior * blended_roas) / (spend + prior)

        penalized = [
            c for c in CHANNELS
            if spend_by_channel.get(c, 0) > 0
            and (channel_roas[c] or 0) < 1.0
        ]
        shares = _clamp_shares(smoothed, guardrails.min_channel_share, guardrails.max_channel_share)
        if len(penalized) == len(CHANNELS):
            # 둘 다 손실이면 어느 쪽도 키우지 않고 반씩 둔다.
            shares = {"search": 0.5, "content": 0.5}
        elif "search" in penalized:
            shares = {
                "search": guardrails.min_channel_share,
                "content": 1 - guardrails.min_channel_share,
            }
        elif "content" in penalized:
            shares = {
                "search": 1 - guardrails.min_channel_share,
                "content": guardrails.min_channel_share,
            }
        best = max(CHANNELS, key=lambda c: smoothed[c])
        basis = (
            f"직전 집행 ROAS(스무딩) 검색 {smoothed['search']:.2f} : 부스팅 {smoothed['content']:.2f}"
            f" → 효율이 높은 {CHANNEL_LABELS[best]} 쪽에 비중을 실었습니다."
        )
        if penalized:
            basis += (
                f" {', '.join(CHANNEL_LABELS[c] for c in penalized)}는 ROAS 1.0 미만이라 최소 비중"
                f"({guardrails.min_channel_share * 100:.0f}%)까지만 배정했습니다."
            )
        cold_start = False

    search_budget = round_to_unit(total_budget * shares["search"], guardrails.budget_unit)
    search_budget = min(search_budget, total_budget)
    content_budget = total_budget - search_budget

    return {
        "total_budget": total_budget,
        "by_channel": {"search": search_budget, "content": content_budget},
        "share": {
            "search": round(search_budget / total_budget, 4),
            "content": round(content_budget / total_budget, 4),
        },
        "channel_roas": {c: (None if channel_roas[c] is None else round(channel_roas[c], 2))
                         for c in CHANNELS},
        "basis": basis,
        "cold_start": cold_start,
        "penalized": penalized,
    }


# ---------------------------------------------------------------------------
# 월간 정산
# ---------------------------------------------------------------------------


def compute_feedback_budget(
    settlement: MonthlySettlement, guardrails: Guardrails
) -> dict[str, Any]:
    """수익 × 되먹임 비율 → 다음 달 광고 예산(안전선 적용)."""
    rate = settlement.feedback_rate if settlement.feedback_rate is not None else guardrails.feedback_rate
    if not 0 < rate <= 1:
        raise ValueError("feedback_rate는 0보다 크고 1 이하여야 합니다.")

    computed = settlement.gross_revenue * rate
    flags: list[str] = []
    budget = computed

    if computed < guardrails.min_monthly_budget:
        if settlement.program_month <= guardrails.seed_max_months:
            budget = guardrails.seed_budget
            flags.append(
                f"수익의 {rate * 100:.0f}%({fmt_won(computed)})가 최소 집행 단위"
                f"({fmt_won(guardrails.min_monthly_budget)})에 못 미쳐 시드 예산 "
                f"{fmt_won(guardrails.seed_budget)}을 적용했습니다"
                f"(프로그램 {settlement.program_month}개월 차, 최대 {guardrails.seed_max_months}개월)."
            )
        else:
            flags.append(
                f"수익의 {rate * 100:.0f}%({fmt_won(computed)})가 최소 집행 단위에 못 미칩니다. "
                "시드 기간이 끝나 강제 집행하지 않고, 이 금액만큼만 배정합니다(유기 확장 우선)."
            )
    if budget > guardrails.max_monthly_budget:
        budget = guardrails.max_monthly_budget
        flags.append(
            f"월 광고비 상한 {fmt_won(guardrails.max_monthly_budget)}을 넘어 상한으로 잘랐습니다."
        )

    return {
        "feedback_rate": rate,
        "computed_budget": round_to_unit(computed, guardrails.budget_unit),
        "budget": round_to_unit(budget, guardrails.budget_unit),
        "flags": flags,
        "seed_applied": budget > computed and budget == guardrails.seed_budget,
        "capped": budget == guardrails.max_monthly_budget and computed > guardrails.max_monthly_budget,
    }


def settle(
    settlement: MonthlySettlement,
    guardrails: Guardrails,
    catalog: list[ProductCandidate] | None = None,
) -> dict[str, Any]:
    """정산 1건을 계산해 리포트용 결과 dict로 만든다."""
    guardrails.validate()
    rate = settlement.feedback_rate if settlement.feedback_rate is not None else guardrails.feedback_rate

    budget_info = compute_feedback_budget(settlement, guardrails)

    revenue = settlement.gross_revenue
    spend = settlement.total_ad_spend
    reach = settlement.total_reach
    clicks = settlement.total_clicks

    roas = safe_div(revenue, spend)
    metrics = {
        "gross_revenue": revenue,
        "total_ad_spend": spend,
        "net_before_reinvestment": revenue - spend,
        "roas": None if roas is None else round(roas, 2),
        "revenue_per_visitor": None if not reach else round(revenue / reach, 2),
        "cost_per_visitor": None if not reach or spend == 0 else round(spend / reach, 2),
        "profit_per_visitor": (
            None if not reach else round((revenue - spend) / reach, 2)
        ),
        "revenue_per_click": None if not clicks else round(revenue / clicks, 2),
        "cost_per_click": None if not clicks or spend == 0 else round(spend / clicks, 2),
        "click_rate": None if not reach else round(clicks / reach, 4),
        "ad_dependency": None if not revenue else round(spend / revenue, 4),
        "revenue_per_view_blog": None if not settlement.naver_blog_views
        else round(settlement.naver_connect_revenue / settlement.naver_blog_views, 2),
        "revenue_per_view_shorts": None if not settlement.youtube_shorts_views
        else round(settlement.coupang_revenue / settlement.youtube_shorts_views, 2),
    }

    attribution = settlement.attribution or DEFAULT_ATTRIBUTION
    attr_total = sum(attribution.values())
    attribution = {c: attribution.get(c, 0) / attr_total for c in CHANNELS}
    revenue_by_channel = {c: revenue * attribution[c] for c in CHANNELS}

    allocation = allocate_budget(
        budget_info["budget"], revenue_by_channel, settlement.ad_spend, guardrails
    )

    result: dict[str, Any] = {
        "month": settlement.month,
        "next_month": next_month(settlement.month),
        "collection_status": settlement.collection_status,
        "note": settlement.note,
        "program_month": settlement.program_month,
        "inputs": {
            "naver_blog_views": settlement.naver_blog_views,
            "naver_blog_visitors": settlement.naver_blog_visitors,
            "youtube_shorts_views": settlement.youtube_shorts_views,
            "coupang_clicks": settlement.coupang_clicks,
            "coupang_revenue": settlement.coupang_revenue,
            "naver_connect_clicks": settlement.naver_connect_clicks,
            "naver_connect_revenue": settlement.naver_connect_revenue,
            "other_revenue": settlement.other_revenue,
            "ad_spend": settlement.ad_spend,
            "total_reach": reach,
            "total_clicks": clicks,
            "feedback_rate": rate,
        },
        "metrics": metrics,
        "attribution": attribution,
        "revenue_by_channel": {c: round(v) for c, v in revenue_by_channel.items()},
        "budget": budget_info,
        "allocation": allocation,
        "guardrails": asdict(guardrails),
        "assumptions": {
            "attribution": (
                "검색 유입 글에서 결제가 일어나고 쇼츠는 발견·재방문에 기여한다는 전제로 "
                f"검색 {attribution['search'] * 100:.0f} : 부스팅 {attribution['content'] * 100:.0f}로 나눴습니다. "
                "매달 실제 전환 데이터가 쌓이면 정산 JSON의 attribution으로 덮어쓰세요."
            ),
            "roas": "ROAS = 당월 수익 ÷ 당월 집행 광고비(전월에 산출한 예산이 당월에 집행된 금액).",
        },
    }

    if catalog is not None:
        current = settlement.current_products or {}
        result["products"] = {
            "target_month": next_month(settlement.month),
            "ranking": rank_products(catalog, next_month(settlement.month)),
            "selection": select_seasonal_products(
                catalog, next_month(settlement.month), current=current,
                switch_margin=guardrails.switch_margin,
            ),
        }
    return result


# ---------------------------------------------------------------------------
# 계절성 상품 스코어링
# ---------------------------------------------------------------------------


def season_fit(product: ProductCandidate, month: str) -> tuple[float, str]:
    season = season_for_month(month)
    if season in product.seasons:
        return 1.0, f"{SEASONS[season]['label']} 시즌 주력"
    if set(product.seasons) & ADJACENT_SEASONS[season]:
        return 0.5, f"{SEASONS[season]['label']} 인접 시즌"
    return 0.15, "비시즌"


def _demand_score(product: ProductCandidate) -> float:
    volume = min(1.0, math.log10(1 + product.monthly_search_volume) / math.log10(1 + 200_000))
    reviews = min(1.0, math.log10(1 + product.review_count) / math.log10(1 + 100_000))
    return 0.65 * volume + 0.35 * reviews


def _price_band_score(price: int) -> float:
    """2~4만 원대가 충동 구매와 수익의 균형점. 너무 싸면 수수료가, 너무 비싸면 전환이 약하다."""
    if price < 5_000:
        return 0.2
    if price <= 45_000:
        return 1.0
    if price <= 80_000:
        return 0.8
    if price <= 150_000:
        return 0.5
    return 0.3


def _economics_score(product: ProductCandidate) -> float:
    commission = product.commission_per_sale
    commission_score = min(1.0, math.log10(1 + commission) / math.log10(1 + 5_000))
    rating_score = max(0.0, min(1.0, (product.rating - 3.5) / 1.5))
    return 0.60 * commission_score + 0.25 * _price_band_score(product.price) + 0.15 * rating_score


def score_product(product: ProductCandidate, month: str) -> dict[str, Any]:
    fit, reason = season_fit(product, month)
    demand = _demand_score(product)
    economics = _economics_score(product)
    confidence = 1.0 if product.verified else 0.0
    total = (
        SEASON_WEIGHT * fit
        + DEMAND_WEIGHT * demand
        + ECONOMICS_WEIGHT * economics
        + CONFIDENCE_WEIGHT * confidence
    )
    return {
        "name": product.name,
        "platform": product.platform,
        "price": product.price,
        "commission_rate": product.commission_rate,
        "commission_per_sale": product.commission_per_sale,
        "season_fit": round(fit, 3),
        "season_reason": reason,
        "demand_score": round(demand, 3),
        "economics_score": round(economics, 3),
        "data_confidence": confidence,
        "score": round(total, 4),
        "verified": product.verified,
        "source": product.source,
        "tags": product.tags,
    }


def rank_products(catalog: list[ProductCandidate], month: str) -> list[dict[str, Any]]:
    scored = [score_product(p, month) for p in catalog]
    return sorted(scored, key=lambda item: item["score"], reverse=True)


def select_seasonal_products(
    catalog: list[ProductCandidate],
    month: str,
    current: dict[str, str] | None = None,
    switch_margin: float = 0.08,
) -> dict[str, Any]:
    """플랫폼별 대표 상품 1종씩 선택.

    "별도 코멘트 전까지 같은 플랫폼 내 같은 제품" 원칙에 따라, 새 후보가
    기존 상품보다 switch_margin 이상 높을 때만 교체한다.
    """
    current = current or {}
    ranking = rank_products(catalog, month)
    selection: dict[str, Any] = {}
    by_platform: dict[str, list[dict[str, Any]]] = {}
    for row in ranking:
        by_platform.setdefault(row["platform"], []).append(row)

    for platform in ("coupang", "naver"):
        rows = by_platform.get(platform, [])
        if not rows:
            continue
        best = rows[0]
        incumbent_name = current.get(platform)
        incumbent = next((r for r in rows if r["name"] == incumbent_name), None)
        if incumbent is None:
            selection[platform] = {
                **best,
                "action": "신규 선정",
                "reason": f"{best['season_reason']} · 종합 {best['score']:.2f}로 1순위입니다.",
            }
        elif best["name"] == incumbent["name"]:
            selection[platform] = {
                **best,
                "action": "유지",
                "reason": "현재 상품이 이번 달에도 1순위라 그대로 유지합니다.",
            }
        elif best["score"] - incumbent["score"] >= switch_margin:
            selection[platform] = {
                **best,
                "action": "교체",
                "previous": incumbent_name,
                "previous_score": incumbent["score"],
                "reason": (
                    f"{best['season_reason']} · {best['name']}가 기존 상품보다 "
                    f"{best['score'] - incumbent['score']:.2f}점 높아 교체를 제안합니다."
                ),
            }
        else:
            selection[platform] = {
                **incumbent,
                "action": "유지",
                "challenger": best["name"],
                "challenger_score": best["score"],
                "reason": (
                    f"1순위 {best['name']}({best['score']:.2f})가 기존 상품"
                    f"({incumbent['score']:.2f})보다 {switch_margin}점 이상 앞서지 않아 유지합니다."
                ),
            }
    return selection


def load_catalog(path: Path | str) -> list[ProductCandidate]:
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    products = []
    for item in raw.get("products", []):
        products.append(ProductCandidate(**item))
    if not products:
        raise ValueError(f"상품 카탈로그가 비어 있습니다: {path}")
    return products


# ---------------------------------------------------------------------------
# 리포트
# ---------------------------------------------------------------------------


def _won_or_dash(value: float | None) -> str:
    return "-" if value is None else fmt_won(value)


def render_markdown(result: dict[str, Any]) -> str:
    month = result["month"]
    nxt = result["next_month"]
    inputs = result["inputs"]
    metrics = result["metrics"]
    budget = result["budget"]
    allocation = result["allocation"]
    status_label = "샘플(추정치)" if result["collection_status"] == "sample" else "실제 집계"

    lines: list[str] = []
    lines.append(f"# {month} 월간 수익·되먹임 정산 리포트 ({status_label})")
    lines.append("")
    if result.get("note"):
        lines.append(f"> {result['note']}")
        lines.append("")

    # 1. 이번 달 요약 -----------------------------------------------------
    lines.append("## 1. 이번 달 정산 요약")
    lines.append("")
    lines.append("| 항목 | 값 |")
    lines.append("| --- | --- |")
    lines.append(f"| 블로그 조회수 / 방문자 | {inputs['naver_blog_views']:,}회 / {inputs['naver_blog_visitors']:,}명 |")
    lines.append(f"| 쇼츠 조회수 | {inputs['youtube_shorts_views']:,}회 |")
    lines.append(f"| 아웃바운드 클릭(쿠팡 / 쇼핑 커넥트) | {inputs['coupang_clicks']:,} / {inputs['naver_connect_clicks']:,} |")
    lines.append(f"| 쿠팡파트너스 수익 | {inputs['coupang_revenue']:,}원 |")
    lines.append(f"| 네이버 쇼핑 커넥트 수익 | {inputs['naver_connect_revenue']:,}원 |")
    if inputs["other_revenue"]:
        lines.append(f"| 기타 수익 | {inputs['other_revenue']:,}원 |")
    lines.append(f"| **총수익** | **{metrics['gross_revenue']:,}원** |")
    lines.append(f"| 집행 광고비 | {metrics['total_ad_spend']:,}원 |")
    lines.append(f"| 되먹임 비율 | {budget['feedback_rate'] * 100:.0f}% |")
    lines.append(f"| **{nxt} 재투자 예산** | **{budget['budget']:,}원** |")
    lines.append("")

    # 2. 효율 지표 --------------------------------------------------------
    lines.append("## 2. 핵심 효율 지표")
    lines.append("")
    lines.append("| 지표 | 값 | 읽는 법 |")
    lines.append("| --- | --- | --- |")
    roas = metrics["roas"]
    lines.append(
        f"| ROAS | {roas if roas is not None else '광고비 0원(유기)'} | "
        "1.0 이상이면 광고비보다 수익이 큽니다 |"
    )
    lines.append(
        f"| 유입당 수익(EPV) | {_won_or_dash(metrics['revenue_per_visitor'])} | "
        "방문자·조회수 1회가 만든 수익 |"
    )
    lines.append(
        f"| 유입당 광고비(CAC 대용) | {_won_or_dash(metrics['cost_per_visitor'])} | "
        "유입 1회를 사 오는 데 쓴 광고비 |"
    )
    lines.append(
        f"| 유입당 이익 | {_won_or_dash(metrics['profit_per_visitor'])} | "
        "광고비를 뺀 뒤 유입 1회가 남긴 이익 |"
    )
    lines.append(
        f"| 클릭당 수익(EPC) | {_won_or_dash(metrics['revenue_per_click'])} | "
        "제휴 클릭 1회가 만든 수익 |"
    )
    lines.append(
        f"| 클릭률 | {fmt_pct(metrics['click_rate'])} | "
        "유입 대비 제휴 링크 클릭 비율 |"
    )
    lines.append(
        f"| 광고 의존도 | {fmt_pct(metrics['ad_dependency'])} | "
        "수익 중 광고비가 차지하는 비율 |"
    )
    lines.append("")

    # 3. 다음 달 예산 -----------------------------------------------------
    lines.append(f"## 3. {nxt} 재투자 예산")
    lines.append("")
    lines.append("| 단계 | 값 |")
    lines.append("| --- | --- |")
    lines.append(f"| 총수익 | {metrics['gross_revenue']:,}원 |")
    lines.append(f"| × 되먹임 {budget['feedback_rate'] * 100:.0f}% | {budget['computed_budget']:,}원 |")
    lines.append(f"| 안전선 적용 후 예산 | **{budget['budget']:,}원** |")
    cash_left = metrics["gross_revenue"] - metrics["total_ad_spend"] - budget["budget"]
    cash_label = "광고 집행 후 남는 현금" if cash_left >= 0 else "광고 집행 후 남는 현금(초기 투자분)"
    lines.append(f"| {cash_label} | {cash_left:,}원 |")
    lines.append("")
    if cash_left < 0:
        lines.append(
            f"- 이번 달은 시드 구간이라 광고비가 수익보다 {abs(cash_left):,}원 많습니다. "
            "초기 투자로 보고, 3개월 뒤 ROAS로 회수 여부를 판단합니다."
        )
        lines.append("")
    if budget["flags"]:
        for flag in budget["flags"]:
            lines.append(f"- {flag}")
        lines.append("")

    # 4. 채널 배분 --------------------------------------------------------
    lines.append("## 4. 채널별 예산 배분")
    lines.append("")
    lines.append("| 채널 | 다음 달 예산 | 비중 | 직전 ROAS |")
    lines.append("| --- | --- | --- | --- |")
    for channel in CHANNELS:
        roas_value = allocation["channel_roas"].get(channel)
        lines.append(
            f"| {CHANNEL_LABELS[channel]} | {allocation['by_channel'][channel]:,}원 | "
            f"{allocation['share'][channel] * 100:.0f}% | "
            f"{roas_value if roas_value is not None else '집행 전'} |"
        )
    lines.append("")
    lines.append(f"- 배분 근거: {allocation['basis']}")
    guard = result.get("guardrails", {})
    min_share = guard.get("min_channel_share", 0.3)
    max_share = guard.get("max_channel_share", 0.7)
    lines.append(
        f"- 안전선: 어느 한 채널도 {min_share * 100:.0f}% 아래, {max_share * 100:.0f}% 위로 가지 않게 "
        "묶어 두었습니다."
    )
    lines.append("")

    # 5. 계절성 상품 ------------------------------------------------------
    products = result.get("products")
    if products:
        target = products["target_month"]
        season = season_for_month(target)
        lines.append(f"## 5. {target} 계절성 대표 상품 ({SEASONS[season]['label']})")
        lines.append("")
        selection = products["selection"]
        lines.append("| 플랫폼 | 상품 | 단가 | 수수료 | 건당 수익 | 점수 | 판단 |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for platform in ("coupang", "naver"):
            row = selection.get(platform)
            if not row:
                continue
            lines.append(
                f"| {'쿠팡파트너스' if platform == 'coupang' else '네이버 쇼핑 커넥트'} | "
                f"{row['name']} | {row['price']:,}원 | {row['commission_rate'] * 100:.1f}% | "
                f"{row['commission_per_sale']:,}원 | {row['score']:.2f} | {row['action']} |"
            )
        lines.append("")
        for platform in ("coupang", "naver"):
            row = selection.get(platform)
            if not row:
                continue
            lines.append(f"- **{row['name']}** ({row['action']}): {row['reason']}")
        lines.append("")
        lines.append("### 플랫폼별 상위 후보")
        lines.append("")
        lines.append("| 순위 | 상품 | 플랫폼 | 계절 적합 | 수요 | 수익성 | 데이터 신뢰 | 종합 |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for idx, row in enumerate(products["ranking"][:10], start=1):
            lines.append(
                f"| {idx} | {row['name']} | {'쿠팡' if row['platform'] == 'coupang' else '네이버'} | {row['season_fit']:.2f} | "
                f"{row['demand_score']:.2f} | {row['economics_score']:.2f} | "
                f"{'확인' if row['verified'] else '추정'} | {row['score']:.2f} |"
            )
        lines.append("")

    # 6. 안전선 -----------------------------------------------------------
    lines.append("## 6. 광고 집행 안전선")
    lines.append("")
    guard = result.get("guardrails", Guardrails().__dict__)
    lines.append(
        f"- 월 광고비 상한: {fmt_won(guard.get('max_monthly_budget'))} "
        "(수익이 커져도 이 선을 넘기지 않습니다)"
    )
    lines.append(
        f"- 되먹임 예산은 수익의 {budget['feedback_rate'] * 100:.0f}%까지만 씁니다. "
        f"나머지 {100 - budget['feedback_rate'] * 100:.0f}%는 현금으로 남깁니다."
    )
    lines.append(
        f"- 채널 최소 비중 {guard.get('min_channel_share', 0.3) * 100:.0f}%: "
        "한쪽 ROAS가 좋아도 다른 채널을 끄지 않습니다."
    )
    lines.append("- ROAS 1.0 미만 채널은 최소 비중까지만 배정합니다.")
    lines.append(
        f"- 시드 예산 {fmt_won(guard.get('seed_budget'))}은 프로그램 "
        f"1~{guard.get('seed_max_months')}개월 차에만 씁니다."
    )
    lines.append(
        f"- 최소 집행 단위 {fmt_won(guard.get('min_monthly_budget'))}: 이보다 작은 예산은 지면이 잡히지 않아 집행하지 않습니다."
    )
    lines.append("")

    # 7. 확인 필요 --------------------------------------------------------
    lines.append("## 7. 승태 님 확인이 필요한 항목")
    lines.append("")
    rate = budget["feedback_rate"]
    lines.append(f"- [ ] 되먹임 비율 {rate * 100:.0f}% 유지 여부 (바꾸시면 다음 정산부터 적용)")
    if budget["seed_applied"]:
        lines.append(f"- [ ] 시드 예산 {fmt_won(budget['budget'])} 집행 승인 (1~3개월 차 한정)")
    selection = (products or {}).get("selection", {})
    for platform, row in selection.items():
        if row["action"] != "유지":
            prev = row.get("previous", "없음")
            lines.append(f"- [ ] {row['name']}로 교체 승인 (기존: {prev})")
    lines.append("- [ ] 상품 카탈로그의 '추정' 데이터를 이번 달 실제 검색량·리뷰수로 갱신")
    lines.append("")

    # 8. 다음 달 실행 -----------------------------------------------------
    lines.append(f"## 8. {nxt} 실행 체크리스트")
    lines.append("")
    lines.append(f"1. 검색광고 예산 {allocation['by_channel']['search']:,}원 — 효율 좋은 글 2~3편에만 집중")
    lines.append(f"2. 콘텐츠 부스팅 예산 {allocation['by_channel']['content']:,}원 — 조회수 상위 쇼츠 1~2편")
    lines.append("3. 매주 월요일: 클릭률·ROAS 중간 점검, 절반 이상 소진된 채널은 증액 보류")
    lines.append(f"4. {nxt} 말: 이 리포트에 실제 수치를 채워 다음 되먹임 계산")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 샘플 정산
# ---------------------------------------------------------------------------


def build_sample_settlement(month: str = "2026-11") -> MonthlySettlement:
    """11월 초기 정산 시뮬레이션용 샘플. 실제 집계값이 아니라 구조 검증용이다."""
    return MonthlySettlement(
        month=month,
        program_month=1,
        naver_blog_views=2_830,
        naver_blog_visitors=1_240,
        youtube_shorts_views=3_150,
        coupang_clicks=96,
        coupang_revenue=8_544,       # 17,800원 × 3% × 16건
        naver_connect_clicks=12,
        naver_connect_revenue=23_256,  # 32,300원 × 12% × 6건
        ad_spend={"search": 0, "content": 0},
        feedback_rate=0.5,
        current_products={
            "coupang": "한스웰 황사 마스크 KF94 100매",
            "naver": "들꽃잠 배 찜질팩",
        },
        collection_status="sample",
        note=(
            "11월 초기 정산 시뮬레이션. 유입·클릭·수익은 구조 검증용 샘플값이며, "
            "실제 값은 11월 말 플랫폼 대시보드에서 확정합니다."
        ),
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _write_outputs(result: dict[str, Any], out_dir: Path, stem: str | None = None) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = stem or f"{result['month']}_settlement"
    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}_report.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(result), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="월간 수익 되먹임·계절성 상품 엔진")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="상품 카탈로그 JSON 경로")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="리포트 출력 폴더")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sim = sub.add_parser("simulate", help="내장 샘플로 정산 시뮬레이션")
    p_sim.add_argument("--month", default="2026-11")
    p_sim.add_argument("--rate", type=float, default=None, help="되먹임 비율(기본 0.5)")

    p_settle = sub.add_parser("settle", help="정산 JSON으로 실행")
    p_settle.add_argument("--input", required=True)
    p_settle.add_argument("--no-print", action="store_true")

    p_score = sub.add_parser("score", help="특정 월의 상품 스코어만 출력")
    p_score.add_argument("--month", required=True)

    args = parser.parse_args(argv)
    catalog = load_catalog(args.catalog) if args.command in ("simulate", "settle", "score") else None
    guardrails = Guardrails()

    if args.command == "score":
        ranking = rank_products(catalog or [], args.month)
        print(json.dumps(ranking, ensure_ascii=False, indent=2))
        return 0

    if args.command == "simulate":
        settlement = build_sample_settlement(args.month)
        if args.rate is not None:
            settlement.feedback_rate = args.rate
        result = settle(settlement, guardrails, catalog)
    else:
        raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
        settlement = MonthlySettlement.from_dict(raw)
        result = settle(settlement, guardrails, catalog)

    paths = _write_outputs(result, Path(args.out_dir))
    if not getattr(args, "no_print", False):
        print(render_markdown(result))
    print(f"\n[저장] {paths['json']}")
    print(f"[저장] {paths['markdown']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
