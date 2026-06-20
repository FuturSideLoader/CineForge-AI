from fastapi import FastAPI
from pydantic import BaseModel
from app.services.project_manager import create_movie_project

app = FastAPI(title="CineForge AI", version="0.1.0")


class ProjectRequest(BaseModel):
    idea: str
    language: str = "fr"
    duration_minutes: int = 2
    scene_count: int = 5

@app.get("/")
def root():
    return {
        "name": "CineForge AI",
        "status": "running",
        "version": "0.1.0"
    }

@app.post("/projects/create")
def create_project(request:ProjectRequest):
    return create_movie_project(
        idea=request.idea,
        language=request.language,
        duration_minutes=request.duration_minutes,
        scene_count=request.scene_count
    )