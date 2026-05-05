import joblib
import pandas as pd
from pathlib import Path
from database import LoanStatus

SAVED_MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "saved_models"


def loan_approve(user_input):
    df = pd.DataFrame([user_input])
    initial_approve = False

     ### for loan approve (rf model):

    rf_model = joblib.load(SAVED_MODELS_DIR / "rf_model.pkl")
    scaler_rf = joblib.load(SAVED_MODELS_DIR / "scaler_rf.pkl")

    x_rf_scaled = scaler_rf.transform(df)
    predicted_loan = rf_model.predict(x_rf_scaled)
    if predicted_loan == 1:
        initial_approve = True
    else:
        return LoanStatus.REJECTED

    ### for loan amount validation (mlr model):
    if initial_approve:
        requested_loan = user_input["loan_amnt"]

        mlr_model = joblib.load(SAVED_MODELS_DIR / "mlr_model.pkl")
        scaler_mlr = joblib.load(SAVED_MODELS_DIR / "scaler_mlr.pkl")

        
        x_mlr = df.drop(columns="loan_amnt")
        x_mlr_scaled = scaler_mlr.transform(x_mlr)

        predicted_loan = mlr_model.predict(x_mlr_scaled)[0]
        max_predicted = max(0.0, float(predicted_loan))

        if requested_loan > predicted_loan:
            if max_predicted ==0.0:
                return LoanStatus.REJECTED
            else:
                return LoanStatus.REJECTED, predicted_loan
        else:
            return LoanStatus.APPROVED


   
