from fastapi import Depends, FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
from .auth import require
from . import metrics as m, nutrition as n, vision, agents

app = FastAPI(title="AuraHealth Core", version="1.0.0")
Instrumentator().instrument(app).expose(app)
coach = agents.build()

class Profile(BaseModel):
    sex: str = Field(pattern="^(male|female)$")
    age: int = Field(ge=14, le=100); weight_kg: float = Field(gt=25, lt=350)
    height_cm: float = Field(gt=100, lt=250)
    neck_cm: float; waist_cm: float; hip_cm: float | None = None
    activity: str = "moderate"; goal: m.Goal = m.Goal.maintain
    level: str = "beginner"; allergies: list[str] = []; insulin_sensitive: bool = False

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/v1/analyze", dependencies=[Depends(require("user"))])
def analyze(p: Profile):
    if p.activity not in m.ACTIVITY: raise HTTPException(422, "unknown activity")
    if p.level not in ("beginner", "intermediate", "advanced"): raise HTTPException(422, "unknown level")
    bmr = m.bmr(p.weight_kg, p.height_cm, p.age, p.sex)
    tdee = bmr * m.ACTIVITY[p.activity]
    target = tdee * (1 + m.KCAL_ADJ[p.goal])
    bf = m.navy_body_fat(p.sex, p.height_cm, p.neck_cm, p.waist_cm, p.hip_cm)
    return {"bmi": round(m.bmi(p.weight_kg, p.height_cm), 1), "bmr": round(bmr), "tdee": round(tdee),
            "target_kcal": round(target), "body_fat_pct": round(bf, 1),
            "lean_mass_kg": round(p.weight_kg * (1 - bf / 100), 1),
            "macros": m.macros(target, p.weight_kg, p.goal),
            "prescription": n.prescribe(p.goal.value, {a.lower() for a in p.allergies}, p.insulin_sensitive),
            "training": n.training_plan(p.level, p.goal.value)}

@app.post("/v1/food/scan", dependencies=[Depends(require("user"))])
async def scan(image: UploadFile = File(...), eat: str = Form(""), avoid: str = Form("")):
    if image.content_type not in ("image/jpeg", "image/png", "image/webp"): raise HTTPException(415, "unsupported image")
    data = await image.read()
    if len(data) > 8_000_000: raise HTTPException(413, "image too large")
    return vision.scan(data, set(filter(None, eat.split(","))), set(filter(None, avoid.split(","))))

@app.post("/v1/coach/brief", dependencies=[Depends(require("user"))])
def brief(profile: dict):
    out = coach.invoke({"profile": profile, "intent": "daily_brief", "notes": [], "briefing": "", "iterations": 0})
    return {"briefing": out["briefing"]}
