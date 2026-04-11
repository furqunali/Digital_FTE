import os
import time
from google import genai
from pathlib import Path

# DIRECT KEY
api_key = "AIzaSyBJAKZEifM019E6n3o2rjs6LdSKs6PjzTA"
client = genai.Client(api_key=api_key)

def start_agent():
    needs_action_path = Path("./Vault/Needs_Action")
    approved_path = Path("./Vault/Approved")
    needs_action_path.mkdir(parents=True, exist_ok=True)
    approved_path.mkdir(parents=True, exist_ok=True)

    print("🚀 BRAIN UPDATED: Watching for ANY .md file...")

    while True:
        files = list(needs_action_path.glob("*.md"))
        for task_file in files:
            print(f"🔍 Found: {task_file.name}")
            try:
                content = task_file.read_text(encoding="utf-8-sig", errors="ignore")
                if content.strip():
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=f"Draft a professional reply for Furqan: {content}"
                    )
                    approval_file = approved_path / f"APPROVE_{task_file.name}"
                    approval_file.write_text(response.text, encoding="utf-8")
                    print(f"✅ Success! Draft created.")
                task_file.unlink() 
            except Exception as e:
                print(f"❌ Error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    start_agent()
