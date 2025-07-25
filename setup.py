#!/usr/bin/env python3
"""
AI Chat Assistant Setup Script
Автоматичне встановлення та налаштування AI Chat Assistant з Ollama
"""

import os
import sys
import subprocess
import platform
import json
import urllib.request
import shutil
from pathlib import Path

class AIChatSetup:
    def __init__(self):
        self.system = platform.system().lower()
        self.project_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.project_dir / "venv"
        self.requirements = [
            "customtkinter>=5.2.0",
            "ollama>=0.1.0",
            "requests>=2.31.0",
            "psutil>=5.9.0",
            "python-dotenv>=1.0.0",
            "beautifulsoup4>=4.11.0",
        ]
        
    def print_step(self, step, message):
        print(f"\n{'='*60}")
        print(f"STEP {step}: {message}")
        print(f"{'='*60}")
        
    def run_command(self, command, check=True, capture_output=False):
        """Виконує команду в терміналі"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
                return result.stdout.strip()
            else:
                subprocess.run(command, shell=True, check=check)
                return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running command: {command}")
            print(f"❌ Error: {e}")
            return False
    
    def check_python_version(self):
        """Перевіряє версію Python"""
        self.print_step(1, "Checking Python version")
        
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required!")
            print(f"❌ Current version: {sys.version}")
            return False
        
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
        return True
    
    def install_ollama(self):
        """Встановлює Ollama"""
        self.print_step(2, "Installing Ollama")
        
        # Перевіряємо чи Ollama вже встановлена
        ollama_installed = self.run_command("ollama --version", check=False, capture_output=True)
        if ollama_installed:
            print("✅ Ollama already installed")
            return True
        
        print("📥 Installing Ollama...")
        
        if self.system == "windows":
            print("🔗 Please download and install Ollama manually from: https://ollama.ai/download")
            print("📝 After installation, restart this script")
            input("Press Enter after installing Ollama...")
            
        elif self.system == "linux" or self.system == "darwin":  # macOS
            install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
            if self.run_command(install_cmd):
                print("✅ Ollama installed successfully")
            else:
                print("❌ Failed to install Ollama")
                return False
        
        # Перевіряємо встановлення
        if self.run_command("ollama --version", check=False, capture_output=True):
            print("✅ Ollama installation verified")
            return True
        else:
            print("❌ Ollama installation failed")
            return False
    
    def start_ollama_service(self):
        """Запускає сервіс Ollama"""
        self.print_step(3, "Starting Ollama service")
        
        # Спочатку перевіряємо чи сервіс запущений через команду
        try:
            result = self.run_command("ollama list", check=True, capture_output=True)
            if result:
                print("✅ Ollama service is running")
                return True
        except:
            pass
        
        # Якщо не працює, запускаємо
        print("🚀 Starting Ollama service...")
        
        if self.system == "windows":
            # На Windows запускаємо як фоновий процес
            import subprocess
            try:
                subprocess.Popen(["ollama", "serve"], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            except FileNotFoundError:
                print("❌ Ollama not found. Please install Ollama first.")
                return False
        else:
            # На Linux/macOS
            self.run_command("ollama serve &", check=False)
        
        # Чекаємо запуск
        import time
        print("⏳ Waiting for Ollama to start...")
        for i in range(10):  # Чекаємо до 10 секунд
            time.sleep(1)
            try:
                result = self.run_command("ollama list", check=False, capture_output=True)
                if result:
                    print("✅ Ollama service started successfully")
                    return True
            except:
                continue
        
        print("⚠️  Ollama might be starting in background. Continuing setup...")
        return True  # Продовжуємо setup навіть якщо не можемо підтвердити запуск
    
    def create_virtual_environment(self):
        """Створює віртуальне середовище"""
        self.print_step(4, "Setting up Python virtual environment")
        
        if self.venv_dir.exists():
            print("✅ Virtual environment already exists")
            return True
        
        print("📦 Creating virtual environment...")
        if self.run_command(f"python -m venv {self.venv_dir}"):
            print("✅ Virtual environment created")
            return True
        else:
            print("❌ Failed to create virtual environment")
            return False
    
    def install_python_dependencies(self):
        """Встановлює Python залежності"""
        self.print_step(5, "Installing Python dependencies")
        
        # Configuration option
        if self.system == "windows":
            pip_cmd = f"{self.venv_dir}\\Scripts\\pip.exe"
            python_cmd = f"{self.venv_dir}\\Scripts\\python.exe"
        else:
            pip_cmd = f"{self.venv_dir}/bin/pip"
            python_cmd = f"{self.venv_dir}/bin/python"
        
        # Check if pip upgrade is available by trying to install first package
        print("📦 Installing packages...")
        first_package = self.requirements[0]
        print(f"  � Installing {first_package}")
        
        # Capture output to check for pip warnings
        import subprocess
        try:
            result = subprocess.run(f"{pip_cmd} install {first_package}", 
                                  shell=True, capture_output=True, text=True, check=True)
            
            # Check if pip upgrade warning is in stderr
            if "however, version" in result.stderr and "You should consider upgrading" in result.stderr:
                print("⚠️  A newer version of pip is available")
                while True:
                    choice = input("Would you like to upgrade pip before continuing? (y/n): ").lower().strip()
                    if choice in ['y', 'yes']:
                        print("⬆️  Upgrading pip...")
                        try:
                            # Try using python -m pip instead of direct pip command
                            subprocess.run(f"{python_cmd} -m pip install --upgrade pip", 
                                         shell=True, check=True)
                            print("✅ Pip upgraded successfully")
                        except subprocess.CalledProcessError:
                            print("⚠️  Pip upgrade failed, but continuing with installation...")
                            print("💡 This won't affect the installation of packages")
                        break
                    elif choice in ['n', 'no']:
                        print("⏭️  Continuing with current pip version")
                        break
                    else:
                        print("Please enter 'y' or 'n'")
            
            print(f"✅ {first_package} installed")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {first_package}")
            print(f"Error: {e}")
            return False
        
        # Install remaining packages
        for package in self.requirements[1:]:
            print(f"  📦 Installing {package}")
            if not self.run_command(f"{pip_cmd} install {package}"):
                print(f"❌ Failed to install {package}")
                return False
        
        print("✅ All Python dependencies installed")
        return True
    
    def download_default_model(self):
        """Завантажує стандартну модель"""
        self.print_step(6, "Downloading default AI model")
        
        print("🤖 Downloading llama3.2:1b (recommended starter model)...")
        print("📝 This may take a few minutes...")
        
        if self.run_command("ollama pull llama3.2:1b"):
            print("✅ Default model downloaded successfully")
            return True
        else:
            print("❌ Failed to download default model")
            print("💡 You can download it later with: ollama pull llama3.2:1b")
            return False
    
    def create_config_file(self):
        """Створює файл конфігурації"""
        self.print_step(7, "Creating configuration")
        
        config_path = self.project_dir / "core" / "config.py"
        
        if config_path.exists():
            print("✅ Configuration file already exists")
            return True
        
        # Створюємо папку core якщо не існує
        config_path.parent.mkdir(exist_ok=True)
        
        config_content = '''"""
