"""Unit tests for Natural-Language LLM Router & Fallback (agents/llm_router.py).

Verifies:
- LLM availability detection and provider reporting
- Deterministic heuristic fallback when LLM keys are absent/offline
- Accurate mapping from LLM JSON schemas to internal Supervisor intents
- Strict data integrity (no hallucination or alteration of tool results)
"""

import pytest
from agents.llm_router import LLMRouter
from agents.supervisor import SupervisorAgent


class TestLLMRouter:
    @pytest.fixture
    def router(self):
        return LLMRouter()

    @pytest.fixture
    def supervisor(self):
        return SupervisorAgent()

    def test_provider_name_without_keys(self, monkeypatch):
        # Ensure environment has no keys for this test
        monkeypatch.setenv("GEMINI_API_KEY", "")
        monkeypatch.setenv("OPENAI_API_KEY", "")
        r = LLMRouter()
        r.gemini_key = ""
        r.openai_key = ""
        
        assert not r.is_llm_available()
        assert "Deterministic Heuristic" in r.get_provider_name()

    def test_tool_mapping_balance(self, supervisor):
        llm_decision = {
            "tool": "get_balance",
            "parameters": {"customer_id": "CUST1002"}
        }
        intent, entities = supervisor._map_llm_tool_to_intent(llm_decision, "Show balance", "CUST1001")
        assert intent == SupervisorAgent.INTENT_BALANCE
        assert entities["customer_id"] == "CUST1002"

    def test_tool_mapping_multi_agent_audit(self, supervisor):
        llm_decision = {
            "tool": "audit_recent_transactions",
            "parameters": {"customer_id": "CUST1001", "limit": 7}
        }
        intent, entities = supervisor._map_llm_tool_to_intent(llm_decision, "Audit transactions", "CUST1001")
        assert intent == SupervisorAgent.INTENT_MULTI_AGENT_AUDIT
        assert entities["limit"] == 7

    def test_tool_mapping_assess_risk(self, supervisor):
        llm_decision = {
            "tool": "assess_risk",
            "parameters": {"transaction_id": "TXN1005"}
        }
        intent, entities = supervisor._map_llm_tool_to_intent(llm_decision, "Check TXN1005", "CUST1001")
        assert intent == SupervisorAgent.INTENT_RISK
        assert entities["transaction_id"] == "TXN1005"

    def test_tool_mapping_evaluate_loan(self, supervisor):
        llm_decision = {
            "tool": "evaluate_loan",
            "parameters": {"customer_id": "CUST1004", "requested_amount": 25000.0}
        }
        intent, entities = supervisor._map_llm_tool_to_intent(llm_decision, "Can I borrow $25,000?", "CUST1001")
        assert intent == SupervisorAgent.INTENT_LOAN
        assert entities["customer_id"] == "CUST1004"
        assert entities["requested_amount"] == 25000.0

    def test_tool_mapping_unknown(self, supervisor):
        llm_decision = {
            "tool": "unknown",
            "parameters": {}
        }
        intent, entities = supervisor._map_llm_tool_to_intent(llm_decision, "Who won the game?", "CUST1001")
        assert intent == SupervisorAgent.INTENT_UNKNOWN

    def test_fallback_routing_mode_recorded_in_trace(self, supervisor):
        res = supervisor.process_request("Show my account balance.", current_customer_id="CUST1001")
        assert res["success"] is True
        trace = res["trace"]
        assert "routing_mode" in trace
        assert "Deterministic Heuristic" in trace["routing_mode"] or "LLM" in trace["routing_mode"]

    def test_synthesize_preserves_default_text_on_fallback(self, router):
        default_message = "Account balance for Sarah Jenkins: $14,850.50 USD."
        output = router.synthesize_response(
            "What is my balance?",
            {"account_balance": 14850.50},
            default_message
        )
        assert output == default_message
