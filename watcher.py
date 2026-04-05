import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from agent_brain import process_task
from pathlib import Path

WATCH_DIR = "./Vault/Needs_Action"

class NewTaskHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            time.sleep(1) 
            process_task(event.src_path)

if __name__ == "__main__":
    Path(WATCH_DIR).mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(NewTaskHandler(), WATCH_DIR, recursive=False)
    print("👀 Digital FTE Watcher is running...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()