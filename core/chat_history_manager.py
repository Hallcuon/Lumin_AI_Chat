# chat_history_manager.py
import os
import json

class ChatHistoryManager:
    def __init__(self, history_dir, char_name):
        self.history_dir = history_dir
        self.char_name = char_name
        os.makedirs(history_dir, exist_ok=True)
        self.last_session_path = os.path.join(history_dir, "last_session.json")

    def save_history(self, messages, char_name=None):
        if char_name is None:
            char_name = self.char_name
        history = [m for m in messages if m.get('role') != 'system']
        try:
            with open(self.last_session_path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save history: {e}")

    def load_last_history(self, system_prompt):
        if os.path.exists(self.last_session_path):
            try:
                with open(self.last_session_path, "r", encoding="utf-8") as f:
                    imported = json.load(f)
                    return [{'role': 'system', 'content': system_prompt}] + imported
            except Exception as e:
                print(f"[ERROR] Failed to load history: {e}")
        return [{'role': 'system', 'content': system_prompt}]

    def export_history(self, messages, file_path):
        history = [m for m in messages if m.get('role') != 'system']
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def import_history(self, file_path, system_prompt):
        if file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                imported = json.load(f)
                return [{'role': 'system', 'content': system_prompt}] + imported
        return [{'role': 'system', 'content': system_prompt}]

    def clear_history(self, system_prompt):
        return [{'role': 'system', 'content': system_prompt}]
