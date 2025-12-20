"""
Blue Shirt — Life Simulation Demo (Streamlit)

Features:
- Lifestyle stats (Sleep, Energy, Hunger, Stress, Routine, Social)
- Actions that update stats (Sleep, Eat, Exercise, Socialize, Study, Leisure)
- Lifestyle Stability score (0-100) and subtle rank categories
- Buddy contextual feedback (non-intrusive, lighthearted)
- Day timeline (Morning/Day/Evening/Night) & Advance Time simulation
- Radar-style Star Chart (matplotlib) — optional dependency
- Local persistence to user_data.json (demo convenience)
- Reset / simulate controls for quick testing

Demo-only: replace persistence and Buddy behavior with production services for real app.
"""

import streamlit as st
from datetime import datetime, date, timedelta
import json, os
from typing import Dict, List
import math

# Optional plotting library used for radar/star chart. Remove if you don't want the extra dep.
import matplotlib.pyplot as plt

# ---------------------------
# Config / Constants
# ---------------------------
USER_DATA_FILE = "user_data.json"

DEFAULT_STATS = {
    "Sleep": 80,      # 0–100 (hours quality)
    "Energy": 80,     # 0–100
    "Hunger": 50,     # 0–100 (0 = starving, 100 = full)
    "Stress": 20,     # 0–100 (0 = relaxed)
    "Routine": 70,    # 0–100
    "Social": 50,     # 0–100
}

DAY_PHASES = ["Morning", "Day", "Evening", "Night"]

# Light, friendly Buddy messages mapped by situation keys
BUDDY_MESSAGES = {
    "all_good": "You're balanced today — little nudges keep the momentum. Nice.",
    "low_energy": "Low energy detected. A short nap or a gentle walk could help.",
    "hungry": "Stomach says hello. A small snack will level you up.",
    "high_stress": "Breathing break? Two deep breaths and a mini leisure session.",
    "low_routine": "A tiny checklist today will boost Routine and ease future days.",
    "low_social": "Ping a friend or say hi — even a 'hey' helps Social currency.",
    "burnout": "You're looking drained. Take a proper rest — screens off, real rest on.",
}

# Actions that players can choose (name + effects on stats)
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
                # ensure stats exist
                if "stats" not in d:
                    d["stats"] = DEFAULT_STATS.copy()
                # ensure history
                if "history" not in d:
                    d["history"] = []
                # ensure datetime fields
                if "last_phase" not in d:
                    d["last_phase"] = DAY_PHASES[0]
                if "last_time" not in d:
                    d["last_time"] = datetime.utcnow().isoformat()
                return d
        except Exception:
            pass
    # default
    return {
        "name": "Alex",
        "stats": DEFAULT_STATS.copy(),
        "history": [],  # list of {"time": iso, "action": str, "effects": dict}
        "last_phase": DAY_PHASES[0],
        "last_time": datetime.utcnow().isoformat(),
        "notes": "",
    }

def save_user(user):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(user, f, indent=2)

def compute_lifestyle_stability(stats: Dict[str,int]) -> int:
    """
    Combine stats to produce a 0-100 stability score.
    Stress reduces the score (penalty). Hunger is treated positive (full is good).
    """
    # ensure numeric with safe defaults
    s = {k: clamp(stats.get(k, 50)) for k in ["Sleep","Energy","Hunger","Routine","Social","Stress"]}
    positive_sum = s["Sleep"] + s["Energy"] + s["Hunger"] + s["Routine"] + s["Social"]
    avg_pos = positive_sum / 5.0
    stress_penalty = s["Stress"]
    stability = avg_pos - (stress_penalty * 0.5)
    stability = clamp(stability)
    return stability
    
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
    """
    Apply effects from ACTIONS to stats; returns updated stats (mutates dict).
    """
    action = next((a for a in ACTIONS if a["name"] == action_name), None)
    if not action:
        return stats
    for stat, delta in action["effects"].items():
        if stat not in stats:
            stats[stat] = 50
        stats[stat] = clamp(stats[stat] + delta)
    # small passive adjustments: after an active action, Routine nudges slightly if not sleeping
    return stats

def passive_time_advance(stats: Dict[str,int], phase: str):
    """
    Simulate gentle passive stat drift when advancing through day phases.
    - Morning -> Day: small energy/hunger changes
    - Day -> Evening: more hunger, energy down, stress may increase
    - Evening -> Night: energy recovery if Sleep action taken later; otherwise energy lowers
    - Night -> Morning: natural recovery if slept; we don't auto-sleep here — player chooses Sleep action
    This is intentionally mild and predictable.
    """
    stats = dict(stats)
    if phase == "Day":
        stats["Hunger"] = clamp(stats["Hunger"] - 12)
        stats["Energy"] = clamp(stats["Energy"] - 10)
        stats["Stress"] = clamp(stats["Stress"] + 4)
    elif phase == "Evening":
        stats["Hunger"] = clamp(stats["Hunger"] - 18)
        stats["Energy"] = clamp(stats["Energy"] - 16)
        stats["Stress"] = clamp(stats["Stress"] + 6)
    elif phase == "Night":
        # small chance to recover Sleep if player uses Sleep action; passive drift toward lower energy
        stats["Hunger"] = clamp(stats["Hunger"] - 8)
        stats["Energy"] = clamp(stats["Energy"] - 8)
        stats["Stress"] = clamp(stats["Stress"] + 2)
    elif phase == "Morning":
        # gentle morning recovery if previous night had Sleep action; we leave it neutral here
        stats["Energy"] = clamp(stats["Energy"] + 4)
        stats["Stress"] = clamp(stats["Stress"] - 2)
    # keep in bounds
    return stats

