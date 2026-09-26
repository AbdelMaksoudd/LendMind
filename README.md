# LendMind

LendMind is an end-to-end loan decision platform. Historical Lending Club data is used to train two models: a Random Forest classifier that estimates credit risk, and a multiple linear regression model that estimates a supportable loan amount. A FastAPI application then collects applicant data, runs those models, stores each decision, and presents results to applicants and administrators.

The application does not issue legally binding credit decisions. It is a demonstration of a data-science pipeline and a small production-style web service.

---

## What the system does

1. An applicant (standard user) signs in and submits a loan application through a web form.
2. The backend engineers derived features (`loan_to_income`, `monthly_burden`, installment, and a 60-month term flag) and scores the request:
   - **Random Forest** classifies the applicant as likely to fully pay (`0`) or charge off (`1`).
   - **Multiple linear regression** predicts a maximum loan amount given the credit profile.
3. The service returns one of:
   - **Approved** for the requested amount.
   - **Rejected**, optionally with a **counter-offer** (a lower predicted amount that the classifier would still support).
   - **Rejected** with no alternative amount.
4. Each application is stored in SQLite. Administrators see a live dashboard (totals, status, and detail pages). New submissions are pushed over WebSockets so the dashboard can refresh without polling.

---

## Repository layout

```
LendMind/
├── notebooks/
│   ├── 01_data_preparation.ipynb      # cleaning, leakage removal, feature selection
│   └── 02_build_and_evaluate_models.ipynb  # training, evaluation, model export
├── server/
│   ├── src/                           # FastAPI app (run from this directory)
│   ├── views/                         # Jinja2 HTML templates
│   ├── public/                        # CSS and client JavaScript
│   ├── saved_models/                  # serialized models and scalers (.pkl)
│   ├── db/                            # created at runtime (SQLite)
│   ├── requirements.txt
│   └── .env.example
├── data/                              # local only; not committed (see Dataset)
└── README.md
```

The web app lives entirely under `server/`. Models used at inference time are loaded from `server/saved_models/`, not from a top-level `saved_models/` folder.

---

## Tech stack

| Area | Libraries / tools |
|------|-------------------|
| Modeling | pandas, NumPy, scikit-learn, joblib |
| API | FastAPI, Uvicorn, Starlette sessions |
| UI | Jinja2 templates, static CSS/JS |
| Persistence | SQLAlchemy, SQLite |
| Realtime | WebSockets (`/ws`) |
| Config | `python-dotenv` |
| Notebooks | Jupyter |

---

## Requirements

