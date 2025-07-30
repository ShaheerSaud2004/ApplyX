import time, random, csv, traceback, os, re

# Conditional import for GUI-dependent modules
pyautogui = None
if os.environ.get('DISPLAY') or os.environ.get('RUNNING_LOCALLY'):
    try:
        import pyautogui
    except ImportError as e:
        print(f"Warning: Could not import pyautogui: {e}")
        print("This is expected in headless environments like DigitalOcean")
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date, datetime
from itertools import product
from pypdf import PdfReader
from openai import OpenAI
from stealth_config import AdvancedHumanBehavior, StealthLinkedInSession

class HumanBehaviorSimulator:
    """Utility class to simulate human-like behavior patterns"""
    
    @staticmethod
    def human_delay(min_sec=1, max_sec=3):
        """Random delay that mimics human thinking/reading time"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    @staticmethod
    def typing_delay(text_length):
        """Delay based on text length to simulate typing speed"""
        # Average human typing: 40 WPM = 200 characters/min = ~3.3 chars/sec
        chars_per_second = random.uniform(2.5, 4.5)  # Realistic range
        base_delay = text_length / chars_per_second
        # Add some randomness
        return random.uniform(base_delay * 0.7, base_delay * 1.3)
    
    @staticmethod
    def simulate_reading(driver, element=None):
        """Simulate human reading behavior with mouse movement and scrolling"""
        try:
            # Simulate reading time based on visible text
            if element:
                text_content = element.text
                # ~250 words per minute reading speed
                reading_time = len(text_content.split()) / 250 * 60
                reading_time = max(1, min(reading_time, 10))  # Cap between 1-10 seconds
            else:
                reading_time = random.uniform(2, 5)
            
            # Simulate eye movement with mouse
            actions = ActionChains(driver)
            for _ in range(random.randint(1, 3)):
                x_offset = random.randint(-30, 30)
                y_offset = random.randint(-20, 20)
                actions.move_by_offset(x_offset, y_offset)
                actions.perform()
                time.sleep(random.uniform(0.2, 0.5))
            
            # Small scroll movements - DISABLED for visible browser mode
            # if random.choice([True, False]):
            #     driver.execute_script(f"window.scrollBy(0, {random.randint(-50, 50)});")
            
            time.sleep(reading_time)
            
        except Exception:
            # Fallback to simple delay
            time.sleep(random.uniform(1, 3))
    
    @staticmethod
    def human_click(driver, element):
        """Simulate human-like clicking with slight delays and movements"""
        try:
            # Move to element first
            actions = ActionChains(driver)
            actions.move_to_element(element)
            actions.perform()
            
            # Small delay before clicking
            time.sleep(random.uniform(0.1, 0.3))
            
            # Sometimes double-click by accident (very rare)
            if random.random() < 0.02:  # 2% chance
                actions.click(element).click(element)
            else:
                actions.click(element)
            
            actions.perform()
            time.sleep(random.uniform(0.2, 0.8))
            
        except Exception:
            # Fallback to regular click
            element.click()
            time.sleep(random.uniform(0.2, 0.8))
    
    @staticmethod
    def human_type(driver, element, text):
        """Simulate human typing with realistic speed and occasional typos"""
        try:
            element.clear()
            time.sleep(random.uniform(0.2, 0.5))
            
            # Calculate typing delay
            typing_delay = HumanBehaviorSimulator.typing_delay(len(text))
            
            # Type with occasional pauses
            words = text.split(' ')
            for i, word in enumerate(words):
                # Small chance of typo and correction (5%)
                if random.random() < 0.05 and len(word) > 3:
                    # Type wrong character
                    wrong_char = random.choice('qwertyuiopasdfghjklzxcvbnm')
                    element.send_keys(word + wrong_char)
                    time.sleep(random.uniform(0.1, 0.3))
                    # Correct it
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(0.1, 0.2))
                    element.send_keys(word[-1])
                else:
                    element.send_keys(word)
                
                # Add space between words (except last word)
                if i < len(words) - 1:
                    element.send_keys(' ')
                
                # Random pause between words
                if random.random() < 0.3:  # 30% chance of pause
                    time.sleep(random.uniform(0.1, 0.5))
            
            # Final delay to simulate review
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception:
            # Fallback to simple send_keys
            element.clear()
            element.send_keys(text)
            time.sleep(random.uniform(0.5, 1.5))
    
    @staticmethod
    def random_scroll(driver):
        """Random scrolling behavior to seem more human - DISABLED for visible browser mode"""
        # Disabled automatic scrolling for better user experience when watching
        return
    
    @staticmethod
    def simulate_distraction(driver):
        """Occasionally simulate human distractions"""
        if random.random() < 0.1:  # 10% chance
            # Brief distraction - open new tab and close it
            try:
                driver.execute_script("window.open('');")
                time.sleep(random.uniform(1, 3))
                driver.switch_to.window(driver.window_handles[-1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(random.uniform(0.5, 1.5))
            except:
                pass
    
    @staticmethod
    def session_break_check():
        """Check if it's time for a longer break to avoid detection"""
        current_time = time.time()
        
        # Store session start time in a file
        session_file = "session_time.txt"
        try:
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    start_time = float(f.read().strip())
            else:
                start_time = current_time
                with open(session_file, 'w') as f:
                    f.write(str(start_time))
            
            # Take a break every 15-25 minutes
            session_duration = current_time - start_time
            if session_duration > random.uniform(900, 1500):  # 15-25 minutes
                break_time = random.uniform(180, 600)  # 3-10 minute break
                print(f"Taking a natural break for {break_time/60:.1f} minutes...")
                time.sleep(break_time)
                
                # Reset session timer
                with open(session_file, 'w') as f:
                    f.write(str(time.time()))
                    
        except Exception:
            pass

class AIResponseGenerator:
    def __init__(self, api_key, personal_info, experience, languages, resume_path, text_resume_path=None, debug=False):
        self.personal_info = personal_info
        self.experience = experience
        self.languages = languages
        self.pdf_resume_path = resume_path
        self.text_resume_path = text_resume_path
        self._resume_content = None
        self._client = OpenAI(api_key=api_key) if api_key else None
        self.debug = debug
    @property
    def resume_content(self):
        if self._resume_content is None:
            # First try to read from text resume if available
            if self.text_resume_path:
                try:
                    with open(self.text_resume_path, 'r', encoding='utf-8') as f:
                        self._resume_content = f.read()
                        print("Successfully loaded text resume")
                        return self._resume_content
                except Exception as e:
                    print(f"Could not read text resume: {str(e)}")

            # Fall back to PDF resume if text resume fails or isn't available
            try:
                content = []
                reader = PdfReader(self.pdf_resume_path)
                for page in reader.pages:
                    content.append(page.extract_text())
                self._resume_content = "\n".join(content)
                print("Successfully loaded PDF resume")
            except Exception as e:
                print(f"Could not extract text from resume PDF: {str(e)}")
                self._resume_content = ""
        return self._resume_content

    def _build_context(self):
        return f"""
        Personal Information:
        - Name: {self.personal_info['First Name']} {self.personal_info['Last Name']}
        - Current Role: {self.experience.get('currentRole', '')}
        - Skills: {', '.join(self.experience.keys())}
        - Languages: {', '.join(f'{lang}: {level}' for lang, level in self.languages.items())}
        - Professional Summary: {self.personal_info.get('MessageToManager', '')}

        Resume Content (Give the greatest weight to this information, if specified):
        {self.resume_content}
        """

    def generate_response(self, question_text, response_type="text", options=None, max_tokens=100):
        """
        Generate a response using OpenAI's API
        
        Args:
            question_text: The application question to answer
            response_type: "text", "numeric", or "choice"
            options: For "choice" type, a list of tuples containing (index, text) of possible answers
            max_tokens: Maximum length of response
            
        Returns:
            - For text: Generated text response or None
            - For numeric: Integer value or None
            - For choice: Integer index of selected option or None
        """
        if not self._client:
            return None
            
        try:
            context = self._build_context()
            
            system_prompt = {
                "text": (
                    "You are a helpful assistant answering job application questions professionally and concisely. "
                    "Use the candidate's background information and resume to personalize responses. "
                    "Always answer in first-person perspective, starting sentences with 'I'. Do NOT mention the candidate's name."
                ),
                "numeric": (
                    "You are a helpful assistant providing numeric answers to job application questions. "
                    "Return a single number based on the candidate's experience. No explanation needed. "
                    "Answer in first person if any wording is required (e.g., '1')."
                ),
                "choice": (
                    "You are a helpful assistant selecting the most appropriate answer choice for job application questions. "
                    "Base your selection on the candidate's background. Return ONLY the index number. "
                    "Do NOT reference the candidate's name; think in first person."
                )
            }[response_type]

            user_content = f"Using this candidate's background and resume:\n{context}\n\nPlease answer this job application question: {question_text}"
            if response_type == "choice" and options:
                options_text = "\n".join([f"{idx}: {text}" for idx, text in options])
                user_content += f"\n\nSelect the most appropriate answer by providing its index number from these options:\n{options_text}"

            response = self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            print(f"AI response: {answer}")  # TODO: Put logging behind a debug flag
            
            if response_type == "numeric":
                # Extract first number from response
                numbers = re.findall(r'\d+', answer)
                if numbers:
                    return int(numbers[0])
                return 0
            elif response_type == "choice":
                # Extract the index number from the response
                numbers = re.findall(r'\d+', answer)
                if numbers and options:
                    index = int(numbers[0])
                    # Ensure index is within valid range
                    if 0 <= index < len(options):
                        return index
                return None  # Return None if the index is not within the valid range
                
            return answer
            
        except Exception as e:
            print(f"Error using AI to generate response: {str(e)}")
            return None

    def evaluate_job_fit(self, job_title, job_description):
        """
        Evaluate whether a job is worth applying to based on the candidate's experience and the job requirements
        
        Args:
            job_title: The title of the job posting
            job_description: The full job description text
            
        Returns:
            bool: True if should apply, False if should skip
        """
        if not self._client:
            return True  # Proceed with application if AI not available
            
        try:
            context = self._build_context()
            
            system_prompt = """You are evaluating job fit for technical roles. 
            Recommend APPLY if:
            - Candidate meets 65 percent of the core requirements
            - Experience gap is 2 years or less
            - Has relevant transferable skills
            
            Return SKIP if:
            - Experience gap is greater than 2 years
            - Missing multiple core requirements
            - Role is clearly more senior
            - The role is focused on an uncommon technology or skill that is required and that the candidate does not have experience with
            - The role is a leadership role or a role that requires managing people and the candidate has no experience leading or managing people

            """
            #Consider the candidate's education level when evaluating whether they meet the core requirements. Having higher education than required should allow for greater flexibility in the required experience.
            
            if self.debug:
                system_prompt += """
                You are in debug mode. Return a detailed explanation of your reasoning for each requirement.

                Return APPLY or SKIP followed by a brief explanation.

                Format response as: APPLY/SKIP: [brief reason]"""
            else:
                system_prompt += """Return only APPLY or SKIP."""

            response = self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Job: {job_title}\n{job_description}\n\nCandidate:\n{context}"}
                ],
                max_tokens=250 if self.debug else 1,  # Allow more tokens when debug is enabled
                temperature=0.2  # Lower temperature for more consistent decisions
            )
            
            answer = response.choices[0].message.content.strip()
            print(f"AI evaluation: {answer}")
            return answer.upper().startswith('A')  # True for APPLY, False for SKIP
            
        except Exception as e:
            print(f"Error evaluating job fit: {str(e)}")
            return True  # Proceed with application if evaluation fails