def buddy_suggestion(stats: Dict[str,int], stability: int) -> str:
    """
    Context-aware buddy suggestions with light tone; choose the most relevant one.
    Priority order: Burnout / Hunger / Energy / Stress / Routine / Social / all_good
    """
    if stability < 30:
        return BUDDY_MESSAGES["burnout"]
    if stats["Hunger"] < 30:
        return BUDDY_MESSAGES["hungry"]
    if stats["Energy"] < 35:
        return BUDDY_MESSAGES["low_energy"]
    if stats["Stress"] > 70:
        return BUDDY_MESSAGES["high_stress"]
    if stats["Routine"] < 40:
        return BUDDY_MESSAGES["low_routine"]
    if stats["Social"] < 30:
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
    # keep history bounded (demo)
    user["history"] = user["history"][:200]

def plot_radar(stats: Dict[str,int]):
    labels = list(stats.keys())
    values = [stats[k] for k in labels]
    # close the plot
    values += values[:1]
    angles = [n / float(len(labels)) * 2 * math.pi for n in range(len(labels))]
    angles += angles[:1]

    fig = plt.figure(figsize=(4,4))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles[:-1], labels, color="white", fontsize=9)
    ax.set_rlabel_position(0)
    max_val = 100
    ax.set_ylim(0, max_val)
    # styling
    ax.plot(angles, values, linewidth=2, linestyle='solid', color="#00e0ff")
    ax.fill(angles, values, alpha=0.25, color="#00e0ff")
    ax.grid(color="gray", linestyle="--", alpha=0.3)
    fig.patch.set_facecolor('#0b3d91')
    ax.set_facecolor('#08284f')
    plt.tight_layout()
    return fig

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Blue Shirt — Life OS (Demo)", page_icon="🕶️", layout="wide")

