#!/usr/bin/env python3
"""revenue_feedback 모듈 단위 테스트.

실행: python3 -m unittest engine.test_revenue_feedback -v
"""

from __future__ import annotations

import json
import unittest

from engine.revenue_feedback import (
    DEFAULT_CATALOG,
    Guardrails,
    MonthlySettlement,
    ProductCandidate,
    allocate_budget,
    build_sample_settlement,
    compute_feedback_budget,
    load_catalog,
    next_month,
    render_markdown,
    score_product,
    select_seasonal_products,
    settle,
)


class FeedbackBudgetTests(unittest.TestCase):
    def setUp(self):
        self.g = Guardrails()

    def test_fifty_percent_of_revenue_above_floor(self):
        s = MonthlySettlement(month="2027-01", program_month=6, coupang_revenue=200_000)
        info = compute_feedback_budget(s, self.g)
        self.assertEqual(info["computed_budget"], 100_000)
        self.assertEqual(info["budget"], 100_000)
        self.assertFalse(info["seed_applied"])

    def test_seed_budget_when_revenue_too_small(self):
        s = MonthlySettlement(month="2026-11", program_month=1, coupang_revenue=31_800)
        info = compute_feedback_budget(s, self.g)
        self.assertEqual(info["computed_budget"], 16_000)  # 15,900 → 1,000원 단위
        self.assertEqual(info["budget"], 50_000)
        self.assertTrue(info["seed_applied"])
        self.assertTrue(any("시드" in f for f in info["flags"]))

    def test_no_forced_spend_after_seed_period(self):
        s = MonthlySettlement(month="2027-04", program_month=6, coupang_revenue=20_000)
        info = compute_feedback_budget(s, self.g)
        self.assertEqual(info["budget"], 10_000)
        self.assertFalse(info["seed_applied"])

    def test_cap_applied(self):
        s = MonthlySettlement(month="2027-02", program_month=4, coupang_revenue=2_000_000)
        info = compute_feedback_budget(s, self.g)
        self.assertEqual(info["budget"], self.g.max_monthly_budget)
        self.assertTrue(info["capped"])

    def test_custom_feedback_rate(self):
        s = MonthlySettlement(month="2027-02", program_month=4,
                              coupang_revenue=100_000, feedback_rate=0.3)
        info = compute_feedback_budget(s, self.g)
        self.assertEqual(info["computed_budget"], 30_000)
        self.assertEqual(info["feedback_rate"], 0.3)

    def test_invalid_rate_rejected(self):
        s = MonthlySettlement(month="2027-02", program_month=4,
                              coupang_revenue=100_000, feedback_rate=1.5)
        with self.assertRaises(ValueError):
            compute_feedback_budget(s, self.g)


class AllocationTests(unittest.TestCase):
    def setUp(self):
        self.g = Guardrails()

    def test_cold_start_split(self):
        out = allocate_budget(
            50_000,
            {"search": 0, "content": 0},
            {"search": 0, "content": 0},
            self.g,
        )
        self.assertEqual(out["total_budget"], 50_000)
        self.assertEqual(out["by_channel"]["search"], 30_000)
        self.assertEqual(out["by_channel"]["content"], 20_000)
        self.assertTrue(out["cold_start"])

    def test_budget_always_sums_to_total(self):
        out = allocate_budget(
            133_000,
            {"search": 70_000, "content": 60_000},
            {"search": 30_000, "content": 20_000},
            self.g,
        )
        self.assertEqual(sum(out["by_channel"].values()), 133_000)
        for channel in ("search", "content"):
            self.assertGreaterEqual(out["share"][channel], self.g.min_channel_share - 1e-9)
            self.assertLessEqual(out["share"][channel], self.g.max_channel_share + 1e-9)

    def test_shifts_toward_higher_roas(self):
        # 부스팅 ROAS 3.0 vs 검색 1.5 → 부스팅 쪽이 더 많이 받아야 한다
        out = allocate_budget(
            100_000,
            {"search": 45_000, "content": 90_000},
            {"search": 30_000, "content": 30_000},
            self.g,
        )
        self.assertGreater(out["by_channel"]["content"], out["by_channel"]["search"])
        self.assertLessEqual(out["share"]["content"], self.g.max_channel_share + 1e-9)

    def test_low_roas_channel_gets_minimum_only(self):
        out = allocate_budget(
            100_000,
            {"search": 20_000, "content": 90_000},
            {"search": 30_000, "content": 30_000},
            self.g,
        )
        self.assertIn("search", out["penalized"])
        self.assertAlmostEqual(out["share"]["search"], self.g.min_channel_share, places=2)

    def test_zero_budget(self):
        out = allocate_budget(0, {"search": 1, "content": 1}, {"search": 0, "content": 0}, self.g)
        self.assertEqual(out["by_channel"], {"search": 0, "content": 0})


