#!/usr/bin/env python3
"""
Database migration to add expanded profile information tables
"""

import sqlite3
import uuid
from datetime import datetime

def create_expanded_profile_tables():
    """Create tables for expanded profile information"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    print("🔧 Creating expanded profile tables...")
    
    # Personal Details Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_personal_details (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            pronouns TEXT DEFAULT '',
            phone_country_code TEXT DEFAULT 'US',
            street_address TEXT DEFAULT '',
            city TEXT DEFAULT '',
            state TEXT DEFAULT '',
            zip_code TEXT DEFAULT '',
            linkedin_url TEXT DEFAULT '',
            portfolio_website TEXT DEFAULT '',
            message_to_manager TEXT DEFAULT '',
            university_gpa REAL DEFAULT 0.0,
            notice_period INTEGER DEFAULT 2,
            weekend_work BOOLEAN DEFAULT TRUE,
            evening_work BOOLEAN DEFAULT TRUE,
            drug_test BOOLEAN DEFAULT TRUE,
            background_check BOOLEAN DEFAULT TRUE,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Work Authorization Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_work_authorization (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            drivers_license BOOLEAN DEFAULT TRUE,
            require_visa BOOLEAN DEFAULT FALSE,
            legally_authorized BOOLEAN DEFAULT TRUE,
            security_clearance BOOLEAN DEFAULT FALSE,
            us_citizen BOOLEAN DEFAULT TRUE,
            degree_completed TEXT DEFAULT "Bachelor's Degree",
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Skills and Experience Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_skills_experience (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            languages_json TEXT DEFAULT '{"english": "Native or bilingual"}',
            technical_skills_json TEXT DEFAULT '{}',
            years_experience_json TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # EEO Information Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_eeo_info (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            gender TEXT DEFAULT '',
            race TEXT DEFAULT '',
            veteran BOOLEAN DEFAULT FALSE,
            disability BOOLEAN DEFAULT FALSE,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for faster lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_personal_details_user_id ON user_personal_details(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_work_auth_user_id ON user_work_authorization(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_skills_exp_user_id ON user_skills_experience(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_eeo_info_user_id ON user_eeo_info(user_id)')
    
    conn.commit()
    conn.close()
    
    print("✅ Expanded profile tables created successfully!")

def migrate_existing_users():
    """Add default expanded profile data for existing users"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    print("🔄 Migrating existing users to expanded profile...")
    
    # Get all existing users
    cursor.execute('SELECT id FROM users')
    users = cursor.fetchall()
    
    current_time = datetime.now().isoformat()
    
    for user_id_tuple in users:
        user_id = user_id_tuple[0]
        
        # Check if expanded profile data already exists
        cursor.execute('SELECT id FROM user_personal_details WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            continue  # Skip if already exists
        
        # Create default personal details
        cursor.execute('''
            INSERT INTO user_personal_details 
            (id, user_id, created_at) VALUES (?, ?, ?)
        ''', (str(uuid.uuid4()), user_id, current_time))
        
        # Create default work authorization
        cursor.execute('''
            INSERT INTO user_work_authorization 
            (id, user_id, created_at) VALUES (?, ?, ?)
        ''', (str(uuid.uuid4()), user_id, current_time))
        
        # Create default skills experience
        cursor.execute('''
            INSERT INTO user_skills_experience 
            (id, user_id, created_at) VALUES (?, ?, ?)
        ''', (str(uuid.uuid4()), user_id, current_time))
        
        # Create default EEO info
        cursor.execute('''
            INSERT INTO user_eeo_info 
            (id, user_id, created_at) VALUES (?, ?, ?)
        ''', (str(uuid.uuid4()), user_id, current_time))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Migrated {len(users)} users to expanded profile!")

if __name__ == "__main__":
    print("🚀 Starting expanded profile migration...")
    create_expanded_profile_tables()
    migrate_existing_users()
    print("🎉 Migration completed successfully!") 