# small CSS for nicer visuals (dark soft theme)
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg,#062a5f 0%, #021125 100%); color: #eaf6ff; }
    .card { padding: 12px; border-radius: 12px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.03); }
    .muted { color: rgba(255,255,255,0.6); font-size: 12px; }
    .small { font-size: 13px; color: #dbeeff; }
    </style>
    """,
    unsafe_allow_html=True
)

# load or init user
if "user" not in st.session_state:
    st.session_state.user = load_user()

user = st.session_state.user

# Header area
header_col1, header_col2 = st.columns([3,1])
with header_col1:
    st.title("🕶️ Blue Shirt — Life OS (Demo)")
    st.markdown("**A subtle life-simulation UI for healthy routines, gentle feedback, and sandbox play.**")
    st.markdown('<div class="muted">Demo-only • No accounts • Local persistence (user_data.json)</div>', unsafe_allow_html=True)
with header_col2:
    st.write(" ")
    st.markdown(f"**Phase:** **{user.get('last_phase', DAY_PHASES[0])}**")
    st.markdown(f"Last update: {user.get('last_time', '')[:19]} UTC")

st.markdown("---")

# top row: stability + buddy + timeline
c1, c2, c3 = st.columns([1.2, 1.6, 1.2])
with c1:
    st.markdown("### 🏁 Lifestyle Stability")
    stability = compute_lifestyle_stability(user["stats"])
    st.progress(stability / 100.0)
    st.markdown(f"**{stability} / 100** — {get_life_rank(stability)}")
    st.caption("Stability is an aggregated, behavior-driven measure of life balance.")
    st.markdown("### Quick Status")
    # show small stat pills
    stat_line = " • ".join([f"{k}: {user['stats'][k]}" for k in ["Sleep","Energy","Hunger","Stress","Routine","Social"]])
    st.markdown(f"<div class='small'>{stat_line}</div>", unsafe_allow_html=True)

with c2:
    st.markdown("### 💬 Buddy")
    buddy_msg = buddy_suggestion(user["stats"], stability)
    # expressive bubble
    st.markdown(f"<div class='card'><strong style='font-size:16px'>Buddy:</strong><p style='margin-top:6px'>{buddy_msg}</p></div>", unsafe_allow_html=True)
    # contextual tips (small)
    tips = []
    if user["stats"]["Hunger"] < 35:
        tips.append("Try eating a small meal.")
    if user["stats"]["Energy"] < 40:
        tips.append("Short nap or easy movement could help.")
    if user["stats"]["Stress"] > 65:
        tips.append("Mini-break: 5 minutes of leisure or breathing.")
    if tips:
        st.markdown("<div class='muted'>Suggestions: " + " • ".join(tips) + "</div>", unsafe_allow_html=True)

with c3:
    st.markdown("### 🕰️ Day Timeline")
    phase = user.get("last_phase", DAY_PHASES[0])
    phase_choice = st.selectbox("Phase", DAY_PHASES, index=DAY_PHASES.index(phase))
    if st.button("Advance Time (pass to selected phase)"):
        # apply passive drift for the chosen phase
        user["stats"] = passive_time_advance(user["stats"], phase_choice)
        user["last_phase"] = phase_choice
        user["last_time"] = datetime.utcnow().isoformat()
        save_user(user)
        st.experimental_rerun()
    st.markdown(f"Current: **{user.get('last_phase','Morning')}**")

st.markdown("---")

# main area: left activities & history, right star chart & controls
left, right = st.columns([2,1])

with left:
    st.markdown("## 🧭 Choose an Activity (one at a time)")
    st.markdown("Actions are natural activities — they update your life stats in small, realistic ways.")
    action_cols = st.columns([1,1,1])
    # show action buttons grouped
    for i, action in enumerate(ACTIONS):
        col = action_cols[i % len(action_cols)]
        if col.button(action["name"]):
            # record before/after for history
            before = dict(user["stats"])
            user["stats"] = apply_action(user["stats"], action["name"])
            after = dict(user["stats"])
            # compute effects difference
            effects = {k: after[k] - before.get(k, 0) for k in after}
            record_history(user, action["name"], effects)
            user["last_time"] = datetime.utcnow().isoformat()
            save_user(user)
            st.experimental_rerun()

    st.markdown("---")
    st.markdown("## 📊 Current Stats")
    # show stat bars with color coding and values; minimalistic labels
    for sname, sval in user["stats"].items():
        # determine color (green/yellow/red)
        if sname == "Stress":
            # reversed meaning: lower is better
            if sval <= 30:
                color = "green"
            elif sval <= 60:
                color = "yellow"
            else:
                color = "red"
        else:
            if sval >= 70:
                color = "green"
            elif sval >= 40:
                color = "yellow"
            else:
                color = "red"
        st.markdown(f"**{sname}** — {sval}  ")
        st.progress(sval / 100.0)

    st.markdown("---")
    st.markdown("## 📜 Recent Activity (demo history)")
    history = user.get("history", [])
    if not history:
        st.markdown("<div class='muted'>No actions yet. Try an activity above to see changes and history.</div>", unsafe_allow_html=True)
    else:
        # show last 12 actions
        for entry in history[:12]:
            t = entry["time"][:19].replace("T", " ")
            act = entry["action"]
            eff = entry["effects"]
            eff_text = ", ".join([f"{k}{'+' if v>=0 else ''}{v}" for k,v in eff.items() if v != 0])
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
        st.experimental_rerun()

    if st.button("Simulate rough day (fast)"):
        # apply a sequence of events to simulate a rough day: less sleep, more stress, lower energy/hunger
        user["stats"]["Sleep"] = clamp(user["stats"]["Sleep"] - 30)
        user["stats"]["Energy"] = clamp(user["stats"]["Energy"] - 30)
        user["stats"]["Hunger"] = clamp(user["stats"]["Hunger"] - 40)
        user["stats"]["Stress"] = clamp(user["stats"]["Stress"] + 30)
        user["last_time"] = datetime.utcnow().isoformat()
        record_history(user, "Simulate rough day", {"Sleep": -30, "Energy": -30, "Hunger": -40, "Stress": +30})
        save_user(user)
        st.experimental_rerun()

    if st.button("Simulate recovery (fast)"):
        user["stats"]["Sleep"] = clamp(user["stats"]["Sleep"] + 30)
        user["stats"]["Energy"] = clamp(user["stats"]["Energy"] + 30)
        user["stats"]["Hunger"] = clamp(user["stats"]["Hunger"] + 20)
        user["stats"]["Stress"] = clamp(user["stats"]["Stress"] - 25)
        user["last_time"] = datetime.utcnow().isoformat()
        record_history(user, "Simulate recovery", {"Sleep": +30, "Energy": +30, "Hunger": +20, "Stress": -25})
        save_user(user)
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("## 📝 Notes (demo)")
    notes = st.text_area("Short notes (saved locally)", value=user.get("notes",""), height=120)
    if st.button("Save notes"):
        user["notes"] = notes
        save_user(user)
        st.success("Notes saved locally.")

st.markdown("---")
st.markdown("<div class='muted'>Design goals: subtle feedback, behavior-driven progression, non-intrusive UI. This demo stores data locally in user_data.json for convenience; do not use this pattern for production user data.</div>", unsafe_allow_html=True)
