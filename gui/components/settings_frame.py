import customtkinter as ctk

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, model_options, character_options, model_var, character_var, update_callback, restart_callback, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Select Ollama Model:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.model_optionmenu = ctk.CTkOptionMenu(self, values=model_options, variable=model_var, command=update_callback)
        self.model_optionmenu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(self, text="Select Character:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.character_optionmenu = ctk.CTkOptionMenu(self, values=character_options, variable=character_var, command=update_callback)
        self.character_optionmenu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.restart_chat_button = ctk.CTkButton(self, text="Restart Chat", command=restart_callback, fg_color="#2a1261", hover_color="#210f4a", text_color="#FFFFFF")
        self.restart_chat_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="nsew")
