#!/usr/bin/env python3

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.9 or higher"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js version: {result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False

def check_chromedriver():
    """Check if ChromeDriver exists"""
    chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')
    if os.path.exists(chromedriver_path):
        print("✅ ChromeDriver found")
        return True
    else:
        print("❌ ChromeDriver not found")
        print("Please download ChromeDriver from https://chromedriver.chromium.org/")
        print("and place it in the project root directory")
        return False

def create_env_file():
    """Create .env file from template"""
    env_path = '.env'
    template_path = 'env.example'
    
    if os.path.exists(env_path):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists(template_path):
        import shutil
        shutil.copy(template_path, env_path)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your credentials:")
        print("   - OPENAI_API_KEY")
        print("   - LINKEDIN_EMAIL")
        print("   - LINKEDIN_PASSWORD")
        return True
    else:
        print("❌ env.example template not found")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing Python dependencies...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Python dependencies installed")
            return True
        else:
            print(f"❌ Failed to install Python dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing Python dependencies: {e}")
        return False

def install_node_dependencies():
    """Install Node.js dependencies"""
    try:
        print("📦 Installing Node.js dependencies...")
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Node.js dependencies installed")
            return True
        else:
            print(f"❌ Failed to install Node.js dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing Node.js dependencies: {e}")
        return False

def initialize_database():
    """Initialize SQLite database"""
    try:
        # Create backend directory if it doesn't exist
        os.makedirs('backend', exist_ok=True)
        
        # Initialize database
        db_path = 'backend/easyapply.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        tables = [
            '''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                linkedin TEXT,
                website TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS job_applications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                job_url TEXT,
                status TEXT DEFAULT 'applied',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resume_used TEXT,
                cover_letter_used TEXT,
                notes TEXT,
                ai_generated BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                positions TEXT,
                locations TEXT,
                remote BOOLEAN DEFAULT FALSE,
                experience_level TEXT,
                job_types TEXT,
                salary_minimum INTEGER,
                preferred_industries TEXT,
                skills_required TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS agent_tasks (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                parameters TEXT,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS agent_status (
                user_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                current_task TEXT,
                applications_submitted INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        conn.commit()
        
        # Create default admin user
        admin_email = "admin@applyx.ai"
        admin_password = "admin123"  # Change this!
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (admin_email,))
        if not cursor.fetchone():
            import uuid
            from werkzeug.security import generate_password_hash
            
            admin_id = str(uuid.uuid4())
            password_hash = generate_password_hash(admin_password)
            
            cursor.execute('''
                INSERT INTO users (id, email, password_hash, first_name, last_name, 
                                 subscription_plan, daily_quota, is_admin, referral_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                admin_id, admin_email, password_hash, 'Admin', 'User',
                'pro', 50, True, 'ADMIN123'
            ))
            
            conn.commit()
            print("✅ Default admin user created")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print("   ⚠️  Please change the admin password after first login!")
        
        conn.close()
        
        print("✅ Database initialized")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'backend/uploads',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 EasyApply Platform Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_node_version():
        return False
    
    if not check_chromedriver():
        return False
    
    # Create environment file
    if not create_env_file():
        return False
    
    # Install dependencies
    if not install_python_dependencies():
        return False
    
    if not install_node_dependencies():
        return False
    
    # Initialize database
    if not initialize_database():
        return False
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your credentials")
    print("2. Update config.yaml with your job preferences")
    print("3. Start the backend: cd backend && python app.py")
    print("4. Start the frontend: npm run dev")
    print("5. Visit http://localhost:3000 to use the platform")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 