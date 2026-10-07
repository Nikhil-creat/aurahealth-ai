"""Pure health math: Mifflin-St Jeor, TDEE, US Navy body fat, LBM, macros."""
from math import log10
from enum import Enum

class Goal(str, Enum):
    fat_loss = "aggressive_fat_loss"; bulk = "lean_bulk"
    recomp = "recomposition"; maintain = "maintenance"

ACTIVITY = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "high": 1.725, "athlete": 1.9}
KCAL_ADJ = {Goal.fat_loss: -0.25, Goal.bulk: 0.10, Goal.recomp: -0.05, Goal.maintain: 0.0}
PROTEIN_G_PER_KG = {Goal.fat_loss: 2.4, Goal.bulk: 2.0, Goal.recomp: 2.2, Goal.maintain: 1.8}

def bmi(kg, cm): return kg / (cm / 100) ** 2

def bmr(kg, cm, age, sex):
    return 10 * kg + 6.25 * cm - 5 * age + (5 if sex == "male" else -161)

def navy_body_fat(sex, cm, neck, waist, hip=None):
    h, n, w = cm / 2.54, neck / 2.54, waist / 2.54
    if sex == "male":
        bf = 495 / (1.0324 - 0.19077 * log10(w - n) + 0.15456 * log10(h)) - 450
    else:
        p = (hip or waist) / 2.54
        bf = 495 / (1.29579 - 0.35004 * log10(w + p - n) + 0.22100 * log10(h)) - 450
    return max(2.0, min(60.0, bf))

def macros(target_kcal, kg, goal: Goal):
    p = PROTEIN_G_PER_KG[goal] * kg
    f = 0.25 * target_kcal / 9
    c = max(0.0, (target_kcal - p * 4 - f * 9) / 4)
    return {"protein_g": round(p), "carbs_g": round(c), "fat_g": round(f)}