- **Python 3.11 or newer** (the pinned stack includes NumPy 2.4 and pandas 3.0).
- A virtual environment tool (`venv` is enough).
- For retraining only: Jupyter, matplotlib, seaborn, and enough disk/RAM to work with a ~1.2 GB CSV (the notebooks subsample to 100,000 rows after cleaning).
- Optional: [Kaggle CLI](https://github.com/Kaggle/kaggle-api) if you want to download the dataset from the command line.

---

## Dataset (notebooks only)

Training uses the [Lending Club loan data CSV](https://www.kaggle.com/datasets/adarshsng/lending-club-loan-data-csv) (`loan.csv`, about 2.26 million rows and 145 columns). The file is not in Git because of size limits.

The notebooks expect:

```
LendMind/data/archive/loan.csv
```

### Download with the Kaggle API

1. Create a Kaggle account, generate an API token, and place `kaggle.json` where the CLI expects it (typically `~/.kaggle/kaggle.json` on macOS/Linux, or `%USERPROFILE%\.kaggle\kaggle.json` on Windows).
2. From the repository root:

```bash
mkdir -p data/archive
kaggle datasets download -d adarshsng/lending-club-loan-data-csv -p data/archive --unzip
```

Confirm that `data/archive/loan.csv` exists. If the zip extracts to a different folder name, move `loan.csv` to that path or update the `read_csv` path in `notebooks/01_data_preparation.ipynb`.

### Manual download

1. Download the dataset from the Kaggle page above.
2. Create `data/archive/` at the repository root.
3. Place `loan.csv` in `data/archive/`.

The `data/` directory is listed in `.gitignore`.

---

## Machine learning pipeline

The notebooks document the full workflow. Summary:

| Step | Detail |
|------|--------|
| Target | Binary status: Fully Paid → `0`, Charged Off → `1`. Other statuses are dropped. |
| Scale | Raw file is ~1.2 GB; after filtering and dropping sparse/null-heavy columns, a 100,000-row sample is used for modeling. |
| Leakage | Post-origination fields such as recoveries, payments received, late fees, outstanding principal, and debt-settlement flags are removed so the model cannot use information that would be unknown at application time. |
| Other cleaning | High-cardinality categoricals, highly correlated numeric pairs (correlation > 0.95), and columns with more than 40% missing values are dropped. |
| Engineered features | `loan_to_income`, `monthly_burden`, plus a 60-month term indicator used at serving time. |
| Feature selection | Top 15 features per task (Random Forest importance for classification; SelectKBest / model-based ranking for amount). Feature name lists are stored as `server/saved_models/rf_columns.json` and `mlr_columns.json`. |
| Models | Random Forest classifier (`n_estimators=200`, `max_depth=15`, `min_samples_split=5`) and `LinearRegression`, both with `StandardScaler`. |
| Held-out metrics (notebook) | RF accuracy ≈ 0.65, ROC-AUC ≈ 0.70. MLR R² ≈ 0.41, MAE ≈ $3,936, RMSE ≈ $6,674. |

Trained artifacts written by `02_build_and_evaluate_models.ipynb`:

```
server/saved_models/rf_model.pkl
server/saved_models/scaler_rf.pkl
server/saved_models/mlr_model.pkl
server/saved_models/scaler_mlr.pkl
```

The FastAPI process **loads all four files at import time**. If any file is missing, the server will not start. Retrain with the notebooks if your clone does not include the full set.

---

## Installation (web application)

From the repository root:

```bash
cd server
python -m venv .venv
```

Activate the environment:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Copy the example environment file:

```bash
# from server/
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux
```

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes in any shared or deployed environment | Secret used by Starlette `SessionMiddleware` for signed cookies. Replace the placeholder with a long random string. |

`load_dotenv()` is invoked from `server/src/main.py` and looks for `.env` in the **process working directory**. Because the app must be started from `server/src` (see below), put `.env` in **`server/src`** as well, or start the process with that directory as cwd and a `.env` file there:

```bash
# from server/src
copy ..\.env.example .env       # Windows
# cp ../.env.example .env       # macOS / Linux
```

If `SECRET_KEY` is unset, the code falls back to a hardcoded default. That is acceptable only for local demos.

There is no separate database URL. SQLite is created automatically at:

```
server/db/loans.db
```

---

## Run the server

Imports in the application are unprefixed (`from database import ...`), so Uvicorn must be started with **`server/src` as the current directory**:

```bash
cd server/src
python main.py
```

The process binds to `0.0.0.0:8000` with reload enabled. Open:

```
http://localhost:8000
```

You should be redirected to `/login`.

---

## Demo accounts

Credentials are hardcoded in `server/src/auth.py` for local demonstration (they are also shown on the login page). Do not reuse them outside a private machine.

| Role | Username | Password | Landing page |
|------|----------|----------|--------------|
| Administrator | `admin_user` | `admin123` | `/dashboard` |
| Applicant | `standard_user` | `user456` | `/apply` |

- **Applicant:** submit the loan form. Amount, rate, term, income, DTI, revolving utilization, bankcard metrics, and account-history fields are required. Client- and server-side checks reject empty names, non-positive amounts/income/term, and out-of-range percentages.
- **Administrator:** review application counts, open `/applications/{id}` for a full record, and receive WebSocket toasts when a new application is saved.

---

## Application routes

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/` | Session | Redirect to dashboard, apply, or login |
| GET/POST | `/login` | Public | Sign in |
| GET | `/logout` | Session | Clear session |
| GET/POST | `/apply` | Role `user` | Application form and scoring |
| GET | `/dashboard` | Role `admin` | Application list and stats |
| GET | `/applications/{id}` | Role `admin` | Application detail |
| WS | `/ws` | Open socket | `NEW_APPLICATION` events |

Static files are served from `/public`.

---

## Retraining models

1. Place `loan.csv` as described under [Dataset](#dataset-notebooks-only).
2. Create a notebook environment. You can reuse `server/.venv` after installing Jupyter and plotting libraries, or use a separate env. Versions in the notebooks’ commented `pip install` lines may differ slightly from `server/requirements.txt`; for serving, keep scikit-learn compatible with the pickle files (the server pins `scikit-learn==1.8.0`).
3. Run `notebooks/01_data_preparation.ipynb` end to end. It writes cleaned feature tables used by the second notebook (follow the save/load cells in that file).
4. Run `notebooks/02_build_and_evaluate_models.ipynb`. The last training cells dump models and scalers into `server/saved_models/`.
5. Restart the FastAPI process so it reloads the new pickles.

---

## Tests

`pytest` is listed in `server/requirements.txt`. Scoring scenarios live in `server/src/services/test_ml_services.py` and require the four pickle files to load. From `server/src`:

```bash
pytest services/test_ml_services.py
```

`server/src/services/test.py` is a small manual script, not part of the pytest suite.

---

## Team

- **Mohamed Ahmed AbdelMaksoud** — AI and backend — [GitHub](https://github.com/AbdelMaksoudd) · [LinkedIn](https://www.linkedin.com/in/abdelmaksoudd)
- **Muhammad Lutfi** — full-stack — [GitHub](https://github.com/muhammadlutf1) · [LinkedIn](https://www.linkedin.com/in/muhammadlutf1)
