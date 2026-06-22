from pathlib import Path

import numpy as np
import soundfile as sf


def generate_placeholder_music(project_data: dict) -> dict:
    music_dir = Path(project_data["folders"]["music"])
    music_dir.mkdir(parents=True, exist_ok=True)

    scenes = project_data["script"].get("scenes", [])
    duration_seconds = sum(
        scene.get("final_video_prompt", {}).get("duration_seconds", 8)
        for scene in scenes
    )

    sample_rate = 44100
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), False)

    base = 0.12 * np.sin(2 * np.pi * 110 * t)
    pad = 0.08 * np.sin(2 * np.pi * 220 * t)
    pulse = 0.04 * np.sin(2 * np.pi * 55 * t)

    audio = base + pad + pulse
    audio = audio / np.max(np.abs(audio)) * 0.3

    output_path = music_dir / "placeholder_music.wav"

    sf.write(output_path, audio, sample_rate)

    project_data["music"] = {
        "status": "generated",
        "type": "placeholder",
        "path": str(output_path),
        "duration_seconds": duration_seconds
    }

    project_data["status"] = "music_generated"

    return project_data