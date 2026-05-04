from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
import enum

DB_DIR = Path(__file__).resolve().parent.parent / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_DIR / 'loans.db'}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class LoanStatus(str, enum.Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Section 1: Loan Details
    loan_amnt = Column(Float, nullable=False)
    int_rate = Column(Float, nullable=False)

    # Section 2: Financial Profile
    annual_inc = Column(Float, nullable=False)
    dti = Column(Float, nullable=False)

    # Section 3: Credit & Debts
    revol_bal = Column(Float, nullable=False)
    revol_util = Column(Float, nullable=False)
    total_bal_ex_mort = Column(Float, nullable=False)
    bc_util = Column(Float, nullable=False)
    bc_open_to_buy = Column(Float, nullable=False)
    total_bc_limit = Column(Float, nullable=False)

    # Section 4: Banking History
    mo_sin_old_rev_tl_op = Column(Integer, nullable=False)
    mo_sin_old_il_acct = Column(Integer, nullable=False)
    tot_cur_bal = Column(Float, nullable=False)
    avg_cur_bal = Column(Float, nullable=False)
    total_rev_hi_lim = Column(Float, nullable=False)

    status = Column(Enum(LoanStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
