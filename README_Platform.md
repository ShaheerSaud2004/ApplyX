# EasyApply Platform - AI-Powered Job Application Assistant

A comprehensive web platform that integrates with your existing LinkedIn Easy Apply bot functionality and adds ChatGPT Agent Mode capabilities for automated job applications.

## 🚀 Features

- **AI Agent Integration**: ChatGPT Agent Mode for intelligent job searching and application
- **Resume Tailoring**: Automatic resume optimization for each job application
- **Multi-Platform Support**: LinkedIn, Indeed, Handshake integration
- **Application Tracking**: Comprehensive dashboard with analytics
- **Secure Authentication**: JWT-based user authentication
- **File Management**: Resume upload and management
- **Real-time Status**: Live agent status and progress monitoring

## 🛠 Technology Stack

### Frontend
- **Next.js 14** with TypeScript
- **Tailwind CSS** for styling
- **ShadCN UI** components
- **Lucide React** icons
- **Recharts** for analytics

### Backend
- **Flask** Python web framework
- **SQLite** database
- **JWT** authentication
- **OpenAI API** integration
- **Selenium** for web automation

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- OpenAI API key
- LinkedIn credentials
- Chrome browser and ChromeDriver

## 🔧 Installation & Setup

### 1. Clone and Install Dependencies

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your credentials:
```env
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
LINKEDIN_EMAIL=your-linkedin-email@example.com
LINKEDIN_PASSWORD=your-linkedin-password
```

### 3. Configure Your Bot Settings

Update your existing `config.yaml` file with the platform integration:

```yaml
# Add these settings to your existing config.yaml
email: your-linkedin-email@example.com
password: your-linkedin-password
openaiApiKey: your-openai-api-key

# Your existing settings
positions:
  - Artificial Intelligence
  - Machine Learning
  - Cybersecurity
locations:
  - Any
remote: false
experienceLevel:
  entry: true
  associate: false
# ... rest of your existing config
```

### 4. Start the Application

```bash
# Terminal 1: Start the backend server
cd backend
python app.py

# Terminal 2: Start the frontend development server
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 🎯 How to Use

### 1. Create an Account
- Visit http://localhost:3000
- Click "Get Started" to create an account
- Fill in your basic information

### 2. Upload Your Resume
- Go to the Dashboard
- Click "Upload Resume" to upload your PDF resume
- The AI will parse and optimize it for job applications

### 3. Configure Job Preferences
- Set your preferred job titles, locations, and criteria
- Configure salary expectations and experience level
- Set up company blacklists if needed

### 4. Start the AI Agent
- Click "Configure Agent" to set up your automation preferences
- Click "Start Agent" to begin automated job applications
- Monitor real-time progress on the dashboard

### 5. Track Applications
- View all your applications in the "Applications" section
- Monitor success rates and response analytics
- Update application statuses as you hear back from companies

## 🤖 AI Agent Features

The platform integrates ChatGPT Agent Mode to:

1. **Intelligent Job Search**: Automatically search for relevant positions across multiple platforms
2. **Resume Tailoring**: Customize your resume for each specific job posting
3. **Cover Letter Generation**: Create personalized cover letters
4. **Application Submission**: Fill out and submit applications automatically
5. **Progress Tracking**: Monitor and report on all activities

## 📊 Dashboard Features

- **Real-time Statistics**: Track applications, success rates, and response times
- **Agent Status**: Monitor AI agent progress and current tasks
- **Application Management**: View, filter, and update your applications
- **Analytics**: Visualize your job search performance
- **Company Insights**: See which companies you've applied to most

## 🔗 Integration with Existing Code

The platform seamlessly integrates with your existing:

- `linkedineasyapply.py` - Core LinkedIn automation functionality
- `main_fast.py` - Continuous application bot with human behavior simulation
- `config.yaml` - All your existing job preferences and settings

Your existing bot functionality is preserved and enhanced with:
- Web-based management interface
- User authentication and data persistence
- Advanced analytics and tracking
- Multi-user support

## 🛡 Security Features

- JWT-based authentication
- Secure password hashing
- File upload validation
- CORS protection
- Input sanitization

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Applications
- `GET /api/applications` - Get user's applications
- `PUT /api/applications/:id/status` - Update application status

### Agent Management
- `POST /api/agent/start` - Start the AI agent
- `POST /api/agent/stop` - Stop the AI agent
- `GET /api/agent/status` - Get agent status

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

### File Management
- `POST /api/resume/upload` - Upload resume file

## 🚦 Running in Production

For production deployment:

1. Set up a proper database (PostgreSQL recommended)
2. Configure environment variables for production
3. Set up SSL certificates
4. Use a proper WSGI server (Gunicorn)
5. Set up reverse proxy (Nginx)
6. Configure monitoring and logging

## 🐛 Troubleshooting

### Common Issues

1. **ChromeDriver Issues**: Ensure ChromeDriver is in your PATH or update the path in the configuration
2. **OpenAI API Errors**: Verify your API key and ensure you have sufficient credits
3. **LinkedIn Login Issues**: Check your credentials and ensure 2FA is disabled for automation
4. **Database Errors**: Ensure the backend has write permissions for the SQLite database

### Getting Help

- Check the browser console for frontend errors
- Check the backend logs for API errors
- Ensure all dependencies are installed correctly
- Verify environment variables are set properly

## 📄 License

This project builds upon your existing LinkedIn Easy Apply bot and adds a comprehensive web platform for enhanced functionality and user experience.

## 🤝 Contributing

To contribute to this platform:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support with this platform integration, please ensure:
- Your existing bot functionality is working correctly
- All dependencies are installed
- Environment variables are properly configured
- The database is accessible and writable 