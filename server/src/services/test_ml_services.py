import os 
import sys
from ml_services import loan_approve
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.append(src_dir)

# الآن نستدعيها باسمها المباشر بدون نقاط
from database import LoanStatus

# ==========================================
# 1. The Ideal User (High income, low debt, reasonable loan)
# Expected: status = 'approved', value = 5000.0
# ==========================================
good_user = {
    "int_rate": 7.5,
    "dti": 10.5,
    "installment": 150.0,
    "annual_inc": 85000.0,
    "revol_util": 20.5,
    "avg_cur_bal": 4500.0,
    "revol_bal": 4000.0,
    "bc_open_to_buy": 15000.0,
    "tot_cur_bal": 85000.0,
    "mo_sin_old_rev_tl_op": 120.0,
    "loan_amnt": 5000.0,
    "bc_util": 25.4,
    "total_bc_limit": 20000.0,
    "total_bal_ex_mort": 25000.0,
    "total_rev_hi_lim": 30000.0
}

# ==========================================
# 2. The High-Risk User (Low income, massive debt, bad history)
# Expected: status = 'rejected', value = None
# ==========================================
bad_user = {
    "int_rate": 24.99,
    "dti": 38.5,
    "installment": 900.0,
    "annual_inc": 25000.0,
    "revol_util": 98.5,
    "avg_cur_bal": 500.0,
    "revol_bal": 20000.0,
    "bc_open_to_buy": 50.0,
    "tot_cur_bal": 15000.0,
    "mo_sin_old_rev_tl_op": 24.0,
    "loan_amnt": 35000.0,
    "bc_util": 99.4,
    "total_bc_limit": 2050.0,
    "total_bal_ex_mort": 35000.0,
    "total_rev_hi_lim": 2100.0
}

# ==========================================
# 3. The Greedy User (Clean record, but asks for way too much)
# Expected: status = 'rejected', value = [Max Safe Amount]
# ==========================================
greedy_user = {
    "int_rate": 10.99,
    "dti": 12.0,
    "installment": 1200.0,
    "annual_inc": 45000.0,
    "revol_util": 30.5,
    "avg_cur_bal": 2000.0,
    "revol_bal": 3000.0,
    "bc_open_to_buy": 10000.0,
    "tot_cur_bal": 25000.0,
    "mo_sin_old_rev_tl_op": 80.0,
    "loan_amnt": 40000.0,
    "bc_util": 20.4,
    "total_bc_limit": 15000.0,
    "total_bal_ex_mort": 10000.0,
    "total_rev_hi_lim": 20000.0
}

# ==========================================
# 4. The Wealthy but Reckless User (Huge salary, bad credit behavior)
# Expected: status = 'rejected', value = None (or 0)
# ==========================================
high_income_bad_history_user = {
    "int_rate": 25.0,
    "dti": 39.0,
    "installment": 1500.0,
    "annual_inc": 150000.0,
    "revol_util": 95.0,
    "avg_cur_bal": 200.0,
    "revol_bal": 50000.0,
    "bc_open_to_buy": 100.0,
    "tot_cur_bal": 55000.0,
    "mo_sin_old_rev_tl_op": 30.0,
    "loan_amnt": 35000.0,
    "bc_util": 98.0,
    "total_bc_limit": 5000.0,
    "total_bal_ex_mort": 60000.0,
    "total_rev_hi_lim": 55000.0
}

# ==========================================
# 5. The Modest User (Average income, requests a tiny loan)
# Expected: status = 'approved', value = 1000.0
# ==========================================
small_loan_user = {
    "int_rate": 6.5,
    "dti": 8.0,
    "installment": 35.0,
    "annual_inc": 55000.0,
    "revol_util": 15.0,
    "avg_cur_bal": 3000.0,
    "revol_bal": 1500.0,
    "bc_open_to_buy": 8000.0,
    "tot_cur_bal": 35000.0,
    "mo_sin_old_rev_tl_op": 150.0,
    "loan_amnt": 1000.0,
    "bc_util": 10.0,
    "total_bc_limit": 10000.0,
    "total_bal_ex_mort": 15000.0,
    "total_rev_hi_lim": 15000.0
}


# ==========================================
# Pytest Unit Tests
# ==========================================

def test_approve_true_requested():
    result = loan_approve(good_user)
    assert result['status'] == LoanStatus.APPROVED
    assert result['value'] == good_user['loan_amnt']

def test_rejected_false_0():
    result = loan_approve(bad_user)
    assert result['status'] == LoanStatus.REJECTED
    # Check for both None and 0 to accommodate the specific conditions in the code
    assert result['value'] in [None, 0] 

def test_rejected_true_max():
    result = loan_approve(greedy_user)
    assert result['status'] == LoanStatus.REJECTED
    assert result['value'] is not None
    assert result['value'] > 0
    assert result['value'] < greedy_user["loan_amnt"]

def test_high_income_bad_history_rejected():
    result = loan_approve(high_income_bad_history_user)
    assert result['status'] == LoanStatus.REJECTED
    assert result['value'] in [None, 0]

def test_small_loan_approved():
    result = loan_approve(small_loan_user)
    assert result['status'] == LoanStatus.APPROVED
    assert result['value'] == small_loan_user['loan_amnt']