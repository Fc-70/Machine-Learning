import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
import os
import gdown
from tensorflow.keras.models import load_model

# --- Constants (must match training) ---
IMG_SIZE = 256

# --- Load Model ---
CURR_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(CURR_DIR, "cnn_binary-class_classifier.h5")

# --- Load Model ---
model = load_model(MODEL_PATH)

# --- App UI ---
st.set_page_config(page_title="Brain Tumor Detection (CNN)", layout="centered")
st.title("🧠 Brain Tumor Detection")
st.write("Upload a brain MRI image to predict tumor presence.")

# --- Image Upload ---
uploaded_file = st.file_uploader(
    "Upload Brain MRI Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    image = image.resize((IMG_SIZE, IMG_SIZE))
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # --- Preprocessing (MATCH ImageDataGenerator) ---
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # --- Prediction ---
    if st.button("Predict"):
        probability = model.predict(img_array)[0][0]
        prediction = 1 if probability >= 0.5 else 0

        if prediction == 1:
            st.error(f"⚠️ Tumor Detected\n\nProbability: {probability:.2f}")
        else:
            st.success(f"✅ No Tumor Detected\n\nProbability: {1 - probability:.2f}")
