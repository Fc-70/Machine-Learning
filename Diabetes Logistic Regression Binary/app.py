import streamlit as st
import numpy as np
import joblib
import os

# --- Load Models ---
@st.cache_resource
def load_models():
    CURR_DIR = os.path.dirname(__file__)
    MODEL_PATH1 = os.path.join(CURR_DIR, "diabetes_logreg.pkl")
    MODEL_PATH2 = os.path.join(CURR_DIR, "diabetes_linreg.pkl")
    with open(MODEL_PATH1, "rb") as file:
        logreg = joblib.load(file)
    with open(MODEL_PATH2, "rb") as file:
        linreg = joblib.load(file)
    return logreg, linreg

logreg_model, linreg_model = load_models()

# --- App UI ---
st.set_page_config(page_title="Diabetes Prediction", layout="centered")
st.title("🩺 Diabetes Prediction")
st.write("Enter patient health metrics to predict diabetes outcome.")

# --- Input Fields (must match diabetes.csv column order) ---
pregnancies = st.number_input("Pregnancies", min_value=0, value=2)
glucose = st.number_input("Glucose Level", min_value=0, value=120)
blood_pressure = st.number_input("Blood Pressure", min_value=0, value=70)
skin_thickness = st.number_input("Skin Thickness", min_value=0, value=20)
insulin = st.number_input("Insulin Level", min_value=0, value=80)
bmi = st.number_input("BMI", min_value=0.0, value=25.0)
diabetes_pedigree = st.number_input("Diabetes Pedigree Function", min_value=0.0, value=0.5)
age = st.number_input("Age", min_value=0, value=33)

input_data = np.array([[
    pregnancies,
    glucose,
    blood_pressure,
    skin_thickness,
    insulin,
    bmi,
    diabetes_pedigree,
    age
]])

# --- Prediction ---
if st.button("Predict"):
    # Logistic Regression (Classification)
    logreg_pred = logreg_model.predict(input_data)[0]
    logreg_prob = logreg_model.predict_proba(input_data)[0][1]

    # Linear Regression (Regression-style score)
    linreg_pred = linreg_model.predict(input_data)[0]

    st.subheader("Results")

    if logreg_pred == 1:
        st.error(f"⚠️ Diabetes Detected (Logistic Regression)\n\nProbability: {logreg_prob:.2f}")
    else:
        st.success(f"✅ No Diabetes Detected (Logistic Regression)\n\nProbability: {1 - logreg_prob:.2f}")

    st.info(f"📈 Linear Regression Output (Risk Score): {linreg_pred:.2f}")
