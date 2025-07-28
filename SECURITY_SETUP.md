# 🔐 Security Setup Guide for ApplyX

This guide explains how to securely configure your ApplyX LinkedIn bot without exposing sensitive credentials in your code or version control.

## 🚨 **Critical Security Changes**

### ⚠️ **Before You Start**
If you have existing credential files (`config.yaml`, `email_config.sh`, `.env`) with real secrets, **DO NOT COMMIT THEM**. These files are now in `.gitignore` to prevent accidental commits.

## 🛠️ **Quick Setup (Recommended)**

Run the automated setup script:

```bash
python3 setup_secrets.py
```

This script will:
- ✅ Create secure template files
- ✅ Generate cryptographically secure secrets
- ✅ Check your `.gitignore` configuration
- ✅ Guide you through the remaining setup steps

## 📝 **Manual Setup**

If you prefer to set up manually, follow these steps:

### 1. **Create Environment File**

```bash
# Copy the template
cp env.example .env

# Edit with your actual credentials
nano .env  # or your preferred editor
```

### 2. **Create Configuration File**

```bash
# Copy the template
cp config.yaml.example config.yaml

# Edit with your preferences and credentials
nano config.yaml
```

### 3. **Create Email Configuration**

```bash
# Copy the template
cp email_config.sh.example email_config.sh

# Edit with your email credentials
nano email_config.sh

# Make it executable
chmod +x email_config.sh
```

## 🔑 **Required Credentials**

### **LinkedIn Credentials**
- **Email**: Your LinkedIn account email
- **Password**: Your LinkedIn account password
- **⚠️ Recommendation**: Use a dedicated LinkedIn account for job applications

### **OpenAI API Key**
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

### **Email Credentials (Gmail)**
1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Generate an app password for "Mail"
3. Use this 16-character password (not your regular Gmail password)

## 📋 **Configuration Priority**

The application loads configuration in this order (later sources override earlier ones):

1. **Default values** (built into the code)
2. **config.yaml file** (your job preferences)
3. **Environment variables** (sensitive credentials)

This allows you to:
- Keep job preferences in `config.yaml`
- Store sensitive data in environment variables
- Override anything via environment variables

## 🔒 **Security Features**

### **Files Protected by .gitignore**
These files will **never** be committed to git:
- `.env` (environment variables)
- `config.yaml` (may contain credentials)
- `email_config.sh` (email credentials)
- `user_config_*.yaml` (user-specific configs)
- `*.log` (may contain sensitive data)
- `uploads/` (resumes and documents)

### **Environment Variable Support**
You can override any sensitive setting using environment variables:

```bash
# LinkedIn credentials
export LINKEDIN_EMAIL="your-email@gmail.com"
export LINKEDIN_PASSWORD="your-password"

# OpenAI API key
export OPENAI_API_KEY="sk-your-api-key"

# Email settings
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_APP_PASSWORD="your-app-password"
```

## 🚀 **Starting the Application**

### **Backend**
```bash
cd backend
source ../email_config.sh  # Load email config
python3 app.py
```

### **Frontend**
```bash
npm run dev
```

### **Using Environment Variables Only**
If you prefer to use only environment variables:

```bash
# Set all required variables
export LINKEDIN_EMAIL="your-email@gmail.com"
export LINKEDIN_PASSWORD="your-password"
export OPENAI_API_KEY="sk-your-api-key"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_APP_PASSWORD="your-app-password"

# Start backend (no need for email_config.sh)
cd backend && python3 app.py
```

## 🔧 **Configuration Examples**

### **Minimal .env File**
```bash
# Required credentials
LINKEDIN_EMAIL=your-email@gmail.com
LINKEDIN_PASSWORD=your-password-here
OPENAI_API_KEY=sk-your-openai-api-key-here

# Email configuration
SENDER_EMAIL=your-email@gmail.com
SENDER_APP_PASSWORD=your-16-char-app-password
SENDER_NAME=ApplyX Team

# Application settings
MAX_APPLICATIONS_PER_DAY=50
AGENT_DELAY_MINUTES=2
```

### **Minimal config.yaml**
```yaml
# Job search preferences (no sensitive data)
positions:
  - Software Engineer
  - Full Stack Developer
  - Python Developer

locations:
  - Remote
  - New York
  - San Francisco

experienceLevel:
  entry: true
  associate: true

jobTypes:
  full-time: true
  contract: true
```

## 🛡️ **Security Best Practices**

### **✅ Do This**
- Use the setup script for secure configuration
- Store credentials in environment variables
- Use strong, unique passwords
- Keep `.gitignore` updated
- Regularly rotate API keys
- Use a dedicated LinkedIn account for automation

### **❌ Never Do This**
- Commit files with real credentials
- Share API keys in screenshots or logs
- Use your main LinkedIn account for automation
- Push secrets to public repositories
- Store credentials in code comments

## 🔍 **Verifying Your Setup**

Check that your secrets are properly protected:

```bash
# Check .gitignore
cat .gitignore | grep -E "(\.env|config\.yaml|email_config\.sh)"

# Verify files won't be committed
git status --ignored

# Test configuration loading
python3 -c "from config_loader import load_secure_config, get_masked_config; config = load_secure_config(); print('Config loaded successfully'); print(get_masked_config(config))"
```

## 🆘 **Troubleshooting**

### **"Config file not found"**
- Run `python3 setup_secrets.py` to create template files
- Or manually copy from `.example` files

### **"Missing credentials"**
- Check your `.env` file has the required variables
- Verify environment variables are set: `echo $LINKEDIN_EMAIL`

### **"Git wants to commit secrets"**
- Check `.gitignore` includes the secret files
- Run `git status --ignored` to see ignored files

### **"Application can't connect to LinkedIn"**
- Verify LinkedIn credentials are correct
- Check if your account requires 2FA (may need app-specific setup)

## 🔄 **Migration from Old Setup**

If you have existing files with hardcoded secrets:

1. **Back up your current settings** (copy job preferences)
2. **Run the setup script**: `python3 setup_secrets.py`
3. **Copy your preferences** to the new template files
4. **Test the configuration** with masked output
5. **Delete old files with secrets** (after confirming new setup works)

---

## 📚 **Additional Resources**

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Gmail App Passwords Guide](https://support.google.com/accounts/answer/185833)
- [LinkedIn Automation Best Practices](https://www.linkedin.com/help/linkedin/answer/56347)
- [Git Security Best Practices](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure)

---

**🔐 Remember: Your security is paramount. Never share your API keys or credentials, and always verify that sensitive files are in `.gitignore` before committing to version control.** 