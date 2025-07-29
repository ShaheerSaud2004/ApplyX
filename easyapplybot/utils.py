import os, yaml, random
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from validate_email import validate_email

__all__ = [
    "init_browser",
    "validate_yaml",
]


def init_browser(user_data_dir: Optional[str] = None, headless: bool = False):
    """Return a configured Chrome WebDriver instance.

    Args:
        user_data_dir: Directory for Chrome user data. Defaults to ./chrome_bot.
        headless: Enable headless mode (useful for CI environments).
    """
    browser_options = Options()

    if headless:
        browser_options.add_argument("--headless=new")
        browser_options.add_argument("window-size=1920,1080")

    # -- Browser fingerprint hardening / stealth options
    extra_options = [
        "--disable-blink-features",
        "--no-sandbox",
        "--start-maximized",
        "--disable-extensions",
        "--ignore-certificate-errors",
        "--disable-blink-features=AutomationControlled",
        "--remote-debugging-port=9222",
    ]

    # Custom user-agent to reduce detection surface
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    browser_options.add_argument(f"--user-agent={random.choice(user_agents)}")

    for option in extra_options:
        browser_options.add_argument(option)

    if user_data_dir is None:
        user_data_dir = os.path.join(os.getcwd(), "chrome_bot")
    browser_options.add_argument(f"user-data-dir={user_data_dir}")

    service = Service(os.path.join(os.getcwd(), "chromedriver"))
    driver = webdriver.Chrome(service=service, options=browser_options)
    driver.implicitly_wait(1)
    driver.set_window_position(0, 0)
    try:
        driver.maximize_window()
    except Exception:
        # headless mode or unsupported environment
        pass
    return driver


def validate_yaml(path: str = "config.yaml"):
    """Load and validate the YAML configuration, returning the parsed dict.

    Raises an Exception with a helpful message when validation fails.
    """
    with open(path, "r", encoding="utf-8") as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    mandatory_params = [
        "email",
        "password",
        "disableAntiLock",
        "remote",
        "lessthanTenApplicants",
        "newestPostingsFirst",
        "experienceLevel",
        "jobTypes",
        "date",
        "positions",
        "locations",
        "residentStatus",
        "distance",
        "outputFileDirectory",
        "checkboxes",
        "universityGpa",
        "languages",
        "experience",
        "personalInfo",
        "eeo",
        "uploads",
    ]

    for param in mandatory_params:
        if param not in parameters:
            raise KeyError(f"{param} is not defined in the config.yaml file!")

    # Field-specific validation (mostly unchanged from the original implementation)
    assert validate_email(parameters["email"])
    assert len(str(parameters["password"])) > 0

    assert isinstance(parameters["disableAntiLock"], bool)
    assert isinstance(parameters["remote"], bool)
    assert isinstance(parameters["lessthanTenApplicants"], bool)
    assert isinstance(parameters["newestPostingsFirst"], bool)
    assert isinstance(parameters["residentStatus"], bool)

    experience_level = parameters.get("experienceLevel", {})
    assert any(experience_level.values())

    job_types = parameters.get("jobTypes", {})
    assert any(job_types.values())

    date_choices = parameters.get("date", {})
    assert any(date_choices.values())

    approved_distances = {0, 5, 10, 25, 50, 100}
    assert parameters["distance"] in approved_distances

    assert parameters["uploads"].get("resume"), "Path to resume missing under uploads > resume"

    checkboxes = parameters.get("checkboxes", {})
    expected_checkboxes = [
        "driversLicence",
        "requireVisa",
        "legallyAuthorized",
        "certifiedProfessional",
        "urgentFill",
        "commute",
        "backgroundCheck",
        "securityClearance",
        "degreeCompleted",
    ]
    for field in expected_checkboxes:
        if field not in checkboxes:
            raise KeyError(f"checkboxes.{field} missing from config.yaml")
    assert isinstance(parameters["universityGpa"], (int, float))

    language_types = {"none", "conversational", "professional", "native or bilingual"}
    for lang, level in parameters.get("languages", {}).items():
        assert level.lower() in language_types, f"Invalid language proficiency for {lang}: {level}"

    for tech, years in parameters.get("experience", {}).items():
        assert isinstance(years, int), f"Experience for {tech} must be an int"

    for key, value in parameters.get("personalInfo", {}).items():
        assert value != "", f"personalInfo.{key} must not be empty"

    for key, value in parameters.get("eeo", {}).items():
        assert value != "", f"eeo.{key} must not be empty"

    # Normalise OpenAI key placeholder
    if parameters.get("openaiApiKey") == "sk-proj-your-openai-api-key":
        print("OpenAI API key not configured. Defaulting to empty responses for text fields.")
        parameters["openaiApiKey"] = None

    return parameters 