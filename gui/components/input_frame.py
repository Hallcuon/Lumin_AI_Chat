import customtkinter as ctk

class InputFrame(ctk.CTkFrame):
    def __init__(self, master, send_callback, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.user_input_entry = ctk.CTkEntry(self, placeholder_text="Type your message...", height=30)
        self.user_input_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.user_input_entry.bind("<Return>", send_callback)
        self.send_button = ctk.CTkButton(self, text="Send", command=send_callback, fg_color="#596112", hover_color="#3f450c", text_color="#FFFFFF")
        self.send_button.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="e")
