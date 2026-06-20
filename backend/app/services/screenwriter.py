import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"


def generate_script(idea: str, language:str, duration_minutes: int, scene_count: int) -> dict:
    prompt = f"""
Tu est Screenwriter AI, le scenariste principal de CineForge AI.

Langue de sortie : {language}
Durée cible : {duration_minutes} minutes
Nombre de scènes : {scene_count}

Idée utilisateur :
{idea}

Tu dois générer un court-métrage structuré.

Répond uniquement en JSON valide, sans markdown.

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
- Ne mets aucun commentaires hors JSON.
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

    raw_text = response.json()["response"].strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)