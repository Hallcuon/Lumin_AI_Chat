import customtkinter as ctk

class ChatFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.chat_history_textbox = ctk.CTkTextbox(self, wrap="word", state="disabled", font=("Arial", 20))
        self.chat_history_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.chat_history_textbox.tag_config("user_tag", foreground="#FAF7F3", lmargin1=20, lmargin2=20, rmargin=100)
        self.chat_history_textbox.tag_config("assistant_tag", foreground="#D9A299", lmargin1=100, lmargin2=100, rmargin=20)
        self.chat_history_textbox.tag_config("system_tag", foreground="#722323")
