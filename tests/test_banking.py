"""Unit tests for Simulated Banking APIs in tools/banking_api.py.

Verifies:
- Customer ID validation (valid & invalid)
- Account balance retrieval
- Transaction history retrieval (limit filtering)
- Transaction ID lookup (valid & unknown)
- Transaction risk evaluation (normal low risk & suspicious high risk)
- Loan eligibility underwriting (approvals & rejections)
"""

import pytest
from tools.banking_api import (
    get_customer,
    get_account_balance,
    get_recent_transactions,
    get_transaction,
    assess_transaction_risk,
    evaluate_loan_eligibility,
    get_all_customers,
    get_all_transactions
)


class TestBankingAPI:
    def test_get_all_customers(self):
        customers = get_all_customers()
        assert len(customers) >= 5
        ids = [c["customer_id"] for c in customers]
        assert "CUST1001" in ids
        assert "CUST1003" in ids

    def test_get_customer_valid(self):
        res = get_customer("CUST1001")
        assert res["success"] is True
        cust = res["customer"]
        assert cust["full_name"] == "Sarah Jenkins"
        assert cust["account_number"] == "ACC-449102"
        assert float(cust["account_balance"]) > 0

    def test_get_customer_invalid(self):
        res = get_customer("CUST9999")
        assert res["success"] is False
        assert "not found" in res["error"].lower()

    def test_get_customer_empty_input(self):
        res = get_customer("")
        assert res["success"] is False
        assert "invalid input" in res["error"].lower()

    def test_get_account_balance(self):
        res = get_account_balance("CUST1001")
        assert res["success"] is True
        assert res["customer_id"] == "CUST1001"
        assert res["account_balance"] == 14850.50
        assert res["currency"] == "USD"
        assert "as_of" in res

    def test_get_account_balance_invalid_customer(self):
        res = get_account_balance("INVALID_ID")
        assert res["success"] is False

    def test_get_recent_transactions_limit(self):
        res = get_recent_transactions("CUST1001", limit=3)
        assert res["success"] is True
        assert len(res["transactions"]) == 3
        # Check timestamps are sorted descending
        ts = [t["timestamp"] for t in res["transactions"]]
        assert ts == sorted(ts, reverse=True)

    def test_get_recent_transactions_invalid_customer(self):
        res = get_recent_transactions("CUST9999", limit=5)
        assert res["success"] is False

    def test_get_transaction_valid(self):
        res = get_transaction("TXN1005")
        assert res["success"] is True
        txn = res["transaction"]
        assert txn["transaction_id"] == "TXN1005"
        assert txn["customer_id"] == "CUST1001"
        assert txn["merchant"] == "Apex Crypto Exchange"
        assert txn["category"] == "Cryptocurrency"

    def test_get_transaction_unknown(self):
        res = get_transaction("TXN9999")
        assert res["success"] is False
        assert "not found" in res["error"].lower()

    def test_assess_risk_normal_transaction(self):
        res = assess_transaction_risk("TXN1001")
        assert res["success"] is True
        assert res["risk_level"] == "LOW"
        assert res["risk_score"] < 30
        assert "cleared" in res["recommended_action"].lower()
        assert len(res["factors"]) > 0

    def test_assess_risk_suspicious_crypto_transaction(self):
        res = assess_transaction_risk("TXN1005")
        assert res["success"] is True
        assert res["risk_level"] == "HIGH"
        assert res["risk_score"] >= 70
        assert "analyst" in res["recommended_action"].lower()
        # Verify factor explanations
        factors_text = " ".join(res["factors"]).lower()
        assert "cryptocurrency" in factors_text
        assert "high monetary amount" in factors_text or "exceeds" in factors_text

    def test_assess_risk_unknown_transaction(self):
        res = assess_transaction_risk("TXN9999")
        assert res["success"] is False

    def test_loan_eligibility_approved(self):
        # CUST1001: Income $7,500, Debt $1,500 (DTI 20%), Credit 760 -> High approval
        res = evaluate_loan_eligibility("CUST1001", requested_amount=10000.0)
        assert res["success"] is True
        assert res["is_eligible"] is True
        assert "Approved" in res["status"]
        assert res["credit_tier"] == "Excellent"
        assert res["max_loan_offer"] > 0
        assert res["estimated_apr_pct"] is not None
        assert "SIMULATION NOTICE" in res["disclaimer"]

    def test_loan_eligibility_declined(self):
        # CUST1003: Income $2,400 (< $3000), Debt $1,800 (DTI 75%), Credit 590 (< 650)
        res = evaluate_loan_eligibility("CUST1003", requested_amount=10000.0)
        assert res["success"] is True
        assert res["is_eligible"] is False
        assert "Declined" in res["status"]
        assert len(res["reasons"]) >= 3  # Failed all 3 criteria
        assert res["max_loan_offer"] == 0.0
