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

    requested_loan = float(df["loan_amnt"].iloc[0])
    annual_inc = float(df['annual_inc'].iloc[0])
    interest_rate = float(df['int_rate'].iloc[0]) if 'int_rate' in df.columns else 12.0

    term_months = float(df['term_months'].iloc[0]) if 'term_months' in df.columns else 36.0
    
    df['term_ 60 months'] = 1 if term_months >= 60 else 0

    initial_installment = calculate_installment(requested_loan, interest_rate, term_months)
    df["installment"] = initial_installment
    df["loan_to_income"] = requested_loan / (annual_inc + 1)
    df["monthly_burden"] = initial_installment / ((annual_inc / 12) + 1)    

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


                new_installment = calculate_installment(max_predicted, interest_rate, term_months)
                df_new_rf["installment"] = new_installment
                df_new_rf["loan_to_income"] = max_predicted / (annual_inc + 1)
                df_new_rf["monthly_burden"] = new_installment / ((annual_inc / 12) + 1)
                
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


        new_installment = calculate_installment(max_predicted, interest_rate, term_months)
        df_new_rf["installment"] = new_installment
        df_new_rf["loan_to_income"] = max_predicted / (annual_inc + 1)
        df_new_rf["monthly_burden"] = new_installment / ((annual_inc / 12) + 1)
        
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

    x_mlr = user_input[scaler_mlr.feature_names_in_]
    x_mlr_scaled = scaler_mlr.transform(x_mlr)

    predicted_loan = mlr_model.predict(x_mlr_scaled)[0]
    return predicted_loan


def calculate_installment(amount, annual_rate, months):
    if amount == 0:
        return 0
    r = (annual_rate / 100) / 12
    if r ==0:
         return amount / months
    return amount * (r * (1 + r)**months) / ((1 + r)**months - 1)