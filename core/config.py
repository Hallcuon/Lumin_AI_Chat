"""
AI Chat Assistant Configuration
"""

import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env in project root
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, use os.getenv defaults
    pass

# Application directories  
CHARACTER_DIR = 'characters'
HISTORY_FILES_DIR = 'chat_histories'

# Ollama settings (configurable via GUI "Ollama Settings")
DEFAULT_OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
DEFAULT_MODELS_PATH = os.getenv('MODELS_PATH', '')  # Empty = use Ollama default location

# Google Search API (configurable via GUI "Web Search")
# Get free keys from: https://developers.google.com/custom-search/v1/introduction  
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', '')

# Auto-create directories
os.makedirs(CHARACTER_DIR, exist_ok=True)
os.makedirs(HISTORY_FILES_DIR, exist_ok=True)
