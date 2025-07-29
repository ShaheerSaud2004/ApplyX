#!/usr/bin/env python3
"""
Script to create an admin user or promote an existing user to admin status.
Usage: python create_admin.py
"""

import sqlite3
import uuid
from werkzeug.security import generate_password_hash

def create_admin():
    """Create an admin user or promote existing user"""
    conn = sqlite3.connect('backend/easyapply.db')
    cursor = conn.cursor()
    
    print("=== ApplyX Admin User Setup ===")
    
    # Check if any admin users exist
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    admin_count = cursor.fetchone()[0]
    
    if admin_count > 0:
        print(f"Found {admin_count} existing admin user(s).")
        choice = input("Do you want to promote an existing user to admin? (y/n): ").lower()
        
        if choice == 'y':
            # Show existing users
            cursor.execute('SELECT id, email, first_name, last_name, is_admin FROM users ORDER BY created_at')
            users = cursor.fetchall()
            
            print("\nExisting users:")
            for i, user in enumerate(users, 1):
                admin_status = "ADMIN" if user[4] else "USER"
                print(f"{i}. {user[1]} ({user[2]} {user[3]}) - {admin_status}")
            
            try:
                user_choice = int(input("\nEnter the number of the user to promote: ")) - 1
                if 0 <= user_choice < len(users):
                    selected_user = users[user_choice]
                    
                    # Update user to admin
                    cursor.execute('''
                        UPDATE users 
                        SET is_admin = 1, status = 'approved', updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    ''', (selected_user[0],))
                    
                    conn.commit()
                    print(f"✅ User {selected_user[1]} has been promoted to admin!")
                    
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")
                
    else:
        print("No admin users found. Let's create one!")
        
        email = input("Enter admin email: ")
        password = input("Enter admin password: ")
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Promote existing user to admin
            cursor.execute('''
                UPDATE users 
                SET is_admin = 1, status = 'approved', updated_at = CURRENT_TIMESTAMP 
                WHERE email = ?
            ''', (email,))
            conn.commit()
            print(f"✅ Existing user {email} has been promoted to admin!")
            
        else:
            # Create new admin user
            user_id = str(uuid.uuid4())
            password_hash = generate_password_hash(password)
            
            cursor.execute('''
                INSERT INTO users (id, email, password_hash, first_name, last_name, 
                                  subscription_plan, daily_quota, daily_usage, is_admin, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, email, password_hash, first_name, last_name,
                'pro', 100, 0, True, 'approved'  # Give admin user pro plan
            ))
            
            conn.commit()
            print(f"✅ Admin user {email} has been created!")
    
    conn.close()
    print("\n🎉 Admin setup complete! You can now log in with admin privileges.")

if __name__ == "__main__":
    create_admin() 