import threading
import time
import random
from datetime import datetime
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("[WARNING] plyer not available - notifications disabled")

import ollama

class ProactiveManager:
    def __init__(self, app_ref):
        self.app = app_ref
        self.thread = None
        self.enabled = True

    def start(self):
        self.enabled = True
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def stop(self):
        self.enabled = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def run(self):
        time.sleep(15)
        while self.enabled:
            try:
                time.sleep(random.randint(45, 90))
                if not self.enabled:
                    break
                    
                if self.app.message_lock.acquire(blocking=False):
                    try:
                        if hasattr(self.app, 'is_processing') and self.app.is_processing:
                            continue
                        current_time = datetime.now().strftime("%H:%M")
                        proactive_messages = [
                            {'role': 'system', 'content': self.app.system_prompt + f"\n\nCurrent time is {current_time}. You can initiate conversation if you want to. If someone asked you to send a message at specific time, check if it matches current time and respond accordingly. For regular conversation, think about our previous context and maintain conversation continuity. Don't start new topics if we're already discussing something. Don't forget what we talked about earlier. If you want to say something, continue our current discussion. If there's nothing relevant to add right now and no time-based requests match current time, respond with 'NOTHING_TO_SAY'."},
                        ]
                        if hasattr(self.app, 'messages') and self.app.messages:
                            proactive_messages.extend(self.app.messages[1:])
                        response = ollama.chat(model=self.app.selected_model.get(), messages=proactive_messages, options={
                            "temperature": 0.8,  # Use safe parameters for proactive messages
                            "top_p": 0.9
                        })
                        potential_message = response['message']['content']
                        
                        # Enhanced filtering for empty/invalid proactive responses
                        if (potential_message and 
                            potential_message.strip() and  # Not empty or whitespace
                            "NOTHING_TO_SAY" not in potential_message and
                            len(potential_message.strip()) > 3):  # At least 4 characters
                            
                            print(f"[PROACTIVE] Generated message: {potential_message[:50]}...")
                            self.app.messages.append({'role': 'assistant', 'content': potential_message})
                            self.app.add_message_to_history(potential_message, "assistant")
                            
                            if NOTIFICATIONS_AVAILABLE:
                                try:
                                    notification.notify(
                                        title=f"{self.app.char_name} said",
                                        message=potential_message[:100] + "..." if len(potential_message) > 100 else potential_message,
                                        app_icon=None,
                                        timeout=10,
                                    )
                                except Exception as e:
                                    print(f"[WARNING] Notification failed: {e}")
                        else:
                            print(f"[PROACTIVE] Filtered out invalid response: '{potential_message}'")
                    finally:
                        self.app.message_lock.release()
            except Exception as e:
                print(f"[ERROR] Proactive manager error: {e}")
                time.sleep(60)  # Wait before retrying
