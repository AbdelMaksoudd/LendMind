import joblib
import pandas as pd
from pathlib import Path
from database import LoanStatus

SAVED_MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "saved_models"


def loan_approve(user_input):
    requested_loan = user_input["loan_amnt"]

    mlr_model = joblib.load(SAVED_MODELS_DIR / "mlr_model.pkl")
    scaler_mlr = joblib.load(SAVED_MODELS_DIR / "scaler_mlr.pkl")

    df = pd.DataFrame([user_input])
    x_mlr = df.drop(columns="loan_amnt")
    x_mlr_scaled = scaler_mlr.transform(x_mlr)

    predicted_loan = mlr_model.predict(x_mlr_scaled)

    if requested_loan > predicted_loan[0]:
        return LoanStatus.REJECTED, predicted_loan[0]

    return LoanStatus.APPROVED, predicted_loan[0]