AI Chat Assistant Configuration
"""

import os

# Directories
CHARACTER_DIR = 'characters'
HISTORY_FILES_DIR = 'chat_histories'

# Google Search API (optional)
# Get your keys from: https://developers.google.com/custom-search/v1/introduction
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', '')

# Ollama settings
OLLAMA_HOST = 'http://localhost:11434'

# Create directories if they don't exist
os.makedirs(CHARACTER_DIR, exist_ok=True)
os.makedirs(HISTORY_FILES_DIR, exist_ok=True)
'''
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("✅ Configuration file created")
        return True
    
    def create_launcher_scripts(self):
        """Створює скрипти для запуску"""
        self.print_step(8, "Creating launcher scripts")
        
        # Windows launcher
        if self.system == "windows":
            launcher_content = f'''@echo off
cd /d "{self.project_dir}"
"{self.venv_dir}\\Scripts\\python.exe" -m gui.app
pause
'''
            with open(self.project_dir / "run.bat", 'w') as f:
                f.write(launcher_content)
            print("✅ Windows launcher (run.bat) created")
        
        # Unix launcher
        launcher_content = f'''#!/bin/bash
cd "{self.project_dir}"
"{self.venv_dir}/bin/python" -m gui.app
'''
        launcher_path = self.project_dir / "run.sh"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        # Configuration option
        if self.system != "windows":
            os.chmod(launcher_path, 0o755)
            print("✅ Unix launcher (run.sh) created")
        
        return True
    
    def verify_installation(self):
        """Перевіряє встановлення"""
        self.print_step(9, "Verifying installation")
        
        # Перевіряємо чи всі файли на місці
        required_files = [
            "gui/app.py",
            "core/config.py",
            "characters/Lumin.txt",
        ]
        
        for file_path in required_files:
            if not (self.project_dir / file_path).exists():
                print(f"❌ Missing required file: {file_path}")
                return False
        
        print("✅ All required files present")
        
        # Перевіряємо Ollama
        try:
            import subprocess
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
            print("✅ Ollama is working")
        except Exception as e:
            print(f"⚠️  Ollama check failed: {e}")
        
        return True
    
    def run_setup(self):
        """Запускає повне встановлення"""
        try:
            print("🚀 AI Chat Assistant Setup")
            print("🤖 This will install and configure everything you need")
            print("")
            print("DEBUG: Starting setup process...")
            
            steps = [
                self.check_python_version,
                self.install_ollama,
                self.start_ollama_service,
                self.create_virtual_environment,
                self.install_python_dependencies,
                self.download_default_model,
                self.create_config_file,
                self.create_launcher_scripts,
                self.verify_installation,
            ]
            
            for i, step in enumerate(steps, 1):
                try:
                    print(f"DEBUG: Running step {i}: {step.__name__}")
                    if not step():
                        print("\n❌ Setup failed!")
                        print("📝 Please check the error messages above")
                        input("Press Enter to exit...")
                        sys.exit(1)
                except KeyboardInterrupt:
                    print("\n⚠️  Setup interrupted by user")
                    input("Press Enter to exit...")
                    sys.exit(1)
                except Exception as e:
                    print(f"\n❌ Unexpected error in {step.__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    input("Press Enter to exit...")
                    sys.exit(1)
        
        except Exception as e:
            print(f"\n❌ Critical error: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to exit...")
            sys.exit(1)
        
        self.print_step("COMPLETE", "Setup finished successfully!")
        print("")
        print("✅ AI Chat Assistant is ready to use!")
        print("")
        print("🚀 To start the application:")
        if self.system == "windows":
            print("   • Double-click 'run.bat'")
            print("   • Or run: python -m gui.app")
        else:
            print("   • Run: ./run.sh")
            print("   • Or run: python -m gui.app")
        print("")
        print("📚 Available characters:")
        print("   • Lumin - Sophisticated virtual companion")
        print("   • Add your own in the 'characters' folder")
        print("")
        print("🎉 Enjoy chatting with AI!")
        print("")
        input("Press Enter to exit...")

if __name__ == "__main__":
    setup = AIChatSetup()
    setup.run_setup()
