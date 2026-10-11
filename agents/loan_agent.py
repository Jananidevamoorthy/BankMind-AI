"""Credit and Loan Agent for BankMind AI.

Specialized agent responsible for:
- Evaluating customer financial metrics (Income, Debt, Credit Score)
- Applying transparent, configurable loan underwriting criteria
- Calculating maximum preliminary borrowing capacity and estimated APR
- Providing comprehensive explainability for approval or denial decisions
- Appending required simulation disclaimers
"""

from typing import Dict, Any, Optional
from tools.banking_api import evaluate_loan_eligibility


class CreditAndLoanAgent:
    """Specialized agent managing credit evaluation, debt-to-income analysis, and loan eligibility."""
    
    NAME = "CreditAndLoanAgent"
    DESCRIPTION = "Evaluates personal loan eligibility, debt-to-income ratios, and credit tier limits."
    
    def __init__(self):
        pass

    def evaluate_loan(self, customer_id: str, requested_amount: float = 10000.0) -> Dict[str, Any]:
        """Perform preliminary loan eligibility evaluation for a customer.
        
        Args:
            customer_id: The customer identifier.
            requested_amount: Loan principal requested (default: $10,000).
            
        Returns:
            Structured decision report with transparent rules breakdown and narrative.
        """
        api_res = evaluate_loan_eligibility(customer_id, requested_amount=requested_amount)
        if not api_res.get("success", False):
            return {
                "agent": self.NAME,
                "status": "error",
                "message": api_res.get("error", f"Could not evaluate loan for customer '{customer_id}'."),
                "data": None
            }
            
        is_eligible = api_res["is_eligible"]
        status = api_res["status"]
        name = api_res["customer_name"]
        score = api_res["credit_score"]
        tier = api_res["credit_tier"]
        income = api_res["monthly_income"]
        debt = api_res["monthly_debt"]
        dti = api_res["dti_ratio_pct"]
        reasons = api_res["reasons"]
        
        if is_eligible:
            max_offer = api_res["max_loan_offer"]
            apr = api_res["estimated_apr_pct"]
            narrative = (
                f"### Preliminary Loan Assessment: **{status}**\n\n"
                f"Applicant **{name}** (`{customer_id}`) meets all required underwriting benchmarks:\n"
                f"- **Credit Profile**: Score of **{score}** ({tier} Tier)\n"
                f"- **Income Verification**: **${income:,.2f}/mo** (Monthly Debt: ${debt:,.2f})\n"
                f"- **Debt-to-Income (DTI)**: **{dti}%** (Underwriting Ceiling: $\\le 45\\%$)\n"
                f"- **Maximum Preliminary Loan Offer**: **${max_offer:,.2f}**\n"
                f"- **Estimated Interest Rate (APR)**: **{apr:.2f}%**\n\n"
                f"**Assessment Summary**: {reasons[0]}\n\n"
                f"> *{api_res['disclaimer']}*"
            )
        else:
            narrative = (
                f"### Preliminary Loan Assessment: **{status}**\n\n"
                f"Applicant **{name}** (`{customer_id}`) does not currently meet underwriting benchmarks for the requested amount:\n"
                f"- **Credit Profile**: Score of **{score}** ({tier} Tier)\n"
                f"- **Income**: **${income:,.2f}/mo** | **Monthly Debt**: **${debt:,.2f}**\n"
                f"- **Debt-to-Income (DTI)**: **{dti}%**\n\n"
                f"**Factors Leading to Denial**:\n" +
                "\n".join([f"- {r}" for r in reasons]) +
                f"\n\n> *{api_res['disclaimer']}*"
            )
            
        return {
            "agent": self.NAME,
            "status": "success",
            "message": narrative,
            "data": api_res
        }
