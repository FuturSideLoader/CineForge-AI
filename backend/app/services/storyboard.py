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


def generate_storyboard_for_scene(scene: dict, language: str = "fr") -> dict:
    prompt = f"""
Tu es Storyboard AI pour CineForge AI.

Langue : {language}

Voici la scène complète :
{json.dumps(scene, ensure_ascii=False, indent=2)}

Ta mission :
Créer un storyboard détaillé compatible génération image et vidéo IA.

Réponds uniquement en JSON valide.

Structure obligatoire :
{{
  "visual_description": "",
  "image_prompt": "",
  "video_prompt": "",
  "negative_prompt": "",
  "first_frame_description": "",
  "last_frame_description": "",
  "continuity_notes": ""
}}

Contraintes :
- Le prompt image doit être très visuel.
- Le prompt vidéo doit inclure le mouvement caméra.
- Garde les personnages, vêtements, lieux et ambiance cohérents.
- Le negative_prompt doit éviter les défauts IA vidéo.
- Aucun texte hors JSON.
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


def generate_storyboard_for_script(script: dict, language: str = "fr") -> dict:
    scenes = script.get("scenes", [])

    print(f"[Storyboard AI] Nombre de scènes reçues : {len(scenes)}")

    for index, scene in enumerate(scenes):
        print(f"[Storyboard AI] Génération storyboard scène {index + 1}")

        try:
            storyboard = generate_storyboard_for_scene(scene, language)
        except Exception as error:
            print(f"[Storyboard AI] Erreur scène {index + 1} : {error}")

            storyboard = {
                "visual_description": scene.get("description", ""),
                "image_prompt": scene.get("video_prompt", ""),
                "video_prompt": scene.get("video_prompt", ""),
                "negative_prompt": "bad anatomy, distorted face, extra fingers, blurry, low quality, flickering, inconsistent character, inconsistent clothing",
                "first_frame_description": "Opening cinematic frame of the scene.",
                "last_frame_description": "Final cinematic frame of the scene.",
                "continuity_notes": "Fallback storyboard generated because Storyboard AI failed."
            }

        scene["storyboard"] = storyboard
        scenes[index] = scene

        print(f"[Storyboard AI] Storyboard ajouté scène {index + 1}")

    script["scenes"] = scenes
    return script