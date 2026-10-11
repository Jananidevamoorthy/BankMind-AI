"""Supervisor / Orchestrator Agent for BankMind AI.

Acts as the central controller and router for the multi-agent system.
Responsibilities:
- Parses user natural-language requests
- Classifies user intent and extracts financial entities (customer_id, transaction_id, loan amount)
- Routes queries to specialized agents (Banking, Fraud, Loan)
- Executes multi-agent joint workflows (e.g., Banking Agent + Fraud Agent collaboration)
- Captures an immutable, transparent Execution Trace for every request
- Safely handles unknown queries, missing data, and validation errors
"""

import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from agents.banking_agent import CustomerBankingAgent
from agents.fraud_agent import RiskAndFraudAgent
from agents.loan_agent import CreditAndLoanAgent
from agents.llm_router import LLMRouter


class SupervisorAgent:
    """Central orchestrator coordinating specialized domain agents with execution tracing."""
    
    NAME = "SupervisorOrchestrator"
    
    INTENT_BALANCE = "BALANCE_ENQUIRY"
    INTENT_TRANSACTIONS = "TRANSACTION_HISTORY"
    INTENT_RISK = "TRANSACTION_RISK_ASSESSMENT"
    INTENT_LOAN = "LOAN_ELIGIBILITY"
    INTENT_MULTI_AGENT_AUDIT = "MULTI_AGENT_TRANSACTION_AUDIT"
    INTENT_PROFILE = "CUSTOMER_PROFILE"
    INTENT_GREETING = "GREETING_OR_HELP"
    INTENT_UNKNOWN = "UNKNOWN_INTENT"
    
    def __init__(self):
        self.banking_agent = CustomerBankingAgent()
        self.fraud_agent = RiskAndFraudAgent()
        self.loan_agent = CreditAndLoanAgent()
        self.llm_router = LLMRouter()

    def process_request(self, user_query: str, current_customer_id: str = "CUST1001") -> Dict[str, Any]:
        """Process natural-language request and coordinate specialized agents.
        
        Args:
            user_query: The raw natural-language question or instruction.
            current_customer_id: Default active customer ID from UI context.
            
        Returns:
            Dictionary containing final text response, execution trace, and structured data.
        """
        trace_id = str(uuid.uuid4())[:8]
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Initialize immutable Execution Trace
        trace: Dict[str, Any] = {
            "trace_id": trace_id,
            "timestamp": start_time,
            "user_query": user_query,
            "detected_intent": None,
            "extracted_entities": {},
            "agents_invoked": [],
            "tool_calls": [],
            "reasoning_notes": [],
            "final_response": None
        }
        
        if not user_query or not user_query.strip():
            trace["detected_intent"] = self.INTENT_UNKNOWN
            trace["final_response"] = "Please enter a valid banking request or question."
            return {
                "success": False,
                "response": trace["final_response"],
                "trace": trace,
                "data": None
            }
            
        # 1. Intent Classification & Entity Extraction (LLM with Heuristic Fallback)
        llm_decision = self.llm_router.route_query_with_llm(user_query, current_customer_id)
        if llm_decision and "tool" in llm_decision:
            trace["routing_mode"] = f"LLM ({self.llm_router.get_provider_name()})"
            intent, entities = self._map_llm_tool_to_intent(llm_decision, user_query, current_customer_id)
        else:
            trace["routing_mode"] = "Deterministic Heuristic Engine (Rule-Based Fallback)"
            intent, entities = self._classify_intent_and_extract_entities(user_query, current_customer_id)

        trace["detected_intent"] = intent
        trace["extracted_entities"] = entities
        
        # 2. Execution Routing based on Intent
        try:
            if intent == self.INTENT_MULTI_AGENT_AUDIT:
                return self._handle_multi_agent_audit(user_query, entities, trace)
                
            elif intent == self.INTENT_BALANCE:
                return self._handle_balance_enquiry(entities, trace)
                
            elif intent == self.INTENT_TRANSACTIONS:
                return self._handle_transactions_enquiry(entities, trace)
                
            elif intent == self.INTENT_RISK:
                return self._handle_risk_assessment(entities, trace)
                
            elif intent == self.INTENT_LOAN:
                return self._handle_loan_evaluation(entities, trace)
                
            elif intent == self.INTENT_PROFILE:
                return self._handle_customer_profile(entities, trace)
                
            elif intent == self.INTENT_GREETING:
                return self._handle_greeting(entities, trace)
                
            else:
                return self._handle_unknown_intent(user_query, trace)
                
        except Exception as e:
            trace["reasoning_notes"].append(f"Orchestration failure encountered: {str(e)}")
            trace["final_response"] = (
                f"An internal error occurred while processing your request: {str(e)}. "
                "Please verify your query parameters."
            )
            return {
                "success": False,
                "response": trace["final_response"],
                "trace": trace,
                "data": None
            }

    def _classify_intent_and_extract_entities(self, query: str, default_cust_id: str) -> Tuple[str, Dict[str, Any]]:
        """Identify user intent and parse relevant entities (IDs, limits, dollar figures)."""
        q_lower = query.lower()
        entities: Dict[str, Any] = {}
        
        # 1. Flexible Customer ID extraction (e.g. CUST1001, cust-1001, cust 1001)
        cust_match = re.search(r"\b(?:CUST|cust)[-_\s]?(\d{4})\b", query, re.IGNORECASE)
        entities["customer_id"] = f"CUST{cust_match.group(1)}" if cust_match else default_cust_id
        
        # 2. Flexible Transaction ID extraction (e.g. TXN1005, txn 1005, txn-1005, transaction 1005)
        txn_match = re.search(r"\b(?:TXN|txn|transaction|tx)[-_\s#]?(\d{4})\b", query, re.IGNORECASE)
        if txn_match:
            entities["transaction_id"] = f"TXN{txn_match.group(1)}"
            
        # 3. Numeric limit extraction
        limit_match = re.search(r"\b(?:last|recent|past|top|show)\s+(\d{1,2})\b", q_lower)
        if limit_match:
            entities["limit"] = int(limit_match.group(1))
        else:
            entities["limit"] = 5
            
        # 4. Loan amount extraction
        amt_match = re.search(r"\$?\s*(\d{1,3}(?:,\d{3})+|\d{4,6})\b", query)
        if amt_match:
            raw_amt = amt_match.group(1).replace(",", "")
            entities["requested_amount"] = float(raw_amt)
        else:
            entities["requested_amount"] = 10000.0

        # --- Semantic Intent Classification ---
        
        # A. Greetings, Help, Introductions, Capabilities
        greetings = ["hi", "hello", "hey", "help", "who are you", "what can you do", "good morning", "good afternoon", "good evening", "how are you", "start", "menu", "assist", "guide"]
        if q_lower.strip() in ["hi", "hello", "hey", "help", "start", "vanakkam", "namaste"] or \
           any(w in q_lower for w in ["who are you", "what can you do", "how can you help", "what do you do", "help me"]):
            return self.INTENT_GREETING, entities

        # B. Fraud Risk for a specific transaction (TXN ID explicitly found or requested)
        if "transaction_id" in entities or (any(w in q_lower for w in ["risk", "fraud", "suspicious", "check", "verify", "flag", "explain"]) and "txn" in q_lower):
            return self.INTENT_RISK, entities

        # C. Multi-Agent Audit / Fraud / Security Scanning (Without a specific transaction ID)
        fraud_keywords = [
            "fraud", "suspicious", "unusual", "safe", "safety", "threat", "risk", "risks", 
            "flag", "flagged", "audit", "security", "scam", "compromised", "protect", "anomalous",
            "suspicious activity", "any fraud", "check fraud", "is there fraud", "are my transactions safe"
        ]
        if any(w in q_lower for w in fraud_keywords) or \
           ("review" in q_lower and any(w in q_lower for w in ["transaction", "transactions", "activity"])) or \
           ("scan" in q_lower):
            return self.INTENT_MULTI_AGENT_AUDIT, entities

        # D. Loan Eligibility / Borrowing / Credit Scoring
        loan_keywords = [
            "loan", "credit", "borrow", "eligible", "eligibility", "mortgage", "lending",
            "interest rate", "apr", "debt", "dti", "apply for loan", "can i get money",
            "need money", "can i borrow", "how much can i borrow", "personal loan", "loan status"
        ]
        if any(w in q_lower for w in loan_keywords):
            return self.INTENT_LOAN, entities

        # E. Account Balance & Available Funds
        balance_keywords = [
            "balance", "funds", "how much money", "account balance", "savings", "checking balance",
            "how much do i have", "how much can i spend", "my money", "total money", "cash",
            "account total", "how much cash", "money in my account", "current balance",
            "available money", "show balance", "what is my balance", "money left"
        ]
        if any(w in q_lower for w in balance_keywords):
            return self.INTENT_BALANCE, entities

        # F. Transaction History & Spending Breakdown
        txn_keywords = [
            "transaction", "transactions", "activity", "purchases", "history", "recent payments",
            "spending", "statement", "where did my money go", "spent", "charges", "orders",
            "payments", "buying", "ledger", "recent transactions", "last transactions"
        ]
        if any(w in q_lower for w in txn_keywords):
            return self.INTENT_TRANSACTIONS, entities

        # G. Customer Profile / Account Details / Overview
        profile_keywords = [
            "profile", "account details", "who am i", "my info", "customer info", "my account",
            "account summary", "overview", "status", "tell me about my account", "check my account",
            "account overview", "account information", "details"
        ]
        if any(w in q_lower for w in profile_keywords):
            return self.INTENT_PROFILE, entities

        return self.INTENT_UNKNOWN, entities

    def _map_llm_tool_to_intent(self, llm_decision: Dict[str, Any], query: str, default_cust_id: str) -> Tuple[str, Dict[str, Any]]:
        """Map LLM-selected tool and parameters to internal intent and entity structure."""
        tool = llm_decision.get("tool", "")
        params = llm_decision.get("parameters", {})
        
        entities: Dict[str, Any] = {
            "customer_id": params.get("customer_id", default_cust_id),
            "limit": int(params.get("limit", 5)),
            "requested_amount": float(params.get("requested_amount", 10000.0))
        }
        
        if "transaction_id" in params and params["transaction_id"]:
            entities["transaction_id"] = str(params["transaction_id"]).upper()
            
        tool_intent_map = {
            "get_balance": self.INTENT_BALANCE,
            "get_transactions": self.INTENT_TRANSACTIONS,
            "assess_risk": self.INTENT_RISK,
            "evaluate_loan": self.INTENT_LOAN,
            "audit_recent_transactions": self.INTENT_MULTI_AGENT_AUDIT,
            "get_profile": self.INTENT_PROFILE
        }
        
        intent = tool_intent_map.get(tool, self.INTENT_UNKNOWN)
        return intent, entities
    # INTENT HANDLERS & MULTI-AGENT EXECUTION
    # =========================================================================

    def _handle_greeting(self, entities: Dict[str, Any], trace: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greetings and capability inquiries with a personalized welcome."""
        cust_id = entities.get("customer_id", "CUST1001")
        cust_res = self.banking_agent.get_customer_profile(cust_id)
        cust_name = cust_res["data"]["customer"]["full_name"] if cust_res.get("data") else "Customer"
        bal_res = self.banking_agent.get_balance(cust_id)
        bal_val = f"${bal_res['data']['account_balance']:,.2f} {bal_res['data']['currency']}" if bal_res.get("data") else "$0.00"
        
        greeting_text = (
            f"Hello **{cust_name}**! 👋 Welcome to **BankMind AI**.\n\n"
            f"You are currently viewing customer profile `{cust_id}` with an available balance of **{bal_val}**.\n\n"
            "I am your central **Supervisor Agent**, coordinating specialized agents to assist you:\n\n"
            "1. 🏦 **Customer Banking Agent**:\n"
            "   - *'Show my account balance.'*\n"
            "   - *'Show my last 5 transactions.'*\n"
            "2. 🛡️ **Risk & Fraud Detection Agent**:\n"
            "   - *'Check transaction TXN1005 for suspicious activity.'*\n"
            "   - *'Explain why transaction TXN1005 was flagged.'*\n"
            "3. 📝 **Credit & Loan Underwriting Agent**:\n"
            "   - *'Am I eligible for a $15,000 personal loan?'*\n"
            "4. ⚡ **Multi-Agent Collaboration**:\n"
            "   - *'Review my recent transactions and identify suspicious ones.'*\n\n"
            "How can I help you right now?"
        )
        
        trace["reasoning_notes"].append(f"Handled greeting for customer '{cust_id}'. Outlined agent capabilities.")
        trace["final_response"] = greeting_text
        return {
            "success": True,
            "response": greeting_text,
            "trace": trace,
            "data": None
        }

    def _handle_balance_enquiry(self, entities: Dict[str, Any], trace: Dict[str, Any]) -> Dict[str, Any]:
        """Use Case 1: Route to CustomerBankingAgent for account balance."""
        cust_id = entities["customer_id"]
        trace["agents_invoked"].append(self.banking_agent.NAME)
        trace["reasoning_notes"].append(
            f"Routing to {self.banking_agent.NAME} to retrieve ledger balance for customer '{cust_id}'."
        )
        
        # Tool execution
        tool_call = {
            "agent": self.banking_agent.NAME,
            "tool": "get_account_balance",
            "parameters": {"customer_id": cust_id},
            "status": "executing"
        }
        res = self.banking_agent.get_balance(cust_id)
        tool_call["status"] = res["status"]
        tool_call["output_summary"] = (
            f"Balance: ${res['data']['account_balance']:,.2f} {res['data']['currency']}"
            if res["status"] == "success" else res["message"]
        )
        trace["tool_calls"].append(tool_call)
        
        trace["final_response"] = res["message"]
        return {
            "success": res["status"] == "success",
            "response": res["message"],
            "trace": trace,
            "data": res.get("data")
        }

    def _handle_transactions_enquiry(self, entities: Dict[str, Any], trace: Dict[str, Any]) -> Dict[str, Any]:
        """Use Case 2: Route to CustomerBankingAgent for transaction history."""
        cust_id = entities["customer_id"]
        limit = entities.get("limit", 5)
        
        trace["agents_invoked"].append(self.banking_agent.NAME)
        trace["reasoning_notes"].append(
            f"Routing to {self.banking_agent.NAME} to retrieve last {limit} transactions for customer '{cust_id}'."
        )
        
        tool_call = {
            "agent": self.banking_agent.NAME,
            "tool": "get_recent_transactions",
            "parameters": {"customer_id": cust_id, "limit": limit},
            "status": "executing"
        }
        res = self.banking_agent.get_recent_transactions(cust_id, limit=limit)
        tool_call["status"] = res["status"]
        tool_call["output_summary"] = (
            f"Retrieved {len(res['data']['transactions'])} transactions"
            if res["status"] == "success" else res["message"]
        )
        trace["tool_calls"].append(tool_call)
        
        trace["final_response"] = res["message"]
        return {
            "success": res["status"] == "success",
            "response": res["message"],
            "trace": trace,
            "data": res.get("data")
        }

    def _handle_risk_assessment(self, entities: Dict[str, Any], trace: Dict[str, Any]) -> Dict[str, Any]:
        """Use Case 3: Route to RiskAndFraudAgent to analyze single transaction."""
        txn_id = entities.get("transaction_id")
        if not txn_id:
            # Fallback: check most recent transaction for current customer
            cust_id = entities["customer_id"]
            recent = self.banking_agent.get_recent_transactions(cust_id, limit=1)
            if recent["status"] == "success" and recent["data"]["transactions"]:
                txn_id = recent["data"]["transactions"][0]["transaction_id"]
                trace["reasoning_notes"].append(
                    f"No specific transaction ID specified; defaulting to customer's most recent transaction '{txn_id}'."
                )
            else:
                trace["final_response"] = "Please provide a valid transaction ID (e.g., 'Check transaction TXN1005')."
                return {"success": False, "response": trace["final_response"], "trace": trace, "data": None}

        trace["agents_invoked"].append(self.fraud_agent.NAME)
        trace["reasoning_notes"].append(
            f"Routing to {self.fraud_agent.NAME} to analyze risk factors and ML anomaly probability for '{txn_id}'."
        )
        
        tool_call = {
            "agent": self.fraud_agent.NAME,
            "tool": "assess_transaction_risk",
            "parameters": {"transaction_id": txn_id},
            "status": "executing"
        }
        res = self.fraud_agent.analyze_transaction(txn_id)
        tool_call["status"] = res["status"]
        if res["status"] == "success":
            tool_call["output_summary"] = (
                f"Risk: {res['data']['risk_level']} (Score: {res['data']['risk_score']}/100, ML: {res['data']['ml_fraud_probability']*100:.1f}%)"
            )
        else:
            tool_call["output_summary"] = res["message"]
        trace["tool_calls"].append(tool_call)
        
        trace["final_response"] = res["message"]
        return {
            "success": res["status"] == "success",
            "response": res["message"],
            "trace": trace,
            "data": res.get("data")
        }

    def _handle_loan_evaluation(self, entities: Dict[str, Any], trace: Dict[str, Any]) -> Dict[str, Any]:
        """Use Case 4: Route to CreditAndLoanAgent to evaluate loan eligibility."""
        cust_id = entities["customer_id"]
        req_amt = entities.get("requested_amount", 10000.0)
        
        trace["agents_invoked"].append(self.loan_agent.NAME)
        trace["reasoning_notes"].append(
            f"Routing to {self.loan_agent.NAME} to evaluate debt-to-income and credit benchmarks for customer '{cust_id}' (Amount: ${req_amt:,.2f})."
        )
        
        tool_call = {
            "agent": self.loan_agent.NAME,
            "tool": "evaluate_loan_eligibility",
            "parameters": {"customer_id": cust_id, "requested_amount": req_amt},
            "status": "executing"
        }
        res = self.loan_agent.evaluate_loan(cust_id, requested_amount=req_amt)
        tool_call["status"] = res["status"]
        if res["status"] == "success":
            tool_call["output_summary"] = f"Result: {res['data']['status']} (Score: {res['data']['credit_score']}, DTI: {res['data']['dti_ratio_pct']}%)"
        else:
            tool_call["output_summary"] = res["message"]
        trace["tool_calls"].append(tool_call)
        
        trace["final_response"] = res["message"]
        return {
            "success": res["status"] == "success",
            "response": res["message"],
            "trace": trace,
            "data": res.get("data")
        }

    def _handle_multi_agent_audit(self, query: str, entities: Dict[str, Any], trace: Dict[str, Any]) -> Dict[str, Any]:
        """Use Case 5: Multi-Agent Collaboration Workflow.
        
        Supervisor coordinates between:
        1. CustomerBankingAgent -> Fetches customer's recent transactions.
        2. RiskAndFraudAgent -> Scans and evaluates each retrieved transaction.
        3. Supervisor synthesizes combined audit report.
        """
        cust_id = entities["customer_id"]
        limit = entities.get("limit", 5)
        
        # Step 1: CustomerBankingAgent retrieves transactions
        trace["agents_invoked"].append(self.banking_agent.NAME)
        trace["reasoning_notes"].append(
            f"Step 1: Invoking {self.banking_agent.NAME} to retrieve recent transactions for '{cust_id}'."
        )
        
        step1_call = {
            "agent": self.banking_agent.NAME,
            "tool": "get_recent_transactions",
            "parameters": {"customer_id": cust_id, "limit": limit},
            "status": "executing"
        }
        txns_res = self.banking_agent.get_recent_transactions(cust_id, limit=limit)
        step1_call["status"] = txns_res["status"]
        
        if txns_res["status"] != "success":
            step1_call["output_summary"] = "Failed to retrieve transactions"
            trace["tool_calls"].append(step1_call)
            trace["final_response"] = f"Multi-agent review aborted: {txns_res['message']}"
            return {"success": False, "response": trace["final_response"], "trace": trace, "data": None}
            
        transactions = txns_res["data"]["transactions"]
        step1_call["output_summary"] = f"Retrieved {len(transactions)} transaction records"
        trace["tool_calls"].append(step1_call)
        
        # Step 2: RiskAndFraudAgent evaluates retrieved transactions
        trace["agents_invoked"].append(self.fraud_agent.NAME)
        trace["reasoning_notes"].append(
            f"Step 2: Passing {len(transactions)} retrieved transaction(s) to {self.fraud_agent.NAME} for multi-factor fraud analysis."
        )
        
        analyzed_records = []
        flagged_records = []
        
        for t in transactions:
            t_id = t["transaction_id"]
            risk_call = {
                "agent": self.fraud_agent.NAME,
                "tool": "assess_transaction_risk",
                "parameters": {"transaction_id": t_id},
                "status": "executing"
            }
            analysis = self.fraud_agent.analyze_transaction(t_id)
            risk_call["status"] = analysis["status"]
            
            if analysis["status"] == "success":
                a_data = analysis["data"]
                analyzed_records.append(a_data)
                risk_call["output_summary"] = f"Risk: {a_data['risk_level']} ({a_data['risk_score']}/100)"
                if a_data["risk_level"] in ["MEDIUM", "HIGH"]:
                    flagged_records.append(a_data)
            else:
                risk_call["output_summary"] = "Analysis error"
                
            trace["tool_calls"].append(risk_call)

        # Step 3: Synthesis of combined multi-agent findings
        trace["reasoning_notes"].append(
            f"Step 3: {self.NAME} synthesizing unified report from {len(analyzed_records)} analyzed transactions ({len(flagged_records)} flagged)."
        )
        
        total_count = len(analyzed_records)
        flagged_count = len(flagged_records)
        
        if flagged_count > 0:
            flagged_bullets = []
            for f in flagged_records:
                flagged_bullets.append(
                    f"- **{f['transaction_id']}** (${f['amount']:,.2f} at *{f['merchant']}*): "
                    f"**{f['risk_level']} RISK** (Score: {f['risk_score']}/100, ML: {f['ml_fraud_probability']*100:.1f}%). "
                    f"Action: *{f['recommended_action']}*"
                )
            flagged_text = "\n".join(flagged_bullets)
            
            final_text = (
                f"### Multi-Agent Audit Report for Customer `{cust_id}`\n\n"
                f"The **Customer Banking Agent** and **Risk & Fraud Detection Agent** completed a joint audit of **{total_count}** recent transactions:\n\n"
                f"⚠️ **{flagged_count} Suspicious Transaction(s) Identified**:\n"
                f"{flagged_text}\n\n"
                f"The remaining **{total_count - flagged_count}** transaction(s) were cleared with **LOW RISK** ratings."
            )
        else:
            final_text = (
                f"### Multi-Agent Audit Report for Customer `{cust_id}`\n\n"
                f"The **Customer Banking Agent** and **Risk & Fraud Detection Agent** completed a joint audit of **{total_count}** recent transactions.\n\n"
                f"✅ **All {total_count} transactions verified clean** with **LOW RISK** ratings. No anomalous velocity, merchant, or geolocation risks were detected."
            )
            
        trace["final_response"] = final_text
        combined_payload = {
            "customer_id": cust_id,
            "total_audited": total_count,
            "total_flagged": flagged_count,
            "analyzed_transactions": analyzed_records,
            "flagged_transactions": flagged_records
        }
        
        return {
            "success": True,
            "response": final_text,
            "trace": trace,
            "data": combined_payload
        }

    def _handle_customer_profile(self, entities: Dict[str, Any], trace: Dict[str, Any]) -> Dict[str, Any]:
        """Route to CustomerBankingAgent for customer profile."""
        cust_id = entities["customer_id"]
        trace["agents_invoked"].append(self.banking_agent.NAME)
        trace["reasoning_notes"].append(f"Routing to {self.banking_agent.NAME} for profile inquiry on '{cust_id}'.")
        
        tool_call = {
            "agent": self.banking_agent.NAME,
            "tool": "get_customer_profile",
            "parameters": {"customer_id": cust_id},
            "status": "executing"
        }
        res = self.banking_agent.get_customer_profile(cust_id)
        tool_call["status"] = res["status"]
        tool_call["output_summary"] = (
            f"Profile: {res['data']['customer']['full_name']}" if res["status"] == "success" else res["message"]
        )
        trace["tool_calls"].append(tool_call)
        trace["final_response"] = res["message"]
        
        return {
            "success": res["status"] == "success",
            "response": res["message"],
            "trace": trace,
            "data": res.get("data")
        }

    def _handle_unknown_intent(self, user_query: str, trace: Dict[str, Any]) -> Dict[str, Any]:
        """Safely handle unsupported queries without invoking tools or hallucinating."""
        trace["reasoning_notes"].append(
            "Query did not match supported banking intents. Safe refusal triggered to avoid hallucination."
        )
        
        safe_response = (
            "I could not determine a supported banking action for your request: "
            f"*\"{user_query}\"*\n\n"
            "As an intelligent banking assistant, I can help you with:\n"
            "1. **Account Balances**: *'What is my account balance?'*\n"
            "2. **Transaction History**: *'Show my last 5 transactions.'*\n"
            "3. **Fraud & Risk Analysis**: *'Check transaction TXN1005 for suspicious activity.'*\n"
            "4. **Loan Eligibility**: *'Am I eligible for a $15,000 personal loan?'*\n"
            "5. **Multi-Agent Audit**: *'Review my recent transactions and identify suspicious ones.'*"
        )
        
        trace["final_response"] = safe_response
        return {
            "success": False,
            "response": safe_response,
            "trace": trace,
            "data": None
        }
