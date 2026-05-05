import joblib
import pandas as pd
from pathlib import Path
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.append(src_dir)

from database import LoanStatus

SAVED_MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "saved_models"

# load models

rf_model = joblib.load(SAVED_MODELS_DIR / "rf_model.pkl")
scaler_rf = joblib.load(SAVED_MODELS_DIR / "scaler_rf.pkl")
mlr_model = joblib.load(SAVED_MODELS_DIR / "mlr_model.pkl")
scaler_mlr = joblib.load(SAVED_MODELS_DIR / "scaler_mlr.pkl")


def calculate_monthly_installment(loan_amnt, int_rate, loan_term):
    P = loan_amnt
    n = loan_term
    r = int_rate / 12 / 100

    if r == 0:
        return round(P / n, 2)

    return round(P * (r * (1 + r) ** n) / ((1 + r) ** n - 1), 2)


def loan_approve(user_input):
    monthly_installment = calculate_monthly_installment(
        user_input["loan_amnt"], user_input["int_rate"], user_input["loan_term"]
    )
    user_input["installment"] = monthly_installment
    user_input.pop("loan_term", None)

    df = pd.DataFrame([user_input])
    initial_approve = False

    ### for loan approve (rf model):
    x_rf_scaled = scaler_rf.transform(df)
    predicted_loan = rf_model.predict(x_rf_scaled)
    if predicted_loan == 1:
        initial_approve = True

    ### for loan amount validation (mlr model):
    predicted_loan = mlr(df)
    max_predicted = max(0.0, float(predicted_loan))
    requested_loan = user_input["loan_amnt"]

    ### conditions
    if initial_approve:
        requested_loan = user_input["loan_amnt"]

        x_mlr = df.drop(columns="loan_amnt")
        x_mlr_scaled = scaler_mlr.transform(x_mlr)

        predicted_loan = mlr_model.predict(x_mlr_scaled)[0]
        max_predicted = max(0.0, float(predicted_loan))

        if requested_loan > predicted_loan:
            if max_predicted == 0.0:
                return LoanStatus.REJECTED
            else:
                df_new_rf = df.copy()
                df_new_rf["loan_amnt"] = max_predicted
                new_rf_loan_status = rf(df_new_rf)
                if new_rf_loan_status == 0:
                    return {
                        "status": LoanStatus.REJECTED,
                        "value": round(max_predicted, 2),
                    }
                else:
                    return {"status": LoanStatus.REJECTED, "value": None}
        else:
            return LoanStatus.APPROVED
