import json
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"


def clean_json_response(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1:
        cleaned = cleaned[start:end + 1]

    return json.loads(cleaned)


def generate_directing_for_scene(scene: dict, language: str = "fr") -> dict:
    prompt = f"""
Tu es Director AI pour CineForge AI.

Langue : {language}

Voici une scène :
{json.dumps(scene, ensure_ascii=False, indent=2)}

Génère les instructions de réalisation cinéma.

Réponds uniquement en JSON valide.

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
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )

    response.raise_for_status()
    raw_text = response.json()["response"]

    return clean_json_response(raw_text)


def generate_directing_for_script(script: dict, language: str = "fr") -> dict:
    scenes = script.get("scenes", [])

    print(f"[Director AI] Nombre de scènes reçues : {len(scenes)}")

    for index, scene in enumerate(scenes):
        print(f"[Director AI] Génération directing scène {index + 1}")

        if "dialogue" in scene and "dialogues" not in scene:
            scene["dialogues"] = scene.pop("dialogue")

        try:
            directing = generate_directing_for_scene(scene, language)
        except Exception as error:
            print(f"[Director AI] Erreur scène {index + 1} : {error}")

            directing = {
                "camera": "Static cinematic camera",
                "shot_type": "Medium shot",
                "camera_movement": "Slow push in",
                "lens": "50mm",
                "lighting": "Cinematic soft lighting",
                "mood": "Mysterious",
                "color_grading": "Dark blue cinematic tones",
                "visual_style": "Realistic cinematic style",
                "director_notes": "Fallback generated because Director AI failed."
            }

        scene["directing"] = directing
        scenes[index] = scene

        print(f"[Director AI] Directing ajouté scène {index + 1}")

    script["scenes"] = scenes
    return script