import json
import re
from pathlib import Path
from datetime import datetime

from app.services.screenwriter import generate_script
from app.services.director import generate_directing_for_script
from app.services.storyboard import generate_storyboard_for_script
from app.services.video_prompt_builder import build_video_prompts_for_script
from app.services.video_renderer import render_placeholder_videos_for_project
from app.services.music_composer import generate_placeholder_music
from app.services.editor import assemble_final_movie, mix_music_with_final_movie, burn_subtitles_into_movie
from app.services.subtitle_generator import generate_subtitles
from app.services.character_consistency import apply_character_consistency



BASE_DIR = Path(__file__).resolve().parents[2]
PROJECTS_DIR = BASE_DIR / "projects"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9àâäéèêëîïôöùûüç]+", "_", text)
    text = text.strip("_")
    return text[:60] or "cineforge_project"


def create_project_folders(project_dir: Path) -> dict:
    folders = {
        "project": str(project_dir),
        "storyboard": str(project_dir / "storyboard"),
        "videos": str(project_dir / "videos"),
        "voices": str(project_dir / "voices"),
        "music": str(project_dir / "music"),
        "sfx": str(project_dir / "sfx"),
        "exports": str(project_dir / "exports"),
        "logs": str(project_dir / "logs")
    }

    for folder_path in folders.values():
        Path(folder_path).mkdir(parents=True, exist_ok=True)

    return folders


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

    script = generate_storyboard_for_script(
        script=script,
        language=language
    )

    script = apply_character_consistency(script)

    script = build_video_prompts_for_script(
        script=script,
        language=language
    )

    title = script.get("title", "CineForge Project")
    project_slug = slugify(title)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    project_id = f"{timestamp}_{project_slug}"
    project_dir = PROJECTS_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    folders = create_project_folders(project_dir)

    project_data = {
        "project_id": project_id,
        "idea": idea,
        "language": language,
        "duration_minutes": duration_minutes,
        "scene_count": scene_count,
        "status": "video_prompts_ready",
        "folders": folders,
        "script": script
    }

    project_data = render_placeholder_videos_for_project(project_data)

    project_data = assemble_final_movie(project_data)

    project_data = generate_placeholder_music(project_data)

    project_data = mix_music_with_final_movie(project_data)

    project_data = generate_subtitles(project_data)

    project_data = burn_subtitles_into_movie(project_data)

    project_file = save_project(project_dir, project_data)

    return {
        "success": True,
        "project_id": project_id,
        "status": project_data["status"],
        "project_file": str(project_file),
        "data": project_data
    }