"""Simulated Banking API Endpoints for BankMind AI.

Provides modular, robust functions mimicking real-world core banking APIs.
Enforces strict input validation, transparent error handling, and separation
between data access and AI orchestration.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
from utils.config import (
    CUSTOMERS_FILE,
    TRANSACTIONS_FILE,
    RISK_THRESHOLD_LOW,
    RISK_THRESHOLD_HIGH,
    MIN_CREDIT_SCORE,
    MAX_DEBT_TO_INCOME_RATIO,
    MIN_MONTHLY_INCOME
)


def _load_customers_df() -> pd.DataFrame:
    """Load and return the customers dataframe from storage."""
    if not CUSTOMERS_FILE.exists():
        raise FileNotFoundError(f"Customer dataset not found at {CUSTOMERS_FILE}")
    return pd.read_csv(CUSTOMERS_FILE)


def _load_transactions_df() -> pd.DataFrame:
    """Load and return the transactions dataframe from storage."""
    if not TRANSACTIONS_FILE.exists():
        raise FileNotFoundError(f"Transaction dataset not found at {TRANSACTIONS_FILE}")
    df = pd.read_csv(TRANSACTIONS_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def get_all_customers() -> List[Dict[str, Any]]:
    """Retrieve all simulated customers for dashboard selectors and lookups."""
    try:
        df = _load_customers_df()
        return df.to_dict(orient="records")
    except Exception as e:
        return []


def get_all_transactions() -> List[Dict[str, Any]]:
    """Retrieve all simulated transactions."""
    try:
        df = _load_transactions_df()
        df["timestamp"] = df["timestamp"].astype(str)
        return df.to_dict(orient="records")
    except Exception as e:
        return []


def get_customer(customer_id: str) -> Dict[str, Any]:
    """Retrieve full customer demographic and profile details.
    
    Args:
        customer_id: The unique customer identifier (e.g., 'CUST1001')
        
    Returns:
        Structured dictionary containing customer record or error information.
    """
    if not customer_id or not isinstance(customer_id, str):
        return {
            "success": False,
            "error": "Invalid input: customer_id must be a non-empty string."
        }
    
    customer_id = customer_id.strip().upper()
    try:
        df = _load_customers_df()
        match = df[df["customer_id"] == customer_id]
        if match.empty:
            return {
                "success": False,
                "error": f"Customer ID '{customer_id}' not found in banking records."
            }
        
        customer_data = match.iloc[0].to_dict()
        return {
            "success": True,
            "customer": customer_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Internal database error while fetching customer: {str(e)}"
        }


def get_account_balance(customer_id: str) -> Dict[str, Any]:
    """Retrieve current account balance and status for a specified customer.
    
    Args:
        customer_id: The unique customer identifier.
        
    Returns:
        Dictionary with balance, currency, account number, and verification status.
    """
    cust_res = get_customer(customer_id)
    if not cust_res["success"]:
        return cust_res
    
    cust = cust_res["customer"]
    return {
        "success": True,
        "customer_id": cust["customer_id"],
        "full_name": cust["full_name"],
        "account_number": cust["account_number"],
        "account_type": cust["account_type"],
        "account_balance": float(cust["account_balance"]),
        "currency": cust["currency"],
        "as_of": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_recent_transactions(customer_id: str, limit: int = 5) -> Dict[str, Any]:
    """Retrieve recent transactions for a customer, ordered from newest to oldest.
    
    Args:
        customer_id: The unique customer identifier.
        limit: Maximum number of transactions to retrieve (default: 5).
        
    Returns:
        Dictionary containing list of transaction records.
    """
    cust_res = get_customer(customer_id)
    if not cust_res["success"]:
        return cust_res
    
    customer_id = customer_id.strip().upper()
    try:
        limit = max(1, int(limit))
    except (ValueError, TypeError):
        limit = 5
        
    try:
        df = _load_transactions_df()
        cust_txns = df[df["customer_id"] == customer_id].sort_values(
            by="timestamp", ascending=False
        )
        
        sliced = cust_txns.head(limit).copy()
        sliced["timestamp"] = sliced["timestamp"].astype(str)
        records = sliced.to_dict(orient="records")
        
        return {
            "success": True,
            "customer_id": customer_id,
            "total_found": len(records),
            "transactions": records
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to retrieve transactions: {str(e)}"
        }


def get_transaction(transaction_id: str) -> Dict[str, Any]:
    """Search and retrieve a single transaction by its unique ID.
    
    Args:
        transaction_id: The transaction ID (e.g., 'TXN1005').
        
    Returns:
        Dictionary containing transaction details or error message.
    """
    if not transaction_id or not isinstance(transaction_id, str):
        return {
            "success": False,
            "error": "Invalid input: transaction_id must be a non-empty string."
        }
        
    transaction_id = transaction_id.strip().upper()
    try:
        df = _load_transactions_df()
        match = df[df["transaction_id"] == transaction_id]
        if match.empty:
            return {
                "success": False,
                "error": f"Transaction '{transaction_id}' not found."
            }
        
        data = match.iloc[0].to_dict()
        data["timestamp"] = str(data["timestamp"])
        return {
            "success": True,
            "transaction": data
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Database error looking up transaction: {str(e)}"
        }


def assess_transaction_risk(transaction_id: str) -> Dict[str, Any]:
    """Execute risk and fraud analysis for a specific transaction.
    
    Applies multi-factor heuristic checks:
    1. Transaction amount deviation relative to customer typical average spend.
    2. Velocity burst (multiple transactions within 60 minutes).
    3. Geographic deviation from customer home location.
    4. Merchant category risk (Cryptocurrency, Wire Transfer, Offshore, Luxury).
    
    Args:
        transaction_id: The transaction identifier.
        
    Returns:
        Structured risk report including numeric score (0-100), classification,
        contributing factors, and recommended action.
    """
    txn_res = get_transaction(transaction_id)
    if not txn_res["success"]:
        return txn_res
    
    txn = txn_res["transaction"]
    customer_id = txn["customer_id"]
    cust_res = get_customer(customer_id)
    cust = cust_res.get("customer", {})
    
    home_location = cust.get("home_location", "Unknown")
    txn_amount = float(txn["amount"])
    txn_category = txn.get("category", "")
    txn_location = txn.get("location", "")
    txn_channel = txn.get("channel", "")
    current_time = pd.to_datetime(txn["timestamp"])
    
    # Analyze historical transactions for this customer to establish baseline
    df = _load_transactions_df()
    cust_txns = df[df["customer_id"] == customer_id]
    
    avg_spend = cust_txns["amount"].mean() if not cust_txns.empty else 100.0
    
    risk_score = 5  # Base baseline score
    factors = []
    
    # 1. Amount Deviation Check
    if txn_amount >= 3000.0:
        points = 35
        risk_score += points
        factors.append(
            f"High monetary amount (${txn_amount:,.2f}) significantly exceeds typical retail threshold (+{points} pts)."
        )
    elif txn_amount > (avg_spend * 3.5):
        points = 25
        risk_score += points
        factors.append(
            f"Amount (${txn_amount:,.2f}) is over 3.5x customer average spend (${avg_spend:,.2f}) (+{points} pts)."
        )
    else:
        factors.append(f"Transaction amount (${txn_amount:,.2f}) is within standard spending pattern (+0 pts).")
        
    # 2. Velocity Burst Check (Transactions within 60 minutes)
    one_hour_window = cust_txns[
        (cust_txns["timestamp"] >= current_time - timedelta(minutes=60)) &
        (cust_txns["timestamp"] <= current_time + timedelta(minutes=60))
    ]
    if len(one_hour_window) >= 2:
        points = 25
        risk_score += points
        factors.append(
            f"Rapid transaction frequency: {len(one_hour_window)} transactions detected within a 60-minute window (+{points} pts)."
        )
        
    # 3. Geographic Anomaly Check
    if home_location != "Unknown" and txn_location != "Online":
        home_country = home_location.split(",")[-1].strip()
        txn_country = txn_location.split(",")[-1].strip()
        if home_country != txn_country:
            points = 25
            risk_score += points
            factors.append(
                f"Geographic mismatch: Physical transaction location ({txn_location}) differs from customer home ({home_location}) (+{points} pts)."
            )
            
    # 4. Merchant Category & Channel Risk Check
    high_risk_categories = {"Cryptocurrency": 30, "Wire Transfer": 25, "Luxury Goods": 20}
    if txn_category in high_risk_categories:
        points = high_risk_categories[txn_category]
        risk_score += points
        factors.append(
            f"High-risk merchant category '{txn_category}' via {txn_channel} (+{points} pts)."
        )
        
    # Cap risk score between 0 and 100
    risk_score = max(0, min(100, risk_score))
    
    # Classification & Action
    if risk_score >= RISK_THRESHOLD_HIGH:
        risk_level = "HIGH"
        recommended_action = "Flag for Fraud Analyst review; place temporary authorization hold on payment."
    elif risk_score >= RISK_THRESHOLD_LOW:
        risk_level = "MEDIUM"
        recommended_action = "Request two-factor SMS/email customer authorization confirmation."
    else:
        risk_level = "LOW"
        recommended_action = "Transaction cleared for automated standard processing."
        
    return {
        "success": True,
        "transaction_id": txn["transaction_id"],
        "customer_id": customer_id,
        "customer_name": cust.get("full_name", "Unknown"),
        "amount": txn_amount,
        "merchant": txn.get("merchant", "Unknown"),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "factors": factors,
        "recommended_action": recommended_action,
        "assessment_type": "Rule-Based Heuristic Evaluation",
        "disclaimer": "SIMULATION NOTICE: This risk score is an educational simulation and does not represent an actual banking block."
    }


def evaluate_loan_eligibility(customer_id: str, requested_amount: float = 10000.0) -> Dict[str, Any]:
    """Assess customer loan eligibility against transparent underwriting criteria.
    
    Evaluation Rules:
    1. Minimum Monthly Income >= $3,000.
    2. Debt-to-Income (DTI) ratio <= 45%.
    3. Credit Score >= 650.
    
    Args:
        customer_id: The unique customer identifier.
        requested_amount: Preliminary loan principal requested (default: $10,000).
        
    Returns:
        Structured assessment containing decision (Approved/Declined), breakdown
        of each rule, estimated interest APR, max loan offer, and simulation notice.
    """
    cust_res = get_customer(customer_id)
    if not cust_res["success"]:
        return cust_res
        
    cust = cust_res["customer"]
    income = float(cust.get("monthly_income", 0.0))
    debt = float(cust.get("monthly_debt", 0.0))
    credit_score = int(cust.get("credit_score", 0))
    
    # Calculate Debt-to-Income (DTI)
    dti_ratio = (debt / income) if income > 0 else 1.0
    dti_percentage = round(dti_ratio * 100, 1)
    
    # Evaluate individual underwriting criteria
    rule_income_pass = income >= MIN_MONTHLY_INCOME
    rule_dti_pass = dti_ratio <= MAX_DEBT_TO_INCOME_RATIO
    rule_credit_pass = credit_score >= MIN_CREDIT_SCORE
    
    rule_evaluations = [
        {
            "criterion": "Minimum Monthly Income",
            "required": f">= ${MIN_MONTHLY_INCOME:,.2f}",
            "actual": f"${income:,.2f}",
            "passed": rule_income_pass
        },
        {
            "criterion": "Debt-to-Income (DTI) Ratio",
            "required": f"<= {int(MAX_DEBT_TO_INCOME_RATIO * 100)}%",
            "actual": f"{dti_percentage}%",
            "passed": rule_dti_pass
        },
        {
            "criterion": "Minimum Credit Score",
            "required": f">= {MIN_CREDIT_SCORE}",
            "actual": str(credit_score),
            "passed": rule_credit_pass
        }
    ]
    
    is_eligible = rule_income_pass and rule_dti_pass and rule_credit_pass
    
    # Detailed reasoning explanations
    reasons = []
    if not rule_income_pass:
        reasons.append(
            f"Monthly income of ${income:,.2f} is below the required ${MIN_MONTHLY_INCOME:,.2f} threshold."
        )
    if not rule_dti_pass:
        reasons.append(
            f"Debt-to-Income ratio ({dti_percentage}%) exceeds the 45.0% maximum allowable ceiling."
        )
    if not rule_credit_pass:
        reasons.append(
            f"Credit score ({credit_score}) does not meet the minimum lending benchmark of {MIN_CREDIT_SCORE}."
        )
        
    if is_eligible:
        reasons.append("Customer satisfies all primary underwriting criteria for unsecured personal lending.")
        
        # Credit Tier & APR Estimate
        if credit_score >= 750:
            credit_tier = "Excellent"
            estimated_apr = 6.49
        elif credit_score >= 700:
            credit_tier = "Good"
            estimated_apr = 8.99
        else:
            credit_tier = "Fair"
            estimated_apr = 11.75
            
        # Max loan capacity based on residual borrowing capacity
        available_monthly_capacity = max(0.0, (income * MAX_DEBT_TO_INCOME_RATIO) - debt)
        max_loan_offer = round(available_monthly_capacity * 36, -2)  # 3-year term estimate
        max_loan_offer = max(5000.0, min(50000.0, max_loan_offer))
    else:
        credit_tier = "Subprime / High Risk" if credit_score < 620 else "Near Prime"
        estimated_apr = None
        max_loan_offer = 0.0

    return {
        "success": True,
        "customer_id": cust["customer_id"],
        "customer_name": cust["full_name"],
        "requested_amount": requested_amount,
        "is_eligible": is_eligible,
        "status": "Approved (Preliminary)" if is_eligible else "Declined (Preliminary)",
        "credit_score": credit_score,
        "credit_tier": credit_tier,
        "monthly_income": income,
        "monthly_debt": debt,
        "dti_ratio_pct": dti_percentage,
        "max_loan_offer": max_loan_offer,
        "estimated_apr_pct": estimated_apr,
        "rules_breakdown": rule_evaluations,
        "reasons": reasons,
        "disclaimer": "SIMULATION NOTICE: This is an educational estimation generated using synthetic criteria. It does not constitute a formal loan offer or credit agreement."
    }
