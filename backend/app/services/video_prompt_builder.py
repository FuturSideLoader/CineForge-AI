def build_video_prompt_for_scene(scene: dict, language: str = "fr") -> dict:
    title = scene.get("title", "")
    location = scene.get("location", "")
    time = scene.get("time", "")
    description = scene.get("description", "")
    original_video_prompt = scene.get("video_prompt", "")

    directing = scene.get("directing", {})
    storyboard = scene.get("storyboard", {})

    camera = directing.get("camera", "")
    shot_type = directing.get("shot_type", "")
    camera_movement = directing.get("camera_movement", "")
    lens = directing.get("lens", "")
    lighting = directing.get("lighting", "")
    mood = directing.get("mood", "")
    color_grading = directing.get("color_grading", "")
    visual_style = directing.get("visual_style", "")

    visual_description = storyboard.get("visual_description", "")
    storyboard_video_prompt = storyboard.get("video_prompt", "")
    first_frame = storyboard.get("first_frame_description", "")
    last_frame = storyboard.get("last_frame_description", "")
    continuity_notes = storyboard.get("continuity_notes", "")

    final_prompt = f"""
Scene title: {title}
Location: {location}
Time: {time}

Main action:
{description}

Visual content:
{visual_description}

Original scene prompt:
{original_video_prompt}

Storyboard video prompt:
{storyboard_video_prompt}

Camera:
{camera}

Shot type:
{shot_type}

Camera movement:
{camera_movement}

Lens:
{lens}

Lighting:
{lighting}

Mood:
{mood}

Color grading:
{color_grading}

Visual style:
{visual_style}

First frame:
{first_frame}

Last frame:
{last_frame}

Continuity:
{continuity_notes}

Render style:
cinematic, realistic, coherent character appearance, stable clothing, stable background, movie shot, high detail, natural motion, no text on screen
""".strip()

    negative_prompt = storyboard.get(
        "negative_prompt",
        "bad anatomy, distorted face, extra fingers, blurry, low quality, flickering, unstable character, inconsistent clothing, text, watermark"
    )

    return {
        "provider": "local_video_ai",
        "target_models": [
            "ltx-video",
            "cogvideox",
            "wan",
            "hunyuanvideo"
        ],
        "duration_seconds": 8,
        "fps": 24,
        "resolution": "1280x720",
        "prompt": final_prompt,
        "negative_prompt": negative_prompt
    }


def build_video_prompts_for_script(script: dict, language: str = "fr") -> dict:
    scenes = script.get("scenes", [])

    print(f"[Video Prompt Builder] Nombre de scènes reçues : {len(scenes)}")

    for index, scene in enumerate(scenes):
        print(f"[Video Prompt Builder] Création prompt vidéo scène {index + 1}")

        scene["final_video_prompt"] = build_video_prompt_for_scene(
            scene=scene,
            language=language
        )

        scenes[index] = scene

        print(f"[Video Prompt Builder] Prompt vidéo ajouté scène {index + 1}")

    script["scenes"] = scenes
    return script