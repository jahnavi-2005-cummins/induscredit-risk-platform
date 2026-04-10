# backend/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pickle
import pandas as pd
import numpy as np
import shap
import openai
import requests
import os
import re
from dotenv import load_dotenv
import category_encoders as ce

load_dotenv()

app = FastAPI(title="IndusCredit Risk Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─── Load All Saved Files ───────────────────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE, '..', 'models')
DATA_DIR  = os.path.join(BASE, '..', 'data')

with open(os.path.join(MODEL_DIR, 'lightgbm_model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'target_encoder.pkl'), 'rb') as f:
    te = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'feature_columns.pkl'), 'rb') as f:
    feature_columns = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'outlier_bounds.pkl'), 'rb') as f:
    outlier_bounds = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'best_threshold.pkl'), 'rb') as f:
    BEST_THRESHOLD = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'ohe_cols.pkl'), 'rb') as f:
    OHE_COLS = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'target_encode_cols.pkl'), 'rb') as f:
    TARGET_ENCODE_COLS = pickle.load(f)

# Load data
loan_train_df  = pd.read_csv(os.path.join(DATA_DIR, 'loan_train.csv'))
loan_test_df   = pd.read_csv(os.path.join(DATA_DIR, 'loan_test.csv'))
submission_df  = pd.read_csv(os.path.join(DATA_DIR, 'submission.csv'))

# SHAP explainer
explainer = shap.TreeExplainer(model)

# API Keys
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
HF_TOKEN   = os.getenv("HF_API_TOKEN")

print("✅ All models and data loaded successfully!")

# ─── Helper: Feature Engineering ───────────────────────────────

CAP_COLS = [
    'annual_income_inr',
    'loan_amount_inr',
    'savings_account_balance_inr'
]

def add_date_features(df):
    df = df.copy()
    if 'application_date' in df.columns:
        df['application_date'] = pd.to_datetime(
            df['application_date'], errors='coerce'
        )
        df['app_month'] = df['application_date'].dt.month.fillna(1).astype(int)
        df['app_year']  = df['application_date'].dt.year.fillna(2024).astype(int)
        df.drop(columns=['application_date'], inplace=True)
    else:
        df['app_month'] = 1
        df['app_year']  = 2024
    return df

def apply_outlier_caps(df):
    df = df.copy()
    for col, (lo, hi) in outlier_bounds.items():
        if col in df.columns:
            df[col] = df[col].clip(lo, hi)
    return df

def engineer_features(df):
    df = df.copy()
    df['loan_to_income_ratio'] = (
        df['loan_amount_inr'] / (df['annual_income_inr'] + 1)
    )
    df['dti_credit_risk'] = (
        df['dti_ratio'] / (df['credit_score'] / 700)
    )
    df['income_per_year_employed'] = (
        df['annual_income_inr'] / (df['employment_years'] + 1)
    )
    df['emi_estimate'] = (
        (df['loan_amount_inr'] * df['interest_rate_pct'] / 1200) /
        (1 - (1 + df['interest_rate_pct'] / 1200) **
         (-df['loan_tenure_months']))
    )
    df['emi_to_income_ratio'] = (
        df['emi_estimate'] / (df['annual_income_inr'] / 12 + 1)
    )
    df['savings_to_loan_ratio'] = (
        df['savings_account_balance_inr'] / (df['loan_amount_inr'] + 1)
    )
    df['payment_stress_score'] = (
        df['missed_payments_2y'] * df['bureau_enquiries_6m']
    )
    df['credit_utilization'] = (
        df['num_existing_loans'] * df['dti_ratio']
    )
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(df.median(numeric_only=True), inplace=True)
    return df

def handle_ltv(df):
    df = df.copy()
    df['ltv_ratio_missing'] = df['ltv_ratio'].isnull().astype(int)
    df['ltv_ratio']         = df['ltv_ratio'].fillna(-1)
    return df

def preprocess_applicant(df):
    """
    Full preprocessing pipeline —
    same as Round 1
    """
    df = add_date_features(df)
    df = apply_outlier_caps(df)
    df = handle_ltv(df)
    df = engineer_features(df)

    # Drop loan_id if present
    if 'loan_id' in df.columns:
        df = df.drop(columns=['loan_id'])
    if 'default_flag' in df.columns:
        df = df.drop(columns=['default_flag'])

    # Target encoding
    df[TARGET_ENCODE_COLS] = te.transform(df[TARGET_ENCODE_COLS])

    # One-hot encoding
    df = pd.get_dummies(df, columns=OHE_COLS, drop_first=True)

    # Align columns
    df = df.reindex(columns=feature_columns, fill_value=0)

    return df

def get_risk_tier(prob):
    if prob < 0.35:
        return "LOW", "APPROVE", "#059669"
    elif prob < 0.60:
        return "MEDIUM", "REVIEW", "#d97706"
    else:
        return "HIGH", "REJECT", "#dc2626"

# ─── Schema ─────────────────────────────────────────────────────

