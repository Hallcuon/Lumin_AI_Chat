# chat_logger.py
import datetime
import os

class ChatLogger:
    def __init__(self, log_dir=None):
        # Use consistent log file name instead of timestamp-based
        self.log_file = os.path.join(log_dir or '', "chat.log")
        
        # Create log file if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOG: Chat log initialized.\n")

    def log(self, timestamp, role, text):
        with open(self.log_file, "a", encoding="utf-8") as logf:
            logf.write(f"[{timestamp}] {role.upper()}: {text}\n")

    def view_log(self, tail=3000):
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                return f.read()[-tail:]
        return ""
