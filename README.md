# 💳 LendMind: AI-Powered Loan Approval & Risk Assessment

**LendMind** is an end-to-end machine learning platform designed to automate and optimize the loan application process. By leveraging historical financial data, the system predicts loan approval probability and suggests appropriate credit limits.

---

## 🏗️ Project Architecture
The repository is organized into a **Monorepo** structure, ensuring a clean separation between data science experiments, backend logic, and user interfaces:

* **`notebooks/`**: Contains documented Jupyter notebooks for data engineering and model evaluation.
    * `01_data_preparation.ipynb`: Data cleaning and EDA.
    * `02_build_and_evaluate_models.ipynb`: Model training and performance metrics.
* **`backend/`**: A high-performance **FastAPI** server serving the ML models.
* **`frontend/`**: A modern **React** application (supporting SSR) for customer and admin portals.
* **`docs/`**: Technical documentation and the `LCDataDictionary.xlsx`.
* **`saved_models/`**: Serialized production-ready models (`.pkl` files).
* **`data/`**: (Local only) Directory for raw datasets.

---

## 📊 Dataset Setup
The system is trained on a massive historical loan dataset (1.2 GB). Due to GitHub's file size limits, `loan.csv` is excluded from the repository.

### Option 1: Automated Download (Kaggle API)
If you have the Kaggle CLI installed, run the following commands in your terminal:
```bash
mkdir DataSet
kaggle datasets download -d [KA-KA-shi/Lending Club Loan Data] -p data/ --unzip
```

### Option 2: Manual Setup
1. Download the DataSet from [https://www.kaggle.com/datasets/adarshsng/lending-club-loan-data-csv].
2. Create a folder named `DataSet/` in the project root.
3. Extract and place `loan.csv` inside the `data/` folder.

---

## 🚀 Getting Started

### 1. Backend (Python)
```bash


```

### 2. Frontend (React)
```bash


```

---

## 🛠️ Tech Stack
* **AI/ML**: Python, Pandas, Scikit-Learn, Numpy, Joblib.
* **Backend**: FastAPI.
* **Frontend**: .
* **Version Control**: Git & GitHub.

---

## 👥 The Engineering Team

* **Mohamed Ahmed AbdelMaksoud** - AI & Backend Architecture
  * [GitHub](https://github.com/AbdelMaksoudd) | [LinkedIn](https://www.linkedin.com/in/abdelmaksoudd)

* **Muhammad Lutfi** - Full-Stack Development
  * [GitHub](https://github.com/muhammadlutf1) | [LinkedIn](https://www.linkedin.com/in/muhammadlutf1)

---
© 2026 LendMind Project - Dedicated to smarter financial decisions.