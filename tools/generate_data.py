"""Deterministic Synthetic Dataset Generator for BankMind AI.

Generates realistic, reproducible customer and transaction data with specific
fraud patterns and diverse credit profiles for demonstration.
"""

from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def generate_datasets():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Synthetic Customers
    customers = [
        {
            "customer_id": "CUST1001",
            "full_name": "Sarah Jenkins",
            "account_number": "ACC-449102",
            "account_type": "Checking",
            "account_balance": 14850.50,
            "currency": "USD",
            "monthly_income": 7500.00,
            "monthly_debt": 1500.00,
            "credit_score": 760,
            "employment_status": "Employed",
            "email": "sarah.jenkins@example.com",
            "home_location": "New York, USA",
            "created_at": "2023-01-15"
        },
        {
            "customer_id": "CUST1002",
            "full_name": "Michael Chang",
            "account_number": "ACC-778219",
            "account_type": "Savings",
            "account_balance": 4200.75,
            "currency": "USD",
            "monthly_income": 5200.00,
            "monthly_debt": 2100.00,
            "credit_score": 680,
            "employment_status": "Employed",
            "email": "michael.chang@example.com",
            "home_location": "San Francisco, USA",
            "created_at": "2023-04-22"
        },
        {
            "customer_id": "CUST1003",
            "full_name": "Elena Rostova",
            "account_number": "ACC-120483",
            "account_type": "Checking",
            "account_balance": 850.20,
            "currency": "USD",
            "monthly_income": 2400.00,
            "monthly_debt": 1800.00,
            "credit_score": 590,
            "employment_status": "Part-Time",
            "email": "elena.rostova@example.com",
            "home_location": "Chicago, USA",
            "created_at": "2023-08-10"
        },
        {
            "customer_id": "CUST1004",
            "full_name": "David Kim",
            "account_number": "ACC-992104",
            "account_type": "Premium Checking",
            "account_balance": 48200.00,
            "currency": "USD",
            "monthly_income": 12500.00,
            "monthly_debt": 2200.00,
            "credit_score": 810,
            "employment_status": "Self-Employed",
            "email": "david.kim@example.com",
            "home_location": "Seattle, USA",
            "created_at": "2022-11-05"
        },
        {
            "customer_id": "CUST1005",
            "full_name": "Amara Okafor",
            "account_number": "ACC-553281",
            "account_type": "Checking",
            "account_balance": 2900.10,
            "currency": "USD",
            "monthly_income": 3100.00,
            "monthly_debt": 1450.00,
            "credit_score": 640,
            "employment_status": "Employed",
            "email": "amara.okafor@example.com",
            "home_location": "Atlanta, USA",
            "created_at": "2024-02-18"
        }
    ]
    
    customers_df = pd.DataFrame(customers)
    customers_path = DATA_DIR / "customers.csv"
    customers_df.to_csv(customers_path, index=False)
    print(f"Generated {len(customers_df)} customer profiles -> {customers_path}")

    # 2. Synthetic Transactions with Realistic & Flagged Scenarios
    # Reference anchor time: 2026-10-11
    base_time = datetime(2026, 10, 11, 14, 30, 0)
    
    transactions = [
        # --- Sarah Jenkins (CUST1001) Normal & Flagged Transactions ---
        {
            "transaction_id": "TXN1001",
            "customer_id": "CUST1001",
            "timestamp": (base_time - timedelta(days=5, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 45.20,
            "merchant": "Trader Joe's Supermarket",
            "category": "Groceries",
            "location": "New York, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1002",
            "customer_id": "CUST1001",
            "timestamp": (base_time - timedelta(days=4, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 12.50,
            "merchant": "Starbucks Coffee",
            "category": "Dining",
            "location": "New York, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1003",
            "customer_id": "CUST1001",
            "timestamp": (base_time - timedelta(days=3, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 89.99,
            "merchant": "Amazon.com",
            "category": "Retail",
            "location": "Online",
            "channel": "Online",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1004",
            "customer_id": "CUST1001",
            "timestamp": (base_time - timedelta(days=1, hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 115.00,
            "merchant": "Con Edison Utilities",
            "category": "Utilities",
            "location": "New York, USA",
            "channel": "Online",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        # USE CASE 3 DEMO TEST CASE: TXN1005 (High amount + Crypto + Online wire)
        {
            "transaction_id": "TXN1005",
            "customer_id": "CUST1001",
            "timestamp": (base_time - timedelta(hours=3, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 4850.00,
            "merchant": "Apex Crypto Exchange",
            "category": "Cryptocurrency",
            "location": "Online",
            "channel": "Wire Transfer",
            "status": "Flagged",
            "is_suspicious": 1,
            "risk_tag": "high_amount_crypto"
        },
        # Velocity Burst & Geographic Anomaly Test Cases (TXN1006, TXN1007 within 12 mins in different locations)
        {
            "transaction_id": "TXN1006",
            "customer_id": "CUST1001",
            "timestamp": (base_time - timedelta(hours=1, minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 185.00,
            "merchant": "Saks Fifth Avenue",
            "category": "Retail",
            "location": "New York, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1007",
            "customer_id": "CUST1001",
            "timestamp": (base_time - timedelta(hours=1, minutes=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 1250.00,
            "merchant": "Galeries Lafayette Paris",
            "category": "Retail",
            "location": "Paris, France",
            "channel": "POS",
            "status": "Flagged",
            "is_suspicious": 1,
            "risk_tag": "rapid_geo_mismatch"
        },

        # --- Michael Chang (CUST1002) ---
        {
            "transaction_id": "TXN1008",
            "customer_id": "CUST1002",
            "timestamp": (base_time - timedelta(days=6, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 6.75,
            "merchant": "Blue Bottle Coffee",
            "category": "Dining",
            "location": "San Francisco, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1009",
            "customer_id": "CUST1002",
            "timestamp": (base_time - timedelta(days=4, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 78.40,
            "merchant": "Whole Foods Market",
            "category": "Groceries",
            "location": "San Francisco, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1010",
            "customer_id": "CUST1002",
            "timestamp": (base_time - timedelta(days=2, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 3200.00,
            "merchant": "Luxury Watch Boutique Geneva",
            "category": "Luxury Goods",
            "location": "Geneva, Switzerland",
            "channel": "POS",
            "status": "Flagged",
            "is_suspicious": 1,
            "risk_tag": "unusual_foreign_luxury"
        },
        {
            "transaction_id": "TXN1011",
            "customer_id": "CUST1002",
            "timestamp": (base_time - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 25.00,
            "merchant": "Shell Gas Station",
            "category": "Transportation",
            "location": "San Francisco, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },

        # --- Elena Rostova (CUST1003) ---
        {
            "transaction_id": "TXN1012",
            "customer_id": "CUST1003",
            "timestamp": (base_time - timedelta(days=5, hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 18.50,
            "merchant": "Subway Sandwiches",
            "category": "Dining",
            "location": "Chicago, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1013",
            "customer_id": "CUST1003",
            "timestamp": (base_time - timedelta(days=3, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 95.00,
            "merchant": "Aldi Groceries",
            "category": "Groceries",
            "location": "Chicago, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1014",
            "customer_id": "CUST1003",
            "timestamp": (base_time - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 42.00,
            "merchant": "CVS Pharmacy",
            "category": "Healthcare",
            "location": "Chicago, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },

        # --- David Kim (CUST1004) ---
        {
            "transaction_id": "TXN1015",
            "customer_id": "CUST1004",
            "timestamp": (base_time - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 650.00,
            "merchant": "Delta Air Lines",
            "category": "Travel",
            "location": "Seattle, USA",
            "channel": "Online",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1016",
            "customer_id": "CUST1004",
            "timestamp": (base_time - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 340.00,
            "merchant": "Four Seasons Dining",
            "category": "Dining",
            "location": "Seattle, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1017",
            "customer_id": "CUST1004",
            "timestamp": (base_time - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 185.20,
            "merchant": "Nordstrom",
            "category": "Retail",
            "location": "Seattle, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1018",
            "customer_id": "CUST1004",
            "timestamp": (base_time - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 8500.00,
            "merchant": "Global Offshore Wire Service",
            "category": "Wire Transfer",
            "location": "Panama City, Panama",
            "channel": "Wire Transfer",
            "status": "Flagged",
            "is_suspicious": 1,
            "risk_tag": "high_amount_offshore"
        },

        # --- Amara Okafor (CUST1005) ---
        {
            "transaction_id": "TXN1019",
            "customer_id": "CUST1005",
            "timestamp": (base_time - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 62.10,
            "merchant": "Publix Supermarket",
            "category": "Groceries",
            "location": "Atlanta, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1020",
            "customer_id": "CUST1005",
            "timestamp": (base_time - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 35.00,
            "merchant": "Chevron Gas",
            "category": "Transportation",
            "location": "Atlanta, USA",
            "channel": "POS",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        },
        {
            "transaction_id": "TXN1021",
            "customer_id": "CUST1005",
            "timestamp": (base_time - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 19.99,
            "merchant": "Netflix Subscription",
            "category": "Entertainment",
            "location": "Online",
            "channel": "Online",
            "status": "Completed",
            "is_suspicious": 0,
            "risk_tag": "normal"
        }
    ]

    transactions_df = pd.DataFrame(transactions)
    transactions_path = DATA_DIR / "transactions.csv"
    transactions_df.to_csv(transactions_path, index=False)
    print(f"Generated {len(transactions_df)} transaction records -> {transactions_path}")

if __name__ == "__main__":
    generate_datasets()
