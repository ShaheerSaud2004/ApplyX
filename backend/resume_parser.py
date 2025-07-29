"""
Resume Parsing Module
Extracts information from uploaded resumes (PDF, DOC, DOCX) to auto-populate profile fields
"""

import os
import re
import json
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not available - PDF parsing disabled")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not available - DOCX parsing disabled")

try:
    import python_docx2txt
    DOC_AVAILABLE = True
except ImportError:
    try:
        import docx2txt
        DOC_AVAILABLE = True
    except ImportError:
        DOC_AVAILABLE = False
        logger.warning("docx2txt not available - DOC parsing disabled")

class ResumeParser:
    """Extract structured information from resume files"""
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1?[-.\s]?)?(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/([a-zA-Z0-9-]+)', re.IGNORECASE)
        self.github_pattern = re.compile(r'github\.com/([a-zA-Z0-9-]+)', re.IGNORECASE)
        self.website_pattern = re.compile(r'https?://[^\s]+', re.IGNORECASE)
        
        # Skills patterns
        self.tech_skills = {
            'Python': r'\bpython\b',
            'JavaScript': r'\b(javascript|js)\b',
            'Java': r'\bjava\b',
            'C++': r'\bc\+\+',
            'C#': r'\bc#',
            'React': r'\breact\b',
            'Node.js': r'\bnode\.?js\b',
            'Angular': r'\bangular\b',
            'Vue': r'\bvue\b',
            'HTML': r'\bhtml\b',
            'CSS': r'\bcss\b',
            'SQL': r'\bsql\b',
            'MongoDB': r'\bmongodb\b',
            'PostgreSQL': r'\bpostgresql\b',
            'MySQL': r'\bmysql\b',
            'Docker': r'\bdocker\b',
            'Kubernetes': r'\bkubernetes\b',
            'AWS': r'\baws\b',
            'Azure': r'\bazure\b',
            'GCP': r'\bgcp\b',
            'Git': r'\bgit\b',
            'Linux': r'\blinux\b',
            'Machine Learning': r'\bmachine learning\b',
            'AI': r'\bartificial intelligence\b',
            'Cybersecurity': r'\bcybersecurity\b',
            'DevOps': r'\bdevops\b',
            'Flask': r'\bflask\b',
            'Django': r'\bdjango\b',
            'FastAPI': r'\bfastapi\b',
            'Selenium': r'\bselenium\b',
            'TensorFlow': r'\btensorflow\b',
            'PyTorch': r'\bpytorch\b',
            'Pandas': r'\bpandas\b',
            'NumPy': r'\bnumpy\b',
            'Scikit-learn': r'\bscikit.?learn\b',
        }
        
        # Location patterns
        self.location_pattern = re.compile(r'([A-Za-z\s]+),\s*([A-Z]{2})\s*(\d{5})?')
        
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse resume file and extract structured information"""
        try:
            # Extract text based on file type
            text = self._extract_text(file_path)
            if not text:
                return {'error': 'Could not extract text from resume'}
            
            # Parse information
            parsed_info = {
                'personal_info': self._extract_personal_info(text),
                'contact_info': self._extract_contact_info(text),
                'skills': self._extract_skills(text),
                'experience': self._extract_experience(text),
                'education': self._extract_education(text),
                'work_authorization': self._extract_work_authorization(text),
                'raw_text': text[:1000] + '...' if len(text) > 1000 else text  # First 1000 chars for debugging
            }
            
            return parsed_info
            
        except Exception as e:
            logger.error(f"Error parsing resume {file_path}: {str(e)}")
            return {'error': f'Failed to parse resume: {str(e)}'}
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from file based on extension"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_ext == '.docx':
                return self._extract_from_docx(file_path)
            elif file_ext == '.doc':
                return self._extract_from_doc(file_path)
            else:
                return ''
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ''
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            return ''
            
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text() + '\n'
                return text
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
            return ''
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            return ''
            
        try:
            doc = docx.Document(file_path)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {str(e)}")
            return ''
    
    def _extract_from_doc(self, file_path: str) -> str:
        """Extract text from DOC file"""
        if not DOC_AVAILABLE:
            return ''
            
        try:
            # Try different docx2txt modules
            try:
                import docx2txt
                return docx2txt.process(file_path)
            except ImportError:
                import python_docx2txt
                return python_docx2txt.process(file_path)
        except Exception as e:
            logger.error(f"Error reading DOC {file_path}: {str(e)}")
            return ''
    
    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extract personal information"""
        lines = text.split('\n')
        first_lines = lines[:5]  # Usually name is in first few lines
        
        # Try to extract name from first few lines
        name_line = ''
        for line in first_lines:
            line = line.strip()
            if line and not any(char in line for char in ['@', 'http', '+1', '(', ')']):
                if len(line.split()) >= 2 and len(line) < 50:
                    name_line = line
                    break
        
        name_parts = name_line.split() if name_line else []
        
        return {
            'first_name': name_parts[0] if name_parts else '',
            'last_name': ' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
            'full_name': name_line
        }
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information"""
        contact_info = {}
        
        # Email
        email_match = self.email_pattern.search(text)
        if email_match:
            contact_info['email'] = email_match.group(0)
        
        # Phone
        phone_match = self.phone_pattern.search(text)
        if phone_match:
            contact_info['phone'] = phone_match.group(0)
        
        # LinkedIn
        linkedin_match = self.linkedin_pattern.search(text)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group(0)
        
        # GitHub
        github_match = self.github_pattern.search(text)
        if github_match:
            contact_info['github'] = github_match.group(0)
        
        # Website
        website_matches = self.website_pattern.findall(text)
        if website_matches:
            # Filter out LinkedIn and GitHub
            websites = [url for url in website_matches 
                       if 'linkedin.com' not in url.lower() and 'github.com' not in url.lower()]
            if websites:
                contact_info['website'] = websites[0]
        
        # Location
        location_match = self.location_pattern.search(text)
        if location_match:
            contact_info['city'] = location_match.group(1).strip()
            contact_info['state'] = location_match.group(2).strip()
            if location_match.group(3):
                contact_info['zip_code'] = location_match.group(3).strip()
        
        return contact_info
    
    def _extract_skills(self, text: str) -> Dict[str, int]:
        """Extract technical skills and estimate proficiency"""
        skills = {}
        text_lower = text.lower()
        
        for skill, pattern in self.tech_skills.items():
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            if matches > 0:
                # Estimate proficiency based on frequency and context
                proficiency = min(5, matches + 2)  # Basic scoring
                skills[skill] = proficiency
        
        return skills
    
    def _extract_experience(self, text: str) -> Dict[str, Any]:
        """Extract work experience information"""
        experience_info = {}
        
        # Look for years of experience
        years_pattern = re.compile(r'(\d+)\+?\s*years?\s*(of\s*)?(experience|exp)', re.IGNORECASE)
        years_match = years_pattern.search(text)
        if years_match:
            experience_info['years_experience'] = int(years_match.group(1))
        
        # Look for job titles
        title_patterns = [
            r'software\s+(engineer|developer)',
            r'data\s+(scientist|analyst)',
            r'security\s+(engineer|analyst)',
            r'machine\s+learning\s+engineer',
            r'full\s+stack\s+developer',
            r'frontend\s+developer',
            r'backend\s+developer',
            r'devops\s+engineer',
            r'cybersecurity\s+(specialist|engineer)',
        ]
        
        titles = []
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            titles.extend(matches)
        
        if titles:
            experience_info['job_titles'] = list(set(titles))
        
        return experience_info
    
    def _extract_education(self, text: str) -> Dict[str, Any]:
        """Extract education information"""
        education_info = {}
        
        # Look for degree types
        degree_patterns = [
            r"bachelor'?s?\s*(of\s*)?(science|arts|engineering|computer science)?",
            r"master'?s?\s*(of\s*)?(science|arts|engineering|computer science)?",
            r"phd|doctorate|doctoral",
            r"associate'?s?",
            r"b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?"
        ]
        
        degrees = []
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                degrees.extend([match[0] if isinstance(match, tuple) else match for match in matches])
        
        if degrees:
            education_info['degrees'] = list(set(degrees))
        
        # Look for GPA
        gpa_pattern = re.compile(r'gpa:?\s*(\d+\.?\d*)', re.IGNORECASE)
        gpa_match = gpa_pattern.search(text)
        if gpa_match:
            education_info['gpa'] = float(gpa_match.group(1))
        
        return education_info
    
    def _extract_work_authorization(self, text: str) -> Dict[str, bool]:
        """Extract work authorization information"""
        auth_info = {}
        text_lower = text.lower()
        
        # US Citizen
        if any(phrase in text_lower for phrase in ['us citizen', 'u.s. citizen', 'american citizen']):
            auth_info['us_citizen'] = True
        
        # Visa requirements
        if any(phrase in text_lower for phrase in ['visa sponsorship', 'require visa', 'h1b', 'f1']):
            auth_info['require_visa'] = True
        
        # Work authorization
        if any(phrase in text_lower for phrase in ['authorized to work', 'work authorization', 'legally authorized']):
            auth_info['legally_authorized'] = True
        
        return auth_info

# Global parser instance
resume_parser = ResumeParser()

def parse_resume_file(file_path: str) -> Dict[str, Any]:
    """Parse a resume file and return extracted information"""
    return resume_parser.parse_resume(file_path) 