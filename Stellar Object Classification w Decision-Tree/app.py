import streamlit as st
import numpy as np
import joblib
import os

# --- Constants (must match training) ---
IMG_SIZE = 256
CURR_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(CURR_DIR, "stellar_classifier.pkl")

# --- Load Model ---
with open(MODEL_PATH, "rb") as file:
    model = joblib.load(file)

# --- App UI ---
st.set_page_config(page_title="Stellar Classification", layout="centered")
st.title("🌟 Stellar Object Classification")
st.write("Enter astronomical feature values to classify the object.")

# --- Input Fields (must match remaining CSV columns EXACTLY) ---
u = st.number_input("u (Ultraviolet)", value=19.0)
g = st.number_input("g (Green)", value=18.0)
r = st.number_input("r (Red)", value=17.0)
i = st.number_input("i (Infrared)", value=16.5)
z = st.number_input("z (Near Infrared)", value=16.0)
redshift = st.number_input("Redshift", value=0.01)
alpha = st.number_input("Alpha", value=180.0)
delta = st.number_input("Delta", value=0.0)

input_data = np.array([[
    u, g, r, i, z, redshift, alpha, delta
]])

# --- Prediction ---
if st.button("Predict"):
    prediction = model.predict(input_data)[0]

    # LabelEncoder mapping (based on training)
    # 0 = QSO, 1 = STAR
    label_map = {0: "Quasar (QSO)", 1: "Star"}

    st.success(f"🌌 **Predicted Class:** {label_map[prediction]}")
