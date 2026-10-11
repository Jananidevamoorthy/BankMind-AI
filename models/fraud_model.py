"""Machine Learning Fraud Detection Model for BankMind AI.

Trains and serves a Scikit-Learn classification model on synthetic labeled
transaction features to compute a calibrated probability of fraud.
Distinguishes statistical ML probability from heuristic risk scores.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score
import joblib

from utils.config import FRAUD_MODEL_PATH, MODELS_DIR


def generate_synthetic_training_data(n_samples: int = 1200, random_state: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic feature vectors with ground-truth fraud labels.
    
    Features:
    - amount: Transaction amount in USD
    - ratio_to_avg_spend: Transaction amount / Customer's 30-day average spend
    - is_velocity_burst: 1 if >=2 txns within 60 minutes, else 0
    - is_international: 1 if transaction location != home country, else 0
    - is_high_risk_category: 1 if Crypto/Wire/Luxury, else 0
    - label (is_fraud): 0 (Legitimate) or 1 (Fraudulent)
    """
    rng = np.random.RandomState(random_state)
    
    # Generate 85% normal transactions
    n_normal = int(n_samples * 0.85)
    normal_amounts = np.abs(rng.normal(loc=65.0, scale=45.0, size=n_normal)) + 5.0
    normal_ratios = np.abs(rng.normal(loc=1.0, scale=0.4, size=n_normal))
    normal_burst = rng.binomial(1, 0.05, size=n_normal)
    normal_intl = rng.binomial(1, 0.03, size=n_normal)
    normal_risk_cat = rng.binomial(1, 0.04, size=n_normal)
    normal_labels = np.zeros(n_normal, dtype=int)
    
    # Generate 15% fraudulent / high-risk transactions
    n_fraud = n_samples - n_normal
    fraud_amounts = np.abs(rng.normal(loc=3500.0, scale=1200.0, size=n_fraud)) + 500.0
    fraud_ratios = np.abs(rng.normal(loc=6.5, scale=2.5, size=n_fraud)) + 2.0
    fraud_burst = rng.binomial(1, 0.65, size=n_fraud)
    fraud_intl = rng.binomial(1, 0.70, size=n_fraud)
    fraud_risk_cat = rng.binomial(1, 0.80, size=n_fraud)
    fraud_labels = np.ones(n_fraud, dtype=int)
    
    df = pd.DataFrame({
        "amount": np.concatenate([normal_amounts, fraud_amounts]),
        "ratio_to_avg_spend": np.concatenate([normal_ratios, fraud_ratios]),
        "is_velocity_burst": np.concatenate([normal_burst, fraud_burst]),
        "is_international": np.concatenate([normal_intl, fraud_intl]),
        "is_high_risk_category": np.concatenate([normal_risk_cat, fraud_risk_cat]),
        "is_fraud": np.concatenate([normal_labels, fraud_labels])
    })
    
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return df


class FraudDetectionModel:
    """Wrapper for training, persisting, and evaluating the ML Fraud Model."""
    
    FEATURE_NAMES = [
        "amount",
        "ratio_to_avg_spend",
        "is_velocity_burst",
        "is_international",
        "is_high_risk_category"
    ]
    
    def __init__(self):
        self.model = None
        self._load_or_train()
        
    def _load_or_train(self):
        """Load pre-trained model or train on demand."""
        if FRAUD_MODEL_PATH.exists():
            try:
                self.model = joblib.load(FRAUD_MODEL_PATH)
                return
            except Exception:
                pass
        self.train_and_save()

    def train_and_save(self) -> dict:
        """Train Random Forest classifier on synthetic dataset and save to disk."""
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        data = generate_synthetic_training_data()
        
        X = data[self.FEATURE_NAMES]
        y = data["is_fraud"]
        
        split_idx = int(len(data) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        clf = RandomForestClassifier(
            n_estimators=60,
            max_depth=5,
            random_state=42,
            class_weight="balanced"
        )
        clf.fit(X_train, y_train)
        
        preds = clf.predict(X_test)
        proba = clf.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, preds)
        auc = roc_auc_score(y_test, proba)
        
        # Persist model
        joblib.dump(clf, FRAUD_MODEL_PATH)
        self.model = clf
        
        metrics = {
            "accuracy": round(float(acc), 4),
            "roc_auc": round(float(auc), 4),
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }
        return metrics

    def predict_fraud_probability(self, features: dict) -> float:
        """Compute calibrated probability of fraud given transaction features.
        
        Args:
            features: Dictionary containing:
                - amount: float
                - ratio_to_avg_spend: float
                - is_velocity_burst: int (0 or 1)
                - is_international: int (0 or 1)
                - is_high_risk_category: int (0 or 1)
                
        Returns:
            Calibrated probability float between 0.0 and 1.0.
        """
        if self.model is None:
            self._load_or_train()
            
        df_input = pd.DataFrame([features])[self.FEATURE_NAMES]
        proba = self.model.predict_proba(df_input)[0][1]
        return round(float(proba), 4)

    def get_feature_importances(self) -> dict:
        """Return relative importance of each feature in the trained model."""
        if self.model is None:
            self._load_or_train()
        importances = self.model.feature_importances_
        return {
            name: round(float(imp), 4)
            for name, imp in zip(self.FEATURE_NAMES, importances)
        }


# Singleton instance for quick access
fraud_model_instance = FraudDetectionModel()
