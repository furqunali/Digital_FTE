import imaplib
import email
import time
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv('GMAIL_EMAIL')
PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
VAULT_PATH = "vault"

def check_and_save_emails():
    """Check Gmail and save unread emails to Needs_Action"""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, PASSWORD)
        mail.select("INBOX")
        
        # Search unread emails
        result, data = mail.search(None, 'UNSEEN')
        
        for num in data[0].split():
            result, msg_data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Get email content
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
            
            # Save to Needs_Action
            needs_action = Path(VAULT_PATH) / "Needs_Action"
            needs_action.mkdir(parents=True, exist_ok=True)
            
            filename = f"email_{int(time.time())}_{from_addr.replace(' ', '_')}.txt"
            filepath = needs_action / filename
            
            content = f"""From: {from_addr}
Subject: {subject}
Received: {time.strftime('%Y-%m-%d %H:%M:%S')}

{body}
"""
            filepath.write_text(content, encoding='utf-8')
            print(f"📧 Email saved: {filename}")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"Email check error: {e}")

if __name__ == "__main__":
    check_and_save_emails()
