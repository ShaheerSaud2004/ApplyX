#!/usr/bin/env python3
"""
ApplyX Secrets Setup Script
===========================
This script helps you securely configure your environment variables
without exposing secrets in your code or version control.
"""

import os
import secrets
import string
import shutil
from pathlib import Path
import getpass

def generate_secret_key(length=32):
    """Generate a cryptographically secure secret key."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_encryption_key():
    """Generate a 32-byte encryption key."""
    return secrets.token_hex(32)

def setup_env_file():
    """Set up the .env file from the template."""
    print("🔧 Setting up environment variables...")
    
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ env.example file not found!")
        return False
    
    if env_file.exists():
        overwrite = input("📄 .env file already exists. Overwrite? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("⏭️ Skipping .env setup")
            return True
    
    # Copy template
    shutil.copy(env_example, env_file)
    
    # Read the file
    with open(env_file, 'r') as f:
        content = f.read()
    
    print("\n🔑 Generating secure values...")
    
    # Generate secure values
    secret_key = generate_secret_key()
    encryption_key = generate_encryption_key()
    hash_salt = generate_secret_key(16)
    
    # Replace placeholder values
    replacements = {
        'generate-a-long-random-secret-key-here-32-characters-minimum': secret_key,
        'generate-a-32-byte-encryption-key-here': encryption_key,
        'generate-a-random-hash-salt-here': hash_salt,
    }
    
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    # Write back
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ .env file created with secure default values")
    print("📝 Please edit .env to add your API keys and credentials")
    return True

def setup_config_yaml():
    """Set up the config.yaml file from the template."""
    print("\n🔧 Setting up config.yaml...")
    
    config_example = Path("config.yaml.example")
    config_file = Path("config.yaml")
    
    if not config_example.exists():
        print("❌ config.yaml.example file not found!")
        return False
    
    if config_file.exists():
        print("⚠️ config.yaml already exists")
        overwrite = input("📄 This file may contain secrets. Overwrite? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("⏭️ Skipping config.yaml setup")
            return True
    
    # Copy template
    shutil.copy(config_example, config_file)
    print("✅ config.yaml created from template")
    print("📝 Please edit config.yaml to add your credentials and preferences")
    return True

def setup_email_config():
    """Set up the email_config.sh file from the template."""
    print("\n🔧 Setting up email configuration...")
    
    email_example = Path("email_config.sh.example")
    email_file = Path("email_config.sh")
    
    if not email_example.exists():
        print("❌ email_config.sh.example file not found!")
        return False
    
    if email_file.exists():
        print("⚠️ email_config.sh already exists")
        overwrite = input("📄 This file may contain secrets. Overwrite? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("⏭️ Skipping email_config.sh setup")
            return True
    
    # Copy template
    shutil.copy(email_example, email_file)
    
    # Make executable
    os.chmod(email_file, 0o755)
    
    print("✅ email_config.sh created from template")
    print("📝 Please edit email_config.sh to add your email credentials")
    return True

def check_gitignore():
    """Check if .gitignore properly excludes secret files."""
    print("\n🔍 Checking .gitignore...")
    
    gitignore = Path(".gitignore")
    if not gitignore.exists():
        print("❌ .gitignore file not found!")
        return False
    
    with open(gitignore, 'r') as f:
        content = f.read()
    
    required_patterns = ['.env', 'config.yaml', 'email_config.sh']
    missing_patterns = []
    
    for pattern in required_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print(f"⚠️ Missing patterns in .gitignore: {', '.join(missing_patterns)}")
        return False
    else:
        print("✅ .gitignore properly configured")
        return True

def display_next_steps():
    """Display next steps for the user."""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("\n1. 🔑 Configure your API keys and credentials:")
    print("   - Edit .env file with your actual values")
    print("   - Edit config.yaml with your LinkedIn credentials")
    print("   - Edit email_config.sh with your email settings")
    
    print("\n2. 🔒 Important Security Notes:")
    print("   - These files are now in .gitignore (won't be committed)")
    print("   - Never commit files containing real credentials")
    print("   - Use strong, unique passwords")
    
    print("\n3. 🚀 To start the application:")
    print("   - Backend: cd backend && source ../email_config.sh && python3 app.py")
    print("   - Frontend: npm run dev")
    
    print("\n4. 📚 Configuration guides:")
    print("   - OpenAI API: https://platform.openai.com/api-keys")
    print("   - Gmail App Password: https://myaccount.google.com/apppasswords")
    print("   - Stripe: https://dashboard.stripe.com/apikeys")
    
    print("\n⚠️  Remember: Never share your API keys or commit them to version control!")

def main():
    """Main setup function."""
    print("🔐 ApplyX Secrets Setup")
    print("=" * 40)
    print("This script will help you configure your environment securely.")
    print("Your secrets will be stored locally and NOT committed to git.\n")
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("package.json").exists():
        print("❌ Please run this script from the project root directory")
        return
    
    success = True
    
    # Setup each component
    success &= setup_env_file()
    success &= setup_config_yaml()
    success &= setup_email_config()
    success &= check_gitignore()
    
    if success:
        display_next_steps()
    else:
        print("\n❌ Some setup steps failed. Please check the errors above.")

if __name__ == "__main__":
    main() 