class LinkedinEasyApply:
    def __init__(self, parameters, driver):
        self.browser = driver
        
        # ===== ULTIMATE SCROLL PREVENTION =====
        # Inject JavaScript to completely disable all scrolling
        self._disable_all_scrolling()
        
        self.email = parameters['email']
        self.password = parameters['password']
        self.openai_api_key = parameters.get('openaiApiKey', '')  # Get API key with empty default
        self.disable_lock = parameters['disableAntiLock']
        self.company_blacklist = parameters.get('companyBlacklist', []) or []
        self.title_blacklist = parameters.get('titleBlacklist', []) or []
        self.poster_blacklist = parameters.get('posterBlacklist', []) or []
        self.positions = parameters.get('positions', [])
        self.locations = parameters.get('locations', [])
        self.residency = parameters.get('residentStatus', [])
        self.base_search_url = self.get_base_search_url(parameters)
        self.seen_jobs = []
        self.file_name = "output"
        self.unprepared_questions_file_name = "unprepared_questions"
        self.output_file_directory = parameters['outputFileDirectory']
        self.resume_dir = parameters['uploads']['resume']
        self.text_resume = parameters.get('textResume', '')
        if 'coverLetter' in parameters['uploads']:
            self.cover_letter_dir = parameters['uploads']['coverLetter']
        else:
            self.cover_letter_dir = ''
        self.checkboxes = parameters.get('checkboxes', [])
        self.university_gpa = parameters['universityGpa']
        self.salary_minimum = parameters['salaryMinimum']
        self.notice_period = int(parameters['noticePeriod'])
        self.languages = parameters.get('languages', [])
        self.experience = parameters.get('experience', [])
        self.personal_info = parameters.get('personalInfo', [])
        self.eeo = parameters.get('eeo', [])
        self.experience_default = int(self.experience['default'])
        self.debug = parameters.get('debug', False)
        self.evaluate_job_fit = parameters.get('evaluateJobFit', True)
        self.fast_mode = False  # Fast mode disables all safety features
        self.continuous_mode = False  # Continuous mode skips session breaks
        self.use_advanced_stealth = True  # Enable advanced stealth behavior
        self.ai_response_generator = AIResponseGenerator(
            api_key=self.openai_api_key,
            personal_info=self.personal_info,
            experience=self.experience,
            languages=self.languages,
            resume_path=self.resume_dir,
            text_resume_path=self.text_resume,
            debug=self.debug
        )
        # Alternate email for application forms
        self.alt_email = parameters.get('alternateEmail', 'shaheersaud.internship@gmail.com')

    def _disable_all_scrolling(self):
        """ULTIMATE scrolling prevention - disables ALL forms of scrolling"""
        try:
            # Inject comprehensive scroll prevention JavaScript
            self.browser.execute_script("""
                // ===== MEGA SCROLL PREVENTION SYSTEM =====
                console.log('🚫 MEGA SCROLL PREVENTION: Starting comprehensive scroll blocking...');
                
                // Store original scroll functions to prevent any future scrolling
                window.originalScrollTo = window.scrollTo;
                window.originalScrollBy = window.scrollBy;
                
                // Override ALL window scroll functions
                window.scrollTo = function() { console.log('🚫 BLOCKED: window.scrollTo'); return false; };
                window.scrollBy = function() { console.log('🚫 BLOCKED: window.scrollBy'); return false; };
                window.scroll = function() { console.log('🚫 BLOCKED: window.scroll'); return false; };
                
                // Override ALL Element prototype scroll functions
                Element.prototype.scrollTo = function() { console.log('🚫 BLOCKED: element.scrollTo'); return false; };
                Element.prototype.scrollBy = function() { console.log('🚫 BLOCKED: element.scrollBy'); return false; };
                Element.prototype.scrollIntoView = function() { console.log('🚫 BLOCKED: element.scrollIntoView'); return false; };
                Element.prototype.scrollIntoViewIfNeeded = function() { console.log('🚫 BLOCKED: element.scrollIntoViewIfNeeded'); return false; };
                
                // Disable scrolling on body and html IMMEDIATELY
                document.body.style.overflow = 'hidden';
                document.body.style.overflowX = 'hidden';
                document.body.style.overflowY = 'hidden';
                document.documentElement.style.overflow = 'hidden';
                document.documentElement.style.overflowX = 'hidden';
                document.documentElement.style.overflowY = 'hidden';
                
                // Block ALL scroll-related events
                ['wheel', 'scroll', 'touchmove', 'keydown'].forEach(function(eventType) {
                    document.addEventListener(eventType, function(e) {
                        if (eventType === 'keydown') {
                            // Block arrow keys, page up/down, space, home, end
                            if ([32, 33, 34, 35, 36, 37, 38, 39, 40].includes(e.keyCode)) {
                                console.log('🚫 BLOCKED: Scroll key ' + e.keyCode);
                                e.preventDefault();
                                e.stopPropagation();
                                return false;
                            }
                        } else {
                            console.log('🚫 BLOCKED: ' + eventType + ' event');
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        }
                    }, { passive: false, capture: true });
                });
                
                // Apply to future elements too
                document.addEventListener('DOMContentLoaded', function() {
                    document.body.style.overflow = 'hidden';
                    document.documentElement.style.overflow = 'hidden';
                    console.log('🚫 DOM loaded - scroll prevention reinforced');
                });
                
                // Block programmatic scrolling attempts
                Object.defineProperty(window, 'scrollX', { value: 0, writable: false });
                Object.defineProperty(window, 'scrollY', { value: 0, writable: false });
                Object.defineProperty(window, 'pageXOffset', { value: 0, writable: false });
                Object.defineProperty(window, 'pageYOffset', { value: 0, writable: false });
                
                console.log('🚫 MEGA SCROLL PREVENTION ACTIVATED - ALL scrolling completely disabled!');
            """)
            print("🚫 MEGA SCROLL PREVENTION: All scrolling functions comprehensively disabled")
        except Exception as e:
            print(f"Warning: Could not inject scroll prevention: {e}")
    
    def _re_disable_scrolling(self):
        """Re-apply comprehensive scroll prevention on new pages"""
        try:
            self.browser.execute_script("""
                console.log('🚫 Re-applying MEGA scroll prevention...');
                
                // Re-override ALL scroll functions
                window.scrollTo = function() { console.log('🚫 BLOCKED: window.scrollTo (reapplied)'); return false; };
                window.scrollBy = function() { console.log('🚫 BLOCKED: window.scrollBy (reapplied)'); return false; };
                window.scroll = function() { console.log('🚫 BLOCKED: window.scroll (reapplied)'); return false; };
                
                Element.prototype.scrollTo = function() { console.log('🚫 BLOCKED: element.scrollTo (reapplied)'); return false; };
                Element.prototype.scrollBy = function() { console.log('🚫 BLOCKED: element.scrollBy (reapplied)'); return false; };
                Element.prototype.scrollIntoView = function() { console.log('🚫 BLOCKED: element.scrollIntoView (reapplied)'); return false; };
                Element.prototype.scrollIntoViewIfNeeded = function() { console.log('🚫 BLOCKED: element.scrollIntoViewIfNeeded (reapplied)'); return false; };
                
                // Re-disable overflow
                document.body.style.overflow = 'hidden';
                document.documentElement.style.overflow = 'hidden';
                
                console.log('🚫 MEGA scroll prevention re-applied successfully');
            """)
        except Exception:
            pass  # Ignore if page not ready
    
    def _ensure_chrome_visible(self):
        """Ensure Chrome window is visible and in foreground"""
        try:
            # Maximize window
            self.browser.maximize_window()
            
            # Use JavaScript to focus the window
            self.browser.execute_script("""
                window.focus();
                if (window.top) window.top.focus();
                console.log('🖥️ Chrome window focused via JavaScript');
            """)
            
            # Use AppleScript to bring Chrome to front on macOS
            import subprocess
            subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to activate'], 
                          capture_output=True, timeout=3)
            
            print("🖥️ Chrome window ensured visible and focused")
        except Exception as e:
            print(f"Could not ensure Chrome visibility: {e}")

    def human_type(self, element, text):
        """Enhanced human typing with advanced behavior patterns"""
        if hasattr(self, 'use_advanced_stealth') and self.use_advanced_stealth:
            AdvancedHumanBehavior.human_typing(element, text)
        else:
            # Fallback to existing behavior
            try:
                element.clear()
                time.sleep(random.uniform(0.2, 0.6))
                
                for char in text:
                    element.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.2))
                    
                time.sleep(random.uniform(0.3, 0.8))
            except Exception as e:
                print(f"⚠️ Typing error: {e}")
                element.send_keys(text)

    def human_click(self, element):
        """Enhanced human clicking with realistic mouse movement"""
        if hasattr(self, 'use_advanced_stealth') and self.use_advanced_stealth:
            try:
                AdvancedHumanBehavior.realistic_mouse_movement(self.browser, element)
                element.click()
            except Exception as e:
                print(f"⚠️ Advanced click failed, using fallback: {e}")
                HumanBehaviorSimulator.human_click(element)
        else:
            HumanBehaviorSimulator.human_click(element)

    def simulate_professional_reading(self, job_container):
        """Simulate how a professional would read a job description"""
        if hasattr(self, 'use_advanced_stealth') and self.use_advanced_stealth:
            try:
                # Find text elements in the job description
                text_elements = job_container.find_elements(By.CSS_SELECTOR, 
                    "div[data-job-id] p, div[data-job-id] span, div[data-job-id] li, .job-details-jobs-unified-top-card__content")
                
                if text_elements:
                    AdvancedHumanBehavior.professional_reading_pattern(self.browser, text_elements)
                else:
                    # Fallback: general page interaction
                    AdvancedHumanBehavior.realistic_page_interaction(self.browser)
                    
            except Exception as e:
                print(f"⚠️ Professional reading simulation failed: {e}")
                # Fallback to basic delay
                HumanBehaviorSimulator.human_delay(3, 8)
        else:
            # Use existing human delay
            HumanBehaviorSimulator.human_delay(3, 6)

    def _merge_experience_with_csv(self, csv_path: str):
        """Merge skills->years mapping from a CSV file with the YAML mapping.

        The CSV must have at least two columns: skill name and integer years.
        For each skill we keep the larger of the YAML value and the CSV value.
        """
        if not os.path.exists(csv_path):
            return  # Nothing to merge

        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 2:
                        continue  # Malformed row
                    skill = row[0].strip()
                    try:
                        years = int(row[1].strip())
                    except ValueError:
                        continue  # Non-numeric years, skip

                    # Compare with YAML value (default 0 if missing)
                    try:
                        current_years = int(self.experience.get(skill, 0))
                    except Exception:
                        current_years = 0

                    if years > current_years:
                        self.experience[skill] = years
        except Exception as e:
            if getattr(self, 'debug', False):
                print(f"Could not merge experience CSV: {e}")

    def login(self):
        try:
            print("🚀 LINKEDIN BOT: Starting login process...")
            print("🚀 LINKEDIN BOT: Step 1 - Attempting to access LinkedIn...")
            
            # Try to go to LinkedIn feed page first
            self.browser.get("https://www.linkedin.com/feed/")
            print("🚀 LINKEDIN BOT: Successfully navigated to LinkedIn feed URL")
            
            # Apply scroll prevention immediately after page load
            self._re_disable_scrolling()
            print("🚀 LINKEDIN BOT: Applied scroll prevention measures")
            
            # Ensure Chrome window is visible
            self._ensure_chrome_visible()
            print("🚀 LINKEDIN BOT: Ensured Chrome window visibility")
            
            if not self.fast_mode:
                print("🚀 LINKEDIN BOT: Applying human-like delay (3-6 seconds)...")
                HumanBehaviorSimulator.human_delay(3, 6)
            else:
                print("🚀 LINKEDIN BOT: Fast mode - minimal delay")
                time.sleep(1)

            # Check for "Welcome Back" screen first
            print("🚀 LINKEDIN BOT: Step 2 - Checking for Welcome Back screen...")
            if self.handle_welcome_back_screen():
                print("🚀 LINKEDIN BOT: ✅ Successfully handled Welcome Back screen, checking login status...")
                if not self.fast_mode:
                    HumanBehaviorSimulator.human_delay(2, 4)
                else:
                    time.sleep(0.5)
            else:
                print("🚀 LINKEDIN BOT: No Welcome Back screen detected")

            # Check if we're logged in by looking for the feed page or need to login
            current_url = self.browser.current_url
            print(f"🚀 LINKEDIN BOT: Current URL after navigation: {current_url}")
            
            if "feed" not in current_url and "login" not in current_url:
                print("🚀 LINKEDIN BOT: Not on feed or login page - redirecting to login...")
                # We might be on a welcome/login selection page
                self.browser.get("https://www.linkedin.com/login")
                print("🚀 LINKEDIN BOT: Navigated to login page")
                if not self.fast_mode:
                    HumanBehaviorSimulator.human_delay(2, 4)
                else:
                    time.sleep(0.5)
                
            if "login" in current_url or self.browser.current_url != "https://www.linkedin.com/feed/":
                print("🚀 LINKEDIN BOT: Step 3 - Login required, proceeding to authentication...")
                self.load_login_page_and_login()
                print("🚀 LINKEDIN BOT: ✅ Login process completed successfully!")
            else:
                print("🚀 LINKEDIN BOT: ✅ Already logged in - proceeding to job search")

        except TimeoutException:
            print("🚀 LINKEDIN BOT: ⚠️ Timeout occurred during login, checking for security challenges...")
            self.security_check()
            # raise Exception("Could not login!")

    def handle_welcome_back_screen(self):
        """Handle LinkedIn's 'Welcome Back' screen where user needs to click their profile"""
        try:
            # Look for the welcome back text
            welcome_elements = self.browser.find_elements(By.XPATH, "//*[contains(text(), 'Welcome Back')]")
            if welcome_elements:
                print("Detected 'Welcome Back' screen")
                
                # Get user's first and last name from personal info
                first_name = self.personal_info.get('First Name', '').strip()
                last_name = self.personal_info.get('Last Name', '').strip()
                full_name = f"{first_name} {last_name}".strip()
                
                # Look for the user's profile/account button to click
                # Try multiple selectors for the profile click area
                profile_selectors = [
                    f"//div[contains(text(), '{full_name}')]/.." if full_name else None,  # Click the div containing the full name
                    f"//div[contains(text(), '{full_name}')]" if full_name else None,     # Click the name directly
                    f"//div[contains(text(), '{first_name}')]/.." if first_name else None,  # Click the div containing first name
                    f"//div[contains(text(), '{first_name}')]" if first_name else None,     # Click first name directly
                    "//div[contains(@class, 'profile') or contains(@class, 'account')]//button",
                    "//button[contains(@class, 'profile') or contains(@class, 'account')]",
                    "//div[contains(@class, 'display-flex')]//button",
                    "//div[@role='button']",
                    "//button[@type='button']",
                    "//div[contains(@class, 'profile-card')]",      # Profile card area
                    "//div[contains(@class, 'identity')]"          # Identity section
                ]
                
                for selector in profile_selectors:
                    # Skip None selectors (when user info is not available)
                    if selector is None:
                        continue
                        
                    try:
                        profile_button = self.browser.find_element(By.XPATH, selector)
                        if profile_button.is_displayed():
                            print(f"Clicking profile button with selector: {selector}")
                            if not self.fast_mode:
                                HumanBehaviorSimulator.simulate_reading(self.browser, profile_button)
                                HumanBehaviorSimulator.human_click(self.browser, profile_button)
                                HumanBehaviorSimulator.human_delay(3, 6)
                            else:
                                profile_button.click()
                                time.sleep(1)
                            return True
                    except:
                        continue
                
                # Fallback - try clicking anywhere on the main content area
                try:
                    content_area = self.browser.find_element(By.TAG_NAME, "main")
                    print("Clicking main content area as fallback")
                    if not self.fast_mode:
                        HumanBehaviorSimulator.human_click(self.browser, content_area)
                        HumanBehaviorSimulator.human_delay(3, 6)
                    else:
                        content_area.click()
                        time.sleep(1)
                    return True
                except:
                    pass
                    
            return False
            
        except Exception as e:
            print(f"Error handling welcome back screen: {e}")
            return False

    def security_check(self):
        current_url = self.browser.current_url
        page_source = self.browser.page_source

        if '/checkpoint/challenge/' in current_url or 'security check' in page_source or 'quick verification' in page_source:
            input("Please complete the security check and press enter on this console when it is done.")
            if not self.fast_mode:
                HumanBehaviorSimulator.human_delay(5, 10)
            else:
                time.sleep(2)

    def load_login_page_and_login(self):
        print("🔐 LINKEDIN BOT: Loading login page...")
        self.browser.get("https://www.linkedin.com/login")
        print("🔐 LINKEDIN BOT: Successfully navigated to login page")
        
        if not self.fast_mode:
            print("🔐 LINKEDIN BOT: Applying human-like reading delay...")
            HumanBehaviorSimulator.human_delay(2, 4)  # Natural delay to read the page
        else:
            print("🔐 LINKEDIN BOT: Fast mode - minimal page load delay")
            time.sleep(1)

        # Wait for the username field to be present
        print("🔐 LINKEDIN BOT: Waiting for username field to be available...")
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        print("🔐 LINKEDIN BOT: ✅ Username field located successfully")

        # Simulate human-like typing (or fast typing in fast mode)
        username_field = self.browser.find_element(By.ID, "username")
        
        # Check if email is properly loaded
        if not self.email:
            print("❌ LINKEDIN BOT: Email credentials not found! Cannot proceed with login.")
            raise Exception("Email credentials missing - please check your configuration")
        
        email_to_show = self.email[:3] + "***" + self.email[-4:] if len(self.email) > 7 else "***"
        print(f"🔐 LINKEDIN BOT: Entering email address: {email_to_show}")
        
        if not self.fast_mode:
            print("🔐 LINKEDIN BOT: Using human-like typing simulation for email...")
            HumanBehaviorSimulator.human_type(self.browser, username_field, self.email)
            HumanBehaviorSimulator.human_delay(0.5, 1.5)  # Natural pause between fields
        else:
            print("🔐 LINKEDIN BOT: Fast mode - direct email entry")
            username_field.clear()
            username_field.send_keys(self.email)
            time.sleep(0.2)
        
        print("🔐 LINKEDIN BOT: ✅ Email address entered successfully")
        
        password_field = self.browser.find_element(By.ID, "password")
        print("🔐 LINKEDIN BOT: Entering password...")
        
        if not self.fast_mode:
            print("🔐 LINKEDIN BOT: Using human-like typing simulation for password...")
            HumanBehaviorSimulator.human_type(self.browser, password_field, self.password)
            HumanBehaviorSimulator.human_delay(1, 2)  # Brief pause before clicking login
        else:
            print("🔐 LINKEDIN BOT: Fast mode - direct password entry")
            password_field.clear()
            password_field.send_keys(self.password)
            time.sleep(0.2)
        
        print("🔐 LINKEDIN BOT: ✅ Password entered successfully")
        
        login_button = self.browser.find_element(By.CSS_SELECTOR, ".btn__primary--large")
        print("🔐 LINKEDIN BOT: Clicking login button...")
        
        if not self.fast_mode:
            print("🔐 LINKEDIN BOT: Using human-like click simulation...")
            HumanBehaviorSimulator.human_click(self.browser, login_button)
        else:
            print("🔐 LINKEDIN BOT: Fast mode - direct click")
            login_button.click()

        print("🔐 LINKEDIN BOT: Login button clicked - waiting for authentication...")

        # Wait for the feed page to load after login
        print("🔐 LINKEDIN BOT: Waiting for LinkedIn feed page to load...")
        WebDriverWait(self.browser, 10).until(
            EC.url_contains("https://www.linkedin.com/feed/")
        )
        print("🔐 LINKEDIN BOT: ✅ Successfully authenticated and redirected to feed!")

        if not self.fast_mode:
            print("🔐 LINKEDIN BOT: Applying post-login delay for natural behavior...")
            HumanBehaviorSimulator.human_delay(3, 6)  # Natural delay after login
        else:
            print("🔐 LINKEDIN BOT: Fast mode - minimal post-login delay")
            time.sleep(1)
            
        print("🔐 LINKEDIN BOT: ✅ Login process completed successfully - ready for job search!")

    def start_applying(self, max_applications=None):
        print("🔍 LINKEDIN BOT: 🚀 STARTING JOB APPLICATION PROCESS! 🚀")
        print("🔍 ===============================================")
        print(f"🔍 📊 APPLICATION SESSION PARAMETERS:")
        print(f"🔍    🎯 Target Positions: {self.positions}")
        print(f"🔍    📍 Target Locations: {self.locations}")
        print(f"🔍    🔢 Max Applications: {max_applications or 'Unlimited'}")
        print(f"🔍    ⚡ Fast Mode: {self.fast_mode}")
        print(f"🔍    🔄 Continuous Mode: {getattr(self, 'continuous_mode', False)}")
        print("🔍 ===============================================")
        
        searches = list(product(self.positions, self.locations))
        random.shuffle(searches)
        
        print(f"🔍 🎲 Generated {len(searches)} search combinations:")
        for i, (pos, loc) in enumerate(searches, 1):
            print(f"🔍    {i}. {pos} in {loc}")
        print("🔍 ===============================================")

        page_sleep = 0
        applications_made = 0
        if self.continuous_mode:
            minimum_time = 10  # Very short time for continuous mode
            print("🔍 ⚡ Continuous mode: Using 10-second page delays")
        elif self.fast_mode:
            minimum_time = 30
            print("🔍 🚀 Fast mode: Using 30-second page delays")
        else:
            minimum_time = 60 * 2
            print("🔍 🐌 Normal mode: Using 2-minute page delays")
        minimum_page_time = time.time() + minimum_time

        search_count = 0
        for (position, location) in searches:
            search_count += 1
            print(f"🔍 🎯 STARTING SEARCH {search_count}/{len(searches)}")
            print(f"🔍 📋 Position: {position}")
            print(f"🔍 📍 Location: {location}")
            
            if max_applications and applications_made >= max_applications:
                print(f"🔍 ✅ TARGET REACHED: {max_applications} applications completed!")
                print(f"🔍 🎉 Final application count: {applications_made}")
                return applications_made
                
            location_url = "&location=" + location
            job_page_number = -1
            
            print(f"🔍 🔍 Starting search for {position} in {location}...")
            if not self.fast_mode:
                print("🔍 ⏱️ Applying human-like search delay...")
                HumanBehaviorSimulator.human_delay(1, 3)  # Natural pause before starting search
            else:
                print("🔍 ⚡ Fast mode - minimal search delay")

            try:
                page_count = 0
                while True:
                    page_count += 1
                    if max_applications and applications_made >= max_applications:
                        print(f"🔍 ✅ TARGET REACHED during page navigation: {max_applications} applications!")
                        return applications_made
                        
                    page_sleep += 1
                    job_page_number += 1
                    print(f"🔍 📄 NAVIGATING TO PAGE {job_page_number + 1} (Page {page_count} of search)")
                    print(f"🔍 🔗 Going to job page {job_page_number} for {position} in {location}")
                    
                    self.next_job_page(position, location_url, job_page_number)
                    print(f"🔍 ✅ Successfully loaded job page {job_page_number}")
                    
                    if not self.fast_mode:
                        print("🔍 ⏱️ Applying human-like page loading delay...")
                        HumanBehaviorSimulator.human_delay(2, 5)  # More natural page loading delay
                        # HumanBehaviorSimulator.random_scroll(self.browser)  # DISABLED - No more scrolling!
                        print("🔍 🚫 Random scrolling disabled for better viewing")
                    else:
                        print("🔍 ⚡ Fast mode - minimal page loading delay")
                        time.sleep(0.5)  # Minimal delay in fast mode
                        
                    print(f"🔍 🚀 STARTING APPLICATION PROCESS FOR PAGE {job_page_number}...")
                    print(f"🔍 📊 Current session stats: {applications_made} applications completed")
                    
                    page_applications = self.apply_jobs(location, max_applications - applications_made if max_applications else None)
                    applications_made += page_applications
                    
                    print(f"🔍 📈 PAGE {job_page_number} COMPLETED!")
                    print(f"🔍 📊 Applications from this page: {page_applications}")
                    print(f"🔍 📊 Total applications so far: {applications_made}")
                    print(f"🔍 🎯 Target: {max_applications or 'Unlimited'}")
                    
                    if page_applications > 0:
                        print(f"🔍 🎉 SUCCESS! Applied to {page_applications} jobs on this page")
                    else:
                        print(f"🔍 ⚠️ No applications made on this page")

                    if max_applications and applications_made >= max_applications:
                        print(f"🔍 🎉 TARGET ACHIEVED: {max_applications} applications completed!")
                        print(f"🔍 ✅ Final count: {applications_made} applications")
                        return applications_made

                    if self.continuous_mode:
                        # Continuous mode: no delays between pages, only between applications
                        time.sleep(1)
                    elif not self.fast_mode:
                        time_left = minimum_page_time - time.time()
                        if time_left > 0:
                            print("Sleeping for " + str(time_left) + " seconds.")
                            time.sleep(time_left)
                            minimum_page_time = time.time() + minimum_time
                        if page_sleep % 5 == 0:
                            sleep_time = random.randint(180, 300)  # Changed from 500, 900 {seconds}
                            print("Sleeping for " + str(sleep_time / 60) + " minutes.")
                            time.sleep(sleep_time)
                            page_sleep += 1
                    else:
                        # Fast mode: minimal delays
                        time.sleep(random.uniform(5, 15))  # Quick page transition
                        
            except:
                traceback.print_exc()
                pass

            if self.continuous_mode:
                # No delays at the end for continuous mode
                pass
            elif not self.fast_mode:
                time_left = minimum_page_time - time.time()
                if time_left > 0:
                    print("Sleeping for " + str(time_left) + " seconds.")
                    time.sleep(time_left)
                    minimum_page_time = time.time() + minimum_time
                if page_sleep % 5 == 0:
                    sleep_time = random.randint(500, 900)
                    print("Sleeping for " + str(sleep_time / 60) + " minutes.")
                    time.sleep(sleep_time)
                    page_sleep += 1
        
        return applications_made

    def apply_jobs(self, location, max_applications=None):
        print("🎯 LINKEDIN BOT: 📋 STARTING JOB APPLICATION PROCESSING...")
        print(f"🎯 📍 Processing jobs in location: {location}")
        print(f"🎯 🔢 Max applications for this page: {max_applications or 'Unlimited'}")
        
        no_jobs_text = ""
        try:
            print("🎯 🔍 Checking for 'no results' banner...")
            no_jobs_element = self.browser.find_element(By.CLASS_NAME,
                                                        'jobs-search-two-pane__no-results-banner--expand')
            no_jobs_text = no_jobs_element.text
            print(f"🎯 📋 No jobs banner text: {no_jobs_text}")
        except:
            print("🎯 ✅ No 'no results' banner found - jobs should be available")
            pass
            
        if 'No matching jobs found' in no_jobs_text:
            print("🎯 ❌ No matching jobs found on this page!")
            raise Exception("No more jobs on this page.")

        if 'unfortunately, things are' in self.browser.page_source.lower():
            print("🎯 ❌ LinkedIn error message detected - no more jobs")
            raise Exception("No more jobs on this page.")

        job_results_header = ""
        maybe_jobs_crap = ""
        print("🎯 🔍 Checking job results header...")
        job_results_header = self.browser.find_element(By.CLASS_NAME, "jobs-search-results-list__text")
        maybe_jobs_crap = job_results_header.text
        print(f"🎯 📋 Job results header: {maybe_jobs_crap}")

        if 'Jobs you may be interested in' in maybe_jobs_crap:
            print("🎯 ⚠️ Found 'Jobs you may be interested in' section - skipping")
            raise Exception("Nothing to do here, moving forward...")

        try:
            print("🎯 🔍 Locating job list container...")
            # TODO: Can we simply use class name scaffold-layout__list for the scroll (necessary to show all li in the dom?)? Does it need to be the ul within the scaffold list?
            #      Then we can simply get all the li scaffold-layout__list-item elements within it for the jobs

            # Define the XPaths for potentially different regions
            xpath_region1 = "/html/body/div[6]/div[3]/div[4]/div/div/main/div/div[2]/div[1]/div"
            xpath_region2 = "/html/body/div[5]/div[3]/div[4]/div/div/main/div/div[2]/div[1]/div"
            job_list = []

            # Attempt to locate the element using XPaths
            try:
                print("🎯 🔍 Trying xpath_region1...")
                job_results = self.browser.find_element(By.XPATH, xpath_region1)
                ul_xpath = "/html/body/div[6]/div[3]/div[4]/div/div/main/div/div[2]/div[1]/div/ul"
                ul_element = self.browser.find_element(By.XPATH, ul_xpath)
                ul_element_class = ul_element.get_attribute("class").split()[0]
                print(f"🎯 ✅ Found using xpath_region1 and detected ul_element as {ul_element_class} based on {ul_xpath}")

            except NoSuchElementException:
                print("🎯 ⚠️ xpath_region1 failed, trying xpath_region2...")
                job_results = self.browser.find_element(By.XPATH, xpath_region2)
                ul_xpath = "/html/body/div[5]/div[3]/div[4]/div/div/main/div/div[2]/div[1]/div/ul"
                ul_element = self.browser.find_element(By.XPATH, ul_xpath)
                ul_element_class = ul_element.get_attribute("class").split()[0]
                print(f"🎯 ✅ Found using xpath_region2 and detected ul_element as {ul_element_class} based on {ul_xpath}")

            # Extract the random class name dynamically
            random_class = job_results.get_attribute("class").split()[0]
            print(f"🎯 🎲 Random class detected: {random_class}")

            # Use the detected class name to find the element
            job_results_by_class = self.browser.find_element(By.CSS_SELECTOR, f".{random_class}")
            print(f"🎯 📋 job_results: {job_results_by_class}")
            print("🎯 ✅ Successfully located the element using the random class name")

            # Scroll logic - DISABLED for visible browser mode (no more annoying scrolling!)
            # self.scroll_slow(job_results_by_class)  # Scroll down - DISABLED
            # self.scroll_slow(job_results_by_class, step=300, reverse=True)  # Scroll up - DISABLED
            print("🎯 🚫 Auto-scrolling disabled for better viewing experience")

            # Find job list elements
            print("🎯 🔍 Finding individual job elements...")
            job_list = self.browser.find_elements(By.CLASS_NAME, ul_element_class)[0].find_elements(By.CLASS_NAME, 'scaffold-layout__list-item')
            print(f"🎯 📊 Found {len(job_list)} jobs on this page")
            print(f"🎯 🎯 Ready to process jobs...")

            if len(job_list) == 0:
                print("🎯 ❌ No jobs found in the list - moving to next page")
                raise Exception("No more jobs on this page.")  # TODO: Seemed to encounter an error where we ran out of jobs and didn't go to next page, perhaps because I didn't have scrolling on?

        except NoSuchElementException:
            print("🎯 ❌ No job results found using the specified XPaths or class")

        except Exception as e:
            print(f"🎯 ❌ An unexpected error occurred while finding jobs: {e}")

        applications_made = 0
        print(f"🎯 🚀 STARTING TO PROCESS {len(job_list)} INDIVIDUAL JOBS...")
        print("🎯 ===============================================")
        
        for job_index, job_tile in enumerate(job_list, 1):
            print(f"🎯 📋 PROCESSING JOB {job_index}/{len(job_list)}")
            
            if max_applications and applications_made >= max_applications:
                print(f"🎯 ✅ Reached maximum applications limit for this page: {max_applications}")
                print(f"🎯 📊 Applications made on this page: {applications_made}")
                break
                
            job_title, company, poster, job_location, apply_method, link = "", "", "", "", "", ""

            try:
                print(f"🎯 🔍 Extracting job details for job {job_index}...")
                ## patch to incorporate new 'verification' crap by LinkedIn
                # job_title = job_tile.find_element(By.CLASS_NAME, 'job-card-list__title').text # original code
                job_title_element = job_tile.find_element(By.CLASS_NAME, 'job-card-list__title--link')
                job_title = job_title_element.find_element(By.TAG_NAME, 'strong').text

                link = job_tile.find_element(By.CLASS_NAME, 'job-card-list__title--link').get_attribute('href').split('?')[0]
                print(f"🎯 💼 Job Title: {job_title}")
                print(f"🎯 🔗 Job Link: {link}")
            except Exception as e:
                print(f"🎯 ⚠️ Error extracting job title/link: {e}")
                pass
            try:
                # company = job_tile.find_element(By.CLASS_NAME, 'job-card-container__primary-description').text # original code
                company = job_tile.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__subtitle').text
                print(f"🎯 🏢 Company: {company}")
            except Exception as e:
                print(f"🎯 ⚠️ Error extracting company: {e}")
                pass
            try:
                # get the name of the person who posted for the position, if any is listed
                hiring_line = job_tile.find_element(By.XPATH, '//span[contains(.,\' is hiring for this\')]')
                hiring_line_text = hiring_line.text
                name_terminating_index = hiring_line_text.find(' is hiring for this')
                if name_terminating_index != -1:
                    poster = hiring_line_text[:name_terminating_index]
                print(f"🎯 👤 Posted by: {poster}")
            except Exception as e:
                print(f"🎯 ⚠️ No poster information found")
                pass
            try:
                job_location = job_tile.find_element(By.CLASS_NAME, 'job-card-container__metadata-item').text
                print(f"🎯 📍 Job Location: {job_location}")
            except Exception as e:
                print(f"🎯 ⚠️ Error extracting job location: {e}")
                pass
            try:
                apply_method = job_tile.find_element(By.CLASS_NAME, 'job-card-container__apply-method').text
                print(f"🎯 📋 Apply Method: {apply_method}")
            except Exception as e:
                print(f"🎯 ⚠️ Error extracting apply method: {e}")
                pass

            print(f"🎯 🔍 FILTERING JOB: {job_title} at {company}")
            contains_blacklisted_keywords = False
            job_title_parsed = job_title.lower().split(' ')

            print(f"🎯 🚫 Checking title blacklist...")
            for word in self.title_blacklist:
                if word.lower() in job_title_parsed:
                    contains_blacklisted_keywords = True
                    print(f"🎯 ❌ BLACKLISTED TITLE KEYWORD: '{word}' found in job title")
                    break

            # Check all filter conditions
            company_blacklisted = company.lower() in [word.lower() for word in self.company_blacklist]
            poster_blacklisted = poster.lower() in [word.lower() for word in self.poster_blacklist]
            already_seen = link in self.seen_jobs
            
            print(f"🎯 📊 FILTER RESULTS:")
            print(f"🎯    Company blacklisted: {company_blacklisted}")
            print(f"🎯    Poster blacklisted: {poster_blacklisted}")
            print(f"🎯    Title blacklisted: {contains_blacklisted_keywords}")
            print(f"🎯    Already seen: {already_seen}")

            if company_blacklisted:
                print(f"🎯 ❌ SKIPPING: Company '{company}' is blacklisted")
                continue
            elif poster_blacklisted:
                print(f"🎯 ❌ SKIPPING: Poster '{poster}' is blacklisted")
                continue
            elif contains_blacklisted_keywords:
                print(f"🎯 ❌ SKIPPING: Job title contains blacklisted keywords")
                continue
            elif already_seen:
                print(f"🎯 ❌ SKIPPING: Job already processed in this session")
                continue
            else:
                print(f"🎯 ✅ JOB PASSED ALL FILTERS - PROCEEDING TO APPLICATION")
                
            if not company_blacklisted and not poster_blacklisted and not contains_blacklisted_keywords and not already_seen:
                try:
                    # Click the job to load description
                    print(f"🎯 🖱️ CLICKING JOB TO LOAD DETAILS: {job_title}")
                    max_retries = 3
                    retries = 0
                    while retries < max_retries:
                        try:
                            # TODO: This is throwing an exception when running out of jobs on a page
                            job_el = job_tile.find_element(By.CLASS_NAME, 'job-card-list__title--link')
                            
                            # Simulate human reading and decision making (only if not in fast mode)
                            if not self.fast_mode:
                                print("🎯 👁️ Simulating human reading behavior...")
                                HumanBehaviorSimulator.simulate_reading(self.browser, job_tile)
                                HumanBehaviorSimulator.human_click(self.browser, job_el)
                                print("🎯 ✅ Human-like click completed")
                            else:
                                print("🎯 ⚡ Fast mode - direct click")
                                job_el.click()
                            break
                        except StaleElementReferenceException:
                            retries += 1
                            print(f"🎯 ⚠️ Stale element reference, retry {retries}/{max_retries}")
                            continue

                    print(f"🎯 ✅ Job clicked successfully - loading job details...")

                    if not self.fast_mode:
                        print("🎯 ⏱️ Applying human-like job reading delay...")
                        HumanBehaviorSimulator.human_delay(3, 6)  # Natural delay to read job details
                        # HumanBehaviorSimulator.random_scroll(self.browser)  # DISABLED - No more scrolling!
                        print("🎯 🚫 Random scrolling disabled for better viewing")
                        if not self.continuous_mode:  # Skip session breaks in continuous mode
                            HumanBehaviorSimulator.session_break_check()  # Check if break is needed
                    else:
                        print("🎯 ⚡ Fast mode - minimal job reading delay")
                        time.sleep(0.5)  # Minimal delay in fast mode

                    # TODO: Check if the job is already applied or the application has been reached
                    # "You've reached the Easy Apply application limit for today. Save this job and come back tomorrow to continue applying."
                    # Do this before evaluating job fit to save on API calls

                    if self.evaluate_job_fit:
                        print("🎯 🤖 AI job fit evaluation enabled - checking compatibility...")
                        try:
                            # Get job description
                            job_description = self.browser.find_element(
                                By.ID, 'job-details'
                            ).text  
                            print("🎯 📝 Job description extracted for AI evaluation")

                            # Evaluate if we should apply
                            print("🎯 🧠 Running AI job fit analysis...")
                            if not self.ai_response_generator.evaluate_job_fit(job_title, job_description):
                                print("🎯 ❌ AI EVALUATION: Job requirements not aligned with candidate profile")
                                print(f"🎯 ⏭️ SKIPPING APPLICATION: {job_title} at {company}")
                                continue
                            else:
                                print("🎯 ✅ AI EVALUATION: Job is a good fit - proceeding with application")
                        except Exception as eval_error:
                            print(f"🎯 ⚠️ Could not load job description for AI evaluation: {eval_error}")
                            print("🎯 🔄 Proceeding with application anyway...")

                    try:
                        print(f"🎯 🚀 STARTING APPLICATION PROCESS: {company} - {job_title}")
                        print(f"🎯 📊 This will be application #{applications_made + 1} on this page")
                        
                        done_applying = self.apply_to_job()
                        
                        if done_applying:
                            applications_made += 1
                            print(f"🎯 🎉 APPLICATION SUCCESSFUL!")
                            print(f"🎯 ✅ Application #{applications_made} sent to {company} for {job_title}")
                            print(f"🎯 🔔 This should trigger write_to_file for database/CSV logging...")
                            
                            # Note: Delay between applications is handled by the calling code
                        else:
                            print(f"🎯 ⏭️ APPLICATION SKIPPED: Job at {company} has been submitted earlier or failed")
                    except Exception as apply_error:
                        print(f"🎯 ❌ APPLICATION FAILED: Error during application process")
                        print(f"🎯 🚨 Error details: {apply_error}")
                        import traceback
                        traceback.print_exc()
                        
                        print(f"🎯 📝 Logging failed application to failed.csv...")
                        temp = self.file_name
                        self.file_name = "failed"
                        print("🎯 🐛 Failed to apply to job. Please submit a bug report with this link: " + link)
                        try:
                            self.write_to_file(company, job_title, link, job_location, location)
                            print("🎯 ✅ Failed application logged successfully")
                        except Exception as log_error:
                            print(f"🎯 ❌ Could not log failed application: {log_error}")
                            pass
                        self.file_name = temp
                        print(f"🎯 🔄 Restored original file name: {temp}")

                    try:
                        print(f"🎯 📝 CALLING write_to_file for successful application...")
                        print(f"🎯 📊 Application details:")
                        print(f"🎯    🏢 Company: {company}")
                        print(f"🎯    💼 Job Title: {job_title}")
                        print(f"🎯    🔗 Job URL: {link}")
                        print(f"🎯    📍 Job Location: {job_location}")
                        print(f"🎯    🎯 Search Location: {location}")
                        
                        self.write_to_file(company, job_title, link, job_location, location)
                        print(f"🎯 ✅ write_to_file completed successfully - application logged!")
                    except Exception as write_error:
                        print(f"🎯 ❌ write_to_file FAILED: {write_error}")
                        print(f"🎯 🚨 Unable to save job information - job title '{job_title}' or company '{company}' may contain special characters")
                        traceback.print_exc()
                        
                except Exception as job_error:
                    print(f"🎯 ❌ CRITICAL ERROR processing job at {company}")
                    print(f"🎯 🚨 Error details: {job_error}")
                    traceback.print_exc()
                    pass
            else:
                print(f"🎯 ❌ Job for {company} by {poster} contains a blacklisted word.")

            print(f"🎯 📝 Adding job to seen_jobs list: {link}")
            self.seen_jobs.append(link)
            print(f"🎯 📊 Total jobs seen in this session: {len(self.seen_jobs)}")
            
        print("🎯 ===============================================")
        print(f"🎯 🎉 PAGE PROCESSING COMPLETED!")
        print(f"🎯 📊 Applications made on this page: {applications_made}")
        print(f"🎯 📈 Jobs processed: {len(job_list)}")
        print(f"🎯 📋 Jobs seen in session: {len(self.seen_jobs)}")
        print("🎯 ===============================================")
        return applications_made

    def apply_to_job(self):
        print("💼 LINKEDIN BOT: 🎯 STARTING JOB APPLICATION PROCESS...")
        easy_apply_button = None

        try:
            print("💼 LINKEDIN BOT: Looking for Easy Apply button...")
            easy_apply_button = self.browser.find_element(By.CLASS_NAME, 'jobs-apply-button')
            print("💼 LINKEDIN BOT: ✅ Easy Apply button found!")
        except:
            print("💼 LINKEDIN BOT: ❌ No Easy Apply button found - skipping this job")
            return False

        try:
            print("💼 LINKEDIN BOT: Locating job description area...")
            job_description_area = self.browser.find_element(By.ID, "job-details")
            print(f"💼 LINKEDIN BOT: ✅ Job description area located: {job_description_area}")
            # self.scroll_slow(job_description_area, end=1600)  # DISABLED - No more job description scrolling!
            # self.scroll_slow(job_description_area, end=1600, step=400, reverse=True)  # DISABLED
            print("💼 LINKEDIN BOT: 🚫 Job description scrolling disabled for better viewing experience")
        except:
            print("💼 LINKEDIN BOT: ⚠️ Could not locate job description area")
            pass

        print("💼 LINKEDIN BOT: 🚀 Clicking Easy Apply button to start application...")
        easy_apply_button.click()
        print("💼 LINKEDIN BOT: ✅ Easy Apply button clicked - application modal should be opening...")

        button_text = ""
        submit_application_text = 'submit application'
        step_count = 0
        
        print("💼 LINKEDIN BOT: 📝 Starting application form completion process...")
        
        while submit_application_text not in button_text.lower():
            step_count += 1
            print(f"💼 LINKEDIN BOT: 📋 Processing application step {step_count}...")
            
            try:
                print("💼 LINKEDIN BOT: 🔄 Filling out current form section...")
                self.fill_up()
                print("💼 LINKEDIN BOT: ✅ Form section completed successfully")
                
                print("💼 LINKEDIN BOT: 🔍 Looking for next/submit button...")
                next_button = self.browser.find_element(By.CLASS_NAME, "artdeco-button--primary")
                button_text = next_button.text.lower()
                print(f"💼 LINKEDIN BOT: 🔘 Found button with text: '{next_button.text}'")
                
                if submit_application_text in button_text:
                    print("💼 LINKEDIN BOT: 🎉 SUBMIT BUTTON FOUND! Preparing to submit application...")
                    try:
                        print("💼 LINKEDIN BOT: 🚫 Attempting to unfollow company...")
                        self.unfollow()
                        print("💼 LINKEDIN BOT: ✅ Successfully unfollowed company")
                    except:
                        print("💼 LINKEDIN BOT: ⚠️ Failed to unfollow company (continuing anyway)")
                        
                print(f"💼 LINKEDIN BOT: ⏱️ Applying human-like delay before clicking...")
                time.sleep(random.uniform(1.5, 2.5))
                
                print(f"💼 LINKEDIN BOT: 🖱️ Clicking '{next_button.text}' button...")
                next_button.click()
                print(f"💼 LINKEDIN BOT: ✅ Button clicked successfully")
                
                print("💼 LINKEDIN BOT: ⏳ Waiting for page response...")
                time.sleep(random.uniform(3.0, 5.0))

                # Newer error handling
                print("💼 LINKEDIN BOT: 🔍 Checking for application errors...")
                error_messages = [
                    'enter a valid',
                    'enter a decimal',
                    'Enter a whole number'
                    'Enter a whole number between 0 and 99',
                    'file is required',
                    'whole number',
                    'make a selection',
                    'select checkbox to proceed',
                    'saisissez un numéro',
                    '请输入whole编号',
                    '请输入decimal编号',
                    '长度超过 0.0',
                    'Numéro de téléphone',
                    'Introduce un número de whole entre',
                    'Inserisci un numero whole compreso',
                    'Preguntas adicionales',
                    'Insira um um número',
                    'Cuántos años'
                    'use the format',
                    'A file is required',
                    '请选择',
                    '请 选 择',
                    'Inserisci',
                    'wholenummer',
                    'Wpisz liczb',
                    'zakresu od',
                    'tussen'
                ]

                if any(error in self.browser.page_source.lower() for error in error_messages):
                    print("💼 LINKEDIN BOT: ❌ CRITICAL ERROR: Failed answering required questions or uploading required files")
                    raise Exception("Failed answering required questions or uploading required files.")
                else:
                    print("💼 LINKEDIN BOT: ✅ No application errors detected - continuing...")
                    
            except:
                print("💼 LINKEDIN BOT: ❌ FATAL ERROR: Exception occurred during application process")
                import traceback
                traceback.print_exc()
                
                print("💼 LINKEDIN BOT: 🚨 Attempting to close application modal...")
                try:
                    self.browser.find_element(By.CLASS_NAME, 'artdeco-modal__dismiss').click()
                    print("💼 LINKEDIN BOT: ✅ Modal dismiss button clicked")
                    time.sleep(random.uniform(3, 5))
                    
                    print("💼 LINKEDIN BOT: 🚨 Confirming modal dismissal...")
                    self.browser.find_elements(By.CLASS_NAME, 'artdeco-modal__confirm-dialog-btn')[0].click()
                    print("💼 LINKEDIN BOT: ✅ Modal dismissal confirmed")
                    time.sleep(random.uniform(3, 5))
                except Exception as modal_error:
                    print(f"💼 LINKEDIN BOT: ⚠️ Error closing modal: {modal_error}")
                    
                raise Exception("Failed to apply to job!")

        print("💼 LINKEDIN BOT: 🎉 APPLICATION SUBMITTED SUCCESSFULLY!")
        closed_notification = False
        print("💼 LINKEDIN BOT: 🧹 Cleaning up notifications and modals...")
        HumanBehaviorSimulator.human_delay(2, 4)  # Natural delay before closing notifications
        
        try:
            print("💼 LINKEDIN BOT: 🚫 Dismissing application modal...")
            dismiss_button = self.browser.find_element(By.CLASS_NAME, 'artdeco-modal__dismiss')
            HumanBehaviorSimulator.human_click(self.browser, dismiss_button)
            print("💼 LINKEDIN BOT: ✅ Application modal dismissed")
            closed_notification = True
        except:
            print("💼 LINKEDIN BOT: ⚠️ No modal dismiss button found")
            pass
        try:
            print("💼 LINKEDIN BOT: 🚫 Dismissing toast notification...")
            toast_dismiss = self.browser.find_element(By.CLASS_NAME, 'artdeco-toast-item__dismiss')
            HumanBehaviorSimulator.human_click(self.browser, toast_dismiss)
            print("💼 LINKEDIN BOT: ✅ Toast notification dismissed")
            closed_notification = True
        except:
            print("💼 LINKEDIN BOT: ⚠️ No toast notification found")
            pass
            
        try:
            print("💼 LINKEDIN BOT: 💾 Looking for save application button...")
            save_button = self.browser.find_element(By.CSS_SELECTOR, 'button[data-control-name="save_application_btn"]')
            HumanBehaviorSimulator.human_click(self.browser, save_button)
            print("💼 LINKEDIN BOT: ✅ Save application button clicked")
            closed_notification = True
        except:
            print("💼 LINKEDIN BOT: ⚠️ No save application button found")
            pass

        print("💼 LINKEDIN BOT: ⏳ Final cleanup delay...")
        HumanBehaviorSimulator.human_delay(2, 4)  # Natural delay after closing

        if closed_notification is False:
            print("💼 LINKEDIN BOT: ❌ ERROR: Could not close the applied confirmation window!")
            raise Exception("Could not close the applied confirmation window!")

        print("💼 LINKEDIN BOT: 🎉✅ JOB APPLICATION PROCESS COMPLETED SUCCESSFULLY! 🎉✅")
        return True

    def home_address(self, form):
        print("Trying to fill up home address fields")
        try:
            groups = form.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping')
            if len(groups) > 0:
                for group in groups:
                    lb = group.find_element(By.TAG_NAME, 'label').text.lower()
                    input_field = group.find_element(By.TAG_NAME, 'input')
                    if 'street' in lb:
                        self.enter_text(input_field, self.personal_info['Street address'])
                    elif 'city' in lb:
                        self.enter_text(input_field, self.personal_info['City'])
                        time.sleep(3)
                        input_field.send_keys(Keys.DOWN)
                        input_field.send_keys(Keys.RETURN)
                    elif 'zip' in lb or 'zip / postal code' in lb or 'postal' in lb:
                        self.enter_text(input_field, self.personal_info['Zip'])
                    elif 'state' in lb or 'province' in lb:
                        self.enter_text(input_field, self.personal_info['State'])
                    else:
                        pass
        except:
            pass

    def get_answer(self, question):
        if self.checkboxes[question]:
            return 'yes'
        else:
            return 'no'

    def additional_questions(self, form):
        print("Trying to fill up additional questions")

        questions = form.find_elements(By.CLASS_NAME, 'fb-dash-form-element')
        for question in questions:
            try:
                # Radio check
                radio_fieldset = question.find_element(By.TAG_NAME, 'fieldset')
                question_span = radio_fieldset.find_element(By.CLASS_NAME, 'fb-dash-form-element__label').find_elements(By.TAG_NAME, 'span')[0]
                radio_text = question_span.text.lower()
                print(f"Radio question text: {radio_text}")

                radio_labels = radio_fieldset.find_elements(By.TAG_NAME, 'label')
                radio_options = [(i, text.text.lower()) for i, text in enumerate(radio_labels)]
                print(f"radio options: {[opt[1] for opt in radio_options]}")
                
                if len(radio_options) == 0:
                    raise Exception("No radio options found in question")

                answer = None

                # Try to determine answer using existing logic - ALWAYS SAY YES for critical questions
                application_critical_keywords = [
                    'willing', 'able', 'authorized', 'eligible', 'available', 'interested',
                    'commit', 'relocate', 'travel', 'work', 'start', 'notice', 'salary',
                    'compensation', 'experience', 'qualified', 'meet', 'requirement'
                ]
                
                # Check if this is an application-critical question
                is_critical = any(keyword in radio_text.lower() for keyword in application_critical_keywords)
                
                if is_critical:
                    # For critical questions, always choose the positive option
                    positive_keywords = ['yes', 'willing', 'able', 'authorized', 'eligible', 'available', 'interested']
                    answer = next((option for option in radio_options if
                                   any(pos_keyword in option[1].lower() for pos_keyword in positive_keywords)), None)
                    if not answer:
                        # If no clear positive option, choose first option
                        answer = radio_options[0] if radio_options else None
                    print(f"Critical question detected - choosing positive answer: {answer[1] if answer else 'None'}")
                
                elif 'driver\'s licence' in radio_text or 'driver\'s license' in radio_text:
                    answer = self.get_answer('driversLicence')
                elif any(keyword in radio_text.lower() for keyword in
                         [
                             'Aboriginal', 'native', 'indigenous', 'tribe', 'first nations',
                             'native american', 'native hawaiian', 'inuit', 'metis', 'maori',
                             'aborigine', 'ancestral', 'native peoples', 'original people',
                             'first people', 'gender', 'race', 'disability', 'latino', 'torres',
                             'do you identify'
                         ]):
                    negative_keywords = ['prefer', 'decline', 'don\'t', 'specified', 'none', 'no']
                    answer = next((option for option in radio_options if
                                   any(neg_keyword in option[1].lower() for neg_keyword in negative_keywords)), None)

                elif 'assessment' in radio_text:
                    answer = self.get_answer("assessment")

                elif 'clearance' in radio_text:
                    answer = self.get_answer("securityClearance")

                elif 'north korea' in radio_text:
                    answer = 'no'

                elif 'previously employ' in radio_text or 'previous employ' in radio_text:
                    answer = 'no'

                elif 'authorized' in radio_text or 'authorised' in radio_text or 'legally' in radio_text:
                    answer = self.get_answer('legallyAuthorized')

                elif any(keyword in radio_text.lower() for keyword in
                         ['certified', 'certificate', 'cpa', 'chartered accountant', 'qualification']):
                    answer = self.get_answer('certifiedProfessional')

                elif 'urgent' in radio_text:
                    answer = self.get_answer('urgentFill')

                elif 'commut' in radio_text or 'on-site' in radio_text or 'hybrid' in radio_text or 'onsite' in radio_text:
                    answer = self.get_answer('commute')

                elif 'remote' in radio_text:
                    answer = self.get_answer('remote')

                elif 'background check' in radio_text:
                    answer = self.get_answer('backgroundCheck')

                elif 'drug test' in radio_text:
                    answer = self.get_answer('drugTest')

                elif 'currently living' in radio_text or 'currently reside' in radio_text or 'right to live' in radio_text:
                    answer = self.get_answer('residency')

                elif 'level of education' in radio_text:
                    for degree in self.checkboxes['degreeCompleted']:
                        if degree.lower() in radio_text:
                            answer = "yes"
                            break

                elif 'experience' in radio_text:
                    if self.experience_default > 0:
                        answer = 'yes'
                    else:
                        for experience in self.experience:
                            if experience.lower() in radio_text:
                                answer = "yes"
                                break

                elif 'data retention' in radio_text:
                    answer = 'no'

                elif 'sponsor' in radio_text or 'visa' in radio_text or 'h-1b' in radio_text or 'employment authorization' in radio_text:
                    answer = self.get_answer('requireVisa')
                    print(f"Sponsorship radio question - requireVisa: {answer}")
                    # For US citizens, we should always answer "No" to sponsorship questions
                    if answer == 'no':  # requireVisa is false for US citizens
                        # Look for "No" options first
                        answer = 'no'
                    else:  # requireVisa is true
                        # Look for "Yes" options
                        answer = 'yes'
                
                to_select = None
                if answer is not None:
                    print(f"Choosing answer: {answer}")
                    i = 0
                    for radio in radio_labels:
                        if answer in radio.text.lower():
                            to_select = radio_labels[i]
                            break
                        i += 1
                    if to_select is None:
                        print("Answer not found in radio options")

                if to_select is None:
                    print("No answer determined - using enhanced AI analysis")
                    self.record_unprepared_question("radio", radio_text)

                    # Enhanced AI analysis with better fallback strategy
                    ai_response = self.ai_response_generator.generate_response(
                        f"For this job application question, choose the best answer that would help get the job: {radio_text}",
                        response_type="choice",
                        options=radio_options
                    )
                    if ai_response is not None:
                        to_select = radio_labels[ai_response]
                        print(f"AI selected option {ai_response}: {radio_labels[ai_response].text}")
                    else:
                        # Smart fallback - look for positive options first
                        positive_options = []
                        for i, label in enumerate(radio_labels):
                            if any(word in label.text.lower() for word in ['yes', 'willing', 'able', 'qualified', 'interested', 'available', 'authorized']):
                                positive_options.append((i, label))
                        
                        if positive_options:
                            to_select = positive_options[0][1]  # Choose first positive option
                            print(f"Chose positive fallback: {to_select.text}")
                        else:
                            to_select = radio_labels[0]  # Choose first option if no positive found
                            print(f"Chose first option fallback: {to_select.text}")
                to_select.click()

                if radio_labels:
                    continue
            except Exception as e:
                print("An exception occurred while filling up radio field")

            # Questions check
            try:
                question_text = question.find_element(By.TAG_NAME, 'label').text.lower()
                print( question_text )  # TODO: Put logging behind debug flag

                txt_field_visible = False
                try:
                    txt_field = question.find_element(By.TAG_NAME, 'input')
                    txt_field_visible = True
                except:
                    try:
                        txt_field = question.find_element(By.TAG_NAME, 'textarea')  # TODO: Test textarea
                        txt_field_visible = True
                    except:
                        raise Exception("Could not find textarea or input tag for question")

                if 'numeric' in txt_field.get_attribute('id').lower():
                    # For decimal and integer response fields, the id contains 'numeric' while the type remains 'text' 
                    text_field_type = 'numeric'
                elif 'text' in txt_field.get_attribute('type').lower():
                    text_field_type = 'text'
                else:
                    raise Exception("Could not determine input type of input field!")

                to_enter = ''
                if 'experience' in question_text or 'how many years in' in question_text:
                    no_of_years = None
                    for experience in self.experience:
                        if experience.lower() in question_text:
                            no_of_years = int(self.experience[experience])
                            break
                    if no_of_years is None:
                        self.record_unprepared_question(text_field_type, question_text)
                        no_of_years = int(self.experience_default)
                    if no_of_years < 1:
                        no_of_years = 1  # never answer 0 years
                    to_enter = no_of_years
                    # Log numeric answer
                    self.log_question_answer(question_text, str(no_of_years))

                elif 'grade point average' in question_text:
                    to_enter = self.university_gpa

                elif 'first name' in question_text:
                    to_enter = self.personal_info['First Name']

                elif 'last name' in question_text:
                    to_enter = self.personal_info['Last Name']

                elif 'name' in question_text:
                    to_enter = self.personal_info['First Name'] + " " + self.personal_info['Last Name']

                elif 'pronouns' in question_text:
                    to_enter = self.personal_info['Pronouns']

                elif 'phone' in question_text:
                    to_enter = self.personal_info['Mobile Phone Number']

                elif 'linkedin' in question_text:
                    to_enter = self.personal_info['Linkedin']

                elif 'message to hiring' in question_text or 'cover letter' in question_text:
                    to_enter = self.personal_info['MessageToManager']

                elif 'website' in question_text or 'github' in question_text or 'portfolio' in question_text:
                    to_enter = self.personal_info['Website']

                elif 'notice' in question_text or 'weeks' in question_text:
                    if text_field_type == 'numeric':
                        to_enter = int(self.notice_period)
                    else:
                        to_enter = str(self.notice_period)

                elif 'salary' in question_text or 'expectation' in question_text or 'compensation' in question_text or 'CTC' in question_text:
                    if text_field_type == 'numeric':
                        to_enter = int(self.salary_minimum)
                    else:
                        to_enter = float(self.salary_minimum)
                    self.record_unprepared_question(text_field_type, question_text)

                # Enhanced AI response with job-focused prompts
                if text_field_type == 'numeric':
                    if not isinstance(to_enter, (int, float)):
                        print(f"Using AI for numeric question: {question_text[:50]}...")
                        ai_response = self.ai_response_generator.generate_response(
                            f"For this job application, provide a realistic numeric answer that would help get the job: {question_text}",
                            response_type="numeric"
                        )
                        to_enter = ai_response if ai_response is not None else 0
                        print(f"AI numeric response: {to_enter}")
                elif to_enter == '':
                    print(f"Using AI for text question: {question_text[:50]}...")
                    ai_response = self.ai_response_generator.generate_response(
                        f"For this job application, provide a professional answer that would help get the job: {question_text}",
                        response_type="text"
                    )
                    to_enter = ai_response if ai_response is not None else "Yes, I am interested and qualified for this position."
                    print(f"AI text response: {to_enter[:50]}...")

                self.enter_text(txt_field, to_enter)
                continue
            except:
                print("An exception occurred while filling up text field")  # TODO: Put logging behind debug flag

            # Date Check
            try:
                date_picker = question.find_element(By.CLASS_NAME, 'artdeco-datepicker__input ')
                date_picker.clear()
                date_picker.send_keys(date.today().strftime("%m/%d/%y"))
                time.sleep(3)
                date_picker.send_keys(Keys.RETURN)
                time.sleep(2)
                continue
            except:
                print("An exception occurred while filling up date picker field")  # TODO: Put logging behind debug flag

            # Dropdown check
            try:
                question_text = question.find_element(By.TAG_NAME, 'label').text.lower()
                print(f"Dropdown question text: {question_text}")  # TODO: Put logging behind debug flag
                dropdown_field = question.find_element(By.TAG_NAME, 'select')

                select = Select(dropdown_field)
                options = [options.text for options in select.options]
                print(f"Dropdown options: {options}")  # TODO: Put logging behind debug flag

                if 'proficiency' in question_text:
                    proficiency = "None"
                    for language in self.languages:
                        if language.lower() in question_text:
                            proficiency = self.languages[language]
                            break
                    self.select_dropdown(dropdown_field, proficiency)

                elif 'clearance' in question_text:
                    answer = self.get_answer('securityClearance')

                    choice = ""
                    for option in options:
                        if answer == 'yes':
                            choice = option
                        else:
                            if 'no' in option.lower():
                                choice = option
                    if choice == "":
                        self.record_unprepared_question(text_field_type, question_text)
                    self.select_dropdown(dropdown_field, choice)

                elif 'assessment' in question_text:
                    answer = self.get_answer('assessment')
                    choice = ""
                    for option in options:
                        if answer == 'yes':
                            choice = option
                        else:
                            if 'no' in option.lower():
                                choice = option
                    # if choice == "":
                    #    choice = options[len(options) - 1]
                    self.select_dropdown(dropdown_field, choice)

                elif 'commut' in question_text or 'on-site' in question_text or 'hybrid' in question_text or 'onsite' in question_text:
                    answer = self.get_answer('commute')

                    choice = ""
                    for option in options:
                        if answer == 'yes':
                            choice = option
                        else:
                            if 'no' in option.lower():
                                choice = option
                    # if choice == "":
                    #    choice = options[len(options) - 1]
                    self.select_dropdown(dropdown_field, choice)

                elif 'country code' in question_text:
                    self.select_dropdown(dropdown_field, self.personal_info['Phone Country Code'])

                elif 'north korea' in question_text:
                    choice = ""
                    for option in options:
                        if 'no' in option.lower():
                            choice = option
                    if choice == "":
                        choice = options[len(options) - 1]
                    self.select_dropdown(dropdown_field, choice)

                elif 'previously employed' in question_text or 'previous employment' in question_text:
                    choice = ""
                    for option in options:
                        if 'no' in option.lower():
                            choice = option
                    if choice == "":
                        choice = options[len(options) - 1]
                    self.select_dropdown(dropdown_field, choice)

                elif 'sponsor' in question_text or 'visa' in question_text or 'h-1b' in question_text or 'employment authorization' in question_text:
                    answer = self.get_answer('requireVisa')
                    choice = ""
                    # For US citizens, we should always answer "No" to sponsorship questions
                    if answer == 'no':  # requireVisa is false for US citizens
                        for option in options:
                            if 'no' in option.lower() or 'not' in option.lower() or 'don\'t' in option.lower():
                                choice = option
                                break
                    else:  # requireVisa is true
                        for option in options:
                            if 'yes' in option.lower():
                                choice = option
                                break
                    if choice == "":
                        # Fallback: if no clear "no" option found, choose the last option
                        choice = options[len(options) - 1]
                    print(f"Sponsorship question - requireVisa: {answer}, selected: {choice}")
                    self.select_dropdown(dropdown_field, choice)

                elif 'above 18' in question_text.lower():  # Check for "above 18" in the question text
                    choice = ""
                    for option in options:
                        if 'yes' in option.lower():  # Select 'yes' option
                            choice = option
                    if choice == "":
                        choice = options[0]  # Default to the first option if 'yes' is not found
                    self.select_dropdown(dropdown_field, choice)

                elif 'currently living' in question_text or 'currently reside' in question_text:
                    answer = self.get_answer('residency')
                    choice = ""
                    for option in options:
                        if answer == 'yes':
                            choice = option
                        else:
                            if 'no' in option.lower():
                                choice = option
                    if choice == "":
                        choice = options[len(options) - 1]
                    self.select_dropdown(dropdown_field, choice)

                elif 'authorized' in question_text or 'authorised' in question_text:
                    answer = self.get_answer('legallyAuthorized')
                    choice = ""
                    for option in options:
                        if answer == 'yes':
                            # find some common words
                            choice = option
                        else:
                            if 'no' in option.lower():
                                choice = option
                    if choice == "":
                        choice = options[len(options) - 1]
                    self.select_dropdown(dropdown_field, choice)

                elif 'citizenship' in question_text:
                    answer = self.get_answer('legallyAuthorized')
                    choice = ""
                    for option in options:
                        if answer == 'yes':
                            if 'no' in option.lower():
                                choice = option
                    if choice == "":
                        choice = options[len(options) - 1]
                    self.select_dropdown(dropdown_field, choice)

                elif 'clearance' in question_text:
                    answer = self.get_answer('clearance')
                    choice = ""
                    for option in options:
                        if answer == 'yes':
                            choice = option
                        else:
                            if 'no' in option.lower():
                                choice = option
                    if choice == "":
                        choice = options[len(options) - 1]

                    self.select_dropdown(dropdown_field, choice)

                elif any(keyword in question_text.lower() for keyword in
                         [
                             'aboriginal', 'native', 'indigenous', 'tribe', 'first nations',
                             'native american', 'native hawaiian', 'inuit', 'metis', 'maori',
                             'aborigine', 'ancestral', 'native peoples', 'original people',
                             'first people', 'gender', 'race', 'disability', 'latino'
                         ]):
                    negative_keywords = ['prefer', 'decline', 'don\'t', 'specified', 'none']

                    choice = ""
                    choice = next((option for options in option.lower() if
                               any(neg_keyword in option.lower() for neg_keyword in negative_keywords)), None)

                    self.select_dropdown(dropdown_field, choice)

                elif 'email' in question_text:
                    continue  # assume email address is filled in properly by default

                elif 'experience' in question_text or 'understanding' in question_text or 'familiar' in question_text or 'comfortable' in question_text or 'able to' in question_text:
                    answer = 'no'
                    if self.experience_default > 0:
                        answer = 'yes'
                    else:
                        for experience in self.experience:
                            if experience.lower() in question_text and self.experience[experience] > 0:
                                answer = 'yes'
                                break
                    if answer == 'no':
                        # record unlisted experience as unprepared questions
                        self.record_unprepared_question("dropdown", question_text)

                    choice = ""
                    for option in options:
                        if answer in option.lower():
                            choice = option
                    if choice == "":
                        choice = options[len(options) - 1]
                    self.select_dropdown(dropdown_field, choice)

                else:
                    print(f"Unhandled dropdown question: {question_text[:50]}... - using enhanced AI")
                    self.record_unprepared_question("dropdown", question_text)

                    # Enhanced AI with job-focused prompt
                    choices = [(i, option) for i, option in enumerate(options)]
                    ai_response = self.ai_response_generator.generate_response(
                        f"For this job application dropdown, choose the best option that would help get the job: {question_text}",
                        response_type="choice",
                        options=choices
                    )
                    if ai_response is not None:
                        choice = options[ai_response]
                        print(f"AI selected dropdown option: {choice}")
                    else:
                        # Smart fallback - look for positive options first
                        choice = ""
                        positive_options = [opt for opt in options if any(word in opt.lower() 
                                           for word in ['yes', 'willing', 'able', 'qualified', 'interested', 'available'])]
                        if positive_options:
                            choice = positive_options[0]
                            print(f"Chose positive dropdown option: {choice}")
                        else:
                            for option in options:
                                if 'yes' in option.lower():
                                    choice = option
                                    break
                            if not choice:
                                choice = options[0] if options else ""

                    print(f"Selected option: {choice}")
                    self.select_dropdown(dropdown_field, choice)
                    # Log dropdown answer
                    self.log_question_answer(question_text, choice)
                continue
            except:
                print("An exception occurred while filling up dropdown field")  # TODO: Put logging behind debug flag

            # Checkbox check for agreeing to terms and service
            try:
                clickable_checkbox = question.find_element(By.TAG_NAME, 'label')
                clickable_checkbox.click()
            except:
                print("An exception occurred while filling up checkbox field")  # TODO: Put logging behind debug flag

    def unfollow(self):
        try:
            follow_checkbox = self.browser.find_element(By.XPATH,
                                                        "//label[contains(.,\'to stay up to date with their page.\')]").click()
            follow_checkbox.click()
        except:
            pass

    def send_resume(self):
        print("Trying to send resume")
        try:
            file_upload_elements = (By.CSS_SELECTOR, "input[name='file']")
            if len(self.browser.find_elements(file_upload_elements[0], file_upload_elements[1])) > 0:
                input_buttons = self.browser.find_elements(file_upload_elements[0], file_upload_elements[1])
                if len(input_buttons) == 0:
                    raise Exception("No input elements found in element")
                for upload_button in input_buttons:
                    upload_type = upload_button.find_element(By.XPATH, "..").find_element(By.XPATH,
                                                                                          "preceding-sibling::*")
                    if 'resume' in upload_type.text.lower():
                        upload_button.send_keys(self.resume_dir)
                    elif 'cover' in upload_type.text.lower():
                        if self.cover_letter_dir != '':
                            upload_button.send_keys(self.cover_letter_dir)
                        elif 'required' in upload_type.text.lower():
                            upload_button.send_keys(self.resume_dir)
        except:
            print("Failed to upload resume or cover letter!")
            pass

    def enter_text(self, element, text):
        element.clear()
        element.send_keys(text)

    def select_dropdown(self, element, text):
        select = Select(element)
        select.select_by_visible_text(text)

    # Radio Select
    def radio_select(self, element, label_text, clickLast=False):
        label = element.find_element(By.TAG_NAME, 'label')
        if label_text in label.text.lower() or clickLast == True:
            label.click()

    # Contact info fill-up
    def contact_info(self, form):
        print("Trying to fill up contact info fields")
        try:
            # First, handle any explicit email inputs or selects
            email_elements = form.find_elements(By.XPATH, ".//input[contains(translate(@id,'EMAIL','email'),'email') or contains(translate(@name,'EMAIL','email'),'email') or contains(translate(@aria-label,'EMAIL','email')] | .//select[contains(translate(@id,'EMAIL','email'),'email') or contains(translate(@name,'EMAIL','email'),'email') or contains(translate(@aria-label,'EMAIL','email')]")
            for em in email_elements:
                tag = em.tag_name.lower()
                try:
                    if tag == 'input':
                        self.enter_text(em, self.alt_email)
                    elif tag == 'select':
                        try:
                            Select(em).select_by_visible_text(self.alt_email)
                        except Exception:
                            # If the email isn't present, try typing it in (some selects allow custom)
                            em.click()
                            em.send_keys(self.alt_email)
                    print("Filled alternate email")
                except Exception as e:
                    print(f"Could not set alternate email: {e}")

            # Continue with existing label-based processing for phone etc.
        except Exception as e:
            print(f"Error locating email fields: {e}")

        frm_el = form.find_elements(By.TAG_NAME, 'label')
        if len(frm_el) == 0:
            return

        for el in frm_el:
            text = el.text.lower()
            if 'email address' in text:
                # already handled above but keep guard
                continue
            if 'phone number' in text:
                try:
                    country_code_picker = el.find_element(By.XPATH,
                                                          '//select[contains(@id,"phoneNumber")][contains(@id,"country")]')
                    self.select_dropdown(country_code_picker, self.personal_info['Phone Country Code'])
                except Exception as e:
                    print("Country code " + self.personal_info[
                        'Phone Country Code'] + " not found. Please make sure it is same as in LinkedIn.")
                    print(e)
                try:
                    phone_number_field = el.find_element(By.XPATH,
                                                         '//input[contains(@id,"phoneNumber")][contains(@id,"nationalNumber")]')
                    self.enter_text(phone_number_field, self.personal_info['Mobile Phone Number'])
                except Exception as e:
                    print("Could not enter phone number:")
                    print(e)

    def fill_up(self):
        try:
            easy_apply_modal_content = self.browser.find_element(By.CLASS_NAME, "jobs-easy-apply-modal__content")
            form = easy_apply_modal_content.find_element(By.TAG_NAME, 'form')
            try:
                label = form.find_element(By.TAG_NAME, 'h3').text.lower()
                if 'home address' in label:
                    self.home_address(form)
                elif 'contact info' in label:
                    self.contact_info(form)
                elif 'resume' in label:
                    self.send_resume()
                else:
                    self.additional_questions(form)
            except Exception as e:
                print("An exception occurred while filling up the form:")
                print(e)
        except:
            print("An exception occurred while searching for form in modal")

    def write_to_file(self, company, job_title, link, location, search_location):
        print("💾 LINKEDIN BOT: 📝 SAVING APPLICATION DATA TO FILE...")
        print(f"💾 LINKEDIN BOT: 🏢 Company: {company}")
        print(f"💾 LINKEDIN BOT: 💼 Job Title: {job_title}")
        print(f"💾 LINKEDIN BOT: 🔗 Job URL: {link}")
        print(f"💾 LINKEDIN BOT: 📍 Job Location: {location}")
        print(f"💾 LINKEDIN BOT: 🎯 Search Location: {search_location}")
        print(f"💾 LINKEDIN BOT: ⏰ Timestamp: {datetime.now()}")
        
        to_write = [company, job_title, link, location, search_location, datetime.now()]
        file_path = self.file_name + ".csv"
        
        print(f"💾 LINKEDIN BOT: 📂 Writing to file: {file_path}")

        try:
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(to_write)
            print(f"💾 LINKEDIN BOT: ✅ Successfully updated {file_path} with application data")
            print(f"💾 LINKEDIN BOT: 🎉 APPLICATION LOGGED TO CSV FILE! 🎉")
        except Exception as e:
            print(f"💾 LINKEDIN BOT: ❌ ERROR: Failed to write to file {file_path}: {e}")
            raise e

    def record_unprepared_question(self, answer_type, question_text):
        to_write = [answer_type, question_text]
        file_path = self.unprepared_questions_file_name + ".csv"

        try:
            with open(file_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(to_write)
                print(f'Updated {file_path} with {to_write}.')
        except:
            print(
                "Special characters in questions are not allowed. Failed to update unprepared questions log.")
            print(question_text)

    def scroll_slow(self, scrollable_element, start=0, end=3600, step=100, reverse=False):
        # Disabled automatic scrolling for better user experience when watching
        print("Scroll disabled for visible browser mode")
        return

    def avoid_lock(self):
        if self.disable_lock:
            return

        # Skip pyautogui operations if not available (headless environment)
        if pyautogui is None:
            print("Warning: pyautogui not available - skipping lock avoidance")
            return

        pyautogui.keyDown('ctrl')
        pyautogui.press('esc')
        pyautogui.keyUp('ctrl')
        time.sleep(1.0)
        pyautogui.press('esc')

    def get_base_search_url(self, parameters):
        remote_url = ""
        lessthanTenApplicants_url = ""
        newestPostingsFirst_url = ""

        if parameters.get('remote'):
            remote_url = "&f_WT=2"
        else:
            remote_url = ""
            # TO DO: Others &f_WT= options { WT=1 onsite, WT=2 remote, WT=3 hybrid, f_WT=1%2C2%2C3 }

        if parameters['lessthanTenApplicants']:
            lessthanTenApplicants_url = "&f_EA=true"

        if parameters['newestPostingsFirst']:
            newestPostingsFirst_url += "&sortBy=DD"

        level = 1
        experience_level = parameters.get('experienceLevel', [])
        experience_url = "f_E="
        for key in experience_level.keys():
            if experience_level[key]:
                experience_url += "%2C" + str(level)
            level += 1

        distance_url = "?distance=" + str(parameters['distance'])

        job_types_url = "f_JT="
        job_types = parameters.get('jobTypes', [])
        # job_types = parameters.get('experienceLevel', [])
        for key in job_types:
            if job_types[key]:
                job_types_url += "%2C" + key[0].upper()

        date_url = ""
        dates = {"all time": "", "month": "&f_TPR=r2592000", "week": "&f_TPR=r604800", "24 hours": "&f_TPR=r86400"}
        date_table = parameters.get('date', [])
        for key in date_table.keys():
            if date_table[key]:
                date_url = dates[key]
                break

        easy_apply_url = "&f_AL=true"

        extra_search_terms = [distance_url, remote_url, lessthanTenApplicants_url, newestPostingsFirst_url, job_types_url, experience_url]
        extra_search_terms_str = '&'.join(
            term for term in extra_search_terms if len(term) > 0) + easy_apply_url + date_url

        return extra_search_terms_str

    def next_job_page(self, position, location, job_page):
        self.browser.get("https://www.linkedin.com/jobs/search/" + self.base_search_url +
                         "&keywords=" + position + location + "&start=" + str(job_page * 25))
        
        # Re-apply scroll prevention on new page
        self._re_disable_scrolling()
        
        # Ensure Chrome window is visible
        self._ensure_chrome_visible()
        
        self.avoid_lock()

    def log_question_answer(self, question_text, answer_text):
        """Save Q&A for later review"""
        try:
            with open("qa_log.csv", "a", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now(), question_text, answer_text])
        except Exception as e:
            if self.debug:
                print(f"Could not log QA: {e}")
