import streamlit as st
import random

st.set_page_config(page_title="Life Simulation", layout="centered")

# -----------------------------
# Initialize Session State
# -----------------------------
if "player_stats" not in st.session_state:
    st.session_state.player_stats = {
        "Energy": 50,
        "Hunger": 50,
        "Stress": 30,
        "Routine": 70,
        "Social": 40
    }

if "log" not in st.session_state:
    st.session_state.log = []

# -----------------------------
# Actions
# -----------------------------
actions = {
    "sleep": {"Energy": +20, "Stress": -10, "Routine": +5},
    "eat": {"Hunger": -30, "Energy": +5, "Stress": -2},
    "run": {"Energy": -10, "Stress": -5, "Routine": +5},
    "talk": {"Social": +15, "Stress": -5},
    "work": {"Energy": -15, "Stress": +10, "Routine": +10},
    "meditate": {"Stress": -15, "Energy": +5},
}

# -----------------------------
# Rank Logic
# -----------------------------
def calculate_rank(stats):
    score = (
        stats["Energy"]
        + (100 - stats["Hunger"])
        + (100 - stats["Stress"])
        + stats["Routine"]
        + stats["Social"]
    ) / 5
    return int(score)

def get_rank(score):
    if score >= 90:
        return "🟢 BALANCED"
    elif score >= 70:
        return "🟡 STABLE"
    elif score >= 50:
        return "🟠 UNSETTLED"
    elif score >= 30:
        return "🔴 STRAINED"
    else:
        return "⚫ BURNED OUT"

# -----------------------------
# UI Header
# -----------------------------
st.title("🧠 Life Simulation Prototype")
st.caption("Type dialogue or actions like *sleep*, *work*, *eat*")

# -----------------------------
# Stats UI
# -----------------------------
st.subheader("📊 Player Stats")
for stat, value in st.session_state.player_stats.items():
    st.progress(value / 100, text=f"{stat}: {value}")

score = calculate_rank(st.session_state.player_stats)
st.markdown(f"### 🏷️ Life Rank: **{get_rank(score)} ({score}/100)**")

# -----------------------------
# Input Box
# -----------------------------
user_input = st.text_input("Enter dialogue or action (*action*)")

if st.button("Submit"):
    text = user_input.lower().strip()

    if text.startswith("*") and text.endswith("*"):
        action = text[1:-1]
        if action in actions:
            for stat, change in actions[action].items():
                st.session_state.player_stats[stat] += change
            st.session_state.log.append(f"✅ Action performed: {action}")
        else:
            st.session_state.log.append("❌ Unknown action")
    else:
        st.session_state.player_stats["Social"] += 2
        st.session_state.log.append(f"🗨️ You said: {user_input}")

    # Clamp stats
    for k in st.session_state.player_stats:
        st.session_state.player_stats[k] = max(
            0, min(100, st.session_state.player_stats[k])
        )

# -----------------------------
# Log Feed
# -----------------------------
st.subheader("📜 Activity Log")
for entry in reversed(st.session_state.log[-6:]):
    st.write(entry)
import streamlit as st
import random

st.set_page_config(page_title="Life Simulation", layout="centered")

# -----------------------------
# Initialize Session State
# -----------------------------
if "player_stats" not in st.session_state:
    st.session_state.player_stats = {
        "Energy": 50,
        "Hunger": 50,
        "Stress": 30,
        "Routine": 70,
        "Social": 40
    }

if "log" not in st.session_state:
    st.session_state.log = []

# -----------------------------
# Actions
# -----------------------------
actions = {
    "sleep": {"Energy": +20, "Stress": -10, "Routine": +5},
    "eat": {"Hunger": -30, "Energy": +5, "Stress": -2},
    "run": {"Energy": -10, "Stress": -5, "Routine": +5},
    "talk": {"Social": +15, "Stress": -5},
    "work": {"Energy": -15, "Stress": +10, "Routine": +10},
    "meditate": {"Stress": -15, "Energy": +5},
}

# -----------------------------
# Rank Logic
# -----------------------------
def calculate_rank(stats):
    score = (
        stats["Energy"]
        + (100 - stats["Hunger"])
        + (100 - stats["Stress"])
        + stats["Routine"]
        + stats["Social"]
    ) / 5
    return int(score)

def get_rank(score):
    if score >= 90:
        return "🟢 BALANCED"
    elif score >= 70:
        return "🟡 STABLE"
    elif score >= 50:
        return "🟠 UNSETTLED"
    elif score >= 30:
        return "🔴 STRAINED"
    else:
        return "⚫ BURNED OUT"

# -----------------------------
# UI Header
# -----------------------------
st.title("🧠 Life Simulation Prototype")
st.caption("Type dialogue or actions like *sleep*, *work*, *eat*")

# -----------------------------
# Stats UI
# -----------------------------
st.subheader("📊 Player Stats")
for stat, value in st.session_state.player_stats.items():
    st.progress(value / 100, text=f"{stat}: {value}")

score = calculate_rank(st.session_state.player_stats)
st.markdown(f"### 🏷️ Life Rank: **{get_rank(score)} ({score}/100)**")

# -----------------------------
# Input Box
# -----------------------------
user_input = st.text_input("Enter dialogue or action (*action*)")

if st.button("Submit"):
    text = user_input.lower().strip()

    if text.startswith("*") and text.endswith("*"):
        action = text[1:-1]
        if action in actions:
            for stat, change in actions[action].items():
                st.session_state.player_stats[stat] += change
            st.session_state.log.append(f"✅ Action performed: {action}")
        else:
            st.session_state.log.append("❌ Unknown action")
    else:
        st.session_state.player_stats["Social"] += 2
        st.session_state.log.append(f"🗨️ You said: {user_input}")

    # Clamp stats
    for k in st.session_state.player_stats:
        st.session_state.player_stats[k] = max(
            0, min(100, st.session_state.player_stats[k])
        )

# -----------------------------
# Log Feed
# -----------------------------
st.subheader("📜 Activity Log")
for entry in reversed(st.session_state.log[-6:]):
    st.write(entry)
