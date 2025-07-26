import customtkinter as ctk
import threading
import os
from core.ollama_manager import get_local_ollama_models
from core.model_metadata import ModelMetadata
from core.character_manager import load_character_prompt, load_chat_history, save_chat_history, get_character_history_file
from core.web_tools import google_search, fetch_url_content
from core.proactive_manager import ProactiveManager
from core.config import CHARACTER_DIR, HISTORY_FILES_DIR, GOOGLE_API_KEY, GOOGLE_CSE_ID
from core.utils import get_timestamp, get_datetime_str
from core.memory import load_long_term_memory, add_fact_to_memory

class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        from core.chat_history_manager import ChatHistoryManager
        from core.chat_logger import ChatLogger
        from core.prompt_manager import PromptManager
        from core.vision_manager import VisionManager
        
        # Initialize basic attributes
        self.title("AI Chat Assistant")
        self.geometry("1200x800")
        self.proactive_enabled = True
        self.message_lock = threading.Lock()
        self.vision_image_path = None
        self.is_processing = False
        
        # Get available models
        available_models = get_local_ollama_models()
        if not available_models or available_models[0].startswith("No models") or available_models[0].startswith("Ollama"):
            available_models = ["llama3.2:1b", "qwen2.5:0.5b", "gemma2:2b"]  # fallback models
            
        self.selected_model = ctk.StringVar(value=available_models[0])
        self.selected_character_name = ctk.StringVar(value="Default AI Assistant")
        self.character_files = self._get_character_files()
        
        # Initialize managers
        self.prompt_manager = PromptManager("You are a helpful AI assistant.")
        self.system_prompt = self.prompt_manager.get_prompt()
        self.char_name = "AI"
        
        # GUI variables
        self.prompt_format = ctk.StringVar(value="Plain")
        self.temperature = ctk.DoubleVar(value=0.7)
        self.top_p = ctk.DoubleVar(value=0.95)
        self.proactive_enabled = ctk.BooleanVar(value=True)  # Proactive behavior toggle
        
        # Grid configuration
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create GUI
        self._init_gui()
        
        # Initialize managers after GUI creation
        self.history_manager = ChatHistoryManager(HISTORY_FILES_DIR, self.char_name)
        self.logger = ChatLogger()
        self.vision_manager = VisionManager()
        self.model_metadata = None
        self.messages = self.history_manager.load_last_history(self.system_prompt)
        
        # Final setup
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.proactive_thread = None
        self.typing_speed = 0.01
        self.proactive_manager = ProactiveManager(self)
        
        # Initialize chat context after complete GUI creation
        self.after(100, lambda: self.update_chat_context(None, initial_load=True))

    def _init_gui(self):
        # Settings frame
        self.settings_frame = ctk.CTkFrame(self, corner_radius=10)
        self.settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.settings_frame.grid_columnconfigure(1, weight=1)
        
        # Model selection and format controls
        ctk.CTkLabel(self.settings_frame, text="Select Ollama Model:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        available_models = get_local_ollama_models()
        if not available_models or available_models[0].startswith("No models"):
            available_models = ["llama3.2:1b", "qwen2.5:0.5b", "gemma2:2b"]
        self.model_optionmenu = ctk.CTkOptionMenu(self.settings_frame, values=available_models, 
                                                  variable=self.selected_model, command=self.update_chat_context)
        self.model_optionmenu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.settings_frame, text="Prompt Format:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.prompt_format_optionmenu = ctk.CTkOptionMenu(self.settings_frame, values=["Plain", "<|system|>", "### System"], 
                                                          variable=self.prompt_format)
        self.prompt_format_optionmenu.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.settings_frame, text="Temperature:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.temp_entry = ctk.CTkEntry(self.settings_frame, textvariable=self.temperature, width=60)
        self.temp_entry.grid(row=1, column=3, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.settings_frame, text="Top-p:").grid(row=1, column=4, padx=10, pady=5, sticky="w")
        self.top_p_entry = ctk.CTkEntry(self.settings_frame, textvariable=self.top_p, width=60)
        self.top_p_entry.grid(row=1, column=5, padx=10, pady=5, sticky="ew")
        
        # Proactive behavior toggle
        self.proactive_checkbox = ctk.CTkCheckBox(self.settings_frame, text="Auto Messages", 
                                                 variable=self.proactive_enabled, command=self.toggle_proactive_manager)
        self.proactive_checkbox.grid(row=1, column=6, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(self.settings_frame, text="Select Character:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        character_options = ["Default AI Assistant"] + self.character_files
        self.character_optionmenu = ctk.CTkOptionMenu(self.settings_frame, values=character_options, 
                                                      variable=self.selected_character_name, command=self.update_chat_context)
        self.character_optionmenu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        self.restart_chat_button = ctk.CTkButton(self.settings_frame, text="Restart Chat", 
                                                command=self.restart_chat_session, fg_color="#2a1261", 
                                                hover_color="#210f4a", text_color="#FFFFFF")
        self.restart_chat_button.grid(row=0, column=7, rowspan=2, padx=10, pady=5, sticky="nsew")
        
        # Model metadata info
        self.model_info_label = ctk.CTkLabel(self.settings_frame, text="", anchor="w", justify="left", font=("Arial", 12))
        self.model_info_label.grid(row=2, column=0, columnspan=7, padx=10, pady=5, sticky="ew")
        
        # Vision input button
        self.vision_button = ctk.CTkButton(self.settings_frame, text="Add Image (Vision)", 
                                          command=self.select_vision_image, fg_color="#1a4a61", 
                                          hover_color="#10304a", text_color="#FFFFFF")
        self.vision_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.vision_image_label = ctk.CTkLabel(self.settings_frame, text="No image selected", anchor="w", font=("Arial", 11))
        self.vision_image_label.grid(row=3, column=1, columnspan=3, padx=10, pady=5, sticky="ew")
        
        # Character doc editor button
        self.char_doc_button = ctk.CTkButton(self.settings_frame, text="Edit Character Doc", 
                                            command=self.open_character_doc_editor, fg_color="#614a12", 
                                            hover_color="#4a370f", text_color="#FFFFFF")
        self.char_doc_button.grid(row=3, column=4, padx=10, pady=5, sticky="ew")
        
        # Modular history buttons
        self.export_history_button = ctk.CTkButton(self.settings_frame, text="Export History", 
                                                  command=self.export_chat_history, fg_color="#12614a", 
                                                  hover_color="#0f4a37", text_color="#FFFFFF")
        self.export_history_button.grid(row=3, column=5, padx=10, pady=5, sticky="ew")
        self.import_history_button = ctk.CTkButton(self.settings_frame, text="Import History", 
                                                  command=self.import_chat_history, fg_color="#614a61", 
                                                  hover_color="#4a374a", text_color="#FFFFFF")
        self.import_history_button.grid(row=3, column=6, padx=10, pady=5, sticky="ew")
        self.clear_history_button = ctk.CTkButton(self.settings_frame, text="Clear History", 
                                                 command=self.clear_chat_history, fg_color="#611212", 
                                                 hover_color="#4a0f0f", text_color="#FFFFFF")
        self.clear_history_button.grid(row=3, column=7, padx=10, pady=5, sticky="ew")
        
        # Manual system prompt field
        self.manual_prompt_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="Manual system prompt (optional)", width=400)
        self.manual_prompt_entry.grid(row=4, column=0, columnspan=5, padx=10, pady=5, sticky="ew")
        self.set_manual_prompt_button = ctk.CTkButton(self.settings_frame, text="Set System Prompt", 
                                                     command=self.set_manual_system_prompt, fg_color="#124a61", 
                                                     hover_color="#0f304a", text_color="#FFFFFF")
        self.set_manual_prompt_button.grid(row=4, column=5, padx=10, pady=5, sticky="ew")
        self.view_log_button = ctk.CTkButton(self.settings_frame, text="View Log File", 
                                            command=self.view_log_file, fg_color="#1a6112", 
                                            hover_color="#0f4a21", text_color="#FFFFFF")
        self.view_log_button.grid(row=4, column=6, padx=10, pady=5, sticky="ew")
        
        self.ollama_settings_button = ctk.CTkButton(self.settings_frame, text="Ollama Settings", 
                                                   command=self.open_ollama_settings, fg_color="#614a12", 
                                                   hover_color="#4a370f", text_color="#FFFFFF")
        self.ollama_settings_button.grid(row=4, column=7, padx=10, pady=5, sticky="ew")
        
        # Web Search Settings button
        self.web_settings_button = ctk.CTkButton(self.settings_frame, text="Web Search", 
                                                command=self.open_web_settings, fg_color="#126140", 
                                                hover_color="#0f4a30", text_color="#FFFFFF")
        self.web_settings_button.grid(row=5, column=6, padx=10, pady=5, sticky="ew")
        
        # Chat frame
        self.chat_frame = ctk.CTkFrame(self, corner_radius=10)
        self.chat_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_history_textbox = ctk.CTkTextbox(self.chat_frame, wrap="word", state="disabled", font=("Arial", 14))
        self.chat_history_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.chat_history_textbox.tag_config("user_tag", foreground="#FAF7F3", lmargin1=20, lmargin2=20, rmargin=100)
        self.chat_history_textbox.tag_config("assistant_tag", foreground="#D9A299", lmargin1=100, lmargin2=100, rmargin=20)
        self.chat_history_textbox.tag_config("system_tag", foreground="#722323")
        
        # Input frame
        self.input_frame = ctk.CTkFrame(self, corner_radius=10)
        self.input_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.user_input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message...", height=30)
        self.user_input_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.user_input_entry.bind("<Return>", self.send_message_on_enter)
        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message, 
                                        fg_color="#596112", hover_color="#3f450c", text_color="#FFFFFF")
        self.send_button.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="e")

    def view_log_file(self):
        import tkinter.messagebox
        import os
        try:
            # Get log file from logger if available, otherwise use default path
            if hasattr(self, 'logger') and self.logger:
                log_file = getattr(self.logger, 'log_file', 'chat.log')
            else:
                log_file = 'chat.log'
            
            # If log file doesn't exist, create it
            if not os.path.exists(log_file):
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(f"[{get_timestamp()}] Chat log initialized.\n")
                tkinter.messagebox.showinfo("Chat Log", "Log file was created. No previous logs found.")
                return
            
            # Read existing log content
            with open(log_file, "r", encoding="utf-8") as f:
                log_content = f.read()
                
            # Show last 3000 characters if file is large
            if len(log_content) > 3000:
                log_content = "...\n" + log_content[-3000:]
                
            if log_content.strip():
                tkinter.messagebox.showinfo("Chat Log", log_content)
            else:
                tkinter.messagebox.showinfo("Chat Log", "Log file exists but is empty.")
                
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to read log: {e}\nAttempted path: {log_file if 'log_file' in locals() else 'Unknown'}")
    def set_manual_system_prompt(self):
        manual_prompt = self.manual_prompt_entry.get().strip()
        if manual_prompt:
            self.system_prompt = manual_prompt
            self.add_message_to_history("System: Manual system prompt set.", "system")
            self.load_character_chat_history()

    def toggle_proactive_manager(self):
        """Toggle proactive manager on/off based on checkbox state"""
        if self.proactive_enabled.get():
            # Enable proactive manager
            if hasattr(self, 'proactive_manager') and self.proactive_manager:
                try:
                    self.proactive_manager.start()
                    self.add_message_to_history("System: Auto messages enabled - AI may initiate conversations.", "system")
                    print("[DEBUG] ProactiveManager enabled")
                except Exception as e:
                    print(f"[ERROR] Failed to start proactive manager: {e}")
                    self.add_message_to_history("System: Failed to enable auto messages.", "system")
        else:
            # Disable proactive manager
            if hasattr(self, 'proactive_manager') and self.proactive_manager:
                try:
                    self.proactive_manager.stop()
                    self.add_message_to_history("System: Auto messages disabled - AI will only respond to your messages.", "system")
                    print("[DEBUG] ProactiveManager disabled")
                except Exception as e:
                    print(f"[ERROR] Failed to stop proactive manager: {e}")

    def on_closing(self):
        self.destroy()

    def restart_chat_session(self):
        # Clear chat history and restart
        self.messages = [{'role': 'system', 'content': self.system_prompt}]
        if hasattr(self, 'chat_history_textbox'):
            self.chat_history_textbox.configure(state="normal")
            self.chat_history_textbox.delete("1.0", ctk.END)
            self.chat_history_textbox.configure(state="disabled")
        self.add_message_to_history("System: Chat session restarted.", "system")

    def add_message_to_history(self, message, role):
        if not hasattr(self, 'chat_history_textbox'):
            return
        
        self.chat_history_textbox.configure(state="normal")
        timestamp = get_timestamp()
        
        if role == "user":
            self.chat_history_textbox.insert("end", f"[{timestamp}] You: {message}\n", "user_tag")
        elif role == "assistant":
            self.chat_history_textbox.insert("end", f"[{timestamp}] {self.char_name}: {message}\n", "assistant_tag")
        elif role == "system":
            self.chat_history_textbox.insert("end", f"[{timestamp}] {message}\n", "system_tag")
        
        self.chat_history_textbox.configure(state="disabled")
        self.chat_history_textbox.see("end")

    def save_current_chat_history(self):
        if hasattr(self, 'history_manager') and self.history_manager:
            try:
                self.history_manager.save_history(self.messages, self.char_name)
            except Exception as e:
                print(f"[ERROR] Failed to save chat history: {e}")
        
    def export_chat_history(self):
        import tkinter.filedialog, json
        file_path = tkinter.filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Export chat history")
        if file_path:
            history = [m for m in self.messages if m.get('role') != 'system']
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            self.add_message_to_history(f"System: Chat history exported to {file_path}", "system")

    def import_chat_history(self):
        import tkinter.filedialog, json
        file_path = tkinter.filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], title="Import chat history")
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    imported = json.load(f)
                
                # JSON format validation
                if not isinstance(imported, list):
                    self.add_message_to_history("System Error: Invalid format - expected list of messages", "system")
                    return
                
                # Check each message
                valid_messages = []
                for i, msg in enumerate(imported):
                    if not isinstance(msg, dict):
                        self.add_message_to_history(f"System Warning: Skipping invalid message at index {i} - not a dictionary", "system")
                        continue
                    
                    if 'role' not in msg or 'content' not in msg:
                        self.add_message_to_history(f"System Warning: Skipping message at index {i} - missing 'role' or 'content'", "system")
                        continue
                    
                    if msg['role'] not in ['user', 'assistant']:
                        self.add_message_to_history(f"System Warning: Skipping message at index {i} - invalid role '{msg.get('role', 'unknown')}'", "system")
                        continue
                    
                    valid_messages.append(msg)
                
                if not valid_messages:
                    self.add_message_to_history("System Error: No valid messages found in the file", "system")
                    return
                
                # Import valid messages
                self.messages = [{'role': 'system', 'content': self.system_prompt}] + valid_messages
                self.chat_history_textbox.configure(state="normal")
                self.chat_history_textbox.delete("1.0", ctk.END)
                
                for msg in valid_messages:
                    if msg['role'] == 'user':
                        self.chat_history_textbox.insert("end", f"[Imported] You: {msg['content']}\n", "user_tag")
                    elif msg['role'] == 'assistant':
                        self.chat_history_textbox.insert("end", f"[Imported] {self.char_name}: {msg['content']}\n", "assistant_tag")
                
                self.chat_history_textbox.configure(state="disabled")
                self.add_message_to_history(f"System: Chat history imported from {file_path} ({len(valid_messages)} messages)", "system")
                
            except json.JSONDecodeError as e:
                self.add_message_to_history(f"System Error: Invalid JSON format: {e}", "system")
            except Exception as e:
                self.add_message_to_history(f"System Error: Failed to import history: {e}", "system")

    def clear_chat_history(self):
        self.messages = [{'role': 'system', 'content': self.system_prompt}]
        self.chat_history_textbox.configure(state="normal")
        self.chat_history_textbox.delete("1.0", ctk.END)
        self.chat_history_textbox.configure(state="disabled")
        self.add_message_to_history("System: Chat history cleared.", "system")
    def select_vision_image(self):
        import tkinter.filedialog
        filetypes = [("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        path = tkinter.filedialog.askopenfilename(title="Select image for Vision", filetypes=filetypes)
        if path:
            self.vision_image_path = path
            self.vision_image_label.configure(text=f"Selected: {os.path.basename(path)}")
        else:
            self.vision_image_path = None
            self.vision_image_label.configure(text="No image selected")

    def open_character_doc_editor(self):
        # Configuration option
        import tkinter as tk
        from tkinter import messagebox
        
        char_name = self.selected_character_name.get()
        doc_path = os.path.join(CHARACTER_DIR, f"{char_name}.doc.txt")
        doc_text = ""
        if os.path.exists(doc_path):
            with open(doc_path, "r", encoding="utf-8") as f:
                doc_text = f.read()
        
        # Create new window
        doc_window = tk.Toplevel(self)
        doc_window.title(f"Character Documentation - {char_name}")
        doc_window.geometry("800x600")
        doc_window.transient(self)
        doc_window.grab_set()
        
        # Текстове field з прокруткою
        text_frame = tk.Frame(doc_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 11))
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Вставляємо існуючий текст
        text_widget.insert("1.0", doc_text)
        
        # Кнопки
        button_frame = tk.Frame(doc_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def save_and_close():
            new_doc = text_widget.get("1.0", tk.END).rstrip()
            try:
                with open(doc_path, "w", encoding="utf-8") as f:
                    f.write(new_doc)
                self.add_message_to_history(f"System: Character documentation updated for {char_name}.", "system")
                doc_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save documentation: {e}")
        
        def cancel():
            doc_window.destroy()
        
        tk.Button(button_frame, text="Save", command=save_and_close, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="Cancel", command=cancel, bg="#f44336", fg="white").pack(side=tk.LEFT)

    def open_ollama_settings(self):
        """Open Ollama configuration dialog"""
        import tkinter as tk
        from tkinter import messagebox, filedialog
        
        # Create settings window
        settings_window = tk.Toplevel(self)
        settings_window.title("Ollama Settings")
        settings_window.geometry("500x300")
        settings_window.transient(self)
        settings_window.grab_set()
        
        # Ollama Host setting
        tk.Label(settings_window, text="Ollama Host:", font=("Arial", 12, "bold")).pack(pady=10)
        host_var = tk.StringVar(value=getattr(self, 'ollama_host', 'http://localhost:11434'))
        host_entry = tk.Entry(settings_window, textvariable=host_var, width=50, font=("Arial", 11))
        host_entry.pack(pady=5)
        
        # Models Path setting
        tk.Label(settings_window, text="Models Storage Path (optional):", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        path_var = tk.StringVar(value=getattr(self, 'models_path', ''))
        path_frame = tk.Frame(settings_window)
        path_frame.pack(pady=5)
        
        path_entry = tk.Entry(path_frame, textvariable=path_var, width=40, font=("Arial", 11))
        path_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        def browse_path():
            folder = filedialog.askdirectory(title="Select Models Storage Folder")
            if folder:
                path_var.set(folder)
        
        tk.Button(path_frame, text="Browse", command=browse_path).pack(side=tk.LEFT)
        
        # Info text
        info_text = """
Note: Leave Models Path empty to use Ollama's default location.
Custom path allows you to store models in a different location
(useful for external drives or specific folders).
        """
        tk.Label(settings_window, text=info_text, justify=tk.LEFT, font=("Arial", 9)).pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(settings_window)
        button_frame.pack(pady=20)
        
        def save_settings():
            try:
                self.ollama_host = host_var.get().strip()
                self.models_path = path_var.get().strip()
                
                # Save to config file
                config_data = f"""# Ollama Configuration
OLLAMA_HOST = '{self.ollama_host}'
MODELS_PATH = '{self.models_path}'
"""
                with open("ollama_config.py", "w") as f:
                    f.write(config_data)
                
                messagebox.showinfo("Success", "Ollama settings saved successfully!")
                settings_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {e}")
        
        def cancel_settings():
            settings_window.destroy()
        
        tk.Button(button_frame, text="Save", command=save_settings, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Cancel", command=cancel_settings, bg="#f44336", fg="white").pack(side=tk.LEFT)

    def open_web_settings(self):
        """Open web search configuration dialog"""
        import tkinter as tk
        from tkinter import messagebox
        import webbrowser
        
        # Create settings window
        web_window = tk.Toplevel(self)
        web_window.title("Web Search Settings")
        web_window.geometry("600x500")
        web_window.transient(self)
        web_window.grab_set()
        
        # Title
        tk.Label(web_window, text="Google Search API Configuration", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Status check
        current_api_key = getattr(self, 'google_api_key', '')
        current_cse_id = getattr(self, 'google_cse_id', '')
        has_keys = bool(current_api_key and current_cse_id)
        
        status_color = "green" if has_keys else "red"
        status_text = "✅ Configured" if has_keys else "❌ Not configured"
        tk.Label(web_window, text=f"Status: {status_text}", 
                font=("Arial", 12), fg=status_color).pack(pady=5)
        
        # Info text
        info_text = """
Web search allows the AI to find current information from the internet.
This requires FREE Google API keys (no payment needed for basic usage).

Without API keys, the AI will work normally but won't be able to:
• Search for current news or information
• Get real-time data
• Answer questions requiring web search
        """
        tk.Label(web_window, text=info_text, justify=tk.LEFT, 
                font=("Arial", 10)).pack(pady=10, padx=20)
        
        # API Key input
        tk.Label(web_window, text="Google API Key:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
        api_key_var = tk.StringVar(value=current_api_key)
        api_key_entry = tk.Entry(web_window, textvariable=api_key_var, width=70, font=("Arial", 10))
        api_key_entry.pack(pady=5, padx=20, fill="x")
        
        # CSE ID input
        tk.Label(web_window, text="Custom Search Engine ID:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
        cse_id_var = tk.StringVar(value=current_cse_id)
        cse_id_entry = tk.Entry(web_window, textvariable=cse_id_var, width=70, font=("Arial", 10))
        cse_id_entry.pack(pady=5, padx=20, fill="x")
        
        # Help button
        def open_help():
            webbrowser.open("https://developers.google.com/custom-search/v1/introduction")
        
        help_frame = tk.Frame(web_window)
        help_frame.pack(pady=10)
        tk.Button(help_frame, text="📖 How to get API keys (opens browser)", 
                 command=open_help, bg="#2196F3", fg="white").pack()
        
        # Test button
        def test_api():
            test_api_key = api_key_var.get().strip()
            test_cse_id = cse_id_var.get().strip()
            
            if not test_api_key or not test_cse_id:
                messagebox.showwarning("Missing Keys", "Please enter both API key and CSE ID to test.")
                return
            
            try:
                from core.web_tools import google_search
                results = google_search("test search", test_api_key, test_cse_id, 1)
                if results:
                    messagebox.showinfo("Success", "✅ API keys work correctly!")
                else:
                    messagebox.showwarning("No Results", "API keys seem valid but no results returned.")
            except Exception as e:
                messagebox.showerror("Error", f"API test failed: {e}")
        
        tk.Button(help_frame, text="🧪 Test API Keys", command=test_api, 
                 bg="#FF9800", fg="white").pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(web_window)
        button_frame.pack(pady=20)
        
        def save_web_settings():
            try:
                self.google_api_key = api_key_var.get().strip()
                self.google_cse_id = cse_id_var.get().strip()
                
                # Update config file
                config_content = f"""# Google Search API Configuration
GOOGLE_API_KEY = '{self.google_api_key}'
GOOGLE_CSE_ID = '{self.google_cse_id}'
"""
                with open("google_config.py", "w") as f:
                    f.write(config_content)
                
                # Update config module
                import core.config as config
                config.GOOGLE_API_KEY = self.google_api_key
                config.GOOGLE_CSE_ID = self.google_cse_id
                
                if self.google_api_key and self.google_cse_id:
                    messagebox.showinfo("Success", "✅ Web search configured successfully!")
                else:
                    messagebox.showinfo("Disabled", "Web search disabled (no API keys).")
                
                web_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {e}")
        
        def clear_keys():
            if messagebox.askyesno("Clear Keys", "Remove API keys and disable web search?"):
                api_key_var.set("")
                cse_id_var.set("")
        
        def cancel_web():
            web_window.destroy()
        
        tk.Button(button_frame, text="💾 Save", command=save_web_settings, 
                 bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="🗑️ Clear", command=clear_keys, 
                 bg="#FF5722", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="❌ Cancel", command=cancel_web, 
                 bg="#9E9E9E", fg="white").pack(side=tk.LEFT, padx=5)

    def _get_character_files(self):
        import os
        if not os.path.exists(CHARACTER_DIR):
            return []
        return [f.replace('.txt', '') for f in os.listdir(CHARACTER_DIR) if f.endswith('.txt')]

    def update_chat_context(self, choice, initial_load=False):
        if not initial_load and hasattr(self, 'messages') and self.messages:
            # Auto save history при зміні персонажа/моделі
            self.save_current_chat_history()
            
        selected_char_name = self.selected_character_name.get()
        selected_model_name = self.selected_model.get()
        
        # Load model metadata
        self.model_metadata = ModelMetadata(selected_model_name)
        meta = self.model_metadata
        info_lines = []
        if meta:
            ram = meta.get_ram_requirement()
            gpu = meta.get_gpu_requirement()
            quant = meta.get_quantization()
            vision = meta.supports_vision()
            desc = meta.get_description()
            info_lines.append(f"Model: {selected_model_name}")
            if desc:
                info_lines.append(f"Description: {desc}")
            if ram:
                info_lines.append(f"Required RAM: {ram}")
            if gpu:
                info_lines.append(f"Required GPU: {gpu}")
            if quant:
                info_lines.append(f"Quantization: {quant}")
            info_lines.append(f"Vision support: {'Yes' if vision else 'No'}")
            
        if hasattr(self, 'model_info_label'):
            self.model_info_label.configure(text="\n".join(info_lines))
        
        # Resource check (dummy, for demo)
        try:
            import psutil
            available_ram = round(psutil.virtual_memory().total / (1024**3), 1)
            if meta and meta.get_ram_requirement():
                try:
                    required_ram = float(str(meta.get_ram_requirement()).replace('GB','').strip())
                    if available_ram < required_ram:
                        self.add_message_to_history(f"System Warning: Model requires {required_ram}GB RAM, but only {available_ram}GB available.", "system")
                except Exception:
                    pass
        except ImportError:
            pass
        
        # Vision warning
        if meta and not meta.supports_vision():
            self.add_message_to_history("System Notice: Selected model does NOT support Vision (image input).", "system")
        
        # Update character and system prompt
        if selected_char_name == "Default AI Assistant":
            self.system_prompt = "You are a helpful AI assistant."
            self.char_name = "AI"
        else:
            prompt = load_character_prompt(selected_char_name)
            if prompt:
                self.system_prompt = prompt
                char_name_line = self.system_prompt.splitlines()[0]
                if char_name_line.startswith("You are "):
                    self.char_name = char_name_line.replace('You are ', '').split(',')[0].strip()
                else:
                    self.char_name = selected_char_name.capitalize()
            else:
                self.system_prompt = "You are a helpful AI assistant."
                self.char_name = "AI"
                self.add_message_to_history(f"System Error: Failed to load character prompt for '{selected_char_name}'. Using default.", "system")
        
        print(f"[DEBUG] Selected model: {selected_model_name}, Selected character: {self.char_name}")
        self.load_character_chat_history()
        
        # Restart proactive manager based on checkbox state
        if hasattr(self, 'proactive_manager') and self.proactive_manager:
            try:
                self.proactive_manager.stop()
            except:
                pass
        try:
            self.proactive_manager = ProactiveManager(self)
            if self.proactive_enabled.get():
                self.proactive_manager.start()
                print("[DEBUG] ProactiveManager started (checkbox enabled)")
            else:
                print("[DEBUG] ProactiveManager created but not started (checkbox disabled)")
        except Exception as e:
            print(f"[WARNING] Could not create proactive manager: {e}")

    def load_character_chat_history(self):
        pass

    def send_message_on_enter(self, event=None):
        self.send_message()

    def send_message(self):
        user_input = self.user_input_entry.get()
        self.user_input_entry.delete(0, ctk.END)
        if not user_input.strip():
            return
        self.add_message_to_history(user_input, "user")
        self.messages.append({'role': 'user', 'content': user_input})
        
        # Log user message
        if hasattr(self, 'logger') and self.logger:
            try:
                self.logger.log(get_timestamp(), "user", user_input)
            except Exception as e:
                print(f"[WARNING] Failed to log user message: {e}")
        
        # Add user message у long-term memory
        add_fact_to_memory(self.char_name, user_input)
        # If image is selected для Vision — додаємо у повідомлення
        if self.vision_image_path and self.model_metadata and self.model_metadata.supports_vision():
            self.messages[-1]['image'] = self.vision_image_path
        thread = threading.Thread(target=self.get_ollama_response)
        thread.start()

    def get_ollama_response(self):
        with self.message_lock:
            import time
            start_time = time.time()
            try:
                self.is_processing = True
                self.send_button.configure(state="disabled", text="Thinking...")
                model_to_use_current = self.selected_model.get()
                last_user_message = self.messages[-1]
                user_input_lower = last_user_message['content'].lower()
                context_messages = list(self.messages[:-1])
                # Додаємо long-term memory у системний промпт (обмежуємо до 10 фактів)
                long_term_memory = load_long_term_memory(self.char_name)
                if long_term_memory:
                    memory_text = "\nLong-term memory (facts learned from user):\n" + "\n".join(long_term_memory[-10:])
                    if context_messages and context_messages[0]['role'] == 'system':
                        context_messages[0]['content'] += memory_text
                    else:
                        context_messages.insert(0, {'role': 'system', 'content': self.system_prompt + memory_text})
                # Configuration option
                prompt_format = self.prompt_format.get()
                if prompt_format == "<|system|>":
                    if context_messages and context_messages[0]['role'] == 'system':
                        context_messages[0]['content'] = f"<|system|>\n{context_messages[0]['content']}"
                elif prompt_format == "### System":
                    if context_messages and context_messages[0]['role'] == 'system':
                        context_messages[0]['content'] = f"### System\n{context_messages[0]['content']}"
                url_pattern = r'(https?://[^\s]+)'
                import re
                urls_in_input = re.findall(url_pattern, user_input_lower)
                if urls_in_input:
                    for url in urls_in_input[:1]:
                        self.add_message_to_history(f"System: Reading content from {url} ...", "system")
                        content = fetch_url_content(url)
                        context_messages.append({
                            'role': 'system',
                            'content': f"System note: The user provided a link. Here is the content from {url}:\n{content}"
                        })
                        self.add_message_to_history("System: Page content fetched and added to context.", "system")
                search_required = False
                search_query = ""
                search_keywords = [
                    "сьогодні", "актуальний час", "останні новини", "що відбувається", 
                    "хто такий", "що таке", "останній", "погода", "новини", 
                    "what time is it", "what is the time", "current time"
                ]
                for keyword in search_keywords:
                    if keyword in user_input_lower:
                        search_required = True
                        search_query = last_user_message['content']
                        break
                if search_required:
                    # Check if web search is configured
                    api_key = getattr(self, 'google_api_key', '') or GOOGLE_API_KEY
                    cse_id = getattr(self, 'google_cse_id', '') or GOOGLE_CSE_ID
                    
                    if api_key and cse_id:
                        self.add_message_to_history("System: Performing a web search...", "system")
                        web_results = google_search(search_query, api_key, cse_id)
                        if web_results:
                            context_messages.append({
                                'role': 'system',
                                'content': "System note: To answer the user's question, I have performed a web search. Here are the results:\n" + "\n".join(web_results[:3])
                            })
                            self.add_message_to_history("System: Web search completed. Results provided to AI.", "system")
                        else:
                            self.add_message_to_history("System: Web search yielded no relevant results.", "system")
                    else:
                        self.add_message_to_history("System: Web search requested but not configured. Configure in 'Web Search' settings.", "system")
                updated_system_prompt = self.system_prompt + "\n" + get_datetime_str()
                if context_messages and context_messages[0]['role'] == 'system':
                    context_messages[0]['content'] = updated_system_prompt
                else:
                    context_messages.insert(0, {'role': 'system', 'content': updated_system_prompt})
                messages_for_ollama = context_messages + [last_user_message]
                import ollama
                
                # Log generation attempt
                print(f"[INFO] Starting generation - Model: {model_to_use_current}, Temp: {self.temperature.get()}, Top-P: {self.top_p.get()}")
                generation_start = time.time()
                
                response = ollama.chat(model=model_to_use_current, messages=messages_for_ollama, options={
                    "temperature": self.temperature.get(),
                    "top_p": self.top_p.get()
                })
                generation_time = time.time() - generation_start
                print(f"[INFO] Generation completed in {generation_time:.2f} seconds")
                
                assistant_response = response['message']['content']
                
                # Enhanced empty response handling
                if not assistant_response or assistant_response.strip() == "":
                    print(f"[WARNING] AI generated empty response - Model: {model_to_use_current}, Temp: {self.temperature.get()}, Top-P: {self.top_p.get()}")
                    print(f"[DEBUG] Raw response: {response}")
                    
                    # Try fallback with safer parameters
                    print("[INFO] Retrying with safer parameters...")
                    try:
                        fallback_response = ollama.chat(model=model_to_use_current, messages=messages_for_ollama, options={
                            "temperature": 0.7,
                            "top_p": 0.9
                        })
                        assistant_response = fallback_response['message']['content']
                        
                        if not assistant_response or assistant_response.strip() == "":
                            print("[ERROR] Fallback also failed, using error message")
                            assistant_response = "⚠️ I'm experiencing technical difficulties generating a response. This might be due to extreme generation parameters or model issues. Please try again or adjust Temperature/Top-P settings."
                        else:
                            print("[SUCCESS] Fallback retry worked!")
                            assistant_response = "🔄 " + assistant_response  # Mark as retry
                    except Exception as fallback_error:
                        print(f"[ERROR] Fallback retry failed: {fallback_error}")
                        assistant_response = f"❌ Critical error: Both primary and fallback generation failed. Model: {model_to_use_current}. Please check Ollama status."
                
                self.messages.append({'role': 'assistant', 'content': assistant_response})
                self.add_message_to_history(assistant_response, "assistant")
                
                # Log assistant response
                if hasattr(self, 'logger') and self.logger:
                    try:
                        self.logger.log(get_timestamp(), "assistant", assistant_response)
                    except Exception as e:
                        print(f"[WARNING] Failed to log assistant response: {e}")
                
                end_time = time.time()
                print(f"[LOG] Generation time: {end_time - start_time:.2f} seconds")
            except Exception as e:
                error_message = f"Ollama Error: {e}. Please check if the model name is correct and if the Ollama server is running."
                self.add_message_to_history(error_message, "system")
            finally:
                self.is_processing = False
                self.send_button.configure(state="normal", text="Send")
                self.user_input_entry.focus()

# Entry point to start the GUI
if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
