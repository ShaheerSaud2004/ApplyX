#!/usr/bin/env python3
"""
📧 ApplyX Email Setup Script

This script helps you configure email notifications for user approvals.
"""

import os
import sys

def main():
    print("📧 ApplyX Email Configuration Setup")
    print("=" * 50)
    print()
    
    print("This script will help you set up email notifications for when you approve/reject users.")
    print("You'll need a Gmail account and an app password.")
    print()
    
    # Check current configuration
    current_email = os.getenv('SENDER_EMAIL')
    current_password = os.getenv('SENDER_APP_PASSWORD')
    current_name = os.getenv('SENDER_NAME', 'ApplyX Team')
    
    if current_email and current_password:
        print(f"✅ Email is already configured:")
        print(f"   Email: {current_email}")
        print(f"   Name: {current_name}")
        print()
        
        choice = input("Do you want to reconfigure? (y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            print("Keeping current configuration. ✅")
            return
        print()
    
    # Get user input
    print("📋 Let's set up your email configuration:")
    print()
    
    # Get Gmail address
    while True:
        email = input("Enter your Gmail address: ").strip()
        if '@' in email and '.' in email:
            break
        print("❌ Please enter a valid email address")
    
    # Get app password
    print()
    print("🔑 You need a Gmail App Password (not your regular password)")
    print("   1. Go to: https://myaccount.google.com/security")
    print("   2. Enable 2-Step Verification (if not already enabled)")
    print("   3. Click 'App passwords' and generate one for 'Mail'")
    print("   4. Copy the 16-character password")
    print()
    
    while True:
        app_password = input("Enter your 16-character app password: ").strip().replace(' ', '')
        if len(app_password) >= 10:  # Allow some flexibility
            break
        print("❌ App password should be 16 characters. Please try again.")
    
    # Get display name
    print()
    sender_name = input(f"Enter sender name (default: ApplyX Team): ").strip()
    if not sender_name:
        sender_name = "ApplyX Team"
    
    # Create export commands
    print()
    print("🔧 Setting up environment variables...")
    
    # Write to a shell script
    script_content = f"""#!/bin/bash
# ApplyX Email Configuration
export SENDER_EMAIL="{email}"
export SENDER_APP_PASSWORD="{app_password}"
export SENDER_NAME="{sender_name}"

echo "✅ Email configuration loaded!"
echo "📧 Sender: {email}"
echo "👤 Name: {sender_name}"
"""
    
    with open('email_config.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('email_config.sh', 0o755)
    
    print()
    print("✅ Configuration saved!")
    print()
    print("📋 To activate the configuration, run:")
    print("   source email_config.sh")
    print()
    print("📋 To make it permanent, add these to your ~/.bashrc or ~/.zshrc:")
    print(f'   export SENDER_EMAIL="{email}"')
    print(f'   export SENDER_APP_PASSWORD="{app_password}"')
    print(f'   export SENDER_NAME="{sender_name}"')
    print()
    
    # Test the configuration
    choice = input("Do you want to test the email configuration now? (Y/n): ").strip().lower()
    if choice not in ['n', 'no']:
        print()
        print("🧪 Testing email configuration...")
        
        # Set environment variables for this session
        os.environ['SENDER_EMAIL'] = email
        os.environ['SENDER_APP_PASSWORD'] = app_password
        os.environ['SENDER_NAME'] = sender_name
        
        try:
            sys.path.append('backend')
            from backend.email_service import email_service
            
            test_email = input("Enter an email to send a test to (or press Enter to skip): ").strip()
            if test_email:
                print(f"📧 Sending test email to {test_email}...")
                result = email_service.send_approval_email(test_email, "Test User")
                
                if result:
                    print("✅ Test email sent successfully!")
                    print("Check the inbox (and spam folder) for the test email.")
                else:
                    print("❌ Test email failed. Check the backend logs for details.")
            else:
                print("Skipping email test.")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("Make sure to restart your backend server after configuring.")
    
    print()
    print("🎉 Email setup complete!")
    print()
    print("📋 Next steps:")
    print("1. Run: source email_config.sh")
    print("2. Restart your backend server: cd backend && python3 app.py")
    print("3. Test by approving a user in the admin dashboard!")

if __name__ == "__main__":
    main() 