class ApplicantInput(BaseModel):
    age:                          int
    gender:                       str
    education:                    str
    state:                        str
    urban_rural:                  str
    employment_type:              str
    employment_years:             int
    annual_income_inr:            float
    loan_type:                    str
    loan_purpose:                 str
    loan_amount_inr:              float
    loan_tenure_months:           int
    interest_rate_pct:            float
    credit_score:                 int
    num_existing_loans:           int
    dti_ratio:                    float
    ltv_ratio:                    Optional[float] = None
    has_collateral:               int
    bureau_enquiries_6m:          int
    missed_payments_2y:           int
    savings_account_balance_inr:  float

# ═══════════════════════════════════════════════════════════════
# ENDPOINT 1 — Predict (Local LightGBM Model)
# ═══════════════════════════════════════════════════════════════

@app.post("/predict")
async def predict_risk(applicant: ApplicantInput):
    try:
        df = pd.DataFrame([applicant.dict()])
        X  = preprocess_applicant(df)

        prob = float(model.predict_proba(X)[0][1])
        risk_tier, recommendation, color = get_risk_tier(prob)

        # SHAP
        shap_values = explainer.shap_values(X)
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        else:
            sv = shap_values[0]

        shap_dict   = dict(zip(feature_columns, sv.tolist()))
        top_features = sorted(
            shap_dict.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:10]

        return {
            "status":                "success",
            "probability_of_default": round(prob, 4),
            "probability_pct":        round(prob * 100, 2),
            "risk_tier":              risk_tier,
            "recommendation":         recommendation,
            "risk_color":             color,
            "threshold_used":         round(BEST_THRESHOLD, 3),
            "top_shap_features":      top_features
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# ═══════════════════════════════════════════════════════════════
# ENDPOINT 2 — Fetch Existing Applicant
# ═══════════════════════════════════════════════════════════════

@app.get("/applicant/{loan_id}")
async def get_applicant(loan_id: str):
    try:
        # Get applicant details
        applicant = loan_test_df[
            loan_test_df['loan_id'] == loan_id
        ]
        if applicant.empty:
            return {
                "status":  "error",
                "message": f"{loan_id} not found"
            }

        data = applicant.iloc[0].to_dict()
        for k, v in data.items():
            if pd.isna(v):
                data[k] = None

        # Get pre-computed prediction from submission.csv
        sub = submission_df[
            submission_df['loan_id'] == loan_id
        ]
        prediction = None
        if not sub.empty:
            prob      = float(sub.iloc[0]['default_prob'])
            risk_band = str(sub.iloc[0]['risk_band'])
            flag      = int(sub.iloc[0]['default_flag'])
            rt, rec, color = get_risk_tier(prob)
            prediction = {
                "probability_of_default": prob,
                "probability_pct":        round(prob * 100, 2),
                "risk_tier":              rt,
                "recommendation":         rec,
                "risk_color":             color,
                "default_flag":           flag
            }

        return {
            "status":     "success",
            "data":       data,
            "prediction": prediction
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# ═══════════════════════════════════════════════════════════════
# ENDPOINT 3 — Google Vision OCR
# ═══════════════════════════════════════════════════════════════

@app.post("/ocr")
async def extract_income(file: UploadFile = File(...)):
    try:
        from google.cloud import vision as gv

        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

        client  = gv.ImageAnnotatorClient()
        content = await file.read()
        image   = gv.Image(content=content)

        response = client.document_text_detection(image=image)
        text     = response.full_text_annotation.text

        income = None
        patterns = [
            r'annual\s+(?:income|salary|ctc)[:\s]+₹?\s*([\d,]+)',
            r'gross\s+annual[:\s]+₹?\s*([\d,]+)',
            r'net\s+annual[:\s]+₹?\s*([\d,]+)',
            r'total\s+income[:\s]+₹?\s*([\d,]+)',
            r'ctc[:\s]+₹?\s*([\d,]+)',
            r'gross\s+salary[:\s]+₹?\s*([\d,]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                income = int(match.group(1).replace(',', ''))
                break

        employer = None
        emp_match = re.search(
            r'(?:employer|company|organization|organisation)'
            r'[:\s]+([A-Za-z\s]+(?:Ltd|Limited|Pvt|LLP)?)',
            text, re.IGNORECASE
        )
        if emp_match:
            employer = emp_match.group(1).strip()

        return {
            "status":        "success",
            "extracted_income": income,
            "employer":      employer,
            "raw_text":      text[:300],
            "income_found":  income is not None
        }

    except Exception as e:
        # Demo mode if Google API not configured
        return {
            "status":           "demo_mode",
            "extracted_income": 580000,
            "employer":         "Demo Company Ltd",
            "income_found":     True,
            "message":          "Running in demo mode: " + str(e)
        }

# ═══════════════════════════════════════════════════════════════
# ENDPOINT 4 — OpenAI GPT-4 Explanation
# ═══════════════════════════════════════════════════════════════

@app.post("/explain")
async def explain_result(data: dict):
    try:
        client_ai = openai.OpenAI(api_key=OPENAI_KEY)

        prob           = data.get('probability_pct', 0)
        risk_tier      = data.get('risk_tier', '')
        recommendation = data.get('recommendation', '')
        top_features   = data.get('top_shap_features', [])
        applicant      = data.get('applicant', {})

        features_text = "\n".join([
            f"  - {feat}: impact = {val:+.3f}"
            for feat, val in top_features[:5]
        ])

        prompt = f"""
        You are a senior credit risk analyst at IndusCredit Finance,
        a leading NBFC in India regulated by RBI.

        Our LightGBM model has ALREADY assessed this loan application.
        Your job is ONLY to explain this decision in simple English
        for a credit officer. Do NOT make any new prediction.

        MODEL RESULT (Already Computed by LightGBM):
        - Default Probability : {prob}%
        - Risk Tier           : {risk_tier}
        - Decision            : {recommendation}

        TOP RISK FACTORS FROM SHAP ANALYSIS:
        {features_text}

        APPLICANT PROFILE:
        - Age              : {applicant.get('age')}
        - Employment       : {applicant.get('employment_type')}
        - Annual Income    : Rs {applicant.get('annual_income_inr')}
        - Loan Type        : {applicant.get('loan_type')}
        - Loan Amount      : Rs {applicant.get('loan_amount_inr')}
        - Credit Score     : {applicant.get('credit_score')}
        - DTI Ratio        : {applicant.get('dti_ratio')}
        - Missed Payments  : {applicant.get('missed_payments_2y')}

        Write exactly 3 simple sentences:
        1. Overall decision summary
        2. Top 2 reasons driving this decision
        3. One actionable suggestion for the applicant

        Use simple language. Reference Indian banking context.
        Do not use ML jargon.
        """

        response = client_ai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You explain credit decisions simply. "
                               "You never predict. Only explain."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )

        return {
            "status":      "success",
            "explanation": response.choices[0].message.content
        }

    except Exception as e:
        return {
            "status": "demo_mode",
            "explanation": (
                f"This applicant has been assessed as {data.get('risk_tier')} risk "
                f"with a default probability of {data.get('probability_pct')}%. "
                f"The key factors driving this decision are missed payments history "
                f"and debt-to-income ratio. "
                f"The applicant should focus on clearing existing dues and "
                f"reducing outstanding loans before reapplying."
            )
        }

# ═══════════════════════════════════════════════════════════════
# ENDPOINT 5 — HuggingFace Summarization
# ═══════════════════════════════════════════════════════════════

@app.post("/summarize")
async def summarize_report(data: dict):
    try:
        report_text = data.get('report_text', '')
        headers     = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload     = {
            "inputs": report_text,
            "parameters": {
                "max_length": 200,
                "min_length": 80,
                "do_sample":  False
            }
        }

        response = requests.post(
            "https://api-inference.huggingface.co/models/"
            "facebook/bart-large-cnn",
            headers=headers,
            json=payload,
            timeout=30
        )

        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            summary = result[0].get('summary_text', '')
        else:
            summary = "Summary unavailable. Please try again."

        return {"status": "success", "summary": summary}

    except Exception as e:
        return {
            "status":  "demo_mode",
            "summary": (
                "IndusCredit Finance portfolio analysis reveals MSME loans "
                "carry highest default risk at 8.2%, followed by Personal "
                "loans at 6.1%. The LightGBM model achieved AUC-ROC of 0.86, "
                "exceeding the RBI threshold. Key risk drivers include missed "
                "payment history, DTI ratio, and credit score. Immediate policy "
                "tightening recommended for MSME and Personal loan segments."
            )
        }

# ═══════════════════════════════════════════════════════════════
# ENDPOINT 6 — Portfolio Summary
# ═══════════════════════════════════════════════════════════════

@app.get("/portfolio/summary")
async def portfolio_summary():
    total        = len(loan_train_df)
    defaults     = int(loan_train_df['default_flag'].sum())
    default_rate = round(
        loan_train_df['default_flag'].mean() * 100, 2
    )
    return {
        "status":             "success",
        "total_applications": total,
        "total_defaults":     defaults,
        "default_rate_pct":   default_rate,
        "portfolio_size_cr":  12800,
        "npa_pct":            4.8,
        "model_auc":          0.86,
        "model_threshold":    round(BEST_THRESHOLD, 3)
    }

@app.get("/portfolio/segments")
async def portfolio_segments(segment_by: str = "loan_type"):
    valid = [
        'loan_type', 'employment_type',
        'urban_rural', 'gender',
        'education', 'state'
    ]
    if segment_by not in valid:
        return {"status": "error", "message": "Invalid segment"}

    result = loan_train_df.groupby(segment_by).agg(
        total=('loan_id', 'count'),
        defaults=('default_flag', 'sum'),
        default_rate=('default_flag', 'mean'),
        avg_credit_score=('credit_score', 'mean'),
        avg_loan_amount=('loan_amount_inr', 'mean')
    ).reset_index()

    result['default_rate']     = (result['default_rate'] * 100).round(2)
    result['avg_credit_score'] = result['avg_credit_score'].round(0)
    result['avg_loan_amount']  = result['avg_loan_amount'].round(0)

    return {
        "status":       "success",
        "segment_by":   segment_by,
        "data":         result.to_dict(orient='records')
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)