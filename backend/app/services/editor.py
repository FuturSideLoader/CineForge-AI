import subprocess
from pathlib import Path


def create_concat_file(video_paths: list[str], exports_dir: str) -> Path:
    concat_file = Path(exports_dir) / "concat_list.txt"

    with open(concat_file, "w", encoding="utf-8") as f:
        for video_path in video_paths:
            safe_path = str(Path(video_path).resolve())
            f.write(f"file '{safe_path}'\n")

    return concat_file


def assemble_final_movie(project_data: dict) -> dict:
    scenes = project_data["script"].get("scenes", [])
    exports_dir = project_data["folders"]["exports"]

    video_paths = []

    for scene in scenes:
        video_render = scene.get("video_render", {})
        video_path = video_render.get("path")

        if video_path and Path(video_path).exists():
            video_paths.append(video_path)

    if not video_paths:
        raise RuntimeError("Aucune vidéo de scène trouvée pour le montage final.")

    output_path = Path(exports_dir) / "final_movie.mp4"
    concat_file = create_concat_file(video_paths, exports_dir)

    command = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_path)
    ]

    subprocess.run(command, check=True)

    project_data["final_export"] = {
        "status": "exported",
        "format": "mp4",
        "path": str(output_path),
        "scene_count": len(video_paths)
    }

    project_data["status"] = "final_movie_exported"

    return project_data