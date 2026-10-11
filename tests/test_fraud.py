"""Unit tests for Risk and Fraud Detection Agent (agents/fraud_agent.py).

Verifies:
- Evaluation of normal transactions (low risk, clear action)
- Evaluation of suspicious cryptocurrency transactions (high risk, review flag)
- ML model probability output vs heuristic score
- Factor explanation extraction
- Batch scanning of customer recent transactions
"""

import pytest
from agents.fraud_agent import RiskAndFraudAgent


class TestFraudAgent:
    @pytest.fixture
    def agent(self):
        return RiskAndFraudAgent()

    def test_analyze_normal_transaction(self, agent):
        res = agent.analyze_transaction("TXN1001")
        assert res["status"] == "success"
        data = res["data"]
        assert data["risk_level"] == "LOW"
        assert data["risk_score"] < 30
        assert data["ml_fraud_probability"] < 0.35
        assert data["flagged_for_review"] is False
        assert "cleared" in data["recommended_action"].lower()

    def test_analyze_suspicious_crypto_transaction(self, agent):
        res = agent.analyze_transaction("TXN1005")
        assert res["status"] == "success"
        data = res["data"]
        assert data["risk_level"] == "HIGH"
        assert data["risk_score"] >= 70
        assert data["ml_fraud_probability"] > 0.60
        assert data["flagged_for_review"] is True
        assert "review" in data["recommended_action"].lower()
        
        # Verify explainable factors
        factors_text = " ".join(data["factors"]).lower()
        assert "cryptocurrency" in factors_text

    def test_analyze_invalid_transaction(self, agent):
        res = agent.analyze_transaction("TXN9999")
        assert res["status"] == "error"
        assert "not found" in res["message"].lower()

    def test_scan_recent_transactions(self, agent):
        # CUST1001 has TXN1005 (crypto) and TXN1007 (rapid geo Paris) in recent history
        res = agent.scan_recent_transactions("CUST1001", limit=10)
        assert res["status"] == "success"
        data = res["data"]
        assert data["total_scanned"] > 0
        assert data["total_flagged"] >= 1
        flagged_ids = [t["transaction_id"] for t in data["flagged_transactions"]]
        assert "TXN1005" in flagged_ids
