# model_metadata.py
# Модуль для отримання метаданих локальних моделей Ollama
import os
import json

OLLAMA_MANIFESTS_DIR = os.path.join(os.path.dirname(__file__), '../../OLLama_Models/manifests')

class ModelMetadata:
    def __init__(self, model_name):
        self.model_name = model_name
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        manifest_path = os.path.join(OLLAMA_MANIFESTS_DIR, f'{self.model_name}.json')
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get_ram_requirement(self):
        return self.metadata.get('ram', None)

    def get_gpu_requirement(self):
        return self.metadata.get('gpu', None)

    def get_quantization(self):
        return self.metadata.get('quantization', None)

    def supports_vision(self):
        return self.metadata.get('vision', False)

    def get_description(self):
        return self.metadata.get('description', '')

    def get_all(self):
        return self.metadata
