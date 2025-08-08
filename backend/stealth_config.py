#!/usr/bin/env python3
"""
Advanced Stealth Configuration for LinkedIn Bot
Implements comprehensive detection evasion techniques
"""

import random
import time
import json
from typing import Dict, List, Optional
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver

class AdvancedStealthConfig:
    """Advanced stealth configuration to evade LinkedIn bot detection"""
    
    # Comprehensive list of realistic user agents
    USER_AGENTS = [
        # Chrome on macOS (most common for professionals)
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        
        # Edge on Windows (common in corporate environments)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        
        # Safari on macOS (some professionals prefer Safari)
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    ]
    
    # Screen resolutions common among professionals
    SCREEN_SIZES = [
        {"width": 1920, "height": 1080},  # Most common
        {"width": 2560, "height": 1440},  # High-end monitors
        {"width": 1440, "height": 900},   # MacBook Air
        {"width": 1680, "height": 1050},  # Common external monitor
        {"width": 3840, "height": 2160},  # 4K (less common but realistic)
        {"width": 2880, "height": 1800},  # MacBook Pro Retina
    ]
    
    # Professional timezones (where LinkedIn users are most active)
    TIMEZONES = [
        "America/New_York",      # EST - Business hub
        "America/Chicago",       # CST
        "America/Denver",        # MST  
        "America/Los_Angeles",   # PST - Tech hub
        "America/Toronto",       # Eastern Canada
        "Europe/London",         # GMT - Financial center
        "Europe/Amsterdam",      # CET
        "Europe/Berlin",         # CET
        "Australia/Sydney",      # AEDT
    ]
    
    # Languages common among professionals
    LANGUAGES = [
        "en-US,en;q=0.9",
        "en-US,en;q=0.9,es;q=0.8",
        "en-GB,en;q=0.9",
        "en-US,en;q=0.9,fr;q=0.8",
        "en-US,en;q=0.9,de;q=0.8",
    ]

    @staticmethod
    def create_stealth_options(user_data_dir: str) -> Options:
        """Create Chrome options with maximum stealth configuration"""
        options = Options()
        
        # Basic stealth options
        user_agent = random.choice(AdvancedStealthConfig.USER_AGENTS)
        screen_size = random.choice(AdvancedStealthConfig.SCREEN_SIZES)
        language = random.choice(AdvancedStealthConfig.LANGUAGES)
        
        # Core arguments for stealth
        stealth_args = [
            f"--user-agent={user_agent}",
            f"--user-data-dir={user_data_dir}",
            f"--window-size={screen_size['width']},{screen_size['height']}",
            
            # Force fresh session arguments (no cache, no saved data)
            "--disable-extensions-file-access-check",
            "--disable-extensions-http-throttling",
            "--disable-component-extensions-with-background-pages",
            
            # Disable automation indicators
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-gpu",
            
            # Hide webdriver property
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-extensions-file-access-check",
            "--disable-extensions-http-throttling",
            
            # Prevent detection through browser features
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-dev-tools",
            "--disable-extensions",
            "--disable-features=TranslateUI",
            "--disable-hang-monitor",
            "--disable-ipc-flooding-protection",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-renderer-backgrounding",
            "--disable-sync",
            "--force-color-profile=srgb",
            "--metrics-recording-only",
            "--no-first-run",
            "--safebrowsing-disable-auto-update",
            "--enable-automation",
            "--password-store=basic",
            "--use-mock-keychain",
            
            # Memory and performance
            "--memory-pressure-off",
            "--max_old_space_size=4096",
            
            # Network and security
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
            "--ignore-certificate-errors-spki-list",
            "--disable-features=VizDisplayCompositor",
            
            # Language and locale
            f"--lang={language.split(',')[0]}",
            f"--accept-lang={language}",
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
            
        # Advanced preferences to avoid fingerprinting
        prefs = {
            # Disable notifications
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1,
            
            # Language settings
            "intl.accept_languages": language,
            
            # Disable password manager
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            
            # Disable extensions
            "extensions.ui.developer_mode": False,
            
            # Geolocation (randomize)
            "profile.default_content_setting_values.geolocation": 2,
            
            # Media settings
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2,
            
            # WebRTC settings to prevent IP leaks
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False,
        }
        
        options.add_experimental_option("prefs", prefs)
        
        # Exclude automation switches
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Add debug port for advanced control
        options.add_argument("--remote-debugging-port=9222")
        
        return options

    @staticmethod
    def create_fresh_session_options() -> Options:
        """Create browser options for completely fresh sessions (no saved data)"""
        import tempfile
        import uuid
        
        # Create temporary directory for this session only
        temp_dir = tempfile.mkdtemp(prefix=f"linkedin_ultra_fresh_{uuid.uuid4().hex[:8]}_")
        
        options = Options()
        
        # Basic stealth options with maximum randomization
        user_agent = random.choice(AdvancedStealthConfig.USER_AGENTS)
        screen_size = random.choice(AdvancedStealthConfig.SCREEN_SIZES)
        language = random.choice(AdvancedStealthConfig.LANGUAGES)
        
        # Ultra-fresh session arguments
        fresh_args = [
            f"--user-agent={user_agent}",
            f"--user-data-dir={temp_dir}",
            f"--window-size={screen_size['width']},{screen_size['height']}",
            
            # Disable ALL persistence and caching
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-sync",
            "--disable-default-apps",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-client-side-phishing-detection",
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-domain-reliability",
            "--disable-features=VizDisplayCompositor",
            
            # Memory and cache settings for fresh sessions
            "--memory-pressure-off",
            "--aggressive-cache-discard",
            "--disable-back-forward-cache",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-gpu",
            
            # Network settings
            "--disable-web-security",
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
            "--ignore-certificate-errors-spki-list",
            
            # Language and locale
            f"--lang={language.split(',')[0]}",
            f"--accept-lang={language}",
            
            # Startup settings
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
        ]
        
        for arg in fresh_args:
            options.add_argument(arg)
            
        # Fresh session preferences (minimal persistence)
        fresh_prefs = {
            # Disable all notifications and popups
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1,
            
            # Language settings
            "intl.accept_languages": language,
            
            # Disable password saving completely
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "autofill.profile_enabled": False,
            "autofill.credit_card_enabled": False,
            
            # Disable extensions and developer features
            "extensions.ui.developer_mode": False,
            
            # Privacy settings
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2,
            
            # Disable all sync and cloud features
            "sync.suppress_start": True,
            "import_autofill_form_data": False,
            "import_bookmarks": False,
            "import_history": False,
            "import_saved_passwords": False,
            "import_search_engine": False,
            
            # Disable background apps and services
            "background_mode.enabled": False,
            "hardware_acceleration_mode.enabled": False,
            
            # WebRTC settings to prevent IP leaks
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False,
        }
        
        options.add_experimental_option("prefs", fresh_prefs)
        
        # Exclude automation switches for fresh sessions
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", [
            "enable-automation",
            "enable-blink-features=AutomationControlled",
            "test-type"
        ])
        
        print(f"🧹 Created ultra-fresh browser options with temp directory: {temp_dir}")
        
        # Schedule cleanup
        import atexit
        def cleanup_ultra_fresh():
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                print(f"🗑️ Ultra-fresh session cleaned up: {temp_dir}")
            except:
                pass
        atexit.register(cleanup_ultra_fresh)
        
        return options

    @staticmethod
    def apply_post_launch_stealth(driver: webdriver.Chrome) -> None:
        """Apply stealth measures after browser launch"""
        
        # Remove webdriver property (with error handling)
        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except:
            # If property is protected, try alternative method
            try:
                driver.execute_script("delete navigator.webdriver")
            except:
                # If both fail, try setting to undefined
                try:
                    driver.execute_script("navigator.webdriver = undefined")
                except:
                    pass  # Skip if all methods fail
        
        # Modify navigator properties to appear more human
        try:
            driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
        except:
            pass
        
        # Override plugin array to look more realistic
        try:
            driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        }
                    ]
                });
            """)
        except:
            pass
        
        # Randomize screen properties
        try:
            screen_size = random.choice(AdvancedStealthConfig.SCREEN_SIZES)
            driver.execute_script(f"""
                Object.defineProperty(screen, 'width', {{get: () => {screen_size['width']}}});
                Object.defineProperty(screen, 'height', {{get: () => {screen_size['height']}}});
                Object.defineProperty(screen, 'availWidth', {{get: () => {screen_size['width']}}});
                Object.defineProperty(screen, 'availHeight', {{get: () => {screen_size['height'] - 40}}});
            """)
        except:
            pass
        
        # Spoof timezone
        try:
            timezone = random.choice(AdvancedStealthConfig.TIMEZONES)
            driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {'timezoneId': timezone})
        except:
            pass
        
        # Randomize permissions (simplified to avoid errors)
        try:
            permissions = ['notifications']  # Simplified to avoid browser context errors
            for permission in permissions:
                state = 'denied'  # Set to denied for privacy
                driver.execute_cdp_cmd('Browser.grantPermissions', {
                    'permissions': [permission]
                })
        except:
            pass

class AdvancedHumanBehavior:
    """Advanced human behavior simulation"""
    
    @staticmethod
    def realistic_mouse_movement(driver: webdriver.Chrome, element) -> None:
        """Simulate realistic mouse movement to element"""
        action = ActionChains(driver)
        
        # Get current mouse position (approximate)
        current_pos = {"x": random.randint(100, 500), "y": random.randint(100, 400)}
        
        # Get target element position
        location = element.location
        size = element.size
        target_x = location['x'] + size['width'] // 2
        target_y = location['y'] + size['height'] // 2
        
        # Calculate path with curve (more human-like)
        steps = random.randint(3, 8)
        for i in range(steps):
            progress = (i + 1) / steps
            
            # Add some curve and randomness
            curve_offset_x = random.randint(-20, 20) * (1 - progress)
            curve_offset_y = random.randint(-15, 15) * (1 - progress)
            
            intermediate_x = current_pos["x"] + (target_x - current_pos["x"]) * progress + curve_offset_x
            intermediate_y = current_pos["y"] + (target_y - current_pos["y"]) * progress + curve_offset_y
            
            action.move_by_offset(
                intermediate_x - current_pos["x"], 
                intermediate_y - current_pos["y"]
            )
            current_pos = {"x": intermediate_x, "y": intermediate_y}
            
            # Small delay between movements
            time.sleep(random.uniform(0.01, 0.05))
        
        # Slight pause before clicking (human hesitation)
        time.sleep(random.uniform(0.1, 0.3))
        action.perform()

    @staticmethod
    def human_typing(element, text: str) -> None:
        """Type text with human-like patterns"""
        # Clear field first
        element.clear()
        time.sleep(random.uniform(0.1, 0.3))
        
        for i, char in enumerate(text):
            element.send_keys(char)
            
            # Variable typing speed
            if char == ' ':
                # Slightly longer pause for spaces
                delay = random.uniform(0.1, 0.2)
            elif char in '.,!?':
                # Pause after punctuation
                delay = random.uniform(0.2, 0.4)
            elif i > 0 and text[i-1:i+1] in ['th', 'he', 'in', 'er', 'an']:
                # Faster for common bigrams
                delay = random.uniform(0.03, 0.08)
            else:
                # Normal typing speed
                delay = random.uniform(0.05, 0.15)
            
            # Occasionally make "typos" and correct them (very human)
            if random.random() < 0.02 and i < len(text) - 1:  # 2% chance
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys('\b')  # Backspace
                time.sleep(random.uniform(0.1, 0.2))
                
            time.sleep(delay)
        
        # Brief pause after typing (review what was typed)
        time.sleep(random.uniform(0.2, 0.6))

    @staticmethod
    def realistic_page_interaction(driver: webdriver.Chrome) -> None:
        """Simulate realistic page interactions"""
        # Random small scrolls (like reading)
        for _ in range(random.randint(1, 3)):
            scroll_amount = random.randint(50, 200)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 1.5))
        
        # Occasionally move mouse randomly (like a human would)
        if random.random() < 0.3:  # 30% chance
            action = ActionChains(driver)
            action.move_by_offset(
                random.randint(-100, 100),
                random.randint(-50, 50)
            )
            action.perform()
            time.sleep(random.uniform(0.2, 0.5))

    @staticmethod
    def professional_reading_pattern(driver: webdriver.Chrome, text_elements: list) -> None:
        """Simulate how professionals read job descriptions"""
        reading_time = 0
        
        for element in text_elements:
            try:
                text_length = len(element.text)
                if text_length > 10:  # Only "read" substantial text
                    # Scroll element into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    
                    # Reading time based on text length (average reading speed: 200-300 wpm)
                    words = text_length / 5  # Approximate words
                    reading_seconds = words / random.uniform(200, 300) * 60
                    reading_seconds = max(0.5, min(reading_seconds, 10))  # Reasonable bounds
                    
                    time.sleep(reading_seconds)
                    reading_time += reading_seconds
                    
                    # Break if we've "read" enough (professionals scan quickly)
                    if reading_time > random.uniform(15, 30):
                        break
                        
            except Exception:
                continue

    @staticmethod
    def advanced_timing_patterns() -> Dict[str, float]:
        """Generate realistic timing patterns based on time of day and user behavior"""
        current_hour = time.localtime().tm_hour
        
        # Different patterns based on time of day
        if 9 <= current_hour <= 11:  # Morning peak productivity
            base_delay = random.uniform(0.8, 1.5)
            interaction_speed = random.uniform(1.2, 2.0)
        elif 14 <= current_hour <= 16:  # Afternoon productivity
            base_delay = random.uniform(1.0, 2.0)
            interaction_speed = random.uniform(1.0, 1.8)
        elif 19 <= current_hour <= 22:  # Evening browsing
            base_delay = random.uniform(1.5, 3.0)
            interaction_speed = random.uniform(0.8, 1.5)
        else:  # Off-peak hours
            base_delay = random.uniform(2.0, 4.0)
            interaction_speed = random.uniform(0.6, 1.2)
        
        return {
            "base_delay": base_delay,
            "interaction_speed": interaction_speed,
            "between_applications": random.uniform(120, 300),  # 2-5 minutes
            "page_reading": random.uniform(5, 15),  # 5-15 seconds
            "form_filling": random.uniform(0.5, 1.5)  # Per field
        }

class StealthLinkedInSession:
    """Manages a stealth LinkedIn session with advanced evasion"""
    
    def __init__(self, user_data_dir: str, fresh_session: bool = False):
        self.user_data_dir = user_data_dir
        self.fresh_session = fresh_session
        self.driver = None
        self.session_start_time = time.time()
        self.actions_performed = 0
        self.timing_profile = AdvancedHumanBehavior.advanced_timing_patterns()
    
    def start_session(self) -> webdriver.Chrome:
        """Start a stealth browser session"""
        if self.fresh_session:
            # Create completely fresh session with temporary directory
            import tempfile
            import uuid
            temp_dir = tempfile.mkdtemp(prefix=f"linkedin_fresh_{uuid.uuid4().hex[:8]}_")
            print(f"🧹 Creating FRESH browser session (no saved cookies/data): {temp_dir}")
            options = AdvancedStealthConfig.create_stealth_options(temp_dir)
            
            # Schedule cleanup of temp directory
            import atexit
            def cleanup_temp():
                try:
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    print(f"🗑️ Cleaned up temporary browser data: {temp_dir}")
                except:
                    pass
            atexit.register(cleanup_temp)
        else:
            # Use persistent user data directory
            options = AdvancedStealthConfig.create_stealth_options(self.user_data_dir)
        
        # Use existing chromedriver
        from selenium.webdriver.chrome.service import Service
        import os
        service = Service(os.path.join(os.getcwd(), "chromedriver"))
        
        try:
            self.driver = webdriver.Chrome(service=service, options=options)
            print("✅ Chrome browser started successfully")
            
            # Wait for browser to be ready
            import time
            time.sleep(2)
            
            # Apply post-launch stealth measures
            print("🔧 Applying stealth measures...")
            AdvancedStealthConfig.apply_post_launch_stealth(self.driver)
            print("✅ Stealth measures applied")
            
            if self.fresh_session:
                print("🥷 FRESH stealth session started - will require login each time")
            else:
                print("🥷 Persistent stealth session started with comprehensive evasion")
            
            return self.driver
            
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            raise
    
    def should_take_break(self) -> bool:
        """Determine if a break should be taken based on realistic patterns"""
        session_duration = time.time() - self.session_start_time
        
        # Take breaks like a real user would
        if session_duration > 1800 and random.random() < 0.3:  # 30 min session, 30% chance
            return True
        elif session_duration > 3600 and random.random() < 0.7:  # 1 hour, 70% chance
            return True
        elif self.actions_performed > 50 and random.random() < 0.2:  # Many actions
            return True
            
        return False
    
    def take_realistic_break(self) -> None:
        """Take a break that mimics real user behavior"""
        break_duration = random.uniform(300, 1200)  # 5-20 minutes
        print(f"🛌 Taking realistic break for {break_duration/60:.1f} minutes")
        
        # During break, occasionally move mouse or scroll (like checking other tabs)
        start_time = time.time()
        while time.time() - start_time < break_duration:
            if random.random() < 0.1:  # 10% chance every loop
                AdvancedHumanBehavior.realistic_page_interaction(self.driver)
            time.sleep(30)  # Check every 30 seconds
    
    def increment_action(self) -> None:
        """Track actions for realistic break timing"""
        self.actions_performed += 1

def create_stealth_browser(fresh_session: bool = True, user_data_dir: str = None) -> 'webdriver.Chrome':
    """
    Convenience function to create a stealth browser with simple options
    
    Args:
        fresh_session: If True, creates completely fresh session (no saved data, requires login)
                      If False, uses persistent session (saves cookies/login)
        user_data_dir: Directory for browser data (only used for persistent sessions)
    
    Returns:
        Chrome WebDriver instance with stealth configuration
    """
    if fresh_session:
        print("🧹 Creating ULTRA-FRESH browser session")
        print("   ✅ No saved cookies or login data")
        print("   ✅ Fresh browser fingerprint")
        print("   ✅ Maximum stealth protection")
        print("   ⚠️  Will require login each time")
        
        # Use the ultra-fresh session options
        from selenium.webdriver.chrome.service import Service
        import os
        
        options = AdvancedStealthConfig.create_fresh_session_options()
        service = Service(os.path.join(os.getcwd(), "chromedriver"))
        
        try:
            driver = webdriver.Chrome(service=service, options=options)
            print("✅ Ultra-fresh browser started successfully")
            
            # Wait for browser to be ready
            import time
            time.sleep(2)
            
            # Apply post-launch stealth
            print("🔧 Applying stealth measures...")
            AdvancedStealthConfig.apply_post_launch_stealth(driver)
            print("✅ Stealth measures applied")
            
            return driver
            
        except Exception as e:
            print(f"❌ Failed to start ultra-fresh browser: {e}")
            if 'driver' in locals():
                try:
                    driver.quit()
                except:
                    pass
            raise
    else:
        print("💾 Creating persistent browser session")
        print("   ✅ Saves login state between runs")
        print("   ⚠️  Less stealth protection")
        print("   ⚠️  May accumulate tracking data")
        
        if user_data_dir is None:
            import os
            user_data_dir = os.path.join(os.getcwd(), "chrome_bot_persistent")
        
        session = StealthLinkedInSession(user_data_dir, fresh_session=False)
        return session.start_session() 