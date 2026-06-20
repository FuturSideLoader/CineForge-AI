import json
import re
from pathlib import Path
from datetime import datetime

from app.services.screenwriter import generate_script
from app.services.director import generate_directing_for_script


BASE_DIR = Path(__file__).resolve().parents[2]
PROJECTS_DIR = BASE_DIR / "projects"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9àâäéèêëîïôöùûüç]+", "_", text)
    text = text.strip("_")
    return text[:60] or "cineforge_project"


def save_project(project_dir: Path, project_data: dict) -> Path:
    project_file = project_dir / "project.json"

    with open(project_file, "w", encoding="utf-8") as f:
        json.dump(project_data, f, ensure_ascii=False, indent=2)

    return project_file


def create_movie_project(
    idea: str,
    language: str = "fr",
    duration_minutes: int = 2,
    scene_count: int = 5
) -> dict:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    script = generate_script(
        idea=idea,
        language=language,
        duration_minutes=duration_minutes,
        scene_count=scene_count
    )

    script = generate_directing_for_script(
        script=script,
        language=language
    )

    title = script.get("title", "CineForge Project")
    project_slug = slugify(title)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    project_id = f"{timestamp}_{project_slug}"
    project_dir = PROJECTS_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    project_data = {
        "project_id": project_id,
        "idea": idea,
        "language": language,
        "duration_minutes": duration_minutes,
        "scene_count": scene_count,
        "status": "directing_generated",
        "script": script
    }

    project_file = save_project(project_dir, project_data)

    return {
        "success": True,
        "project_id": project_id,
        "status": "directing_generated",
        "project_file": str(project_file),
        "data": project_data
    }