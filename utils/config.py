"""System Configuration and Constants for BankMind AI.

Centralizes file paths, environment variables, demo settings, and risk thresholds.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory and default file paths
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
CUSTOMERS_FILE = DATA_DIR / "customers.csv"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"

# Models directory
MODELS_DIR = BASE_DIR / "models"
FRAUD_MODEL_PATH = MODELS_DIR / "fraud_detector.joblib"

# Simulation / Demo Mode
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Keys (optional; fallback operates automatically if keys are unset)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Risk Threshold Constants
RISK_THRESHOLD_LOW = 30
RISK_THRESHOLD_HIGH = 70

# Loan Assessment Constants
MIN_CREDIT_SCORE = 650
MAX_DEBT_TO_INCOME_RATIO = 0.45
MIN_MONTHLY_INCOME = 3000.0
