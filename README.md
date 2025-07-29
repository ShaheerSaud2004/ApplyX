# LinkedIn Easy Apply Bot

A Python-based LinkedIn job application bot that automates the application process for job seekers.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Chrome browser
- LinkedIn account

### Installation
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `config.yaml` with your LinkedIn credentials and preferences
4. Place your resume as `Shaheer_Saud_Resume.pdf` in the root directory

## 📁 Project Structure

```
├── main.py              # Standard application mode
├── main_fast.py         # Continuous application mode (1-2 min delays)
├── linkedineasyapply.py # Core bot functionality
├── easyapplybot/        # Utility functions
│   └── utils.py
├── config.yaml          # Configuration file
├── requirements.txt     # Python dependencies
├── Shaheer_Saud_Resume.pdf # Your resume
├── chromedriver         # Chrome WebDriver
└── chrome_bot/         # Browser session data
```

## 🎯 Usage

### Standard Mode
```bash
python main.py
```
- Applies to jobs with safety features
- Human-like behavior simulation
- Session breaks and delays

### Continuous Mode (Fast Apply)
```bash
python main_fast.py
```
- Continuous applications with 1-2 minute delays
- Full safety features enabled
- Press Ctrl+C to stop safely

## ⚙️ Configuration

Edit `config.yaml` to customize:
- LinkedIn credentials
- Job search preferences
- Personal information
- Application responses

## 📊 Output Files

- `output.csv` - Successful applications
- `failed.csv` - Failed applications
- `qa_log.csv` - Question-answer logs
- `unprepared_questions.csv` - Questions that need manual answers

## 🔒 Safety Features

- Human behavior simulation
- Random delays and breaks
- Stealth browser configuration
- Session management

## 📝 License

See LICENSE file for details.