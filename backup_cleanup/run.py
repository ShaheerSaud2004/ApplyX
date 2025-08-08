#!/usr/bin/env python3
"""
LinkedIn Easy Apply Bot Launcher
Choose your application mode
"""

import os
import sys

def main():
    print("=" * 60)
    print("🚀 LINKEDIN EASY APPLY BOT")
    print("=" * 60)
    print("Choose your application mode:")
    print()
    print("1. Standard Mode (main.py)")
    print("   - Safe, human-like behavior")
    print("   - Session breaks and delays")
    print("   - Good for occasional use")
    print()
    print("2. Continuous Mode (main_fast.py)")
    print("   - Continuous applications")
    print("   - 1-2 minute delays between jobs")
    print("   - Full safety features")
    print("   - Press Ctrl+C to stop")
    print()
    print("3. Exit")
    print("=" * 60)
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting Standard Mode...")
            os.system("python main.py")
            break
        elif choice == "2":
            print("\n🚀 Starting Continuous Mode...")
            os.system("python main_fast.py")
            break
        elif choice == "3":
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main() 