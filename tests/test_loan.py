"""Unit tests for Credit and Loan Agent (agents/loan_agent.py).

Verifies:
- Approval recommendation for qualified customer (CUST1001)
- Rejection recommendation with explainable reasons for unqualified customer (CUST1003)
- Max loan offer and APR calculations
- Simulation disclaimer presence
- Handling of invalid customer IDs
"""

import pytest
from agents.loan_agent import CreditAndLoanAgent


class TestLoanAgent:
    @pytest.fixture
    def agent(self):
        return CreditAndLoanAgent()

    def test_evaluate_loan_approved(self, agent):
        res = agent.evaluate_loan("CUST1001", requested_amount=15000.0)
        assert res["status"] == "success"
        data = res["data"]
        assert data["is_eligible"] is True
        assert "Approved" in data["status"]
        assert data["credit_tier"] == "Excellent"
        assert data["max_loan_offer"] > 0
        assert data["estimated_apr_pct"] is not None
        assert "SIMULATION NOTICE" in data["disclaimer"]

    def test_evaluate_loan_declined(self, agent):
        res = agent.evaluate_loan("CUST1003", requested_amount=10000.0)
        assert res["status"] == "success"
        data = res["data"]
        assert data["is_eligible"] is False
        assert "Declined" in data["status"]
        assert len(data["reasons"]) >= 3
        # Confirm failure reasons explain income and DTI
        reasons_text = " ".join(data["reasons"]).lower()
        assert "income" in reasons_text
        assert "debt-to-income" in reasons_text or "dti" in reasons_text

    def test_evaluate_loan_invalid_customer(self):
        agent = CreditAndLoanAgent()
        res = agent.evaluate_loan("CUST9999")
        assert res["status"] == "error"
        assert "not found" in res["message"].lower()
