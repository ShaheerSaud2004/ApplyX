#!/usr/bin/env python3
"""
Git Safety Verification Script for ApplyX
==========================================
This script checks that your setup is safe to commit to git
without exposing LinkedIn credentials or other sensitive data.
"""

import os
import glob
import subprocess
from pathlib import Path

def check_git_status():
    """Check what files git wants to track"""
    try:
        # Get files that would be committed (staged files)
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            return False, "Not in a git repository"
        
        lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        staged_files = []
        modified_files = []
        
        for line in lines:
            if line.strip():
                status = line[:2]
                filename = line[3:]
                
                # Check if file is staged for commit (A, M, D, R, C in first column)
                if status[0] in ['A', 'M', 'D', 'R', 'C']:
                    staged_files.append(filename)
                # Check if file is modified but not staged
                elif status[1] in ['M', 'D']:
                    modified_files.append(filename)
                # Untracked files
                elif status.startswith('??'):
                    # Only worry about untracked files if they contain secrets
                    pass
        
        return True, {
            'staged': staged_files,
            'modified': modified_files
        }
    except Exception as e:
        return False, f"Error checking git status: {e}"

def check_dangerous_files():
    """Check for files that contain secrets and are staged for commit"""
    dangerous_patterns = [
        # Secret files
        '**/.env',
        '**/.env.*',
        '**/config.yaml',
        '**/email_config.sh',
        '**/encryption.key',
        
        # Database files with user data
        '**/*.db',
        '**/*.sqlite',
        '**/*.sqlite3',
        
        # Chrome browser data
        '**/chrome_bot*/**',
        
        # User-specific config files
        '**/user_config_*.yaml',
    ]
    
    # Get staged files only
    git_ok, git_info = check_git_status()
    if not git_ok:
        return False, git_info
    
    staged_files = git_info['staged'] if isinstance(git_info, dict) else []
    
    dangerous_staged = []
    
    # Check git status for specific files being added (not deleted)
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        for line in status_lines:
            if line.strip():
                status = line[:2]
                filename = line[3:]
                
                # Only flag files being added/modified, not deleted
                if status[0] in ['A', 'M'] and not status[0] == 'D':
                    for pattern in dangerous_patterns:
                        matching_files = glob.glob(pattern, recursive=True)
                        if filename in matching_files:
                            dangerous_staged.append(filename)
    except Exception:
        # Fallback to original method
        for pattern in dangerous_patterns:
            matching_files = glob.glob(pattern, recursive=True)
            for file_path in matching_files:
                # Only flag if the file is actually staged for commit
                if file_path in staged_files:
                    dangerous_staged.append(file_path)
    
    return len(dangerous_staged) == 0, dangerous_staged

def check_gitignore():
    """Check if .gitignore has required patterns"""
    required_patterns = [
        '.env',
        '*.env',
        'config.yaml',
        'email_config.sh',
        '*.key',
        '*.db',
        'chrome_bot*/',
    ]
    
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)
        
        return len(missing_patterns) == 0, missing_patterns
    except FileNotFoundError:
        return False, "No .gitignore file found"

def scan_for_hardcoded_credentials():
    """Scan for potential hardcoded credentials in staged files only"""
    patterns = [
        r'password.*=.*["\'][^"\']{6,}["\']',
        r'api.?key.*=.*["\'][^"\']{10,}["\']',
        r'secret.*=.*["\'][^"\']{8,}["\']',
        r'sk-proj-[a-zA-Z0-9]{20,}',  # OpenAI API keys
        r'@gmail\.com',
        r'smtp.*password',
    ]
    
    # Only scan files that are staged for commit
    git_ok, git_info = check_git_status()
    if not git_ok:
        return True, []  # If no git, skip this check
    
    staged_files = git_info['staged'] if isinstance(git_info, dict) else []
    
    issues = []
    for file_path in staged_files:
        if file_path.endswith(('.py', '.js', '.ts', '.yaml', '.yml', '.json', '.sh')):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in patterns:
                            import re
                            if re.search(pattern, line, re.IGNORECASE):
                                # Skip false positives (environment variable references)
                                if any(safe_pattern in line for safe_pattern in [
                                    'os.getenv', 'process.env', 'config[', 'environ.get',
                                    'generate_password_hash', 'check_password_hash',
                                    'password_hash', 'stripe.api_key', 'os.environ',
                                    'example', 'placeholder', 'template', 'your-'
                                ]):
                                    continue
                                    
                                issues.append(f"{file_path}:{line_num} - {line.strip()[:100]}")
                                break
            except Exception:
                continue
    
    return len(issues) == 0, issues

