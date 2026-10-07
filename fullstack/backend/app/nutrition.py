"""Rule-based Foods to Eat / Avoid matrix (GI, allergens, goal)."""
FOODS = [  # name, GI, allergens
    ("Oats", 55, {"gluten"}), ("Lentils", 32, set()), ("Greek yogurt", 11, {"dairy"}),
    ("Eggs", 0, {"egg"}), ("Chicken breast", 0, set()), ("Salmon", 0, {"fish"}),
    ("Quinoa", 53, set()), ("Almonds", 15, {"nuts"}), ("Leafy greens", 15, set()),
    ("Paneer", 27, {"dairy"}), ("White rice", 73, set()), ("White bread", 75, {"gluten"}),
    ("Sugary drinks", 90, set()), ("Pastries", 80, {"gluten", "dairy"}),
]

def prescribe(goal: str, allergies: set[str], insulin_sensitive: bool):
    gi_cap = 55 if (insulin_sensitive or goal == "aggressive_fat_loss") else 70
    eat, avoid = [], []
    for name, gi, alg in FOODS:
        if alg & allergies: avoid.append({"food": name, "reason": "allergen"})
        elif gi > gi_cap: avoid.append({"food": name, "reason": f"GI {gi} above cap {gi_cap}"})
        else: eat.append({"food": name, "gi": gi})
    return {"gi_cap": gi_cap, "eat": eat, "avoid": avoid}

def training_plan(level: str, goal: str):
    base = {"beginner": {"zone2_min_week": 150, "hiit": "none until week 4", "strength": "3x full body"},
            "intermediate": {"zone2_min_week": 180, "hiit": "1x 8x30s/90s", "strength": "4x upper/lower, double progression"},
            "advanced": {"zone2_min_week": 200, "hiit": "2x 6x1min/2min", "strength": "5x PPL, RPE-based overload"}}[level]
    base["fasting_window"] = "14:10" if level == "beginner" else "16:8"
    if goal == "lean_bulk": base["hiit"] = "max 1x/week to protect recovery"
    return base
