import subprocess
from pathlib import Path
import re


def render_placeholder_video_for_scene(scene: dict, videos_dir: str) -> dict:
    scene_number = scene.get("scene_number", 0)
    title = scene.get("title", f"Scene {scene_number}")
    description = scene.get("description", "")

    final_video_prompt = scene.get("final_video_prompt", {})
    duration_seconds = final_video_prompt.get("duration_seconds", 8)

    output_path = Path(videos_dir) / f"scene_{scene_number:02d}.mp4"

    text = f"SCENE {scene_number} - {title}"

    safe_text = re.sub(r"[^a-zA-Z0-9À-ÿ _-]", "", text)

    command = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s=1280x720:d={duration_seconds}",
        "-vf",
        (
            "drawtext="
            "fontcolor=white:"
            "fontsize=34:"
            "x=(w-text_w)/2:"
            "y=(h-text_h)/2:"
            f"text={safe_text}"
        ),
        "-r", "24",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]

    subprocess.run(command, check=True)

    return {
        "status": "rendered",
        "type": "placeholder",
        "path": str(output_path),
        "duration_seconds": duration_seconds
    }


def render_placeholder_videos_for_project(project_data: dict) -> dict:
    videos_dir = project_data["folders"]["videos"]
    scenes = project_data["script"].get("scenes", [])

    print(f"[Video Renderer] Nombre de scènes reçues : {len(scenes)}")

    for index, scene in enumerate(scenes):
        print(f"[Video Renderer] Rendu placeholder scène {index + 1}")

        render_info = render_placeholder_video_for_scene(
            scene=scene,
            videos_dir=videos_dir
        )

        scene["video_render"] = render_info
        scenes[index] = scene

        print(f"[Video Renderer] Vidéo créée : {render_info['path']}")

    project_data["script"]["scenes"] = scenes
    project_data["status"] = "placeholder_videos_rendered"

    return project_data