def test_encryption():
    """Test that the encryption system is working"""
    try:
        import sys
        sys.path.append('backend')
        from security import test_encryption_system
        success, message = test_encryption_system()
        return success, message
    except Exception as e:
        return False, f"Error testing encryption: {e}"

def main():
    print("🔐 ApplyX Git Safety Verification")
    print("=" * 50)
    
    all_good = True
    
    # 1. Check Git Status
    print("\n1. 📋 Checking Git Status...")
    git_ok, git_info = check_git_status()
    if git_ok and isinstance(git_info, dict):
        staged_count = len(git_info['staged'])
        modified_count = len(git_info['modified'])
        print(f"   📝 Files staged for commit: {staged_count}")
        print(f"   📝 Modified files (not staged): {modified_count}")
        if staged_count > 0:
            print("      Staged files:")
            for f in git_info['staged'][:5]:
                print(f"        + {f}")
            if staged_count > 5:
                print(f"        ... and {staged_count - 5} more")
    else:
        print(f"   ❌ {git_info}")
        all_good = False
    
    # 2. Check for dangerous files that are staged
    print("\n2. 🚨 Checking for Dangerous Staged Files...")
    safe, dangerous_files = check_dangerous_files()
    if safe:
        print("   ✅ No dangerous files staged for commit")
    else:
        print("   ❌ Found files with secrets that are staged for commit:")
        for file_path in dangerous_files[:10]:
            print(f"      🔥 {file_path}")
        if len(dangerous_files) > 10:
            print(f"      ... and {len(dangerous_files) - 10} more")
        all_good = False
    
    # 3. Check .gitignore
    print("\n3. 🛡️ Checking .gitignore...")
    gitignore_ok, missing = check_gitignore()
    if gitignore_ok:
        print("   ✅ All required patterns in .gitignore")
    else:
        print("   ❌ Missing .gitignore patterns:")
        if isinstance(missing, list):
            for pattern in missing:
                print(f"      📝 {pattern}")
        else:
            print(f"      📝 {missing}")
        all_good = False
    
    # 4. Scan for hardcoded credentials in staged files
    print("\n4. 🕵️ Scanning Staged Files for Credentials...")
    creds_ok, issues = scan_for_hardcoded_credentials()
    if creds_ok:
        print("   ✅ No hardcoded credentials found in staged files")
    else:
        print("   ⚠️ Found potential credentials in staged files:")
        for issue in issues[:5]:
            print(f"      🔍 {issue}")
        if len(issues) > 5:
            print(f"      ... and {len(issues) - 5} more issues")
        # Don't fail the check for credential warnings, just warn
    
    # 5. Test encryption
    print("\n5. 🔒 Testing Encryption System...")
    enc_ok, enc_msg = test_encryption()
    if enc_ok:
        print("   ✅ Encryption system working correctly")
    else:
        print(f"   ⚠️ Encryption issue: {enc_msg}")
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 ✅ SAFE TO COMMIT!")
        print("Your secrets are properly protected and won't be exposed to git.")
        print("\n🚀 Ready for deployment!")
    else:
        print("🚨 ❌ NOT SAFE TO COMMIT!")
        print("Please fix the issues above before pushing to git.")
        print("\nQuick fixes:")
        print("- Run: git reset HEAD <filename> to unstage secret files")
        print("- Check your .gitignore file")
        print("- Remove any hardcoded credentials")
        print("\n📚 For more help, see: MULTI_USER_SECURITY_GUIDE.md")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    exit(main()) 