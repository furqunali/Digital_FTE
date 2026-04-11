import time
import json
from pathlib import Path
from datetime import datetime

VAULT_PATH = "vault"

class AIEmployee:
    def __init__(self):
        self.vault = Path(VAULT_PATH)
        for folder in ["Needs_Action", "Done", "Pending_Approval", "Approved", "Rejected", "Logs"]:
            (self.vault / folder).mkdir(parents=True, exist_ok=True)
        print("[OK] AI Employee Ready!")
    
    def run(self):
        print(f"[WATCHING] {self.vault}/Needs_Action")
        print("[TIP] Create a .md file in that folder to test")
        print("[PRESS] Ctrl+C to stop\n")
        
        while True:
            for file in (self.vault / "Needs_Action").glob("*.md"):
                print(f"\n[PROCESSING] {file.name}")
                
                # Read request
                content = file.read_text(encoding='utf-8')
                
                # Check if needs approval
                if "APPROVAL" in content.upper() or "PAYMENT" in content.upper():
                    approval_file = self.vault / "Pending_Approval" / f"approval_{file.stem}.md"
                    approval_file.write_text(f"# APPROVAL NEEDED\n\n{content}", encoding='utf-8')
                    print(f"   [ALERT] Approval needed! File moved to Pending_Approval")
                else:
                    # Simple response
                    response = f"# Response to {file.name}\n\n[OK] Task processed successfully!\n\nOriginal: {content[:200]}"
                    (self.vault / "Done" / f"response_{file.name}").write_text(response, encoding='utf-8')
                    print(f"   [OK] Processed and saved to Done folder")
                
                # Move original file
                file.rename(self.vault / "Done" / file.name)
            
            time.sleep(5)

if __name__ == "__main__":
    print("="*50)
    print("PERSONAL AI EMPLOYEE - WORKING VERSION")
    print("="*50)
    
    # Create test file
    employee = AIEmployee()
    test_file = employee.vault / "Needs_Action" / "test_request.md"
    if not test_file.exists():
        test_file.write_text("Hello! Please process this request.", encoding='utf-8')
        print("[OK] Test file created\n")
    
    # Run
    employee.run()
