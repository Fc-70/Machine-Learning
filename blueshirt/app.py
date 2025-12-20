"""
Blue Shirt — Life Simulation Demo (Streamlit)

Fully patched version: safe key access, no KeyErrors.
"""

import streamlit as st
from datetime import datetime
import json, os
from typing import Dict
import math

import matplotlib.pyplot as plt

# ---------------------------
# Config / Constants
# ---------------------------
USER_DATA_FILE = "user_data.json"

DEFAULT_STATS = {
    "Sleep": 80,
    "Energy": 80,
    "Hunger": 50,
    "Stress": 20,
    "Routine": 70,
    "Social": 50,
}

DAY_PHASES = ["Morning", "Day", "Evening", "Night"]

BUDDY_MESSAGES = {
    "all_good": "You're balanced today — little nudges keep the momentum. Nice.",
    "low_energy": "Low energy detected. A short nap or a gentle walk could help.",
    "hungry": "Stomach says hello. A small snack will level you up.",
    "high_stress": "Breathing break? Two deep breaths and a mini leisure session.",
    "low_routine": "A tiny checklist today will boost Routine and ease future days.",
    "low_social": "Ping a friend or say hi — even a 'hey' helps Social currency.",
    "burnout": "You're looking drained. Take a proper rest — screens off, real rest on.",
}

ACTIONS = [
    {"name": "Sleep (Nap / Sleep)", "effects": {"Sleep": +20, "Energy": +25, "Stress": -12}},
    {"name": "Eat (Meal / Snack)", "effects": {"Hunger": +35, "Energy": +6, "Stress": -4}},
    {"name": "Exercise (Light)", "effects": {"Energy": -15, "Stress": -8, "Routine": +4, "Social": +1}},
    {"name": "Socialize", "effects": {"Social": +18, "Stress": -6, "Routine": +2}},
    {"name": "Study / Work", "effects": {"Routine": +6, "Stress": +6, "Energy": -8}},
    {"name": "Leisure (Relax)", "effects": {"Stress": -10, "Energy": +6, "Routine": +1}},
]

# ---------------------------
# Utility Functions
# ---------------------------
def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, int(round(v))))

def load_user():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r") as f:
                d = json.load(f)
                # ensure all keys
                d["stats"] = {k: d.get("stats", {}).get(k, DEFAULT_STATS[k]) for k in DEFAULT_STATS}
                d["history"] = d.get("history", [])
                d["last_phase"] = d.get("last_phase", DAY_PHASES[0])
                d["last_time"] = d.get("last_time", datetime.utcnow().isoformat())
                d["notes"] = d.get("notes", "")
                d["name"] = d.get("name", "Alex")
                return d
        except Exception:
            pass
    return {
        "name": "Alex",
        "stats": DEFAULT_STATS.copy(),
        "history": [],
        "last_phase": DAY_PHASES[0],
        "last_time": datetime.utcnow().isoformat(),
        "notes": "",
    }

def save_user(user):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(user, f, indent=2)

def compute_lifestyle_stability(stats: Dict[str,int]) -> int:
    s = {k: clamp(stats.get(k, DEFAULT_STATS[k])) for k in ["Sleep","Energy","Hunger","Routine","Social","Stress"]}
    positive_sum = s["Sleep"] + s["Energy"] + s["Hunger"] + s["Routine"] + s["Social"]
    avg_pos = positive_sum / 5.0
    stress_penalty = s["Stress"]
    stability = avg_pos - (stress_penalty * 0.5)
    return clamp(stability)

def get_life_rank(stability: int) -> str:
    if stability >= 90:
        return "🟢 Balanced"
    elif stability >= 70:
        return "🟡 Stable"
    elif stability >= 50:
        return "🟠 Unsettled"
    elif stability >= 30:
        return "🔴 Strained"
    else:
        return "⚫ Burned Out"

def apply_action(stats: Dict[str,int], action_name: str) -> Dict[str,int]:
    action = next((a for a in ACTIONS if a["name"] == action_name), None)
    if not action:
        return stats
    for stat, delta in action["effects"].items():
        stats[stat] = clamp(stats.get(stat, DEFAULT_STATS.get(stat, 50)) + delta)
    return stats

def passive_time_advance(stats: Dict[str,int], phase: str):
    stats = {k: clamp(stats.get(k, DEFAULT_STATS.get(k, 50))) for k in DEFAULT_STATS}
    if phase == "Day":
        stats["Hunger"] = clamp(stats["Hunger"] - 12)
        stats["Energy"] = clamp(stats["Energy"] - 10)
        stats["Stress"] = clamp(stats["Stress"] + 4)
    elif phase == "Evening":
        stats["Hunger"] = clamp(stats["Hunger"] - 18)
        stats["Energy"] = clamp(stats["Energy"] - 16)
        stats["Stress"] = clamp(stats["Stress"] + 6)
    elif phase == "Night":
        stats["Hunger"] = clamp(stats["Hunger"] - 8)
        stats["Energy"] = clamp(stats["Energy"] - 8)
        stats["Stress"] = clamp(stats["Stress"] + 2)
    elif phase == "Morning":
        stats["Energy"] = clamp(stats["Energy"] + 4)
        stats["Stress"] = clamp(stats["Stress"] - 2)
    return stats

