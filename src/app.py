"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import json
from pydantic import BaseModel

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")


# Modelo para criação/atualização de atividade
class Activity(BaseModel):
    name: str
    description: str
    schedule: str
    max_participants: int
    participants: list[str] = []
# Caminho para o arquivo de atividades
ACTIVITIES_FILE = current_dir / "activities.json"

def load_activities():
    if ACTIVITIES_FILE.exists():
        with open(ACTIVITIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_activities(activities):
    with open(ACTIVITIES_FILE, "w", encoding="utf-8") as f:
        json.dump(activities, f, ensure_ascii=False, indent=2)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Retorna todas as atividades como um dicionário por nome"""
    activities = load_activities()
    # Retorna como dict para compatibilidade com frontend
    return {a["name"]: a for a in activities}
# Criar nova atividade
@app.post("/activities")
def create_activity(activity: Activity):
    activities = load_activities()
    if any(a["name"] == activity.name for a in activities):
        raise HTTPException(status_code=400, detail="Activity already exists")
    activities.append(activity.dict())
    save_activities(activities)
    return {"message": f"Activity '{activity.name}' created"}

# Atualizar atividade
@app.put("/activities/{activity_name}")
def update_activity(activity_name: str, activity: Activity):
    activities = load_activities()
    for i, a in enumerate(activities):
        if a["name"] == activity_name:
            # Mantém os participantes existentes se não vier no payload
            if not activity.participants:
                activity.participants = a["participants"]
            activities[i] = activity.dict()
            save_activities(activities)
            return {"message": f"Activity '{activity_name}' updated"}
    raise HTTPException(status_code=404, detail="Activity not found")

# Excluir atividade
@app.delete("/activities/{activity_name}")
def delete_activity(activity_name: str):
    activities = load_activities()
    for i, a in enumerate(activities):
        if a["name"] == activity_name:
            activities.pop(i)
            save_activities(activities)
            return {"message": f"Activity '{activity_name}' deleted"}
    raise HTTPException(status_code=404, detail="Activity not found")
@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Inscreve um estudante em uma atividade"""
    activities = load_activities()
    for activity in activities:
        if activity["name"] == activity_name:
            if email in activity["participants"]:
                raise HTTPException(status_code=400, detail="Student is already signed up")
            if len(activity["participants"]) >= activity["max_participants"]:
                raise HTTPException(status_code=400, detail="Activity is full")
            activity["participants"].append(email)
            save_activities(activities)
            return {"message": f"Signed up {email} for {activity_name}"}
    raise HTTPException(status_code=404, detail="Activity not found")


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Remove um estudante de uma atividade"""
    activities = load_activities()
    for activity in activities:
        if activity["name"] == activity_name:
            if email not in activity["participants"]:
                raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
            activity["participants"].remove(email)
            save_activities(activities)
            return {"message": f"Unregistered {email} from {activity_name}"}
    raise HTTPException(status_code=404, detail="Activity not found")
