import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import gdown

# --- Constants (must match training) ---
IMG_SIZE = 256

# ⚠️ MUST match train_generator.class_indices order at training time
# Example: ['glioma', 'meningioma', 'notumor', 'pituitary']
CLASS_NAMES = [
    "glioma",
    "meningioma",
    "notumor",
    "pituitary"
]

# --- Load Model ---
MODEL_PATH = "model.h5"

if not os.path.exists(MODEL_PATH):
    url = "https://drive.google.com/uc?id=1ccunGJUmdHBo1WFnHHCaufXU7VamiGCE"
    gdown.download(url, MODEL_PATH, quiet=False)

model = load_model(MODEL_PATH)

# --- App UI ---
st.set_page_config(page_title="Brain Tumor Classification (Multi-Class CNN)", layout="centered")
st.title("🧠 Brain Tumor Classification")
st.write("Upload a brain MRI image to classify the tumor type.")

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
        predictions = model.predict(img_array)[0]
        predicted_index = np.argmax(predictions)
        predicted_class = CLASS_NAMES[predicted_index]
        confidence = predictions[predicted_index]

        st.success(
            f"🧠 **Prediction:** {predicted_class}\n\n"
            f"📊 **Confidence:** {confidence:.2f}"
        )

        st.write("### Class Probabilities")
        for class_name, prob in zip(CLASS_NAMES, predictions):
            st.write(f"{class_name}: {prob:.2f}")
