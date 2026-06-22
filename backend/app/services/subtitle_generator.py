from pathlib import Path


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def generate_subtitles(project_data: dict) -> dict:
    exports_dir = Path(project_data["folders"]["exports"])
    subtitles_path = exports_dir / "subtitles.srt"

    scenes = project_data["script"].get("scenes", [])

    current_time = 0.0
    subtitle_index = 1

    lines = []

    for scene in scenes:
        duration = scene.get("final_video_prompt", {}).get("duration_seconds", 8)
        dialogues = scene.get("dialogues", [])

        if not dialogues:
            current_time += duration
            continue

        dialogue_duration = duration / max(len(dialogues), 1)

        for dialogue in dialogues:
            start = current_time
            end = current_time + dialogue_duration

            character = dialogue.get("character", "")
            line = dialogue.get("line", "")

            text = f"{character}: {line}" if character else line

            lines.append(str(subtitle_index))
            lines.append(f"{format_timestamp(start)} --> {format_timestamp(end)}")
            lines.append(text)
            lines.append("")

            subtitle_index += 1
            current_time = end

    with open(subtitles_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    project_data["subtitles"] = {
        "status": "generated",
        "format": "srt",
        "path": str(subtitles_path)
    }

    project_data["status"] = "subtitles_generated"

    return project_data