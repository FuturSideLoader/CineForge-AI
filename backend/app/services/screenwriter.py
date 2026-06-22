import json
import re
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"


def extract_json_block(raw_text: str) -> str:
    cleaned = raw_text.strip()
    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1:
        cleaned = cleaned[start:end + 1]

    return cleaned


def remove_invalid_control_chars(text: str) -> str:
    return "".join(
        char
        for char in text
        if char == "\n" or char == "\r" or char == "\t" or ord(char) >= 32
    )


def repair_common_json_errors(text: str) -> str:
    text = remove_invalid_control_chars(text)

    text = text.replace("\r\n", "\\n")
    text = text.replace("\r", "\\n")

    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)

    return text


def parse_llm_json(raw_text: str) -> dict:
    cleaned = extract_json_block(raw_text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        repaired = repair_common_json_errors(cleaned)
        return json.loads(repaired)


def normalize_script(script: dict) -> dict:
    scenes = script.get("scenes", [])

    for scene in scenes:
        if "dialogue" in scene and "dialogues" not in scene:
            scene["dialogues"] = scene.pop("dialogue")

        if "dialogues" not in scene:
            scene["dialogues"] = []

        if "sound_effects" not in scene:
            scene["sound_effects"] = []

        if "video_prompt" not in scene:
            scene["video_prompt"] = scene.get("description", "")

        if "music_prompt" not in scene:
            scene["music_prompt"] = "cinematic ambient music"

    script["scenes"] = scenes

    if "characters" not in script:
        script["characters"] = []

    if "title" not in script:
        script["title"] = "CineForge Project"

    if "logline" not in script:
        script["logline"] = ""

    if "synopsis" not in script:
        script["synopsis"] = ""

    return script


def generate_script(idea: str, language: str, duration_minutes: int, scene_count: int) -> dict:
    prompt = f"""
Tu es Screenwriter AI, le scénariste principal de CineForge AI.

Langue de sortie : {language}
Durée cible : {duration_minutes} minutes
Nombre exact de scènes : {scene_count}

Idée utilisateur :
{idea}

Tu dois générer un court-métrage structuré.

IMPORTANT :
Réponds uniquement en JSON valide.
Pas de markdown.
Pas de commentaire.
Pas de retour à la ligne à l'intérieur des valeurs texte JSON.
Tous les dialogues doivent être sur une seule ligne.
Utilise toujours le champ "dialogues", jamais "dialogue".

Structure obligatoire :
{{
  "title": "",
  "logline": "",
  "synopsis": "",
  "characters": [
    {{
      "name": "",
      "age": "",
      "role": "",
      "personality": "",
      "visual_description": ""
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "title": "",
      "location": "",
      "time": "",
      "description": "",
      "dialogues": [
        {{
          "character": "",
          "line": ""
        }}
      ],
      "video_prompt": "",
      "music_prompt": "",
      "sound_effects": []
    }}
  ]
}}

Contraintes :
- Le scénario doit être cohérent.
- Les scènes doivent pouvoir être générées en vidéo IA.
- Les descriptions visuelles doivent être précises.
- Les dialogues doivent être courts.
- Exactement {scene_count} scènes.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        },
        timeout=180
    )

    response.raise_for_status()

    raw_text = response.json()["response"].strip()

    script = parse_llm_json(raw_text)
    script = normalize_script(script)

    return script