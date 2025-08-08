#!/usr/bin/env python3
"""
Email Processor for ApplyX
Checks for email approvals and processes them automatically
"""

import imaplib
import email
import re
import requests
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

class EmailProcessor:
    def __init__(self):
        self.email = os.getenv('SENDER_EMAIL', 'shaheersaud2004@gmail.com')
        self.password = os.getenv('SENDER_APP_PASSWORD', 'ayjxbqjujewfgucn')
        self.api_url = "http://localhost:5001"
        
    def check_for_approvals(self):
        """Check email for approval/rejection commands"""
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.email, self.password)
            mail.select("INBOX")
            
            # Search for unread emails
            status, messages = mail.search(None, "UNSEEN")
            
            if status != 'OK':
                print("No messages found")
                return
            
            for num in messages[0].split():
                status, msg_data = mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                subject = email_message["subject"]
                from_email = email_message["from"]
                
                # Check if this is a reply to an admin notification
                if "New User Registration" in subject or "Action Required" in subject:
                    # Get email body
                    body = self.get_email_body(email_message)
                    
                    # Look for approval/rejection commands
                    approval_match = re.search(r'APPROVE\s+([a-f0-9\-]+)', body, re.IGNORECASE)
                    rejection_match = re.search(r'REJECT\s+([a-f0-9\-]+)', body, re.IGNORECASE)
                    
                    if approval_match:
                        user_id = approval_match.group(1)
                        print(f"Found approval command for user: {user_id}")
                        self.process_approval(user_id, "approve")
                        
                    elif rejection_match:
                        user_id = rejection_match.group(1)
                        print(f"Found rejection command for user: {user_id}")
                        self.process_approval(user_id, "reject")
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            print(f"Error checking emails: {e}")
    
    def get_email_body(self, email_message):
        """Extract email body from message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()
        
        return body
    
    def process_approval(self, user_id, action):
        """Process approval/rejection via API"""
        try:
            url = f"{self.api_url}/api/admin/email-approval"
            data = {
                "user_id": user_id,
                "action": action
            }
            
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {action.capitalize()} processed successfully: {result.get('message')}")
                
                # Send confirmation email
                self.send_confirmation_email(user_id, action)
            else:
                print(f"❌ Failed to process {action}: {response.text}")
                
        except Exception as e:
            print(f"Error processing {action}: {e}")
    
    def send_confirmation_email(self, user_id, action):
        """Send confirmation email to admin"""
        try:
            subject = f"Email {action.capitalize()} Processed - User {user_id}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                    .content {{ background: #f9f9f9; padding: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Email {action.capitalize()} Processed</h1>
                    </div>
                    <div class="content">
                        <h2>Confirmation</h2>
                        <p>The user with ID <strong>{user_id}</strong> has been {action}d successfully via email command.</p>
                        <p><strong>Action:</strong> {action.upper()}</p>
                        <p><strong>User ID:</strong> {user_id}</p>
                        <p><strong>Time:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p>This action was processed automatically by the ApplyX email processor.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Email {action.capitalize()} Processed
            
            The user with ID {user_id} has been {action}d successfully via email command.
            
            Action: {action.upper()}
            User ID: {user_id}
            Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
            
            This action was processed automatically by the ApplyX email processor.
            """
            
            # Send confirmation to admin
            msg = MIMEMultipart('alternative')
            msg['From'] = f"ApplyX System <{self.email}>"
            msg['To'] = self.email
            msg['Subject'] = subject
            
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            print(f"✅ Confirmation email sent for {action}")
            
        except Exception as e:
            print(f"Error sending confirmation email: {e}")

def main():
    """Main function to run email processor"""
    processor = EmailProcessor()
    
    print("🔍 Checking for email approvals...")
    processor.check_for_approvals()
    print("✅ Email check completed")

if __name__ == "__main__":
    main() 