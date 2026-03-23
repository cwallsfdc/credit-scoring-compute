"""
Tests for the Credit Scoring API endpoints, including the protected
/api/credit-scoring/ endpoint and the public / and /health endpoints.
"""
import os

import pytest
from unittest.mock import MagicMock, AsyncMock

from tests.conftest import _make_account_record


class TestPublicEndpoints:
    """Tests for the publicly accessible endpoints."""

    def test_root_returns_welcome(self, client):
        response = client.get("/")
        assert response.status_code == 200
        body = response.json()
        assert "message" in body
        assert "Credit Scoring" in body["message"]
        assert body["docs_url"] == "/docs"
        assert body["salesforce_api_prefix"] == "/api"

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCreditScoringEndpoint:
    """Tests for POST /api/credit-scoring/."""

    def _mock_query_result(self, mock_context, records):
        """Helper to set the mock data_api.query return value."""
        result = MagicMock()
        result.records = records
        mock_context.data_api.query = AsyncMock(return_value=result)

    def test_altman_z_score_default_method(self, client, mock_context):
        record = _make_account_record()
        self._mock_query_result(mock_context, [record])
        mock_context.data_api.create = AsyncMock()

        response = client.post(
            "/api/credit-scoring/",
            json={"data": {"accountId": "001XX000003GYQXYA4"}},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["accountId"] == "001XX000003GYQXYA4"
        assert body["accountName"] == "Acme Corporation"
        assert body["method"] == "altman_z_score"
        assert isinstance(body["score"], float)
        assert body["creditScoring"] in ("AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D")
        assert body["riskCategory"] in ("Safe", "Grey Zone", "Distress")

    def test_logistic_regression_method(self, client, mock_context, monkeypatch):
        monkeypatch.setenv("SCORING_METHOD", "logistic_regression")
        record = _make_account_record()
        self._mock_query_result(mock_context, [record])
        mock_context.data_api.create = AsyncMock()

        response = client.post(
            "/api/credit-scoring/",
            json={"data": {"accountId": "001XX000003GYQXYA4"}},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["method"] == "logistic_regression"
        assert isinstance(body["score"], float)
        assert body["creditScoring"] in ("AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D")

    def test_unknown_method_defaults_to_altman(self, client, mock_context, monkeypatch):
        monkeypatch.setenv("SCORING_METHOD", "unknown_method")
        record = _make_account_record()
        self._mock_query_result(mock_context, [record])
        mock_context.data_api.create = AsyncMock()

        response = client.post(
            "/api/credit-scoring/",
            json={"data": {"accountId": "001XX000003GYQXYA4"}},
        )

        assert response.status_code == 200
        assert response.json()["method"] == "altman_z_score"

    def test_account_not_found_returns_404(self, client, mock_context):
        self._mock_query_result(mock_context, [])

        response = client.post(
            "/api/credit-scoring/",
            json={"data": {"accountId": "001NOTFOUND"}},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_query_failure_returns_500(self, client, mock_context):
        mock_context.data_api.query = AsyncMock(
            side_effect=Exception("SOQL error")
        )

        response = client.post(
            "/api/credit-scoring/",
            json={"data": {"accountId": "001XX000003GYQXYA4"}},
        )

        assert response.status_code == 500
        assert "Failed to query" in response.json()["detail"]

    def test_zero_assets_returns_422(self, client, mock_context):
        record = _make_account_record(total_assets=0, total_liabilities=0)
        self._mock_query_result(mock_context, [record])

        response = client.post(
            "/api/credit-scoring/",
            json={"data": {"accountId": "001XX000003GYQXYA4"}},
        )

        assert response.status_code == 422
        assert "non-zero" in response.json()["detail"].lower()

    def test_platform_event_published(self, client, mock_context):
        record = _make_account_record()
        self._mock_query_result(mock_context, [record])
        mock_context.data_api.create = AsyncMock()

        response = client.post(
            "/api/credit-scoring/",
            json={"data": {"accountId": "001XX000003GYQXYA4"}},
        )

        assert response.status_code == 200
        mock_context.data_api.create.assert_called_once()
        call_args = mock_context.data_api.create.call_args[0][0]
        assert call_args["type"] == "GenerateCreditScoring__e"
        assert call_args["fields"]["AccountId__c"] == "001XX000003GYQXYA4"
        assert "Rating__c" in call_args["fields"]
        assert "Score__c" in call_args["fields"]
        assert "RiskCategory__c" in call_args["fields"]

    def test_platform_event_failure_returns_500(self, client, mock_context):
        record = _make_account_record()
        self._mock_query_result(mock_context, [record])
        mock_context.data_api.create = AsyncMock(
            side_effect=Exception("Event publish error")
        )

        response = client.post(
            "/api/credit-scoring/",
            json={"data": {"accountId": "001XX000003GYQXYA4"}},
        )

        assert response.status_code == 500
        assert "Platform Event" in response.json()["detail"]

    def test_missing_account_id_returns_422(self, client, mock_context):
        response = client.post(
            "/api/credit-scoring/",
            json={"data": {}},
        )

        assert response.status_code == 422

    def test_distress_financials_produce_low_rating(self, client, mock_context):
        record = _make_account_record(
            working_capital=-50000,
            total_assets=1000000,
            retained_earnings=-100000,
            ebit=-20000,
            market_value_equity=100000,
            total_liabilities=900000,
            sales=200000,
        )
        self._mock_query_result(mock_context, [record])
        mock_context.data_api.create = AsyncMock()

        response = client.post(
            "/api/credit-scoring/",
            json={"data": {"accountId": "001XX000003GYQXYA4"}},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["riskCategory"] == "Distress"
        assert body["creditScoring"] in ("B", "CCC", "D")
