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


def loan_approve(user_input):
    df = pd.DataFrame([user_input])
    initial_approve = False

    ### for loan approve (rf model):
    rf_loan_status = rf(df)
    if rf_loan_status == 0:
        initial_approve = True

    ### for loan amount validation (mlr model):
    predicted_loan = mlr(df)
    max_predicted = max(0.0, float(predicted_loan))
    requested_loan = user_input["loan_amnt"]

    ### conditions

    if initial_approve:
        if requested_loan > max_predicted:
            if max_predicted == 0.0:
                return {"status": LoanStatus.REJECTED, "value": 0}

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
            return {"status": LoanStatus.APPROVED, "value": requested_loan}
    else:
        if max_predicted == 0.0:
            return {"status": LoanStatus.REJECTED, "value": None}
        df_new_rf = df.copy()
        df_new_rf["loan_amnt"] = max_predicted
        new_rf_loan_status = rf(df_new_rf)
        if new_rf_loan_status == 0:
            return {"status": LoanStatus.REJECTED, "value": round(max_predicted, 2)}
        else:
            return {"status": LoanStatus.REJECTED, "value": None}


def rf(user_input):
    x_rf = user_input[scaler_rf.feature_names_in_]
    x_rf_scaled = scaler_rf.transform(x_rf)
    rf_loan_status = rf_model.predict(x_rf_scaled)[0]
    return rf_loan_status


def mlr(user_input):

    x_mlr = user_input.drop(columns="loan_amnt")
    x_mlr = x_mlr[scaler_mlr.feature_names_in_]
    x_mlr_scaled = scaler_mlr.transform(x_mlr)

    predicted_loan = mlr_model.predict(x_mlr_scaled)[0]
    return predicted_loan
