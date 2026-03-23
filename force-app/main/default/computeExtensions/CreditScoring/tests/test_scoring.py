"""
Unit tests for the credit rating scoring functions.
"""
import pytest
import numpy as np


class TestComputeAltmanZScore:
    """Tests for compute_altman_z_score."""

    def test_known_safe_score(self):
        from main import compute_altman_z_score

        # Strong financials should produce a high Z-Score
        score = compute_altman_z_score(
            working_capital=500000,
            total_assets=1000000,
            retained_earnings=200000,
            ebit=150000,
            market_value_equity=800000,
            total_liabilities=400000,
            sales=900000,
        )
        assert score > 2.99, f"Expected safe score > 2.99, got {score}"

    def test_known_distress_score(self):
        from main import compute_altman_z_score

        # Weak financials should produce a low Z-Score
        score = compute_altman_z_score(
            working_capital=-50000,
            total_assets=1000000,
            retained_earnings=-100000,
            ebit=-20000,
            market_value_equity=100000,
            total_liabilities=900000,
            sales=200000,
        )
        assert score < 1.81, f"Expected distress score < 1.81, got {score}"

    def test_manual_calculation(self):
        from main import compute_altman_z_score

        # X1=0.5, X2=0.2, X3=0.15, X4=2.0, X5=0.9
        # Z = 1.2*0.5 + 1.4*0.2 + 3.3*0.15 + 0.6*2.0 + 1.0*0.9
        #   = 0.6 + 0.28 + 0.495 + 1.2 + 0.9 = 3.475
        score = compute_altman_z_score(
            working_capital=500000,
            total_assets=1000000,
            retained_earnings=200000,
            ebit=150000,
            market_value_equity=800000,
            total_liabilities=400000,
            sales=900000,
        )
        expected = round(
            1.2 * 0.5 + 1.4 * 0.2 + 3.3 * 0.15 + 0.6 * 2.0 + 1.0 * 0.9, 4
        )
        assert score == expected

    def test_zero_total_assets_raises(self):
        from main import compute_altman_z_score

        with pytest.raises(ValueError, match="non-zero"):
            compute_altman_z_score(
                working_capital=100,
                total_assets=0,
                retained_earnings=100,
                ebit=100,
                market_value_equity=100,
                total_liabilities=100,
                sales=100,
            )

    def test_zero_total_liabilities_raises(self):
        from main import compute_altman_z_score

        with pytest.raises(ValueError, match="non-zero"):
            compute_altman_z_score(
                working_capital=100,
                total_assets=100,
                retained_earnings=100,
                ebit=100,
                market_value_equity=100,
                total_liabilities=0,
                sales=100,
            )

    def test_return_type_is_float(self):
        from main import compute_altman_z_score

        score = compute_altman_z_score(
            working_capital=100,
            total_assets=1000,
            retained_earnings=50,
            ebit=80,
            market_value_equity=500,
            total_liabilities=300,
            sales=700,
        )
        assert isinstance(score, float)


class TestComputeCreditScoreLR:
    """Tests for compute_credit_score_lr (scikit-learn logistic regression)."""

    def test_returns_score_in_range(self):
        from main import compute_credit_score_lr

        score = compute_credit_score_lr(
            working_capital=500000,
            total_assets=1000000,
            retained_earnings=200000,
            ebit=150000,
            market_value_equity=800000,
            total_liabilities=400000,
            sales=900000,
        )
        assert 1.0 <= score <= 4.0, f"Score {score} out of expected 1.0-4.0 range"

    def test_strong_financials_higher_than_weak(self):
        from main import compute_credit_score_lr

        strong = compute_credit_score_lr(
            working_capital=500000,
            total_assets=1000000,
            retained_earnings=200000,
            ebit=150000,
            market_value_equity=800000,
            total_liabilities=400000,
            sales=900000,
        )
        weak = compute_credit_score_lr(
            working_capital=-50000,
            total_assets=1000000,
            retained_earnings=-100000,
            ebit=-20000,
            market_value_equity=100000,
            total_liabilities=900000,
            sales=200000,
        )
        assert strong > weak, f"Strong ({strong}) should exceed weak ({weak})"

    def test_zero_total_assets_raises(self):
        from main import compute_credit_score_lr

        with pytest.raises(ValueError, match="non-zero"):
            compute_credit_score_lr(
                working_capital=100,
                total_assets=0,
                retained_earnings=100,
                ebit=100,
                market_value_equity=100,
                total_liabilities=100,
                sales=100,
            )

    def test_zero_total_liabilities_raises(self):
        from main import compute_credit_score_lr

        with pytest.raises(ValueError, match="non-zero"):
            compute_credit_score_lr(
                working_capital=100,
                total_assets=100,
                retained_earnings=100,
                ebit=100,
                market_value_equity=100,
                total_liabilities=0,
                sales=100,
            )

    def test_return_type_is_float(self):
        from main import compute_credit_score_lr

        score = compute_credit_score_lr(
            working_capital=100,
            total_assets=1000,
            retained_earnings=50,
            ebit=80,
            market_value_equity=500,
            total_liabilities=300,
            sales=700,
        )
        assert isinstance(score, float)


class TestMapZScoreToRating:
    """Tests for map_z_score_to_rating across all rating boundaries."""

    @pytest.mark.parametrize(
        "z_score, expected_rating, expected_risk",
        [
            (3.5, "AAA", "Safe"),
            (3.01, "AAA", "Safe"),
            (3.0, "AA", "Safe"),
            (2.85, "AA", "Safe"),
            (2.7, "A", "Safe"),
            (2.5, "A", "Safe"),
            (2.4, "BBB", "Grey Zone"),
            (2.2, "BBB", "Grey Zone"),
            (2.0, "BB", "Grey Zone"),
            (1.9, "BB", "Grey Zone"),
            (1.8, "B", "Distress"),
            (1.6, "B", "Distress"),
            (1.5, "CCC", "Distress"),
            (1.2, "CCC", "Distress"),
            (1.0, "D", "Distress"),
            (0.5, "D", "Distress"),
            (-1.0, "D", "Distress"),
        ],
    )
    def test_rating_boundaries(self, z_score, expected_rating, expected_risk):
        from main import map_z_score_to_rating

        rating, risk = map_z_score_to_rating(z_score)
        assert rating == expected_rating, f"z={z_score}: expected {expected_rating}, got {rating}"
        assert risk == expected_risk, f"z={z_score}: expected {expected_risk}, got {risk}"
