import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

def main():
    test = {
  "int_rate": 13.99,
  "dti": 11.56,
  "installment": 246.05,
  "annual_inc": 30000.0,
  "revol_util": 50.5,
  "avg_cur_bal": 1098.0,
  "revol_bal": 1162.0,
  "bc_open_to_buy": 538.0,
  "tot_cur_bal": 5491.0,
  "mo_sin_old_rev_tl_op": 58.0,
  "loan_amnt": 1000000000,
  "bc_util": 68.4,
  "total_bc_limit": 1700.0,
  "total_bal_ex_mort": 5491.0,
  "total_rev_hi_lim": 2300.0
  
}

    print(loan_approve(test))




def loan_approve(user_input):
    requsted_loan = user_input['loan_amnt']

    mlr_model = joblib.load('saved_models/mlr_model.pkl')
    scaler_mlr = joblib.load('saved_models/scaler_mlr.pkl')

    df = pd.DataFrame([user_input])
    x_mlr = df.drop(columns='loan_amnt')
    x_mlr_scaled = scaler_mlr.transform(x_mlr)
    

    predicted_loan = mlr_model.predict(x_mlr_scaled) 

    if requsted_loan > predicted_loan[0]:


        return f'''يمكن تتقبل ويمكن اهزقك تانى يا مهزق {predicted_loan[0]}روح قدم طلب تانى ب {requsted_loan} احا يا فندم انت مش شايف حالك عامل ازاى وجاى تقدم على قرض ب'''
    

    





if __name__ == '__main__':
    main()