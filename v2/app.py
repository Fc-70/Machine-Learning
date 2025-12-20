# Life Simulation Prototype with Dialogue + Actions

import random

# -----------------------------
# Player Stats
# -----------------------------
player_stats = {
    "Energy": 50,
    "Hunger": 50,
    "Stress": 30,
    "Routine": 70,
    "Social": 40
}

# -----------------------------
# Actions Mapping
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
# Rank Calculation
# -----------------------------
def calculate_rank(stats):
    # Higher is better: Energy, Routine, Social; Lower is better: Stress, Hunger
    weighted_score = (
        stats["Energy"] +
        (100 - stats["Hunger"]) +
        (100 - stats["Stress"]) +
        stats["Routine"] +
        stats["Social"]
    ) / 5
    return weighted_score

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
# Display Stats
# -----------------------------
def show_stats():
    print("\n--- Current Stats ---")
    for stat, value in player_stats.items():
        clamped = max(0, min(100, value))
        print(f"{stat}: {clamped}")
    score = calculate_rank(player_stats)
    print(f"Overall Life Rank: {get_rank(score)} ({int(score)}/100)")
    print("--------------------\n")

# -----------------------------
# Process Player Input
# -----------------------------
def process_input(user_input):
    user_input = user_input.lower().strip()
    
    # Detect *action*
    if user_input.startswith("*") and user_input.endswith("*"):
        action_name = user_input[1:-1].strip()
        if action_name in actions:
            for stat, change in actions[action_name].items():
                player_stats[stat] += change
            print(f"✅ Action performed: {action_name}")
            # Random flavor text
            flavor = random.choice([
                "That felt productive!",
                "You feel a little different now.",
                "Nice choice, keep it up!",
                "You notice a subtle change in your day."
            ])
            print(f"💬 {flavor}")
        else:
            print(f"❌ Unknown action: {action_name}")
    else:
        # Treat as dialogue
        print(f"🗨️ You said: '{user_input}'")
        # Dialogue slightly affects Social
        player_stats["Social"] += 2
        # Random flavor text
        flavor = random.choice([
            "Your interaction brightened your day.",
            "Talking helps you feel connected.",
            "You feel a small boost in mood."
        ])
        print(f"💬 {flavor}")

    # Clamp stats to 0–100
    for key in player_stats:
        player_stats[key] = max(0, min(100, player_stats[key]))

# -----------------------------
# Main Game Loop
# -----------------------------
def main():
    print("Welcome to Life Simulation Prototype!")
    print("Type your dialogue or actions (use *action* for actions). Type 'quit' to exit.\n")
    
    while True:
        show_stats()
        user_input = input("Enter dialogue or action (*action*): ")
        if user_input.lower() in ["quit", "exit"]:
            print("Exiting Life Simulation. Goodbye!")
            break
        process_input(user_input)

# -----------------------------
# Run Game
# -----------------------------
if __name__ == "__main__":
    main()
