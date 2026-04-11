import os
import time
import json
import smtplib
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai

# ============================================
# CONFIGURATION
# ============================================
API_KEY = "AIzaSyBJAKZEifM019E6n3o2rjs6LdSKs6PjzTA"
VAULT_PATH = "vault"

# ============================================
# AI EMPLOYEE CLASS
# ============================================
class AIEmployee:
    def __init__(self):
        self.vault = Path(VAULT_PATH)
        self.setup_folders()
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        print("🤖 AI Employee Initialized with Gemini")
    
    def setup_folders(self):
        \"\"\"Create all required vault folders\"\"\"
        folders = [
            "Needs_Action", "In_Progress", "Plans", 
            "Pending_Approval", "Approved", "Rejected",
            "Done", "Briefings", "Logs", "Accounting"
        ]
        for folder in folders:
            (self.vault / folder).mkdir(parents=True, exist_ok=True)
    
    def process_with_gemini(self, request_text, request_type="general"):
        \"\"\"Process any request using Gemini AI\"\"\"
        prompt = f\"\"\"
You are an AI Employee. Process this {request_type} request:

{request_text}

Provide a professional response with:
1. Acknowledgment of the request
2. Specific action plan with checkboxes
3. Any recommendations or next steps

Use markdown formatting.
\"\"\"
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def request_approval(self, action_type, details):
        \"\"\"Create a human-in-the-loop approval request\"\"\"
        request_id = f"{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        content = f\"\"\"---
type: approval_request
id: {request_id}
action: {action_type}
created: {datetime.now().isoformat()}
status: pending
---

## 🔐 Approval Required: {action_type.upper()}

### Details
{json.dumps(details, indent=2)}

### Instructions
- **To APPROVE**: Move this file to /Approved folder
- **To REJECT**: Move this file to /Rejected folder
\"\"\"
        filepath = self.vault / "Pending_Approval" / f"{request_id}.md"
        filepath.write_text(content)
        print(f"📋 Approval request created: {request_id}")
        return request_id
    
    def send_email(self, to, subject, body):
        \"\"\"Send email via SMTP (Gmail)\"\"\"
        print(f"📧 Would send email to: {to}")
        print(f"   Subject: {subject}")
        print(f"   Body preview: {body[:100]}...")
        # In dry-run mode, just log it
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "to": to,
            "subject": subject,
            "dry_run": True
        }
        log_file = self.vault / "Logs" / f"email_{datetime.now().strftime('%Y%m%d')}.json"
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        else:
            logs = []
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))
        return True
    
    def monitor_and_process(self):
        \"\"\"Main loop - monitor Needs_Action and process files\"\"\"
        needs_action = self.vault / "Needs_Action"
        
        print("👀 Monitoring for new actions...")
        print(f"📁 Watch folder: {needs_action.absolute()}")
        print("\n💡 To test: Create a .md file in that folder")
        print("Press Ctrl+C to stop\n")
        
        while True:
            files = list(needs_action.glob("*.md"))
            
            for file in files:
                print(f"\n📄 Processing: {file.name}")
                
                # Read the request
                request = file.read_text(encoding='utf-8')
                
                # Check if this needs approval
                if "APPROVAL" in request.upper() or "PAYMENT" in request.upper():
                    self.request_approval("sensitive_action", {"file": file.name, "content": request[:200]})
                    # Move to pending
                    pending_dir = self.vault / "In_Progress"
                    pending_dir.mkdir(exist_ok=True)
                    file.rename(pending_dir / file.name)
                else:
                    # Process with AI
                    response = self.process_with_gemini(request, "action")
                    
                    # Save response
                    response_file = self.vault / "Done" / f"response_{file.stem}.md"
                    response_file.write_text(f"# Response to {file.name}\n\n{response}")
                    
                    # Move original to Done
                    file.rename(self.vault / "Done" / file.name)
                    
                    print(f"✅ Completed: {file.name}")
                    print(f"📝 Response saved: {response_file.name}")
            
            time.sleep(10)  # Check every 10 seconds
    
    def create_sample_request(self):
        \"\"\"Create a sample request for testing\"\"\"
        sample = self.vault / "Needs_Action" / "sample_client_email.md"
        sample.write_text(\"\"\"
# Client Email Request

**From:** john@example.com
**Subject:** Question about pricing

Hi Team,

I'm interested in your AI Employee solution. Can you send me pricing information for the Silver Tier?

Also, do you offer any discounts for students?

Thanks,
John
\"\"\")
        print("✅ Sample request created in Needs_Action/")
        
        # Also create an approval sample
        approval_sample = self.vault / "Needs_Action" / "payment_approval_needed.md"
        approval_sample.write_text(\"\"\"
# PAYMENT APPROVAL NEEDED

**Action:** Send invoice to client
**Amount:** 
**Client:** ABC Corp
**Reason:** Monthly subscription fee

APPROVAL REQUIRED before proceeding.
\"\"\")
        print("✅ Sample approval request created")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 AI EMPLOYEE - SILVER TIER")
    print("=" * 50)
    
    employee = AIEmployee()
    employee.create_sample_request()
    
    print("\n" + "=" * 50)
    employee.monitor_and_process()
