"""Unit tests for Supervisor / Orchestrator Agent (agents/supervisor.py).

Verifies all 5 core use cases, execution trace generation, multi-agent collaboration,
and safe handling of unknown queries.
"""

import pytest
from agents.supervisor import SupervisorAgent


class TestSupervisorAgent:
    @pytest.fixture
    def supervisor(self):
        return SupervisorAgent()

    def test_use_case_1_balance_enquiry(self, supervisor):
        res = supervisor.process_request("Show my account balance.", current_customer_id="CUST1001")
        assert res["success"] is True
        trace = res["trace"]
        assert trace["detected_intent"] == SupervisorAgent.INTENT_BALANCE
        assert "CustomerBankingAgent" in trace["agents_invoked"]
        assert any(tc["tool"] == "get_account_balance" for tc in trace["tool_calls"])
        assert "14,850.50" in res["response"]

    def test_use_case_2_transaction_history(self, supervisor):
        res = supervisor.process_request("Show my last 3 transactions.", current_customer_id="CUST1001")
        assert res["success"] is True
        trace = res["trace"]
        assert trace["detected_intent"] == SupervisorAgent.INTENT_TRANSACTIONS
        assert "CustomerBankingAgent" in trace["agents_invoked"]
        assert any(tc["tool"] == "get_recent_transactions" for tc in trace["tool_calls"])
        assert len(res["data"]["transactions"]) == 3

    def test_use_case_3_fraud_risk_assessment(self, supervisor):
        res = supervisor.process_request("Check transaction TXN1005 for suspicious activity.", current_customer_id="CUST1001")
        assert res["success"] is True
        trace = res["trace"]
        assert trace["detected_intent"] == SupervisorAgent.INTENT_RISK
        assert "RiskAndFraudAgent" in trace["agents_invoked"]
        assert any(tc["tool"] == "assess_transaction_risk" for tc in trace["tool_calls"])
        assert "HIGH" in res["response"]
        assert res["data"]["risk_level"] == "HIGH"

    def test_use_case_4_loan_eligibility(self, supervisor):
        res = supervisor.process_request("Am I eligible for a $15,000 personal loan?", current_customer_id="CUST1001")
        assert res["success"] is True
        trace = res["trace"]
        assert trace["detected_intent"] == SupervisorAgent.INTENT_LOAN
        assert "CreditAndLoanAgent" in trace["agents_invoked"]
        assert any(tc["tool"] == "evaluate_loan_eligibility" for tc in trace["tool_calls"])
        assert "Approved" in res["response"]
        assert "SIMULATION NOTICE" in res["response"]

    def test_use_case_5_multi_agent_collaboration(self, supervisor):
        res = supervisor.process_request(
            "Review my recent transactions and identify suspicious ones.",
            current_customer_id="CUST1001"
        )
        assert res["success"] is True
        trace = res["trace"]
        
        # 1. Intent check
        assert trace["detected_intent"] == SupervisorAgent.INTENT_MULTI_AGENT_AUDIT
        
        # 2. Multi-agent check: BOTH agents must have executed
        assert "CustomerBankingAgent" in trace["agents_invoked"]
        assert "RiskAndFraudAgent" in trace["agents_invoked"]
        
        # 3. Multiple tools executed across agents
        tools_executed = [tc["tool"] for tc in trace["tool_calls"]]
        assert "get_recent_transactions" in tools_executed
        assert "assess_transaction_risk" in tools_executed
        
        # 4. Verify actual fraud analysis results found in CUST1001 (TXN1005 is high risk)
        assert res["data"]["total_audited"] > 0
        assert res["data"]["total_flagged"] >= 1
        assert "Multi-Agent Audit Report" in res["response"]

    def test_unknown_query_handling(self, supervisor):
        res = supervisor.process_request("What is the stock price of Apple right now?")
        assert res["success"] is False
        trace = res["trace"]
        assert trace["detected_intent"] == SupervisorAgent.INTENT_UNKNOWN
        assert len(trace["agents_invoked"]) == 0
        assert len(trace["tool_calls"]) == 0  # Zero hallucinated tool calls
        assert "could not determine a supported banking action" in res["response"].lower()

    def test_empty_query_handling(self, supervisor):
        res = supervisor.process_request("")
        assert res["success"] is False
        assert "valid banking request" in res["response"].lower()
