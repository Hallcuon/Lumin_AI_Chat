# prompt_manager.py
class PromptManager:
    def __init__(self, default_prompt):
        self.system_prompt = default_prompt

    def set_manual_prompt(self, manual_prompt):
        if manual_prompt:
            self.system_prompt = manual_prompt
        return self.system_prompt

    def get_prompt(self):
        return self.system_prompt
