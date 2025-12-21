import streamlit as st
from datetime import date

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(
    page_title="SoulSync",
    page_icon="✨",
    layout="wide"
)

# -----------------------------
# Session State Init
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "stats" not in st.session_state:
    st.session_state.stats = {
        "Knowledge": {"level": 1, "xp": 0},
        "Guts": {"level": 1, "xp": 0},
        "Proficiency": {"level": 1, "xp": 0},
        "Kindness": {"level": 1, "xp": 0},
        "Charm": {"level": 1, "xp": 0},
    }

if "streak" not in st.session_state:
    st.session_state.streak = 0

if "missions" not in st.session_state:
    st.session_state.missions = [
        {"title": "📚 Study for 20 minutes", "stat": "Knowledge", "xp": 20, "done": False},
        {"title": "🏃 Walk or stretch 10 minutes", "stat": "Guts", "xp": 15, "done": False},
        {"title": "🌙 Sleep without phone", "stat": "Proficiency", "xp": 15, "done": False},
        {"title": "🥗 Eat one healthy item", "stat": "Kindness", "xp": 10, "done": False},
        {"title": "🧠 Write 3 positive lines", "stat": "Charm", "xp": 10, "done": False},
    ]

# -----------------------------
# XP Logic
# -----------------------------
def xp_needed(level):
    return 20 * (level ** 2)

def apply_xp(stat, xp):
    s = st.session_state.stats[stat]
    s["xp"] += xp
    while s["xp"] >= xp_needed(s["level"]) and s["level"] < 10:
        s["xp"] -= xp_needed(s["level"])
        s["level"] += 1

# -----------------------------
# Login / Onboarding
# -----------------------------
def login():
    st.title("✨ SoulSync")
    st.subheader("A life-RPG for building healthy habits")

    with st.form("login"):
        name = st.text_input("Enter your name")
        goal = st.text_input("Your main goal (optional)")
        submit = st.form_submit_button("Start Journey ✨")

    if submit and name:
        st.session_state.user = {
            "name": name,
            "goal": goal,
            "joined": date.today()
        }
        st.success("Welcome to SoulSync!")
        st.rerun()

# -----------------------------
# Dashboard
# -----------------------------
def dashboard():
    user = st.session_state.user
    st.title(f"🏠 Dashboard — {user['name']}")
    st.caption(f"Goal: {user['goal'] or 'Not set'}")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("🔥 Streak", f"{st.session_state.streak} days")

    with col2:
        done = sum(1 for m in st.session_state.missions if m["done"])
        st.metric("✅ Missions Done", f"{done}/5")

    st.markdown("### 🌈 Your Stats")

    for stat, data in st.session_state.stats.items():
        st.write(f"**{stat}** — Level {data['level']}")
        need = xp_needed(data["level"])
        st.progress(min(data["xp"] / need, 1.0))
        st.caption(f"XP: {data['xp']} / {need}")

# -----------------------------
# Missions Page
# -----------------------------
def missions():
    st.title("✅ Daily Missions")
    completed_today = True

    for i, m in enumerate(st.session_state.missions):
        col1, col2 = st.columns([0.75, 0.25])

        with col1:
            st.write(m["title"])
            st.caption(f"+{m['xp']} XP → {m['stat']}")

        with col2:
            if m["done"]:
                st.success("Done")
            else:
                if st.button("Complete", key=i):
                    apply_xp(m["stat"], m["xp"])
                    m["done"] = True
                    st.toast(f"+{m['xp']} XP!", icon="✨")
                    st.rerun()

        if not m["done"]:
            completed_today = False

    if completed_today:
        st.session_state.streak += 1
        st.success("🎉 All missions completed! Streak increased!")

# -----------------------------
# Settings
# -----------------------------
def settings():
    st.title("⚙️ Settings")
    if st.button("Reset Demo"):
        st.session_state.clear()
        st.rerun()

    st.info("This is a demo version for project submission.")

# -----------------------------
# Main App
# -----------------------------
if st.session_state.user is None:
    login()
else:
    page = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "Missions", "Settings"]
    )

    if page == "Dashboard":
        dashboard()
    elif page == "Missions":
        missions()
    else:
        settings()
