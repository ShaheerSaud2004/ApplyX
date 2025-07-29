#!/usr/bin/env python3

import requests
import json
import sqlite3
import datetime
import time
import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    title: str
    company: str
    location: str
    salary: Optional[str]
    posted_date: str
    url: str
    category: str
    description: Optional[str]
    is_remote: bool
    experience_level: str
    source: str
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'salary': self.salary,
            'posted_date': self.posted_date,
            'url': self.url,
            'category': self.category,
            'description': self.description,
            'is_remote': self.is_remote,
            'experience_level': self.experience_level,
            'source': self.source,
            'tags': json.dumps(self.tags),
            'id': hashlib.md5(f"{self.title}{self.company}{self.url}".encode()).hexdigest()
        }

class JobAggregator:
    def __init__(self, db_path: str = "job_listings.db"):
        self.db_path = db_path
        self.init_database()
        
        # Comprehensive category mapping
        self.categories = {
            'software': ['software', 'developer', 'engineer', 'programming', 'frontend', 'backend', 'fullstack', 'web'],
            'data': ['data', 'analytics', 'scientist', 'machine learning', 'ai', 'ml', 'statistics'],
            'cybersecurity': ['security', 'cyber', 'penetration', 'infosec', 'ciso', 'security analyst'],
            'it': ['devops', 'system', 'network', 'infrastructure', 'cloud', 'sre', 'admin'],
            'product': ['product', 'pm', 'product manager', 'product owner', 'roadmap'],
            'design': ['design', 'ux', 'ui', 'graphic', 'visual', 'creative'],
            'marketing': ['marketing', 'growth', 'digital marketing', 'seo', 'content', 'social media'],
            'sales': ['sales', 'business development', 'account', 'revenue', 'customer success'],
            'finance': ['finance', 'accounting', 'financial', 'analyst', 'controller', 'treasury'],
            'hr': ['hr', 'human resources', 'recruiting', 'talent', 'people ops'],
            'operations': ['operations', 'logistics', 'supply chain', 'procurement', 'vendor'],
            'legal': ['legal', 'counsel', 'attorney', 'compliance', 'regulatory'],
            'healthcare': ['healthcare', 'medical', 'nurse', 'doctor', 'clinical'],
            'education': ['education', 'teacher', 'professor', 'academic', 'research'],
            'consulting': ['consulting', 'consultant', 'advisory', 'strategy'],
            'engineering': ['mechanical', 'electrical', 'civil', 'chemical', 'aerospace'],
            'startup': ['startup', 'founder', 'co-founder', 'early stage', 'seed'],
        }
        
        # Job sources
        self.github_repos = [
            'SimplifyJobs/Summer2024-Internships',
            'SimplifyJobs/New-Grad-Positions',  
            'ReaVNaiL/New-Grad-2024',
            'Ouckah/Summer2025-Internships',
            'pittcsc/Summer2024-Internships',
            'ChrisDryden/Canadian-Tech-Internships-Summer-2024',
        ]
        
        self.job_boards = [
            'https://jobs.github.com/positions.json',
            # 'https://remoteok.io/api',  # Disabled due to data format issues
            'https://jobs.lever.co/lever',
        ]

    def init_database(self):
        """Initialize the job listings database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_listings (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                salary TEXT,
                posted_date TEXT,
                url TEXT UNIQUE,
                category TEXT,
                description TEXT,
                is_remote BOOLEAN,
                experience_level TEXT,
                source TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category ON job_listings(category);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_posted_date ON job_listings(posted_date);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_company ON job_listings(company);
        ''')
        
        conn.commit()
        conn.close()

    def categorize_job(self, title: str, description: str = "") -> str:
        """Categorize a job based on title and description"""
        text = f"{title} {description}".lower()
        
        # Score each category
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return the category with highest score, default to 'other'
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return 'other'

    def determine_experience_level(self, title: str, description: str = "") -> str:
        """Determine experience level based on job title and description"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['intern', 'internship', 'entry', 'junior', 'grad', 'new grad']):
            return 'entry'
        elif any(word in text for word in ['senior', 'lead', 'principal', 'staff']):
            return 'senior'
        elif any(word in text for word in ['director', 'vp', 'chief', 'head of', 'manager']):
            return 'executive'
        else:
            return 'mid'

    def is_remote_job(self, location: str, description: str = "") -> bool:
        """Determine if job is remote"""
        text = f"{location} {description}".lower()
        return any(word in text for word in ['remote', 'work from home', 'distributed', 'anywhere'])

    async def fetch_github_jobs(self) -> List[JobListing]:
        """Fetch jobs from GitHub repositories"""
        jobs = []
        
        async with aiohttp.ClientSession() as session:
            for repo in self.github_repos:
                try:
                    url = f"https://api.github.com/repos/{repo}/contents/README.md"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            content = data.get('content', '')
                            
                            # Decode base64 content
                            import base64
                            decoded_content = base64.b64decode(content).decode('utf-8')
                            
                            # Parse job listings from markdown
                            parsed_jobs = self.parse_github_markdown(decoded_content, repo)
                            jobs.extend(parsed_jobs)
                            
                except Exception as e:
                    logger.error(f"Error fetching from {repo}: {e}")
        
        return jobs

    def parse_github_markdown(self, content: str, source: str) -> List[JobListing]:
        jobs = []
        
        # Split content into lines for better parsing
        lines = content.split('\n')
        
        # Look for markdown tables
        in_table = False
        headers = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check if this is a table header
            if '|' in line and ('company' in line.lower() or 'position' in line.lower() or 'location' in line.lower()):
                headers = [h.strip().lower() for h in line.split('|') if h.strip()]
                in_table = True
                continue
                
            # Skip table separator lines
            if in_table and line.startswith('|') and all(c in '-|: ' for c in line):
                continue
                
            # Parse table rows
            if in_table and line.startswith('|'):
                cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove empty first/last cells
                
                if len(cells) >= 2 and cells[0] and cells[1]:  # At least company and position
                    try:
                        # Extract basic info
                        company = self.clean_cell_content(cells[0])
                        position = self.clean_cell_content(cells[1])
                        location = self.clean_cell_content(cells[2]) if len(cells) > 2 else "Remote"
                        
                        # Skip header rows and empty entries
                        if (company.lower() in ['company', 'employer', 'organization'] or 
                            position.lower() in ['position', 'role', 'title', 'job']):
                            continue
                            
                        # Extract application URL if available
                        app_url = self.extract_url_from_cell(cells[3]) if len(cells) > 3 else f"https://github.com/{source}"
                        
                        # Create job listing
                        job = JobListing(
                            title=position,
                            company=company,
                            location=location,
                            salary=None,
                            posted_date=datetime.datetime.now().isoformat(),
                            url=app_url,
                            category=self.categorize_job(position),
                            description=None,
                            is_remote=self.is_remote_job(location),
                            experience_level=self.determine_experience_level(position),
                            source=f"GitHub: {source}",
                            tags=self.extract_tags_from_position(position)
                        )
                        jobs.append(job)
                        
                    except Exception as e:
                        logger.error(f"Error parsing job row: {e}")
                        continue
            
            # Look for bullet point lists (alternative format)
            elif line.startswith('- ') or line.startswith('* '):
                try:
                    job_info = self.parse_bullet_point_job(line, source)
                    if job_info:
                        jobs.append(job_info)
                except Exception as e:
                    logger.error(f"Error parsing bullet point job: {e}")
                    continue
        
        logger.info(f"Parsed {len(jobs)} jobs from {source}")
        return jobs
    
    def clean_cell_content(self, cell: str) -> str:
        """Clean markdown cell content"""
        # Remove markdown links but keep the text
        import re
        
        # Extract text from markdown links [text](url)
        cell = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cell)
        
        # Remove HTML tags
        cell = re.sub(r'<[^>]+>', '', cell)
        
        # Remove extra whitespace
        cell = ' '.join(cell.split())
        
        return cell.strip()
    
    def extract_url_from_cell(self, cell: str) -> str:
        """Extract URL from markdown cell"""
        import re
        
        # Look for markdown links [text](url)
        match = re.search(r'\]\(([^)]+)\)', cell)
        if match:
            return match.group(1)
            
        # Look for direct URLs
        match = re.search(r'https?://[^\s<>"]+', cell)
        if match:
            return match.group(0)
            
        return ""
    
    def extract_tags_from_position(self, position: str) -> List[str]:
        """Extract relevant tags from position title"""
        tags = []
        position_lower = position.lower()
        
        # Common tech stacks and skills
        tech_keywords = {
            'react': 'React', 'vue': 'Vue.js', 'angular': 'Angular',
            'python': 'Python', 'javascript': 'JavaScript', 'typescript': 'TypeScript',
            'java': 'Java', 'c++': 'C++', 'golang': 'Go', 'rust': 'Rust',
            'aws': 'AWS', 'azure': 'Azure', 'gcp': 'Google Cloud',
            'docker': 'Docker', 'kubernetes': 'Kubernetes',
            'ml': 'Machine Learning', 'ai': 'Artificial Intelligence',
            'frontend': 'Frontend', 'backend': 'Backend', 'fullstack': 'Full Stack',
            'mobile': 'Mobile', 'ios': 'iOS', 'android': 'Android'
        }
        
        for keyword, tag in tech_keywords.items():
            if keyword in position_lower:
                tags.append(tag)
        
        return tags
    
    def parse_bullet_point_job(self, line: str, source: str) -> Optional[JobListing]:
        """Parse job from bullet point format"""
        # Remove bullet point
        line = line.lstrip('- *').strip()
        
        # Common patterns: "Company - Position - Location"
        parts = [part.strip() for part in line.split(' - ')]
        
        if len(parts) >= 2:
            company = parts[0]
            position = parts[1]
            location = parts[2] if len(parts) > 2 else "Remote"
            
            return JobListing(
                title=position,
                company=company,
                location=location,
                salary=None,
                posted_date=datetime.datetime.now().isoformat(),
                url=f"https://github.com/{source}",
                category=self.categorize_job(position),
                description=None,
                is_remote=self.is_remote_job(location),
                experience_level=self.determine_experience_level(position),
                source=f"GitHub: {source}",
                tags=self.extract_tags_from_position(position)
            )
        
        return None

    async def fetch_job_board_apis(self) -> List[JobListing]:
        """Fetch jobs from various job board APIs"""
        jobs = []
        
        # Job board APIs temporarily disabled for stability
        # Future: Add more reliable job board APIs here
        
        # RemoteOK API - DISABLED due to data format issues
        # async with aiohttp.ClientSession() as session:
        #     try:
        #         async with session.get('https://remoteok.io/api') as response:
        #             if response.status == 200:
        #                 data = await response.json()
        #                 if isinstance(data, list) and len(data) > 1:
        #                     for job_data in data[1:]:  # Skip first element (metadata)
        #                         if isinstance(job_data, dict):
        #                             job = self.parse_remoteok_job(job_data)
        #                             if job:
        #                                 jobs.append(job)
        #     except Exception as e:
        #         logger.error(f"Error fetching RemoteOK jobs: {e}")
        
        # Job board APIs temporarily disabled for stability
        # TODO: Re-enable with better error handling
        
        return jobs

    def parse_remoteok_job(self, job_data: Dict) -> Optional[JobListing]:
        """Parse a job from RemoteOK API response - DISABLED"""
        # RemoteOK parsing is disabled due to data format incompatibilities
        logger.debug("RemoteOK job parsing is disabled")
        return None

    def parse_date_safely(self, date_value) -> str:
        """Safely parse date from various formats (timestamp, string, etc.)"""
        try:
            if date_value is None:
                return datetime.datetime.now().isoformat()
            
            # If it's already a string, try to parse it
            if isinstance(date_value, str):
                try:
                    # Try parsing as ISO format first
                    return datetime.datetime.fromisoformat(date_value.replace('Z', '+00:00')).isoformat()
                except:
                    try:
                        # Try parsing as timestamp string
                        return datetime.datetime.fromtimestamp(float(date_value)).isoformat()
                    except:
                        # Default to current time if parsing fails
                        return datetime.datetime.now().isoformat()
            
            # If it's a number (timestamp)
            if isinstance(date_value, (int, float)):
                return datetime.datetime.fromtimestamp(date_value).isoformat()
            
            # Default fallback
            return datetime.datetime.now().isoformat()
            
        except Exception as e:
            logger.warning(f"Error parsing date {date_value}: {e}")
            return datetime.datetime.now().isoformat()

    def fetch_company_careers_pages(self) -> List[JobListing]:
        """Fetch jobs from major company career pages"""
        jobs = []
        
        # Major tech companies
        companies = [
            {
                'name': 'Google',
                'url': 'https://careers.google.com/api/v3/search/',
                'type': 'api'
            },
            {
                'name': 'Apple',
                'url': 'https://jobs.apple.com/api/role/search',
                'type': 'api'
            },
            # Add more companies here
        ]
        
        for company in companies:
            try:
                if company['type'] == 'api':
                    company_jobs = self.fetch_company_api(company)
                    jobs.extend(company_jobs)
            except Exception as e:
                logger.error(f"Error fetching {company['name']} jobs: {e}")
        
        return jobs

    def fetch_company_api(self, company: Dict) -> List[JobListing]:
        """Fetch jobs from a company's API"""
        # Implementation would depend on each company's API
        # This is a placeholder for company-specific implementations
        return []

    def save_jobs_to_db(self, jobs: List[JobListing]):
        """Save job listings to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for job in jobs:
            job_dict = job.to_dict()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO job_listings 
                    (id, title, company, location, salary, posted_date, url, category, 
                     description, is_remote, experience_level, source, tags, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    job_dict['id'], job_dict['title'], job_dict['company'], 
                    job_dict['location'], job_dict['salary'], job_dict['posted_date'],
                    job_dict['url'], job_dict['category'], job_dict['description'],
                    job_dict['is_remote'], job_dict['experience_level'], 
                    job_dict['source'], job_dict['tags']
                ))
            except sqlite3.IntegrityError:
                # Job already exists, update it
                pass
        
        conn.commit()
        conn.close()

    def get_jobs_from_db(self, 
                        category: Optional[str] = None,
                        limit: int = 100,
                        offset: int = 0,
                        search: Optional[str] = None,
                        sort_by: str = 'posted_date',
                        sort_order: str = 'DESC') -> List[Dict]:
        """Retrieve jobs from database with filtering and sorting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM job_listings WHERE 1=1"
        params = []
        
        if category and category != 'all':
            query += " AND category = ?"
            params.append(category)
        
        if search:
            query += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        query += f" ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to dictionaries
        columns = [desc[0] for desc in cursor.description]
        jobs = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return jobs

    def get_category_counts(self) -> Dict[str, int]:
        """Get job counts by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM job_listings 
            GROUP BY category 
            ORDER BY count DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return {category: count for category, count in results}

    async def update_all_jobs(self):
        """Update all job listings from all sources"""
        logger.info("Starting job update process...")
        
        all_jobs = []
        
        # Fetch from GitHub
        logger.info("Fetching from GitHub repositories...")
        github_jobs = await self.fetch_github_jobs()
        all_jobs.extend(github_jobs)
        logger.info(f"Fetched {len(github_jobs)} jobs from GitHub")
        
        # Fetch from job boards
        logger.info("Fetching from job board APIs...")
        api_jobs = await self.fetch_job_board_apis()
        all_jobs.extend(api_jobs)
        logger.info(f"Fetched {len(api_jobs)} jobs from APIs")
        
        # Fetch from company pages
        logger.info("Fetching from company career pages...")
        company_jobs = self.fetch_company_careers_pages()
        all_jobs.extend(company_jobs)
        logger.info(f"Fetched {len(company_jobs)} jobs from companies")
        
        # Save to database
        logger.info(f"Saving {len(all_jobs)} total jobs to database...")
        self.save_jobs_to_db(all_jobs)
        
        logger.info("Job update process completed!")
        return len(all_jobs)

# Scheduler for daily updates
class JobUpdateScheduler:
    def __init__(self, aggregator: JobAggregator):
        self.aggregator = aggregator
        
    def schedule_daily_updates(self):
        """Schedule daily job updates"""
        import schedule
        
        # Update jobs every day at 6 AM
        schedule.every().day.at("06:00").do(self.run_update)
        
        # Also update every 6 hours
        schedule.every(6).hours.do(self.run_update)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_update(self):
        """Run the job update process"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.aggregator.update_all_jobs())
            logger.info(f"Updated {result} jobs successfully")
        except Exception as e:
            logger.error(f"Error in scheduled update: {e}")

if __name__ == "__main__":
    # Initialize and run job aggregator
    aggregator = JobAggregator()
    
    # Run initial update
    loop = asyncio.get_event_loop()
    loop.run_until_complete(aggregator.update_all_jobs())
    
    # Start scheduler for daily updates
    scheduler = JobUpdateScheduler(aggregator)
    scheduler.schedule_daily_updates() 