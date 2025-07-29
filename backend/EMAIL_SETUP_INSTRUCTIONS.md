# 📧 Email Setup Instructions for ApplyX

## Quick Setup Guide

### 1. 🔑 Generate Gmail App Password

1. **Go to Google Account Settings:**
   - Visit: https://myaccount.google.com/
   - Click "Security" in the left sidebar

2. **Enable 2-Factor Authentication (if not already enabled):**
   - Under "Signing in to Google", click "2-Step Verification"
   - Follow the setup process

3. **Generate App Password:**
   - Still in "Security", click "2-Step Verification"
   - Scroll down and click "App passwords"
   - Select "Mail" and your device
   - **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### 2. 🌍 Set Environment Variables

**Option A: Using export commands (recommended)**
```bash
# Add these to your terminal session or ~/.bashrc / ~/.zshrc
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_APP_PASSWORD="abcd efgh ijkl mnop"  # The 16-char password from step 1
export SENDER_NAME="ApplyX Team"
```

**Option B: Create .env file**
```bash
# Create .env file in the backend/ directory
cd backend
echo "SENDER_EMAIL=your-email@gmail.com" > .env
echo "SENDER_APP_PASSWORD=abcd efgh ijkl mnop" >> .env
echo "SENDER_NAME=ApplyX Team" >> .env
```

### 3. ✅ Test Email Setup

```bash
# Test the email service
cd backend
python3 -c "
from email_service import email_service
print('Testing email configuration...')
result = email_service.send_approval_email('test@example.com', 'Test User')
print(f'Email test result: {result}')
"
```

### 4. 🚀 Restart Backend Server

```bash
# Make sure to restart your backend server to load the new environment variables
cd backend
python3 app.py
```

## 📋 Troubleshooting

### Error: "Email credentials not configured"
- **Solution:** Make sure environment variables are set correctly
- **Check:** Run `echo $SENDER_EMAIL` to verify the variable is set

### Error: "Authentication failed"
- **Solution:** Verify your app password is correct (16 characters, no spaces)
- **Note:** Use the app password, NOT your regular Gmail password

### Error: "Less secure app access"
- **Solution:** Use App Password instead of enabling "less secure apps"
- **Note:** Google deprecated "less secure app" access

### Gmail Alternative: Use Other Email Providers

**For Outlook/Hotmail:**
```bash
export SENDER_EMAIL="your-email@outlook.com"
export SENDER_APP_PASSWORD="your-app-password"
# The SMTP server will be auto-detected, but you can override:
# export SMTP_SERVER="smtp-mail.outlook.com"
# export SMTP_PORT="587"
```

**For Yahoo:**
```bash
export SENDER_EMAIL="your-email@yahoo.com"
export SENDER_APP_PASSWORD="your-app-password"
# export SMTP_SERVER="smtp.mail.yahoo.com"
# export SMTP_PORT="587"
```

## 🎯 What Happens After Setup

1. **User Signs Up:** Gets beautiful waitlist confirmation
2. **Admin Approves:** User receives email with login instructions
3. **User Rejected:** User receives polite rejection email
4. **Email Content:** Professional HTML emails with ApplyX branding

## 🔧 Advanced Configuration

### Custom Email Templates
Edit `backend/email_service.py` to customize:
- Email subject lines
- HTML templates
- Logo and branding
- Call-to-action buttons

### Email Logging
All email attempts are logged to console with:
- ✅ Success messages
- ⚠️ Failure warnings  
- ❌ Error details

## 📞 Support

If you need help setting this up:
1. Check the console logs for specific error messages
2. Verify environment variables: `env | grep SENDER`
3. Test with a simple Python script first
4. Make sure 2FA is enabled on your Gmail account

---

**⚡ Once configured, your admin approvals will automatically send beautiful email notifications to users!** 