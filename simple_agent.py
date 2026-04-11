"""
simple_agent.py - AI Employee with Client Auto-Reply
"""

import time
import shutil
import smtplib
import imaplib
import email
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================
GMAIL_EMAIL = "furqanfarrukh12345@gmail.com"
GMAIL_PASSWORD = "hwykrcjppufhysfi"
GMAIL_NAME = "AI Employee"
VAULT_PATH = "vault"

class AIEmployee:
    def __init__(self):
        self.vault = Path(VAULT_PATH)
        self.setup_folders()
        self.processed_count = 0
        print("=" * 50)
        print("🤖 AI EMPLOYEE ACTIVATED")
        print(f"📧 Email: {GMAIL_EMAIL}")
        print("=" * 50)
    
    def setup_folders(self):
        folders = ["Needs_Action", "Done", "Pending_Approval", "Approved", "Rejected", "Logs"]
        for folder in folders:
            (self.vault / folder).mkdir(parents=True, exist_ok=True)
        print("✅ Folders ready")
    
    def extract_client_email(self, email_content):
        """Extract client email from the email content"""
        lines = email_content.split('\n')
        for line in lines:
            if line.lower().startswith('from:'):
                # Extract email from "Name <email>" or just "email"
                import re
                match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
                if match:
                    return match.group()
        return GMAIL_EMAIL  # fallback to owner
    
    def send_email(self, to_address, subject, body):
        """Send email using Gmail"""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{GMAIL_NAME} <{GMAIL_EMAIL}>"
            msg['To'] = to_address
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            print(f"  ✅ Email sent to: {to_address}")
            return True
        except Exception as e:
            print(f"  ❌ Email error: {e}")
            return False
    
    def check_emails(self):
        """Direct email reading from Gmail"""
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(GMAIL_EMAIL, GMAIL_PASSWORD)
            mail.select("INBOX")
            
            result, data = mail.search(None, 'UNSEEN')
            
            for num in data[0].split():
                result, msg_data = mail.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject = msg['subject']
                from_addr = msg['from']
                body = ""
                
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                
                # Save to Needs_Action with client email info
                filename = f"email_{int(time.time())}.txt"
                filepath = self.vault / "Needs_Action" / filename
                
                content = f"""From: {from_addr}
Subject: {subject}
ClientEmail: {from_addr}

{body}
"""
                filepath.write_text(content, encoding='utf-8')
                print(f"  📧 New email from: {from_addr}")
            
            mail.close()
            mail.logout()
        except Exception as e:
            pass
    
    def process_file(self, filepath):
        content = filepath.read_text(encoding='utf-8')
        content_upper = content.upper()
        
        # Extract client email
        client_email = GMAIL_EMAIL
        for line in content.split('\n'):
            if line.startswith('From:'):
                parts = line.split(':')
                if len(parts) > 1:
                    client_email = parts[1].strip()
                break
        
        # Check for approval keywords
        if any(word in content_upper for word in ["APPROVAL", "PAYMENT", "INVOICE", "$", "SEND MONEY"]):
            dest = self.vault / "Pending_Approval" / filepath.name
            filepath.rename(dest)
            print(f"  ⚠️ APPROVAL NEEDED: {filepath.name}")
            
            # Send acknowledgment to CLIENT (not just owner!)
            client_msg = f"""Dear Client,

Thank you for your request. I have received it and it is currently waiting for approval.

Request ID: {filepath.name}
Status: Pending Approval

You will receive another confirmation once approved.

Best regards,
AI Employee System
"""
            self.send_email(client_email, "Request Received - Pending Approval", client_msg)
            
            # Also notify owner
            owner_msg = f"Request '{filepath.name}' from {client_email} needs approval."
            self.send_email(GMAIL_EMAIL, f"Approval Needed: {filepath.name}", owner_msg)
        
        elif "SEND EMAIL" in content_upper:
            lines = content.split('\n')
            to_email = None
            subject = "AI Employee Response"
            body = content
            
            for line in lines:
                if line.lower().startswith("to:"):
                    to_email = line[3:].strip()
                elif line.lower().startswith("subject:"):
                    subject = line[8:].strip()
            
            if to_email:
                self.send_email(to_email, subject, body)
                dest = self.vault / "Done" / filepath.name
                filepath.rename(dest)
                print(f"  ✅ EMAIL SENT to: {to_email}")
        
        else:
            response = f"""AI RESPONSE
Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Task completed successfully.
"""
            response_file = self.vault / "Done" / f"response_{filepath.name}"
            response_file.write_text(response)
            dest = self.vault / "Done" / filepath.name
            filepath.rename(dest)
            print(f"  ✅ PROCESSED: {filepath.name}")
        
        self.processed_count += 1
    
    def check_approvals(self):
        """Check Approved folder and execute actions"""
        approved_folder = self.vault / "Approved"
        for file in approved_folder.glob("*"):
            if file.is_file():
                print(f"  ✅ EXECUTING approved action: {file.name}")
                content = file.read_text()
                
                # Extract client email
                client_email = GMAIL_EMAIL
                for line in content.split('\n'):
                    if line.startswith('ClientEmail:'):
                        client_email = line.split(':', 1)[1].strip()
                    elif line.startswith('From:'):
                        client_email = line.split(':', 1)[1].strip()
                
                # Send confirmation to CLIENT
                client_msg = f"""Dear Client,

Your request '{file.name}' has been APPROVED and is being processed.

Status: Completed
Processed by: AI Employee System

Thank you for your business.
"""
                self.send_email(client_email, f"Request Approved: {file.name}", client_msg)
                
                # Also notify owner
                self.send_email(GMAIL_EMAIL, f"Executed: {file.name}", 
                               f"Request from {client_email} has been approved and executed.")
                
                file.rename(self.vault / "Done" / f"executed_{file.name}")
        
        # Handle rejected
        rejected_folder = self.vault / "Rejected"
        for file in rejected_folder.glob("*"):
            if file.is_file():
                print(f"  ❌ REJECTED: {file.name}")
                content = file.read_text()
                
                client_email = GMAIL_EMAIL
                for line in content.split('\n'):
                    if line.startswith('ClientEmail:'):
                        client_email = line.split(':', 1)[1].strip()
                
                client_msg = f"""Dear Client,

Your request '{file.name}' has been REJECTED.

Please contact support for more information.

Regards,
AI Employee System
"""
                self.send_email(client_email, f"Request Rejected: {file.name}", client_msg)
                
                file.rename(self.vault / "Done" / f"rejected_{file.name}")
    
    def run(self):
        print(f"\n📁 Watching: {self.vault}/Needs_Action")
        print(f"📧 Auto-checking Gmail every 30 seconds")
        print("💡 AI will reply to BOTH client AND owner")
        print("❌ Press Ctrl+C to stop\n")
        
        email_check_count = 0
        
        while True:
            try:
                if email_check_count >= 10:
                    self.check_emails()
                    email_check_count = 0
                email_check_count += 1
                
                files = list((self.vault / "Needs_Action").glob("*"))
                for file in files:
                    if not file.is_file() or file.suffix in ['.tmp', '.swp']:
                        continue
                    self.process_file(file)
                
                self.check_approvals()
                time.sleep(3)
                
            except KeyboardInterrupt:
                print(f"\n\n🛑 Shutdown. Processed: {self.processed_count} files")
                break
            except Exception as e:
                print(f"  ❌ Error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🎯 PERSONAL AI EMPLOYEE - WITH CLIENT AUTO-REPLY")
    print("=" * 50 + "\n")
    
    ai = AIEmployee()
    ai.run()
