#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash

def migrate_database():
    """Migrate existing database to add new columns and tables"""
    db_path = 'backend/easyapply.db'
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Run setup.py first.")
        return False
    
    print("🔄 Migrating database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if migration is needed by checking for new columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        migrations_needed = []
        
        # Check which columns are missing
        expected_columns = [
            'subscription_plan', 'stripe_customer_id', 'subscription_id', 
            'subscription_status', 'current_period_end', 'daily_quota', 
            'daily_usage', 'last_usage_reset', 'is_admin', 'referral_code', 'referred_by',
            'linkedin_email_encrypted', 'linkedin_password_encrypted'
        ]
        
        for col in expected_columns:
            if col not in columns:
                migrations_needed.append(col)
        
        # Add missing columns
        if migrations_needed:
            print(f"📝 Adding missing columns: {', '.join(migrations_needed)}")
            
            column_definitions = {
                'subscription_plan': 'TEXT DEFAULT "free"',
                'stripe_customer_id': 'TEXT',
                'subscription_id': 'TEXT',
                'subscription_status': 'TEXT',
                'current_period_end': 'TIMESTAMP',
                'daily_quota': 'INTEGER DEFAULT 5',
                'daily_usage': 'INTEGER DEFAULT 0',
                'last_usage_reset': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'is_admin': 'BOOLEAN DEFAULT FALSE',
                'referral_code': 'TEXT',
                'referred_by': 'TEXT',
                'linkedin_email_encrypted': 'TEXT',
                'linkedin_password_encrypted': 'TEXT'
            }
            
            for col in migrations_needed:
                try:
                    alter_sql = f"ALTER TABLE users ADD COLUMN {col} {column_definitions[col]}"
                    cursor.execute(alter_sql)
                    print(f"✅ Added column: {col}")
                except Exception as e:
                    print(f"⚠️  Column {col} might already exist or error: {e}")
        
        # Create new tables if they don't exist
        new_tables = [
            '''CREATE TABLE IF NOT EXISTS billing_events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                stripe_event_id TEXT UNIQUE,
                event_type TEXT NOT NULL,
                subscription_plan TEXT,
                amount INTEGER,
                currency TEXT DEFAULT 'usd',
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS usage_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                quota_used INTEGER DEFAULT 1,
                remaining_quota INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS referrals (
                id TEXT PRIMARY KEY,
                referrer_id TEXT NOT NULL,
                referred_id TEXT NOT NULL,
                referral_code TEXT NOT NULL,
                bonus_granted BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (id),
                FOREIGN KEY (referred_id) REFERENCES users (id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS agent_status (
                user_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                current_task TEXT,
                applications_submitted INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            '''CREATE TABLE IF NOT EXISTS user_preferences (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                job_titles TEXT,
                locations TEXT,
                remote BOOLEAN DEFAULT TRUE,
                experience TEXT DEFAULT 'mid',
                salary_min TEXT,
                skills TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )'''
        ]
        
        for table_sql in new_tables:
            cursor.execute(table_sql)
            print("✅ Created/verified table")
        
        # Update existing users with default values
        cursor.execute('''
            UPDATE users 
            SET daily_quota = 5, daily_usage = 0, subscription_plan = 'free'
            WHERE daily_quota IS NULL OR subscription_plan IS NULL
        ''')
        
        # Generate referral codes for existing users without them
        cursor.execute('SELECT id FROM users WHERE referral_code IS NULL')
        users_without_codes = cursor.fetchall()
        
        for (user_id,) in users_without_codes:
            referral_code = generate_referral_code(user_id)
            cursor.execute('UPDATE users SET referral_code = ? WHERE id = ?', (referral_code, user_id))
        
        if users_without_codes:
            print(f"✅ Generated referral codes for {len(users_without_codes)} users")
        
        # Create admin user if it doesn't exist
        admin_email = "admin@applyx.ai"
        cursor.execute('SELECT id FROM users WHERE email = ?', (admin_email,))
        if not cursor.fetchone():
            admin_id = str(uuid.uuid4())
            password_hash = generate_password_hash("admin123")
            referral_code = generate_referral_code(admin_id)
            
            cursor.execute('''
                INSERT INTO users (id, email, password_hash, first_name, last_name, 
                                 subscription_plan, daily_quota, is_admin, referral_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                admin_id, admin_email, password_hash, 'Admin', 'User',
                'pro', 50, True, referral_code
            ))
            
            print("✅ Created admin user")
            print(f"   Email: {admin_email}")
            print("   Password: admin123")
            print("   ⚠️  Please change the admin password after first login!")
        
        conn.commit()
        conn.close()
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        conn.close()
        return False

def generate_referral_code(user_id):
    """Generate a unique referral code"""
    import hashlib
    import random
    raw = f"{user_id}{random.randint(1000, 9999)}{datetime.now().timestamp()}"
    return hashlib.md5(raw.encode()).hexdigest()[:8].upper()

if __name__ == "__main__":
    success = migrate_database()
    exit(0 if success else 1) 