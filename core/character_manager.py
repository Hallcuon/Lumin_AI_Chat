import os
import json

CHARACTER_DIR = 'characters'
HISTORY_FILES_DIR = 'chat_histories'

def get_character_history_file(character_name):
    safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    if not safe_name:
        safe_name = "default_character"
    os.makedirs(HISTORY_FILES_DIR, exist_ok=True)
    return os.path.join(HISTORY_FILES_DIR, f"chat_history_{safe_name}.json")

def save_chat_history(messages_to_save, character_name):
    history_file = get_character_history_file(character_name)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(messages_to_save, f, ensure_ascii=False, indent=4)

def load_chat_history(character_name):
    history_file = get_character_history_file(character_name)
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def load_character_prompt(character_name):
    file_path = os.path.join(CHARACTER_DIR, f"{character_name}.txt")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return None
