# vision_manager.py
import os
class VisionManager:
    def select_image_dialog(self):
        import tkinter.filedialog
        filetypes = [("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        path = tkinter.filedialog.askopenfilename(title="Select image for Vision", filetypes=filetypes)
        return self.select_image(path)
    def __init__(self):
        self.image_path = None

    def select_image(self, path):
        if path and os.path.exists(path):
            self.image_path = path
        else:
            self.image_path = None
        return self.image_path

    def clear_image(self):
        self.image_path = None

    def get_image(self):
        return self.image_path