def buddy_suggestion(stats: Dict[str,int], stability: int) -> str:
    if stability < 30:
        return BUDDY_MESSAGES["burnout"]
    if stats.get("Hunger", 50) < 30:
        return BUDDY_MESSAGES["hungry"]
    if stats.get("Energy", 50) < 35:
        return BUDDY_MESSAGES["low_energy"]
    if stats.get("Stress", 20) > 70:
        return BUDDY_MESSAGES["high_stress"]
    if stats.get("Routine", 70) < 40:
        return BUDDY_MESSAGES["low_routine"]
    if stats.get("Social", 50) < 30:
        return BUDDY_MESSAGES["low_social"]
    return BUDDY_MESSAGES["all_good"]

def record_history(user: Dict, action_name: str, effects: Dict[str,int]):
    entry = {
        "time": datetime.utcnow().isoformat(),
        "phase": user.get("last_phase", DAY_PHASES[0]),
        "action": action_name,
        "effects": effects
    }
    user.setdefault("history", []).insert(0, entry)
    user["history"] = user["history"][:200]

def plot_radar(stats: Dict[str,int]):
    labels = list(stats.keys())
    values = [stats.get(k, DEFAULT_STATS.get(k, 50)) for k in labels]
    values += values[:1]
    angles = [n / float(len(labels)) * 2 * math.pi for n in range(len(labels))]
    angles += angles[:1]

    fig = plt.figure(figsize=(4,4))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles[:-1], labels, color="white", fontsize=9)
    ax.set_rlabel_position(0)
    ax.set_ylim(0, 100)
    ax.plot(angles, values, linewidth=2, linestyle='solid', color="#00e0ff")
    ax.fill(angles, values, alpha=0.25, color="#00e0ff")
    fig.patch.set_facecolor('#0b3d91')
    ax.set_facecolor('#08284f')
    plt.tight_layout()
    return fig

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Blue Shirt — Life OS (Demo)", page_icon="🕶️", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg,#062a5f 0%, #021125 100%); color: #eaf6ff; }
    .card { padding: 12px; border-radius: 12px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.03); }
    .muted { color: rgba(255,255,255,0.6); font-size: 12px; }
    .small { font-size: 13px; color: #dbeeff; }
    </style>
    """, unsafe_allow_html=True
)

if "user" not in st.session_state:
    st.session_state.user = load_user()
user = st.session_state.user

# Header
header_col1, header_col2 = st.columns([3,1])
with header_col1:
    st.title("🕶️ Blue Shirt — Life OS (Demo)")
    st.markdown("**A subtle life-simulation UI for healthy routines, gentle feedback, and sandbox play.**")
    st.markdown('<div class="muted">Demo-only • Local persistence (user_data.json)</div>', unsafe_allow_html=True)
with header_col2:
    st.markdown(f"**Phase:** **{user.get('last_phase', DAY_PHASES[0])}**")
    st.markdown(f"Last update: {user.get('last_time', '')[:19]} UTC")

st.markdown("---")

# Stability + Buddy + Timeline
c1, c2, c3 = st.columns([1.2,1.6,1.2])
with c1:
    st.markdown("### 🏁 Lifestyle Stability")
    stability = compute_lifestyle_stability(user["stats"])
    st.progress(stability/100)
    st.markdown(f"**{stability}/100** — {get_life_rank(stability)}")
    st.caption("Aggregated measure of life balance.")
    st.markdown("### Quick Status")
    stat_line = " • ".join([f"{k}: {user['stats'].get(k, DEFAULT_STATS[k])}" for k in ["Sleep","Energy","Hunger","Stress","Routine","Social"]])
    st.markdown(f"<div class='small'>{stat_line}</div>", unsafe_allow_html=True)

with c2:
    st.markdown("### 💬 Buddy")
    buddy_msg = buddy_suggestion(user["stats"], stability)
    st.markdown(f"<div class='card'><strong style='font-size:16px'>Buddy:</strong><p style='margin-top:6px'>{buddy_msg}</p></div>", unsafe_allow_html=True)
    tips=[]
    if user["stats"].get("Hunger",50)<35: tips.append("Try eating a small meal.")
    if user["stats"].get("Energy",50)<40: tips.append("Short nap or easy movement could help.")
    if user["stats"].get("Stress",20)>65: tips.append("Mini-break: 5 minutes of leisure or breathing.")
    if tips:
        st.markdown("<div class='muted'>Suggestions: " + " • ".join(tips) + "</div>", unsafe_allow_html=True)

with c3:
    st.markdown("### 🕰️ Day Timeline")
    phase = user.get("last_phase", DAY_PHASES[0])
    phase_choice = st.selectbox("Phase", DAY_PHASES, index=DAY_PHASES.index(phase))
    if st.button("Advance Time (pass to selected phase)"):
        user["stats"] = passive_time_advance(user["stats"], phase_choice)
        user["last_phase"] = phase_choice
        user["last_time"] = datetime.utcnow().isoformat()
        save_user(user)
        st.rerun()
    st.markdown(f"Current: **{user.get('last_phase','Morning')}**")

st.markdown("---")

# Main content
left, right = st.columns([2,1])
with left:
    st.markdown("## 🧭 Choose an Activity")
    action_cols = st.columns([1,1,1])
    for i, action in enumerate(ACTIONS):
        col = action_cols[i % len(action_cols)]
        if col.button(action["name"]):
            before = dict(user["stats"])
            user["stats"] = apply_action(user["stats"], action["name"])
            after = dict(user["stats"])
            effects = {k: after[k]-before.get(k,50) for k in after}
            record_history(user, action["name"], effects)
            user["last_time"] = datetime.utcnow().isoformat()
            save_user(user)
            st.rerun()

    st.markdown("---")
    st.markdown("## 📊 Current Stats")
    for sname in ["Sleep","Energy","Hunger","Stress","Routine","Social"]:
        sval = user["stats"].get(sname, DEFAULT_STATS[sname])
        if sname=="Stress":
            color="green" if sval<=30 else "yellow" if sval<=60 else "red"
        else:
            color="green" if sval>=70 else "yellow" if sval>=40 else "red"
        st.markdown(f"**{sname}** — {sval}")
        st.progress(sval/100.0)

    st.markdown("---")
    st.markdown("## 📜 Recent Activity")
    history = user.get("history", [])
    if not history:
        st.markdown("<div class='muted'>No actions yet.</div>", unsafe_allow_html=True)
    else:
        for entry in history[:12]:
            t = entry["time"][:19].replace("T"," ")
            act = entry["action"]
            eff = entry["effects"]
            eff_text = ", ".join([f"{k}{'+' if v>=0 else ''}{v}" for k,v in eff.items() if v!=0])
            st.markdown(f"- **{t}** • _{act}_ — {eff_text}")

with right:
    st.markdown("## ✨ Star Chart — Life Stats")
    try:
        fig = plot_radar(user["stats"])
        st.pyplot(fig)
    except Exception:
        st.write(user["stats"])
        st.caption("Install matplotlib for radar chart: `pip install matplotlib`")

    st.markdown("---")
    st.markdown("## ⚙️ Controls & Quick Sim")
    if st.button("Reset demo to defaults"):
        if os.path.exists(USER_DATA_FILE):
            os.remove(USER_DATA_FILE)
        st.session_state.user = load_user()
        save_user(st.session_state.user)
        st.rerun()

    if st.button("Simulate rough day"):
        user["stats"]["Sleep"] = clamp(user["stats"].get("Sleep",50)-30)
        user["stats"]["Energy"] = clamp(user["stats"].get("Energy",50)-30)
        user["stats"]["Hunger"] = clamp(user["stats"].get("Hunger",50)-40)
        user["stats"]["Stress"] = clamp(user["stats"].get("Stress",20)+30)
        user["last_time"]=datetime.utcnow().isoformat()
        record_history(user,"Simulate rough day",{"Sleep":-30,"Energy":-30,"Hunger":-40,"Stress":30})
        save_user(user)
        st.rerun()

    if st.button("Simulate recovery"):
        user["stats"]["Sleep"] = clamp(user["stats"].get("Sleep",50)+30)
        user["stats"]["Energy"] = clamp(user["stats"].get("Energy",50)+30)
        user["stats"]["Hunger"] = clamp(user["stats"].get("Hunger",50)+20)
        user["stats"]["Stress"] = clamp(user["stats"].get("Stress",20)-25)
        user["last_time"]=datetime.utcnow().isoformat()
        record_history(user,"Simulate recovery",{"Sleep":30,"Energy":30,"Hunger":20,"Stress":-25})
        save_user(user)
        st.rerun()

    st.markdown("---")
    st.markdown("## 📝 Notes")
    notes = st.text_area("Short notes (saved locally)", value=user.get("notes",""), height=120)
    if st.button("Save notes"):
        user["notes"] = notes
        save_user(user)
        st.success("Notes saved locally.")

st.markdown("---")
st.markdown("<div class='muted'>Subtle feedback, behavior-driven progression, non-intrusive UI. Demo-only, local persistence.</div>", unsafe_allow_html=True)