class MetricsTests(unittest.TestCase):
    def test_unit_economics(self):
        s = MonthlySettlement(
            month="2026-11",
            naver_blog_visitors=1_000,
            youtube_shorts_views=1_000,
            coupang_clicks=50,
            coupang_revenue=10_000,
            naver_connect_clicks=10,
            naver_connect_revenue=5_000,
            ad_spend={"search": 10_000, "content": 5_000},
        )
        result = settle(s, Guardrails())
        m = result["metrics"]
        self.assertEqual(m["gross_revenue"], 15_000)
        self.assertEqual(m["total_ad_spend"], 15_000)
        self.assertEqual(m["roas"], 1.0)
        self.assertEqual(m["revenue_per_visitor"], 7.5)
        self.assertEqual(m["cost_per_visitor"], 7.5)
        self.assertEqual(m["revenue_per_click"], 250.0)
        self.assertEqual(m["click_rate"], 0.03)
        self.assertEqual(m["ad_dependency"], 1.0)

    def test_zero_spend_roas_is_none(self):
        result = settle(build_sample_settlement(), Guardrails())
        self.assertIsNone(result["metrics"]["roas"])

    def test_allocation_after_real_spend(self):
        s = MonthlySettlement(
            month="2027-01", program_month=3,
            coupang_revenue=120_000,
            naver_connect_revenue=80_000,
            ad_spend={"search": 40_000, "content": 20_000},
            attribution={"search": 0.5, "content": 0.5},
        )
        result = settle(s, Guardrails())
        alloc = result["allocation"]
        self.assertEqual(alloc["total_budget"], 100_000)
        self.assertFalse(alloc["cold_start"])
        self.assertEqual(sum(alloc["by_channel"].values()), 100_000)

    def test_next_month_rollover(self):
        self.assertEqual(next_month("2026-12"), "2027-01")
        self.assertEqual(next_month("2026-11"), "2026-12")


class SeasonalityTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog(DEFAULT_CATALOG)

    def test_winter_products_win_in_november(self):
        selection = select_seasonal_products(self.catalog, "2026-11")
        self.assertEqual(selection["coupang"]["name"], "한스웰 황사 마스크 KF94 100매")
        self.assertEqual(selection["naver"]["name"], "들꽃잠 배 찜질팩")

    def test_summer_products_win_in_july(self):
        selection = select_seasonal_products(self.catalog, "2027-07")
        self.assertEqual(selection["coupang"]["name"], "신일 리모컨 서큘레이터")
        self.assertEqual(selection["naver"]["name"], "삐아 쿨링 패치 30매")

    def test_season_fit_scoring(self):
        mask = next(p for p in self.catalog if p.name.startswith("한스웰"))
        fan = next(p for p in self.catalog if p.name.startswith("신일"))
        winter = score_product(mask, "2026-12")
        self.assertEqual(winter["season_fit"], 1.0)
        # 여름 전용 상품은 겨울에 비시즌(0.15)으로 떨어진다
        off_season = score_product(fan, "2026-12")
        self.assertEqual(off_season["season_fit"], 0.15)
        self.assertGreater(winter["score"], off_season["score"])

    def test_keeps_incumbent_without_clear_winner(self):
        current = {"coupang": "듀라온 온수 찜질기 (허리·배)",
                   "naver": "들꽃잠 배 찜질팩"}
        selection = select_seasonal_products(
            self.catalog, "2026-11", current=current, switch_margin=0.20
        )
        self.assertEqual(selection["coupang"]["action"], "유지")
        self.assertEqual(selection["coupang"]["name"], "듀라온 온수 찜질기 (허리·배)")

    def test_switches_on_clear_winner(self):
        current = {"coupang": "위닉스 제습기 16L", "naver": "삐아 쿨링 패치 30매"}
        selection = select_seasonal_products(
            self.catalog, "2026-11", current=current, switch_margin=0.05
        )
        self.assertEqual(selection["coupang"]["action"], "교체")
        self.assertEqual(selection["naver"]["action"], "교체")

    def test_naver_commission_matches_known_value(self):
        pouch = next(p for p in self.catalog if p.name == "들꽃잠 배 찜질팩")
        self.assertEqual(pouch.commission_per_sale, 3_876)


class ReportTests(unittest.TestCase):
    def test_markdown_has_core_sections(self):
        result = settle(build_sample_settlement(), Guardrails(), load_catalog(DEFAULT_CATALOG))
        md = render_markdown(result)
        for heading in ("이번 달 정산 요약", "핵심 효율 지표", "재투자 예산",
                        "채널별 예산 배분", "계절성 대표 상품", "광고 집행 안전선",
                        "승태 님 확인이 필요한 항목", "실행 체크리스트"):
            self.assertIn(heading, md)
        self.assertIn("한스웰", md)
        self.assertIn("들꽃잠", md)

    def test_json_serializable(self):
        result = settle(build_sample_settlement(), Guardrails(), load_catalog(DEFAULT_CATALOG))
        text = json.dumps(result, ensure_ascii=False)
        self.assertGreater(len(text), 500)
        loaded = json.loads(text)
        self.assertEqual(loaded["month"], "2026-11")
        self.assertEqual(loaded["next_month"], "2026-12")


class ValidationTests(unittest.TestCase):
    def test_negative_input_rejected(self):
        with self.assertRaises(ValueError):
            MonthlySettlement.from_dict({"month": "2026-11", "coupang_clicks": -5})

    def test_unknown_field_rejected(self):
        with self.assertRaises(ValueError):
            MonthlySettlement.from_dict({"month": "2026-11", "whatever": 1})

    def test_bad_month_rejected(self):
        with self.assertRaises(ValueError):
            MonthlySettlement.from_dict({"month": "2026/11"})

    def test_guardrail_validation(self):
        with self.assertRaises(ValueError):
            Guardrails(feedback_rate=0).validate()
        with self.assertRaises(ValueError):
            Guardrails(min_channel_share=0.8, max_channel_share=0.7).validate()


if __name__ == "__main__":
    unittest.main()
