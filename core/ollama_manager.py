import ollama

def get_local_ollama_models():
    try:
        models_info = ollama.list()
        if not isinstance(models_info.models, list):
            return ["Unexpected Ollama response format"]
        local_models = []
        for model_obj in models_info.models:
            if hasattr(model_obj, 'model'):
                local_models.append(model_obj.model)
        if not local_models:
            return ["No models found - check Ollama"]
        return local_models
    except ollama.ResponseError:
        return ["Ollama server error - check connection"]
    except Exception:
        return ["Unknown model error - see console for details"]
