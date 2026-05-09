import os 
import sys
from ml_services import loan_approve

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.append(src_dir)

from database import LoanStatus

# ==========================================
# 1. The Ideal User (High income, low debt, reasonable loan)
# Expected: status = 'approved', value = 5000.0
# ==========================================
good_user = {
    "int_rate": 7.5,
    "dti": 10.5,
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
    "total_rev_hi_lim": 30000.0,
    "term_months": 36,  # العميل اختار السداد على 3 سنوات (قياسي)
    
    # الأعمدة المضافة حديثاً
    "mo_sin_old_il_acct": 140.0,  # تاريخ طويل ومستقر لقروض التقسيط
    "total_acc": 20.0,            # عدد حسابات جيد يدل على الخبرة الائتمانية
    "mort_acc": 1.0,              # يمتلك عقار (مؤشر استقرار عالي)
    "num_bc_sats": 5.0,           # يمتلك 5 بطاقات بنكية في حالة جيدة
    "num_bc_tl": 8.0              # إجمالي البطاقات التي تعامل معها
}

# ==========================================
# 2. The High-Risk User (Low income, massive debt, bad history)
# Expected: status = 'rejected', value = None
# ==========================================
bad_user = {
    "int_rate": 24.99,
    "dti": 38.5,
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
    "total_rev_hi_lim": 2100.0,
    "term_months": 60,  # العميل اختار 5 سنوات لتقليل القسط، لكنه ما زال خطراً

    # الأعمدة المضافة حديثاً
    "mo_sin_old_il_acct": 15.0,   # تاريخ حديث جداً (خبرة قليلة)
    "total_acc": 8.0,             # عدد حسابات قليل
    "mort_acc": 0.0,              # لا يمتلك عقار (مخاطرة أعلى)
    "num_bc_sats": 1.0,           # بطاقة واحدة فقط في حالة جيدة (الباقي متأخرات غالباً)
    "num_bc_tl": 6.0              # إجمالي البطاقات
}

# ==========================================
# 3. The Greedy User (Clean record, but asks for way too much)
# Expected: status = 'rejected', value = [Max Safe Amount]
# ==========================================
greedy_user = {
    "int_rate": 10.99,
    "dti": 12.0,
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
    "total_rev_hi_lim": 20000.0,
    "term_months": 24,  # العميل جشع ويريد سداد رقم ضخم في سنتين!

    # الأعمدة المضافة حديثاً
    "mo_sin_old_il_acct": 90.0,   # تاريخ جيد
    "total_acc": 15.0,            # عدد حسابات معقول
    "mort_acc": 0.0,              # لا يمتلك عقار
    "num_bc_sats": 4.0,           # يدير بطاقاته بشكل جيد
    "num_bc_tl": 7.0              
}

# ==========================================
# 4. The Wealthy but Reckless User (Huge salary, bad credit behavior)
# Expected: status = 'rejected', value = None (or 0)
# ==========================================
high_income_bad_history_user = {
    "int_rate": 25.0,
    "dti": 39.0,
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
    "total_rev_hi_lim": 55000.0,
    "term_months": 36,

    # الأعمدة المضافة حديثاً
    "mo_sin_old_il_acct": 40.0,   # تاريخ قصير نسبياً رغم الدخل العالي
    "total_acc": 35.0,            # يفتح حسابات كثيرة بشكل متهور
    "mort_acc": 2.0,              # لديه قروض عقارية تزيد من التزاماته
    "num_bc_sats": 3.0,           # نسبة قليلة من حساباته في حالة مرضية
    "num_bc_tl": 15.0             # تاريخ مليء بالبطاقات
}

# ==========================================
# 5. The Modest User (Average income, requests a tiny loan)
# Expected: status = 'approved', value = 1000.0
# ==========================================
small_loan_user = {
    "int_rate": 6.5,
    "dti": 8.0,
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
    "total_rev_hi_lim": 15000.0,
    "term_months": 12,  # قرض صغير جداً يمكن سداده في سنة واحدة بسهولة

    # الأعمدة المضافة حديثاً
    "mo_sin_old_il_acct": 120.0,  # تاريخ طويل وموثوق
    "total_acc": 12.0,            # عدد حسابات معتدل
    "mort_acc": 1.0,              # مستقر
    "num_bc_sats": 3.0,           
    "num_bc_tl": 5.0              
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
    assert result['value'] in [None, 0] 

def test_rejected_true_max():
    result = loan_approve(greedy_user)
    assert result['status'] == LoanStatus.REJECTED
    assert result['value'] is None or (0 < result['value'] < greedy_user["loan_amnt"])

def test_high_income_bad_history_rejected():
    result = loan_approve(high_income_bad_history_user)
    assert result['status'] == LoanStatus.REJECTED
    assert result['value'] in [None, 0]

def test_small_loan_approved():
    result = loan_approve(small_loan_user)
    assert result['status'] == LoanStatus.APPROVED
    assert result['value'] == small_loan_user['loan_amnt']