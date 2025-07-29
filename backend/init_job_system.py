#!/usr/bin/env python3

"""
Job System Initialization Script
This script initializes the job aggregation system and performs an initial data load.
"""

import sys
import os
import asyncio
import logging

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from job_aggregator import JobAggregator, JobUpdateScheduler
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all required packages are installed:")
    print("pip install aiohttp beautifulsoup4 schedule")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize and populate the job database"""
    print("🚀 Initializing ApplyX Job Aggregation System")
    print("=" * 50)
    
    try:
        # Initialize job aggregator
        print("📊 Initializing job aggregator...")
        aggregator = JobAggregator(db_path="job_listings.db")
        print("✅ Job aggregator initialized successfully")
        
        # Run initial job update
        print("\n🔍 Starting initial job data collection...")
        print("This may take a few minutes as we fetch from multiple sources...")
        
        # Run the async update function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            total_jobs = loop.run_until_complete(aggregator.update_all_jobs())
            print(f"✅ Successfully loaded {total_jobs} jobs from all sources!")
        finally:
            loop.close()
        
        # Display statistics
        print("\n📈 Job Database Statistics:")
        category_counts = aggregator.get_category_counts()
        for category, count in category_counts.items():
            print(f"  • {category.title()}: {count} jobs")
        
        print(f"\n🎉 Job system initialization complete!")
        print(f"📊 Total jobs in database: {sum(category_counts.values())}")
        print("\n💡 You can now:")
        print("  • Visit http://localhost:3000/manual-apply to see the jobs")
        print("  • The system will automatically update every 6 hours")
        print("  • Use the 'Update Jobs' button in the UI for manual updates")
        
    except Exception as e:
        logger.error(f"❌ Error during initialization: {e}")
        print(f"\n❌ Initialization failed: {e}")
        print("\nTroubleshooting:")
        print("  • Check your internet connection")
        print("  • Ensure all required packages are installed")
        print("  • Check the logs for more detailed error information")
        return False
    
    return True

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    missing_deps = []
    
    try:
        import aiohttp
        print("  ✅ aiohttp")
    except ImportError:
        missing_deps.append("aiohttp")
        print("  ❌ aiohttp")
    
    try:
        import sqlite3
        print("  ✅ sqlite3")
    except ImportError:
        missing_deps.append("sqlite3")
        print("  ❌ sqlite3")
    
    try:
        from bs4 import BeautifulSoup
        print("  ✅ beautifulsoup4")
    except ImportError:
        missing_deps.append("beautifulsoup4")
        print("  ❌ beautifulsoup4")
    
    try:
        import schedule
        print("  ✅ schedule")
    except ImportError:
        missing_deps.append("schedule")
        print("  ❌ schedule")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Please install them with:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    print("✅ All dependencies available")
    return True

if __name__ == "__main__":
    print("🔧 ApplyX Job System Initializer")
    print("=" * 40)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Run initialization
    success = main()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Initialization completed successfully!")
        print("The job aggregation system is now ready to use.")
    else:
        print("\n" + "=" * 50)
        print("❌ Initialization failed. Please check the errors above.")
        sys.exit(1) 