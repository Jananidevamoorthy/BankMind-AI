"""Customer Banking Agent for BankMind AI.

Specialized agent responsible for:
- Retrieving customer profile information
- Checking account balances
- Fetching recent transactions
- Searching individual transactions by ID
"""

from typing import Dict, Any, Optional
from tools.banking_api import (
    get_customer,
    get_account_balance,
    get_recent_transactions,
    get_transaction
)


class CustomerBankingAgent:
    """Specialized agent managing all standard customer account operations."""
    
    NAME = "CustomerBankingAgent"
    DESCRIPTION = "Handles customer profile lookups, account balance inquiries, and transaction history."
    
    def __init__(self):
        pass

    def get_balance(self, customer_id: str) -> Dict[str, Any]:
        """Fetch account balance for the given customer ID.
        
        Returns:
            Dictionary containing agent response status, human-readable narrative,
            and structured account balance data.
        """
        api_res = get_account_balance(customer_id)
        if not api_res.get("success", False):
            return {
                "agent": self.NAME,
                "status": "error",
                "message": api_res.get("error", f"Could not retrieve balance for customer '{customer_id}'."),
                "data": None
            }
            
        bal = api_res["account_balance"]
        curr = api_res["currency"]
        name = api_res["full_name"]
        acc_num = api_res["account_number"]
        acc_type = api_res["account_type"]
        
        narrative = (
            f"Account balance for **{name}** ({acc_type} Account `{acc_num}`): "
            f"**${bal:,.2f} {curr}** as of {api_res['as_of']}."
        )
        
        return {
            "agent": self.NAME,
            "status": "success",
            "message": narrative,
            "data": api_res
        }

    def get_recent_transactions(self, customer_id: str, limit: int = 5) -> Dict[str, Any]:
        """Fetch recent transaction history for the given customer.
        
        Returns:
            Dictionary containing transaction records list and summary narrative.
        """
        api_res = get_recent_transactions(customer_id, limit=limit)
        if not api_res.get("success", False):
            return {
                "agent": self.NAME,
                "status": "error",
                "message": api_res.get("error", f"Could not retrieve transactions for customer '{customer_id}'."),
                "data": None
            }
            
        txns = api_res.get("transactions", [])
        total = len(txns)
        
        if total == 0:
            narrative = f"No recent transactions found for customer ID `{customer_id}`."
        else:
            narrative = (
                f"Retrieved **{total}** most recent transaction(s) for customer `{customer_id}`. "
                f"Most recent was **${txns[0]['amount']:,.2f}** at **{txns[0]['merchant']}** on {txns[0]['timestamp']}."
            )
            
        return {
            "agent": self.NAME,
            "status": "success",
            "message": narrative,
            "data": api_res
        }

    def get_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """Retrieve full details for a specific transaction ID."""
        api_res = get_transaction(transaction_id)
        if not api_res.get("success", False):
            return {
                "agent": self.NAME,
                "status": "error",
                "message": api_res.get("error", f"Transaction '{transaction_id}' was not found."),
                "data": None
            }
            
        t = api_res["transaction"]
        narrative = (
            f"Transaction **{t['transaction_id']}**: **${t['amount']:,.2f}** at **{t['merchant']}** "
            f"({t['category']}, via {t['channel']}) on {t['timestamp']}. Status: `{t['status']}`."
        )
        
        return {
            "agent": self.NAME,
            "status": "success",
            "message": narrative,
            "data": api_res
        }

    def get_customer_profile(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve customer demographic and financial profile."""
        api_res = get_customer(customer_id)
        if not api_res.get("success", False):
            return {
                "agent": self.NAME,
                "status": "error",
                "message": api_res.get("error", f"Customer '{customer_id}' not found."),
                "data": None
            }
            
        c = api_res["customer"]
        narrative = (
            f"Customer **{c['full_name']}** (`{c['customer_id']}`): {c['employment_status']}, "
            f"Monthly Income: **${float(c['monthly_income']):,.2f}**, Credit Score: **{c['credit_score']}**."
        )
        return {
            "agent": self.NAME,
            "status": "success",
            "message": narrative,
            "data": api_res
        }
