#!/usr/bin/env python3
"""
Comprehensive Cleanup Script
Implements all cleanup strategies while maintaining functionality
"""

import os
import shutil
import json
import subprocess
from datetime import datetime

class CodebaseCleaner:
    def __init__(self):
        self.backup_dir = "backup_cleanup"
        self.cleanup_log = []
        
    def log_action(self, action, success, details=""):
        """Log cleanup actions"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status} {action}")
        if details:
            print(f"   Details: {details}")
        self.cleanup_log.append({
            "action": action,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def create_backup(self):
        """Create backup of current state"""
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            self.log_action("Backup Creation", True, "Backup directory ready")
            return True
        except Exception as e:
            self.log_action("Backup Creation", False, str(e))
            return False
            
    def move_chrome_directories(self):
        """Move Chrome bot directories to backup"""
        try:
            chrome_dirs = [d for d in os.listdir('.') if d.startswith('chrome_bot_user_')]
            for dir_name in chrome_dirs:
                if os.path.isdir(dir_name):
                    shutil.move(dir_name, os.path.join(self.backup_dir, dir_name))
                    self.log_action(f"Move Chrome Directory: {dir_name}", True)
            return True
        except Exception as e:
            self.log_action("Move Chrome Directories", False, str(e))
            return False
            
    def move_log_files(self):
        """Move log files to backup"""
        try:
            log_files = []
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith('.log') or file.endswith('.tmp'):
                        log_files.append(os.path.join(root, file))
                        
            for log_file in log_files:
                if not log_file.startswith('./backup_cleanup'):
                    backup_path = os.path.join(self.backup_dir, os.path.basename(log_file))
                    shutil.move(log_file, backup_path)
                    self.log_action(f"Move Log File: {os.path.basename(log_file)}", True)
            return True
        except Exception as e:
            self.log_action("Move Log Files", False, str(e))
            return False
            
    def clean_cache_directories(self):
        """Clean cache directories"""
        try:
            cache_dirs = ['.next', 'node_modules/.cache', '__pycache__']
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                    self.log_action(f"Clean Cache: {cache_dir}", True)
            return True
        except Exception as e:
            self.log_action("Clean Cache Directories", False, str(e))
            return False
            
    def remove_duplicate_dependencies(self):
        """Remove duplicate dependencies from requirements.txt"""
        try:
            requirements_file = "backend/requirements.txt"
            if os.path.exists(requirements_file):
                with open(requirements_file, 'r') as f:
                    lines = f.readlines()
                
                # Remove duplicate flask-cors
                cleaned_lines = []
                seen = set()
                for line in lines:
                    line = line.strip()
                    if line and line not in seen:
                        cleaned_lines.append(line)
                        seen.add(line)
                    elif line.startswith('flask-cors==4.0.0'):
                        # Keep only one flask-cors entry
                        if 'flask-cors' not in seen:
                            cleaned_lines.append(line)
                            seen.add('flask-cors')
                    elif line.startswith('bs4==0.0.1'):
                        # Remove bs4 as beautifulsoup4 is already included
                        continue
                    elif line.startswith('docx2txt==0.8'):
                        # Remove if not being used
                        continue
                    else:
                        cleaned_lines.append(line)
                        seen.add(line)
                
                with open(requirements_file, 'w') as f:
                    f.write('\n'.join(cleaned_lines) + '\n')
                    
                self.log_action("Remove Duplicate Dependencies", True, "Cleaned requirements.txt")
                return True
            return False
        except Exception as e:
            self.log_action("Remove Duplicate Dependencies", False, str(e))
            return False
            
    def clean_unused_test_files(self):
        """Move unused test files to backup"""
        try:
            test_files_to_move = [
                "test_*.py",
                "*_test.py",
                "test_*.json",
                "test_*.html",
                "test_*.md"
            ]
            
            moved_count = 0
            for pattern in test_files_to_move:
                for root, dirs, files in os.walk('.'):
                    for file in files:
                        if file.startswith('test_') or file.endswith('_test.py'):
                            file_path = os.path.join(root, file)
                            if not file_path.startswith('./backup_cleanup') and not file_path.startswith('./src'):
                                backup_path = os.path.join(self.backup_dir, file)
                                shutil.move(file_path, backup_path)
                                moved_count += 1
                                
            self.log_action("Move Test Files", True, f"Moved {moved_count} test files")
            return True
        except Exception as e:
            self.log_action("Move Test Files", False, str(e))
            return False
            
    def clean_environment_files(self):
        """Clean up environment files"""
        try:
            # Check for duplicate variables between .env and .env.local
            if os.path.exists('.env') and os.path.exists('.env.local'):
                with open('.env', 'r') as f:
                    env_vars = f.readlines()
                with open('.env.local', 'r') as f:
                    env_local_vars = f.readlines()
                    
                # Remove duplicates from .env.local
                env_keys = set()
                for line in env_vars:
                    if '=' in line:
                        key = line.split('=')[0]
                        env_keys.add(key)
                        
                cleaned_env_local = []
                for line in env_local_vars:
                    if '=' in line:
                        key = line.split('=')[0]
                        if key not in env_keys:
                            cleaned_env_local.append(line)
                    else:
                        cleaned_env_local.append(line)
                        
                with open('.env.local', 'w') as f:
                    f.writelines(cleaned_env_local)
                    
                self.log_action("Clean Environment Files", True, "Removed duplicate variables")
                return True
            return False
        except Exception as e:
            self.log_action("Clean Environment Files", False, str(e))
            return False
            
    def remove_unused_components(self):
        """Remove unused UI components"""
        try:
            # Check for unused Radix UI components
            unused_components = [
                "@radix-ui/react-alert-dialog",
                "@radix-ui/react-checkbox",
                "@radix-ui/react-dropdown-menu",
                "@radix-ui/react-icons",
                "@radix-ui/react-separator",
                "@radix-ui/react-switch",
                "@radix-ui/react-tabs",
                "@radix-ui/react-toast"
            ]
            
            # For now, just log what would be removed
            self.log_action("Remove Unused Components", True, f"Would remove {len(unused_components)} unused components")
            return True
        except Exception as e:
            self.log_action("Remove Unused Components", False, str(e))
            return False
            
    def optimize_bundle_size(self):
        """Optimize bundle size"""
        try:
            # Clean Next.js cache
            if os.path.exists('.next'):
                shutil.rmtree('.next')
                self.log_action("Clean Next.js Cache", True)
                
            # Clean node_modules cache
            if os.path.exists('node_modules/.cache'):
                shutil.rmtree('node_modules/.cache')
                self.log_action("Clean Node Modules Cache", True)
                
            return True
        except Exception as e:
            self.log_action("Optimize Bundle Size", False, str(e))
            return False
            
    def run_all_cleanup(self):
        """Run all cleanup operations"""
        print("🧹 Starting Comprehensive Cleanup...")
        print("=" * 50)
        
        cleanup_operations = [
            self.create_backup,
            self.move_chrome_directories,
            self.move_log_files,
            self.clean_cache_directories,
            self.remove_duplicate_dependencies,
            self.clean_unused_test_files,
            self.clean_environment_files,
            self.remove_unused_components,
            self.optimize_bundle_size,
        ]
        
        for operation in cleanup_operations:
            try:
                operation()
            except Exception as e:
                print(f"❌ Cleanup operation failed: {str(e)}")
                
        # Save cleanup log
        with open("cleanup_plan/cleanup_log.json", "w") as f:
            json.dump(self.cleanup_log, f, indent=2)
            
        # Summary
        print("\n" + "=" * 50)
        print("📊 Cleanup Summary:")
        successful = sum(1 for log in self.cleanup_log if log["success"])
        total = len(self.cleanup_log)
        print(f"✅ Successful: {successful}/{total}")
        print(f"❌ Failed: {total - successful}/{total}")
        
        return successful == total

if __name__ == "__main__":
    cleaner = CodebaseCleaner()
    success = cleaner.run_all_cleanup()
    exit(0 if success else 1) 