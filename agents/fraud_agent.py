"""Risk and Fraud Detection Agent for BankMind AI.

Specialized agent responsible for:
- Evaluating transaction risks using explainable heuristics and ML model
- Computing heuristic risk score (0-100) vs calibrated ML fraud probability
- Classifying risk level (LOW, MEDIUM, HIGH)
- Breaking down contributing risk factors
- Recommending review actions (flagging for human analyst, not automatic blocks)
"""

from typing import Dict, Any, List, Optional
from tools.banking_api import (
    assess_transaction_risk,
    get_transaction,
    get_recent_transactions,
    get_customer,
    _load_transactions_df
)
from models.fraud_model import fraud_model_instance


class RiskAndFraudAgent:
    """Specialized agent managing fraud detection, risk scoring, and explainability."""
    
    NAME = "RiskAndFraudAgent"
    DESCRIPTION = "Performs multi-factor risk analysis, ML fraud scoring, and explainable flag recommendations."
    
    def __init__(self):
        self.ml_model = fraud_model_instance

    def analyze_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Perform comprehensive risk evaluation on an individual transaction.
        
        Combines rule-based heuristic scoring with Scikit-Learn ML probability.
        
        Args:
            transaction_id: The unique transaction ID (e.g., 'TXN1005').
            
        Returns:
            Structured risk assessment report with explainable breakdown.
        """
        # 1. Obtain rule-based heuristic risk evaluation from banking core
        heuristic_res = assess_transaction_risk(transaction_id)
        if not heuristic_res.get("success", False):
            return {
                "agent": self.NAME,
                "status": "error",
                "message": heuristic_res.get("error", f"Could not analyze transaction '{transaction_id}'."),
                "data": None
            }
            
        # 2. Extract feature vector for ML model scoring
        txn_res = get_transaction(transaction_id)
        txn = txn_res["transaction"]
        cust_res = get_customer(txn["customer_id"])
        cust = cust_res.get("customer", {})
        
        # Calculate baseline ratio to average customer spend
        df = _load_transactions_df()
        cust_txns = df[df["customer_id"] == txn["customer_id"]]
        avg_spend = cust_txns["amount"].mean() if not cust_txns.empty else 100.0
        ratio_to_avg = float(txn["amount"]) / max(1.0, avg_spend)
        
        # Check velocity burst (>=2 txns within 60 mins)
        is_burst = 1 if any("Rapid transaction frequency" in f for f in heuristic_res["factors"]) else 0
        
        # Check international deviation
        is_intl = 1 if any("Geographic mismatch" in f for f in heuristic_res["factors"]) else 0
        
        # Check high-risk merchant category
        is_high_risk_cat = 1 if any("High-risk merchant category" in f for f in heuristic_res["factors"]) else 0
        
        ml_features = {
            "amount": float(txn["amount"]),
            "ratio_to_avg_spend": round(ratio_to_avg, 2),
            "is_velocity_burst": is_burst,
            "is_international": is_intl,
            "is_high_risk_category": is_high_risk_cat
        }
        
        ml_fraud_prob = self.ml_model.predict_fraud_probability(ml_features)
        
        # 3. Assemble composite risk assessment
        score = heuristic_res["risk_score"]
        level = heuristic_res["risk_level"]
        factors = heuristic_res["factors"]
        action = heuristic_res["recommended_action"]
        
        narrative = (
            f"Risk analysis for transaction **{transaction_id}** (${float(txn['amount']):,.2f} at {txn['merchant']}):\n"
            f"- **Classification**: `{level} RISK`\n"
            f"- **Heuristic Risk Score**: **{score}/100**\n"
            f"- **Calibrated ML Fraud Probability**: **{ml_fraud_prob * 100:.1f}%**\n"
            f"- **Recommended Action**: {action}\n"
            f"- **Key Contributing Factors**:\n" +
            "\n".join([f"  * {f}" for f in factors])
        )
        
        composite_data = {
            "transaction_id": transaction_id,
            "customer_id": txn["customer_id"],
            "merchant": txn["merchant"],
            "amount": float(txn["amount"]),
            "risk_score": score,
            "risk_level": level,
            "ml_fraud_probability": ml_fraud_prob,
            "ml_features_evaluated": ml_features,
            "factors": factors,
            "recommended_action": action,
            "flagged_for_review": level in ["MEDIUM", "HIGH"],
            "disclaimer": heuristic_res["disclaimer"]
        }
        
        return {
            "agent": self.NAME,
            "status": "success",
            "message": narrative,
            "data": composite_data
        }

    def scan_recent_transactions(self, customer_id: str, limit: int = 5) -> Dict[str, Any]:
        """Scan customer's recent transactions and identify any suspicious records.
        
        Args:
            customer_id: The customer ID.
            limit: Number of transactions to scan.
            
        Returns:
            Dictionary containing list of analyzed transactions, flagged subset, and summary.
        """
        txns_res = get_recent_transactions(customer_id, limit=limit)
        if not txns_res.get("success", False):
            return {
                "agent": self.NAME,
                "status": "error",
                "message": txns_res.get("error", f"Could not retrieve transactions for customer '{customer_id}'."),
                "data": None
            }
            
        txns = txns_res.get("transactions", [])
        analyzed_list = []
        flagged_list = []
        
        for t in txns:
            analysis = self.analyze_transaction(t["transaction_id"])
            if analysis["status"] == "success":
                t_data = analysis["data"]
                analyzed_list.append(t_data)
                if t_data["risk_level"] in ["MEDIUM", "HIGH"]:
                    flagged_list.append(t_data)
                    
        total_scanned = len(analyzed_list)
        total_flagged = len(flagged_list)
        
        if total_flagged > 0:
            narrative = (
                f"Scanned **{total_scanned}** recent transaction(s) for customer `{customer_id}`. "
                f"**{total_flagged} transaction(s) flagged for review** (Risk Level: MEDIUM or HIGH)."
            )
        else:
            narrative = (
                f"Scanned **{total_scanned}** recent transaction(s) for customer `{customer_id}`. "
                f"**All transactions appear normal (LOW RISK)**."
            )
            
        return {
            "agent": self.NAME,
            "status": "success",
            "message": narrative,
            "data": {
                "customer_id": customer_id,
                "total_scanned": total_scanned,
                "total_flagged": total_flagged,
                "analyzed_transactions": analyzed_list,
                "flagged_transactions": flagged_list
            }
        }
