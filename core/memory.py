import json
import os

def get_memory_file(character_name):
    safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_')
    if not safe_name:
        safe_name = "default_character"
    mem_dir = 'chat_histories'
    os.makedirs(mem_dir, exist_ok=True)
    return os.path.join(mem_dir, f"long_term_memory_{safe_name}.json")

# Load long-term memory
def load_long_term_memory(character_name):
    file_path = get_memory_file(character_name)
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# Save long-term memory
def save_long_term_memory(character_name, memory):
    file_path = get_memory_file(character_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# Add new fact to memory
def add_fact_to_memory(character_name, fact):
    memory = load_long_term_memory(character_name)
    if fact not in memory:
        memory.append(fact)
        save_long_term_memory(character_name, memory)
    return memory
