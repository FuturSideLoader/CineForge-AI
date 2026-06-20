import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"

def generate_directing_for_scene(scene: dict, language: str = "fr") -> dict:
    prompt = f"""
Tu est Director AI pour CineForge AI.

Langue : {language}

Voici une scène :
{json.dumps(scene, ensure_ascii=False, indent=2)}

Transforme cette scene en instructions de réalisation cinéma.

Répond uniquement en JSON validen sans markdown.

Structure obligatoire :
{{
    "camera": "",
    "shot_type": "",
    "camera_movement": "",
    "lens": "",
    "lighting": "",
    "mood": "",
    "color_grading": "",
    "visual_style": "",
    "director_notes": ""
}}

Contraintes :
- Instruction courtes mais précises.
- Style cinématographique.
- Compatible génération vidéo IA.
- Aucun texte hors JSON.
"""

    response = request.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )

    response.raise_for_status()

    raw_text = response.json()["response"].strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()


def generate_directing_for_script(script: dict, language: str = "fr") -> dict:
    scenes = script.get("scenes", [])

    for scene in scenes:
        if "dialogue" in scene and "dialogues" not in scene:
            scene["dialogues"] = scene.pop("dialogue")

            scene["directing"] = generate_directing_for_scene(
                scene=scene,
                language=language
            )

    script["scenes"] = scenes
    return script