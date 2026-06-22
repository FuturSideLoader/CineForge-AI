import re


def slugify_character_name(name: str) -> str:
    text = name.lower().strip()
    text = re.sub(r"[^a-z0-9àâäéèêëîïôöùûüç]+", "_", text)
    text = text.strip("_")
    return text or "character"


def build_character_id(character: dict, index: int) -> str:
    name = character.get("name", f"character_{index}")
    slug = slugify_character_name(name)
    return f"char_{index:02d}_{slug}"


def generate_character_sheet(character: dict, index: int) -> dict:
    character_id = build_character_id(character, index)

    name = character.get("name", "")
    age = character.get("age", "")
    role = character.get("role", "")
    personality = character.get("personality", "")
    visual_description = character.get("visual_description", "")

    locked_prompt = (
        f"{name}, {age}, {role}. "
        f"Personality: {personality}. "
        f"Visual appearance: {visual_description}. "
        "Keep same face, same age, same body shape, same hairstyle, same clothing style, "
        "same cinematic identity across all scenes."
    )

    return {
        "character_id": character_id,
        "name": name,
        "age": age,
        "role": role,
        "personality": personality,
        "visual_description": visual_description,
        "locked_visual_prompt": locked_prompt,
        "reference_images": {
            "face": None,
            "body": None,
            "expressions": []
        },
        "consistency_rules": [
            "same face across all scenes",
            "same hairstyle across all scenes",
            "same clothing style unless the script explicitly changes it",
            "same body shape and age",
            "no random face changes",
            "no random outfit changes"
        ]
    }


def generate_character_consistency(script: dict) -> dict:
    characters = script.get("characters", [])
    character_sheets = []

    print(f"[Character Consistency AI] Nombre de personnages : {len(characters)}")

    for index, character in enumerate(characters, start=1):
        sheet = generate_character_sheet(character, index)
        character_sheets.append(sheet)

        character["character_id"] = sheet["character_id"]
        character["locked_visual_prompt"] = sheet["locked_visual_prompt"]

        print(
            f"[Character Consistency AI] Character ID créé : "
            f"{sheet['character_id']}"
        )

    script["characters"] = characters
    script["character_sheets"] = character_sheets

    return script


def find_characters_in_scene(scene: dict, character_sheets: list[dict]) -> list[dict]:
    scene_text_parts = [
        scene.get("title", ""),
        scene.get("description", ""),
        scene.get("video_prompt", "")
    ]

    for dialogue in scene.get("dialogues", []):
        scene_text_parts.append(dialogue.get("character", ""))
        scene_text_parts.append(dialogue.get("line", ""))

    scene_text = " ".join(scene_text_parts).lower()

    found = []

    for sheet in character_sheets:
        name = sheet.get("name", "").lower()

        if name and name in scene_text:
            found.append(sheet)

    return found


def inject_character_consistency_into_scenes(script: dict) -> dict:
    scenes = script.get("scenes", [])
    character_sheets = script.get("character_sheets", [])

    for index, scene in enumerate(scenes):
        characters_in_scene = find_characters_in_scene(scene, character_sheets)

        scene["characters_in_scene"] = [
            {
                "character_id": character["character_id"],
                "name": character["name"],
                "locked_visual_prompt": character["locked_visual_prompt"]
            }
            for character in characters_in_scene
        ]

        if "final_video_prompt" in scene:
            character_block = "\n".join(
                character["locked_visual_prompt"]
                for character in characters_in_scene
            )

            if character_block:
                old_prompt = scene["final_video_prompt"]["prompt"]

                scene["final_video_prompt"]["prompt"] = (
                    old_prompt
                    + "\n\nCharacter consistency:\n"
                    + character_block
                )

        scenes[index] = scene

    script["scenes"] = scenes

    return script


def apply_character_consistency(script: dict) -> dict:
    script = generate_character_consistency(script)
    script = inject_character_consistency_into_scenes(script)

    return script