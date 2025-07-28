import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Email configuration - these will be set via environment variables
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('SENDER_EMAIL')  # Your personal email
        self.sender_password = os.getenv('SENDER_APP_PASSWORD')  # Your app password
        self.sender_name = os.getenv('SENDER_NAME', 'ApplyX Team')
        
    def send_approval_email(self, user_email, user_name):
        """Send approval email to user"""
        try:
            subject = "🎉 Your ApplyX Account Has Been Approved!"
            
            # Create HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Welcome to ApplyX!</h1>
                        <p>Your account has been approved</p>
                    </div>
                    <div class="content">
                        <h2>Hi {user_name}!</h2>
                        <p>Great news! Your ApplyX account has been <strong>approved</strong> and you can now start using our AI-powered job application platform.</p>
                        
                        <p><strong>What you can do now:</strong></p>
                        <ul>
                            <li>✅ Log in to your dashboard</li>
                            <li>🤖 Set up your AI job application bot</li>
                            <li>📄 Upload your resume and configure preferences</li>
                            <li>🎯 Start applying to jobs automatically</li>
                        </ul>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:3000" class="button">Login to ApplyX</a>
                        </p>
                        
                        <p>If you have any questions or need help getting started, feel free to reply to this email.</p>
                        
                        <p>Best regards,<br>The ApplyX Team</p>
                    </div>
                    <div class="footer">
                        <p>ApplyX - AI-Powered Job Applications by Nebula.AI</p>
                        <p>This email was sent because your account was approved by an administrator.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_content = f"""
            Hi {user_name}!

            Great news! Your ApplyX account has been approved and you can now start using our AI-powered job application platform.

            What you can do now:
            ✅ Log in to your dashboard
            🤖 Set up your AI job application bot
            📄 Upload your resume and configure preferences
            🎯 Start applying to jobs automatically

            Login here: http://localhost:3000

            If you have any questions or need help getting started, feel free to reply to this email.

            Best regards,
            The ApplyX Team

            ---
            ApplyX - AI-Powered Job Applications by Nebula.AI
            This email was sent because your account was approved by an administrator.
            """
            
            return self._send_email(user_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Error sending approval email to {user_email}: {e}")
            return False

    def send_rejection_email(self, user_email, user_name, reason=""):
        """Send rejection email to user"""
        try:
            subject = "ApplyX Account Application Update"
            
            # Create HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #ef4444; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>ApplyX Account Update</h1>
                    </div>
                    <div class="content">
                        <h2>Hi {user_name},</h2>
                        <p>Thank you for your interest in ApplyX. After reviewing your application, we're unable to approve your account at this time.</p>
                        
                        {f'<p><strong>Reason:</strong> {reason}</p>' if reason else ''}
                        
                        <p>You're welcome to reapply in the future. If you have any questions about this decision, please feel free to contact our support team.</p>
                        
                        <p>Best regards,<br>The ApplyX Team</p>
                    </div>
                    <div class="footer">
                        <p>ApplyX - AI-Powered Job Applications by Nebula.AI</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_content = f"""
            Hi {user_name},

            Thank you for your interest in ApplyX. After reviewing your application, we're unable to approve your account at this time.

            {f'Reason: {reason}' if reason else ''}

            You're welcome to reapply in the future. If you have any questions about this decision, please feel free to contact our support team.

            Best regards,
            The ApplyX Team

            ---
            ApplyX - AI-Powered Job Applications by Nebula.AI
            """
            
            return self._send_email(user_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Error sending rejection email to {user_email}: {e}")
            return False

    def _send_email(self, to_email, subject, html_content, text_content):
        """Internal method to send email"""
        try:
            if not self.sender_email or not self.sender_password:
                logger.error("Email credentials not configured. Please set SENDER_EMAIL and SENDER_APP_PASSWORD environment variables.")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Create text and HTML parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            # Add parts to message
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

# Create global email service instance
email_service = EmailService() 