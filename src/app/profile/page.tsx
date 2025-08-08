'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  User, 
  Shield, 
  Settings,
  Save,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle,
  FileText,
  Upload,
  Download,
  Trash2,
  Brain,
  Briefcase,
  GraduationCap,
  MapPin,
  Globe,
  Mail,
  Phone,
  Star,
  Zap,
  Award,
  Target,
  Clock,
  Users,
  Building2,
  Sparkles
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '@/components/AuthProvider'
import { ResumeUploadModal } from '@/components/ResumeUploadModal'
import { getApiUrl } from '@/lib/utils'

interface UploadedResume {
  id: string
  filename: string
  originalName: string
  uploadedAt: string
  isDefault: boolean
}

export default function ProfilePage() {
  const { token, user: authUser } = useAuth()
  
  // Basic Profile Information
  const [userProfile, setUserProfile] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    website: ''
  })

  // LinkedIn Credentials
  const [linkedinCreds, setLinkedinCreds] = useState({
    email: '',
    password: ''
  })

  // Personal Details (from config)
  const [personalDetails, setPersonalDetails] = useState({
    pronouns: '',
    phoneCountryCode: 'United States (+1)',
    streetAddress: '',
    city: '',
    state: '',
    zipCode: '',
    linkedinUrl: '',
    portfolioWebsite: '',
    messageToManager: '',
    universityGpa: '',
    noticePeriod: '2',
    weekendWork: true,
    eveningWork: true,
    drugTest: true,
    backgroundCheck: true
  })

  // Work Authorization & Legal Status
  const [workAuthorization, setWorkAuthorization] = useState({
    driversLicense: true,
    requireVisa: false,
    legallyAuthorized: true,
    securityClearance: false,
    usCitizen: true,
    degreeCompleted: 'Bachelor\'s Degree'
  })

  // Skills & Experience with proficiency levels
  const [skillsExperience, setSkillsExperience] = useState({
    languages: {
      english: 'Native or bilingual'
    },
    technicalSkills: {} as Record<string, number>,
    yearsExperience: {} as Record<string, number>
  })

  // Job Preferences
  const [jobPreferences, setJobPreferences] = useState({
    jobTitles: [] as string[],
    locations: [] as string[],
    remote: true,
    experienceLevel: {
      internship: false,
      entry: true,
      associate: false,
      'mid-senior level': false,
      director: false,
      executive: false
    },
    jobTypes: {
      'full-time': true,
      contract: true,
      'part-time': false,
      temporary: false,
      internship: false,
      other: false,
      volunteer: false
    },
    salaryMin: '',
    datePreference: 'all time'
  })

  // Application Responses (common questions)
  const [applicationResponses, setApplicationResponses] = useState({
    referral: '',
    citizenship: 'U.S. Citizen/Permanent Resident',
    salary: '65000',
    startDate: 'Immediately available',
    weekends: 'Yes',
    evenings: 'Yes',
    references: 'Available upon request'
  })

  // EEO Information (optional)
  const [eeoInfo, setEeoInfo] = useState({
    gender: '',
    race: '',
    veteran: false,
    disability: false
  })

  // UI State
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [showResumeModal, setShowResumeModal] = useState(false)
  const [uploadedResumes, setUploadedResumes] = useState<UploadedResume[]>([])
  const [activeTab, setActiveTab] = useState('personal')
  const [resumeParsing, setResumeParsing] = useState(false)
  const [aiProvider, setAiProvider] = useState<'openai' | 'local' | 'none'>('none')

  // Skills and technologies for dropdowns
  const availableSkills = [
    'Python', 'JavaScript', 'Java', 'C++', 'C#', 'React', 'Node.js', 'Angular', 'Vue',
    'HTML', 'CSS', 'SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Docker', 'Kubernetes',
    'AWS', 'Azure', 'GCP', 'Git', 'Linux', 'Machine Learning', 'AI', 'Cybersecurity',
    'DevOps', 'Flask', 'Django', 'FastAPI', 'Selenium', 'TensorFlow', 'PyTorch',
    'Pandas', 'NumPy', 'Scikit-learn', 'Networking', 'Security Analysis'
  ]

  const commonJobTitles = [
    'Software Engineer', 'Data Scientist', 'Security Engineer', 'Machine Learning Engineer',
    'Full Stack Developer', 'Frontend Developer', 'Backend Developer', 'DevOps Engineer',
    'Cybersecurity Specialist', 'AI Engineer', 'Security Analyst', 'Network Engineer'
  ]

  const commonLocations = [
    'Remote', 'New York, NY', 'San Francisco, CA', 'Seattle, WA', 'Austin, TX',
    'Boston, MA', 'Los Angeles, CA', 'Chicago, IL', 'Washington, DC', 'Atlanta, GA'
  ]

  useEffect(() => {
    if (token) {
      loadUserProfile()
      loadUploadedResumes()
    }
  }, [token])

  useEffect(() => {
    // Probe AI configuration so we can hide the OpenAI banner if local LLM exists
    const fetchAiConfig = async () => {
      try {
        const r = await fetch(getApiUrl('/api/ai/config'))
        if (r.ok) {
          const data = await r.json()
          setAiProvider((data.provider as any) || 'none')
        }
      } catch {}
    }
    fetchAiConfig()
  }, [])

  const loadUserProfile = async () => {
    try {
          const response = await fetch(getApiUrl('/api/profile'), {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      
      if (response.ok) {
        const data = await response.json()
        setUserProfile(data.user || {})
        setPersonalDetails(data.personalDetails || {})
        setJobPreferences(data.jobPreferences || {})
        setWorkAuthorization(data.workAuthorization || {})
        setSkillsExperience(data.skillsExperience || {})
        setApplicationResponses(data.applicationResponses || {})
        setEeoInfo(data.eeoInfo || {})
      }
    } catch (error) {
      console.error('Error loading profile:', error)
    }
  }

  const loadUploadedResumes = async () => {
    try {
          const response = await fetch(getApiUrl('/api/resumes'), {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      
      if (response.ok) {
        const data = await response.json()
        setUploadedResumes(data.resumes || [])
      }
    } catch (error) {
      console.error('Error loading resumes:', error)
    }
  }

  const parseResume = async (resumeId: string) => {
    setResumeParsing(true)
    try {
      const response = await fetch(getApiUrl('/api/resume/parse'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ resume_id: resumeId })
      })

      if (response.ok) {
        const data = await response.json()
        const parsed = data.parsed_data
        
        // Auto-fill profile with parsed data
        if (parsed.personal_info) {
          setUserProfile(prev => ({
            ...prev,
            firstName: parsed.personal_info.first_name || prev.firstName,
            lastName: parsed.personal_info.last_name || prev.lastName
          }))
        }
        
        if (parsed.contact_info) {
          setUserProfile(prev => ({
            ...prev,
            email: parsed.contact_info.email || prev.email,
            phone: parsed.contact_info.phone || prev.phone,
            website: parsed.contact_info.website || prev.website
          }))
          
          setPersonalDetails(prev => ({
            ...prev,
            city: parsed.contact_info.city || prev.city,
            state: parsed.contact_info.state || prev.state,
            zipCode: parsed.contact_info.zip_code || prev.zipCode,
            linkedinUrl: parsed.contact_info.linkedin || prev.linkedinUrl
          }))
        }
        
        if (parsed.skills) {
          setSkillsExperience(prev => ({
            ...prev,
            technicalSkills: { ...prev.technicalSkills, ...parsed.skills }
          }))
        }
        
        if (parsed.education?.gpa) {
          setPersonalDetails(prev => ({
            ...prev,
            universityGpa: parsed.education.gpa.toString()
          }))
        }
        
        if (parsed.work_authorization) {
          setWorkAuthorization(prev => ({
            ...prev,
            ...parsed.work_authorization
          }))
        }

        setMessage({ type: 'success', text: 'Resume parsed successfully! Profile fields have been auto-filled.' })
      } else {
        const errorData = await response.json()
        setMessage({ type: 'error', text: errorData.error || 'Failed to parse resume' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error parsing resume. Please try again.' })
    } finally {
      setResumeParsing(false)
    }
  }

  const aiCompleteProfile = async () => {
    setLoading(true)
    setMessage({ type: '', text: '' })
    
    try {
      const response = await fetch(getApiUrl('/api/profile/ai-complete'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const result = await response.json()
        const aiData = result.data
        
        // Populate all form fields with AI-generated data
        if (aiData.user) {
          setUserProfile(prev => ({
            ...prev,
            firstName: aiData.user.firstName || prev.firstName,
            lastName: aiData.user.lastName || prev.lastName,
            email: aiData.user.email || prev.email,
            phone: aiData.user.phone || prev.phone,
            website: aiData.user.website || prev.website
          }))
        }
        
        if (aiData.personalDetails) {
          setPersonalDetails(prev => ({
            ...prev,
            ...aiData.personalDetails
          }))
        }
        
        if (aiData.workAuthorization) {
          setWorkAuthorization(prev => ({
            ...prev,
            ...aiData.workAuthorization
          }))
        }
        
        if (aiData.skillsExperience) {
          setSkillsExperience(prev => ({
            ...prev,
            ...aiData.skillsExperience
          }))
        }
        
        if (aiData.jobPreferences) {
          setJobPreferences(prev => ({
            ...prev,
            ...aiData.jobPreferences
          }))
        }
        
        if (aiData.applicationResponses) {
          setApplicationResponses(prev => ({
            ...prev,
            ...aiData.applicationResponses
          }))
        }
        
        if (aiData.eeoInfo) {
          setEeoInfo(prev => ({
            ...prev,
            ...aiData.eeoInfo
          }))
        }

        setMessage({ 
          type: 'success', 
          text: 'AI has automatically filled your profile! Please review and modify the information as needed before saving.' 
        })
        
        // Scroll to top to show the success message
        window.scrollTo({ top: 0, behavior: 'smooth' })
        
      } else {
        const errorData = await response.json()
        setMessage({ 
          type: 'error', 
          text: errorData.error || 'Failed to complete profile with AI' 
        })
      }
    } catch (error) {
      console.error('Error with AI completion:', error)
      setMessage({ 
        type: 'error', 
        text: 'Error connecting to AI service. Please try again.' 
      })
    } finally {
      setLoading(false)
    }
  }

  const addSkill = (skill: string) => {
    if (skill && !skillsExperience.technicalSkills[skill]) {
      setSkillsExperience(prev => ({
        ...prev,
        technicalSkills: { ...prev.technicalSkills, [skill]: 3 }
      }))
    }
  }

  const removeSkill = (skill: string) => {
    setSkillsExperience(prev => ({
      ...prev,
      technicalSkills: Object.fromEntries(
        Object.entries(prev.technicalSkills).filter(([k]) => k !== skill)
      )
    }))
  }

  const addJobTitle = (title: string) => {
    if (title && !jobPreferences.jobTitles.includes(title)) {
      setJobPreferences(prev => ({
        ...prev,
        jobTitles: [...prev.jobTitles, title]
      }))
    }
  }

  const removeJobTitle = (title: string) => {
    setJobPreferences(prev => ({
      ...prev,
      jobTitles: prev.jobTitles.filter(t => t !== title)
    }))
  }

  const addLocation = (location: string) => {
    if (location && !jobPreferences.locations.includes(location)) {
      setJobPreferences(prev => ({
        ...prev,
        locations: [...prev.locations, location]
      }))
    }
  }

  const removeLocation = (location: string) => {
    setJobPreferences(prev => ({
      ...prev,
      locations: prev.locations.filter(l => l !== location)
    }))
  }

  const saveProfile = async () => {
    setLoading(true)
    try {
      const profileData = {
        user: userProfile,
        personalDetails,
        jobPreferences,
        workAuthorization,
        skillsExperience,
        applicationResponses,
        eeoInfo
      }

      const response = await fetch(getApiUrl('/api/profile'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(profileData)
      })

      if (response.ok) {
        setMessage({ type: 'success', text: 'Profile saved successfully!' })
        setSaveSuccess(true)
        setTimeout(() => setSaveSuccess(false), 3000)
      } else {
        setMessage({ type: 'error', text: 'Failed to save profile' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error saving profile' })
    } finally {
      setLoading(false)
    }
  }

  const saveLinkedInCredentials = async () => {
    setLoading(true)
    try {
      const response = await fetch(getApiUrl('/api/profile'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          linkedin_email: linkedinCreds.email,
          linkedin_password: linkedinCreds.password
        })
      })

      if (response.ok) {
        setMessage({ type: 'success', text: 'LinkedIn credentials saved successfully!' })
      } else {
        const errorData = await response.json()
        setMessage({ type: 'error', text: errorData.error || 'Failed to save LinkedIn credentials' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error saving LinkedIn credentials' })
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'personal', name: 'Personal Info', icon: User },
    { id: 'contact', name: 'Contact & Location', icon: MapPin },
    { id: 'skills', name: 'Skills & Experience', icon: Brain },
    { id: 'preferences', name: 'Job Preferences', icon: Target },
    { id: 'authorization', name: 'Work Authorization', icon: Shield },
    { id: 'questions', name: 'Application Questions', icon: FileText },
    { id: 'resume', name: 'Resume Management', icon: Upload },
    { id: 'linkedin', name: 'LinkedIn Settings', icon: Globe }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-pink-100">
      {/* Header */}
      <header className="px-3 sm:px-4 lg:px-6 h-14 sm:h-16 flex items-center border-b bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-sm">
        <div className="container flex items-center">
          <Link href="/" className="flex items-center space-x-2">
            <div className="relative">
              <div className="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
                <svg className="h-4 w-4 sm:h-5 sm:w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <polygon points="13,2 3,14 12,14 11,22 21,10 12,10 13,2"></polygon>
                </svg>
              </div>
              <div className="absolute -top-1 -right-1 w-2 h-2 sm:w-3 sm:h-3 bg-green-500 rounded-full animate-pulse"></div>
            </div>
            <span className="font-bold text-base sm:text-lg md:text-xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              ApplyX
            </span>
          </Link>
          <div className="ml-auto flex items-center space-x-2 md:space-x-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm" className="text-xs sm:text-sm">Dashboard</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 opacity-90"></div>
        <div className="absolute inset-0">
          <div className="absolute top-6 sm:top-10 left-6 sm:left-10 w-12 h-12 sm:w-20 sm:h-20 bg-white/20 rounded-full blur-xl"></div>
          <div className="absolute top-12 sm:top-20 right-12 sm:right-20 w-20 h-20 sm:w-32 sm:h-32 bg-yellow-300/20 rounded-full blur-xl"></div>
          <div className="absolute bottom-6 sm:bottom-10 left-1/3 w-16 h-16 sm:w-24 sm:h-24 bg-blue-300/20 rounded-full blur-xl"></div>
        </div>
        <div className="relative px-3 sm:px-4 py-6 sm:py-8 md:py-12 mx-auto max-w-7xl lg:px-6">
          <div className="text-center">
            <div className="flex items-center justify-center mb-3 sm:mb-4">
              <Sparkles className="h-5 w-5 sm:h-6 sm:w-6 md:h-8 md:w-8 text-yellow-300 mr-1 sm:mr-2" />
              <h1 className="text-xl sm:text-2xl md:text-4xl lg:text-5xl font-bold text-white">
                Complete Your Profile
              </h1>
              <Sparkles className="h-5 w-5 sm:h-6 sm:w-6 md:h-8 md:w-8 text-yellow-300 ml-1 sm:ml-2" />
            </div>
            <p className="text-sm sm:text-base md:text-xl text-white/90 max-w-3xl mx-auto px-2 sm:px-4">
              Set up your comprehensive job application profile with resume parsing, 
              skills tracking, and automated question responses.
            </p>
            
            {/* Action Buttons */}
            <div className="mt-4 sm:mt-6 md:mt-8 flex flex-col sm:flex-row justify-center gap-2 sm:gap-3 md:gap-4 px-2 sm:px-4">
              <Button 
                onClick={() => setShowResumeModal(true)}
                className="bg-white/20 text-white border-white/30 hover:bg-white/30 backdrop-blur-sm w-full sm:w-auto text-sm sm:text-base"
                size="lg"
              >
                <Upload className="h-4 w-4 sm:h-5 sm:w-5 mr-1 sm:mr-2" />
                Upload & Parse Resume
              </Button>
              <Button 
                onClick={aiCompleteProfile}
                disabled={loading || uploadedResumes.length === 0}
                className="bg-gradient-to-r from-purple-500 to-pink-600 text-white hover:from-purple-600 hover:to-pink-700 backdrop-blur-sm w-full sm:w-auto text-sm sm:text-base"
                size="lg"
              >
                <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 mr-1 sm:mr-2" />
                {loading ? 'AI Working...' : 'AI Smart Fill'}
              </Button>
              <Button 
                onClick={saveProfile}
                disabled={loading}
                className="bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700 w-full sm:w-auto text-sm sm:text-base"
                size="lg"
              >
                <Save className="h-4 w-4 sm:h-5 sm:w-5 mr-1 sm:mr-2" />
                {loading ? 'Saving...' : 'Save Profile'}
              </Button>
            </div>
            
            {/* AI Smart Fill Description */}
            <div className="mt-4 sm:mt-6 text-center">
              <p className="text-white/80 text-xs sm:text-sm max-w-2xl mx-auto px-2">
                ✨ <strong>AI Smart Fill:</strong> Upload your resume and let our AI automatically complete your entire profile! 
                It will analyze your resume and intelligently fill in all sections including skills, job preferences, and experience levels. 
                Just review and modify the suggestions before saving.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Message Display */}
        {message.text && (
          <div className={`mb-6 p-4 rounded-lg border ${
            message.type === 'success' 
              ? 'bg-green-50 border-green-200 text-green-800' 
              : 'bg-red-50 border-red-200 text-red-800'
          }`}>
            <div className="flex items-center">
              {message.type === 'success' ? (
                <CheckCircle className="h-5 w-5 mr-2" />
              ) : (
                <AlertCircle className="h-5 w-5 mr-2" />
              )}
              {message.text}
            </div>
          </div>
        )}

        {/* AI provider warning (only if none configured) */}
        {aiProvider === 'none' && (
          <div className="mb-6 p-3 rounded-lg border bg-amber-50 border-amber-200 text-amber-900">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 mr-2" />
              OpenAI/Local AI not configured. Set OPENAI_API_KEY or run a local OpenAI-compatible server and set LOCAL_AI_BASE_URL.
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="flex flex-wrap justify-center gap-2 p-1 bg-white/60 backdrop-blur-sm rounded-xl border">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-4 py-2 rounded-lg font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                      : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.name}
                </button>
              )
            })}
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {/* Personal Information Tab */}
          {activeTab === 'personal' && (
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-t-lg">
                <CardTitle className="flex items-center text-2xl">
                  <User className="h-6 w-6 mr-3 text-blue-600" />
                  Personal Information
                </CardTitle>
                <CardDescription>
                  Basic personal details and preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name</Label>
                    <Input
                      id="firstName"
                      value={userProfile.firstName}
                      onChange={(e) => setUserProfile(prev => ({...prev, firstName: e.target.value}))}
                      className="border-purple-200 focus:border-purple-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input
                      id="lastName"
                      value={userProfile.lastName}
                      onChange={(e) => setUserProfile(prev => ({...prev, lastName: e.target.value}))}
                      className="border-purple-200 focus:border-purple-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="pronouns">Pronouns</Label>
                    <Select 
                      value={personalDetails.pronouns} 
                      onValueChange={(value) => setPersonalDetails(prev => ({...prev, pronouns: value}))}
                    >
                      <SelectTrigger className="border-purple-200 focus:border-purple-500">
                        <SelectValue placeholder="Select pronouns" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="He/Him">He/Him</SelectItem>
                        <SelectItem value="She/Her">She/Her</SelectItem>
                        <SelectItem value="They/Them">They/Them</SelectItem>
                        <SelectItem value="Mr.">Mr.</SelectItem>
                        <SelectItem value="Ms.">Ms.</SelectItem>
                        <SelectItem value="Mx.">Mx.</SelectItem>
                        <SelectItem value="prefer-not-to-say">Prefer not to say</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="universityGpa">University GPA</Label>
                    <Input
                      id="universityGpa"
                      type="number"
                      step="0.1"
                      min="0"
                      max="4"
                      value={personalDetails.universityGpa}
                      onChange={(e) => setPersonalDetails(prev => ({...prev, universityGpa: e.target.value}))}
                      className="border-purple-200 focus:border-purple-500"
                      placeholder="e.g., 3.7"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="messageToManager">Message to Hiring Manager</Label>
                  <Textarea
                    id="messageToManager"
                    value={personalDetails.messageToManager}
                    onChange={(e) => setPersonalDetails(prev => ({...prev, messageToManager: e.target.value}))}
                    className="border-purple-200 focus:border-purple-500"
                    placeholder="Hi, I am interested to join your organization. Please have a look at my resume. Thank you."
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Contact & Location Tab */}
          {activeTab === 'contact' && (
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-r from-green-50 to-blue-50 rounded-t-lg">
                <CardTitle className="flex items-center text-2xl">
                  <MapPin className="h-6 w-6 mr-3 text-green-600" />
                  Contact & Location
                </CardTitle>
                <CardDescription>
                  Contact information and address details
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={userProfile.email}
                      onChange={(e) => setUserProfile(prev => ({...prev, email: e.target.value}))}
                      className="border-green-200 focus:border-green-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={userProfile.phone}
                      onChange={(e) => setUserProfile(prev => ({...prev, phone: e.target.value}))}
                      className="border-green-200 focus:border-green-500"
                      placeholder="(555) 123-4567"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="streetAddress">Street Address</Label>
                    <Input
                      id="streetAddress"
                      value={personalDetails.streetAddress}
                      onChange={(e) => setPersonalDetails(prev => ({...prev, streetAddress: e.target.value}))}
                      className="border-green-200 focus:border-green-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="city">City</Label>
                    <Input
                      id="city"
                      value={personalDetails.city}
                      onChange={(e) => setPersonalDetails(prev => ({...prev, city: e.target.value}))}
                      className="border-green-200 focus:border-green-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="state">State</Label>
                    <Input
                      id="state"
                      value={personalDetails.state}
                      onChange={(e) => setPersonalDetails(prev => ({...prev, state: e.target.value}))}
                      className="border-green-200 focus:border-green-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="zipCode">ZIP Code</Label>
                    <Input
                      id="zipCode"
                      value={personalDetails.zipCode}
                      onChange={(e) => setPersonalDetails(prev => ({...prev, zipCode: e.target.value}))}
                      className="border-green-200 focus:border-green-500"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="linkedinUrl">LinkedIn Profile URL</Label>
                    <Input
                      id="linkedinUrl"
                      value={personalDetails.linkedinUrl}
                      onChange={(e) => setPersonalDetails(prev => ({...prev, linkedinUrl: e.target.value}))}
                      className="border-green-200 focus:border-green-500"
                      placeholder="https://linkedin.com/in/yourname"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="portfolioWebsite">Portfolio/Website</Label>
                    <Input
                      id="portfolioWebsite"
                      value={personalDetails.portfolioWebsite}
                      onChange={(e) => setPersonalDetails(prev => ({...prev, portfolioWebsite: e.target.value}))}
                      className="border-green-200 focus:border-green-500"
                      placeholder="https://yourwebsite.com"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Skills & Experience Tab */}
          {activeTab === 'skills' && (
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-t-lg">
                <CardTitle className="flex items-center text-2xl">
                  <Brain className="h-6 w-6 mr-3 text-purple-600" />
                  Skills & Experience
                </CardTitle>
                <CardDescription>
                  Technical skills with proficiency levels (1-5 scale)
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                {/* Add Skills */}
                <div className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    {availableSkills.map(skill => (
                      <Button
                        key={skill}
                        variant="outline"
                        size="sm"
                        onClick={() => addSkill(skill)}
                        disabled={!!skillsExperience.technicalSkills[skill]}
                        className={`${
                          skillsExperience.technicalSkills[skill] 
                            ? 'bg-purple-100 border-purple-300 text-purple-700' 
                            : 'hover:bg-purple-50 hover:border-purple-300'
                        }`}
                      >
                        <Zap className="h-3 w-3 mr-1" />
                        {skill}
                        {skillsExperience.technicalSkills[skill] && (
                          <span className="ml-2 text-xs">
                            {skillsExperience.technicalSkills[skill]}/5
                          </span>
                        )}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Skills List */}
                <div className="space-y-4">
                  <h4 className="font-semibold text-lg flex items-center">
                    <Star className="h-5 w-5 mr-2 text-yellow-500" />
                    Your Skills
                  </h4>
                  {!skillsExperience.technicalSkills || Object.entries(skillsExperience.technicalSkills).length === 0 ? (
                    <p className="text-gray-500 italic">No skills added yet. Click the skills above to add them.</p>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {skillsExperience.technicalSkills && Object.entries(skillsExperience.technicalSkills).map(([skill, level]) => (
                        <div key={skill} className="p-4 border border-purple-200 rounded-lg bg-gradient-to-r from-purple-50 to-pink-50">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{skill}</span>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeSkill(skill)}
                              className="text-red-500 hover:text-red-700"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                          <div className="space-y-2">
                            <Label>Proficiency Level: {level}/5</Label>
                            <input
                              type="range"
                              min="1"
                              max="5"
                              value={level}
                              onChange={(e) => setSkillsExperience(prev => ({
                                ...prev,
                                technicalSkills: {
                                  ...prev.technicalSkills,
                                  [skill]: parseInt(e.target.value)
                                }
                              }))}
                              className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer"
                            />
                            <div className="flex justify-between text-xs text-gray-500">
                              <span>Beginner</span>
                              <span>Expert</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Job Preferences Tab */}
          {activeTab === 'preferences' && (
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-t-lg">
                <CardTitle className="flex items-center text-2xl">
                  <Target className="h-6 w-6 mr-3 text-indigo-600" />
                  Job Preferences
                </CardTitle>
                <CardDescription>
                  Define your ideal job search criteria
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                {/* Job Titles */}
                <div className="space-y-4">
                  <h4 className="font-semibold text-lg flex items-center">
                    <Briefcase className="h-5 w-5 mr-2 text-indigo-600" />
                    Desired Job Titles
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {commonJobTitles.map(title => (
                      <Button
                        key={title}
                        variant="outline"
                        size="sm"
                        onClick={() => addJobTitle(title)}
                        disabled={jobPreferences.jobTitles.includes(title)}
                        className={`${
                          jobPreferences.jobTitles.includes(title)
                            ? 'bg-indigo-100 border-indigo-300 text-indigo-700'
                            : 'hover:bg-indigo-50 hover:border-indigo-300'
                        }`}
                      >
                        {title}
                      </Button>
                    ))}
                  </div>
                  
                  {jobPreferences.jobTitles.length > 0 && (
                    <div className="space-y-2">
                      <Label>Selected Job Titles:</Label>
                      <div className="flex flex-wrap gap-2">
                        {jobPreferences.jobTitles.map(title => (
                          <div key={title} className="flex items-center bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full">
                            <span className="text-sm">{title}</span>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeJobTitle(title)}
                              className="ml-2 h-4 w-4 p-0 text-indigo-600 hover:text-indigo-800"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Locations */}
                <div className="space-y-4">
                  <h4 className="font-semibold text-lg flex items-center">
                    <MapPin className="h-5 w-5 mr-2 text-green-600" />
                    Preferred Locations
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {commonLocations.map(location => (
                      <Button
                        key={location}
                        variant="outline"
                        size="sm"
                        onClick={() => addLocation(location)}
                        disabled={jobPreferences.locations.includes(location)}
                        className={`${
                          jobPreferences.locations.includes(location)
                            ? 'bg-green-100 border-green-300 text-green-700'
                            : 'hover:bg-green-50 hover:border-green-300'
                        }`}
                      >
                        {location}
                      </Button>
                    ))}
                  </div>
                  
                  {jobPreferences.locations.length > 0 && (
                    <div className="space-y-2">
                      <Label>Selected Locations:</Label>
                      <div className="flex flex-wrap gap-2">
                        {jobPreferences.locations.map(location => (
                          <div key={location} className="flex items-center bg-green-100 text-green-800 px-3 py-1 rounded-full">
                            <span className="text-sm">{location}</span>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeLocation(location)}
                              className="ml-2 h-4 w-4 p-0 text-green-600 hover:text-green-800"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Experience Level */}
                <div className="space-y-4">
                  <h4 className="font-semibold text-lg flex items-center">
                    <GraduationCap className="h-5 w-5 mr-2 text-purple-600" />
                    Experience Level
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {jobPreferences.experienceLevel && Object.entries(jobPreferences.experienceLevel).map(([level, checked]) => (
                      <label key={level} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={(e) => setJobPreferences(prev => ({
                            ...prev,
                            experienceLevel: {
                              ...prev.experienceLevel,
                              [level]: e.target.checked
                            }
                          }))}
                          className="rounded border-purple-300 text-purple-600 focus:ring-purple-500"
                        />
                        <span className="capitalize text-sm">{level}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Job Types */}
                <div className="space-y-4">
                  <h4 className="font-semibold text-lg flex items-center">
                    <Clock className="h-5 w-5 mr-2 text-blue-600" />
                    Job Types
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {jobPreferences.jobTypes && Object.entries(jobPreferences.jobTypes).map(([type, checked]) => (
                      <label key={type} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={(e) => setJobPreferences(prev => ({
                            ...prev,
                            jobTypes: {
                              ...prev.jobTypes,
                              [type]: e.target.checked
                            }
                          }))}
                          className="rounded border-blue-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="capitalize text-sm">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Salary and Remote */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="salaryMin">Minimum Salary ($)</Label>
                    <Input
                      id="salaryMin"
                      type="number"
                      value={jobPreferences.salaryMin}
                      onChange={(e) => setJobPreferences(prev => ({...prev, salaryMin: e.target.value}))}
                      className="border-indigo-200 focus:border-indigo-500"
                      placeholder="65000"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Remote Work Preference</Label>
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={jobPreferences.remote}
                        onChange={(e) => setJobPreferences(prev => ({...prev, remote: e.target.checked}))}
                        className="rounded border-indigo-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="text-sm">Open to remote work</span>
                    </label>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Work Authorization Tab */}
          {activeTab === 'authorization' && (
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-r from-red-50 to-orange-50 rounded-t-lg">
                <CardTitle className="flex items-center text-2xl">
                  <Shield className="h-6 w-6 mr-3 text-red-600" />
                  Work Authorization & Legal Status
                </CardTitle>
                <CardDescription>
                  Legal authorization and compliance information
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-semibold text-lg">Work Authorization</h4>
                    <div className="space-y-3">
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={workAuthorization.usCitizen}
                          onChange={(e) => setWorkAuthorization(prev => ({...prev, usCitizen: e.target.checked}))}
                          className="rounded border-red-300 text-red-600 focus:ring-red-500"
                        />
                        <span className="text-sm">U.S. Citizen</span>
                      </label>
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={workAuthorization.legallyAuthorized}
                          onChange={(e) => setWorkAuthorization(prev => ({...prev, legallyAuthorized: e.target.checked}))}
                          className="rounded border-red-300 text-red-600 focus:ring-red-500"
                        />
                        <span className="text-sm">Legally authorized to work in the US</span>
                      </label>
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={workAuthorization.requireVisa}
                          onChange={(e) => setWorkAuthorization(prev => ({...prev, requireVisa: e.target.checked}))}
                          className="rounded border-red-300 text-red-600 focus:ring-red-500"
                        />
                        <span className="text-sm">Require visa sponsorship</span>
                      </label>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="font-semibold text-lg">Additional Authorizations</h4>
                    <div className="space-y-3">
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={workAuthorization.driversLicense}
                          onChange={(e) => setWorkAuthorization(prev => ({...prev, driversLicense: e.target.checked}))}
                          className="rounded border-red-300 text-red-600 focus:ring-red-500"
                        />
                        <span className="text-sm">Valid driver's license</span>
                      </label>
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={workAuthorization.securityClearance}
                          onChange={(e) => setWorkAuthorization(prev => ({...prev, securityClearance: e.target.checked}))}
                          className="rounded border-red-300 text-red-600 focus:ring-red-500"
                        />
                        <span className="text-sm">Security clearance</span>
                      </label>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-semibold text-lg">Education & Compliance</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="degreeCompleted">Highest Degree Completed</Label>
                      <Select 
                        value={workAuthorization.degreeCompleted} 
                        onValueChange={(value) => setWorkAuthorization(prev => ({...prev, degreeCompleted: value}))}
                      >
                        <SelectTrigger className="border-red-200 focus:border-red-500">
                          <SelectValue placeholder="Select degree" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="High School">High School</SelectItem>
                          <SelectItem value="Associate's Degree">Associate's Degree</SelectItem>
                          <SelectItem value="Bachelor's Degree">Bachelor's Degree</SelectItem>
                          <SelectItem value="Master's Degree">Master's Degree</SelectItem>
                          <SelectItem value="Doctoral Degree">Doctoral Degree</SelectItem>
                          <SelectItem value="Professional Degree">Professional Degree</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="noticePeriod">Notice Period (weeks)</Label>
                      <Input
                        id="noticePeriod"
                        type="number"
                        min="0"
                        max="12"
                        value={personalDetails.noticePeriod}
                        onChange={(e) => setPersonalDetails(prev => ({...prev, noticePeriod: e.target.value}))}
                        className="border-red-200 focus:border-red-500"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={personalDetails.weekendWork}
                          onChange={(e) => setPersonalDetails(prev => ({...prev, weekendWork: e.target.checked}))}
                          className="rounded border-red-300 text-red-600 focus:ring-red-500"
                        />
                        <span className="text-sm">Available for weekend work</span>
                      </label>
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={personalDetails.eveningWork}
                          onChange={(e) => setPersonalDetails(prev => ({...prev, eveningWork: e.target.checked}))}
                          className="rounded border-red-300 text-red-600 focus:ring-red-500"
                        />
                        <span className="text-sm">Available for evening work</span>
                      </label>
                    </div>
                    
                    <div className="space-y-3">
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={personalDetails.drugTest}
                          onChange={(e) => setPersonalDetails(prev => ({...prev, drugTest: e.target.checked}))}
                          className="rounded border-red-300 text-red-600 focus:ring-red-500"
                        />
                        <span className="text-sm">Willing to undergo drug testing</span>
                      </label>
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={personalDetails.backgroundCheck}
                          onChange={(e) => setPersonalDetails(prev => ({...prev, backgroundCheck: e.target.checked}))}
                          className="rounded border-red-300 text-red-600 focus:ring-red-500"
                        />
                        <span className="text-sm">Willing to undergo background check</span>
                      </label>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Application Questions Tab */}
          {activeTab === 'questions' && (
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-t-lg">
                <CardTitle className="flex items-center text-2xl">
                  <FileText className="h-6 w-6 mr-3 text-yellow-600" />
                  Common Application Questions
                </CardTitle>
                <CardDescription>
                  Pre-filled responses to frequently asked application questions
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="referral">How did you hear about this position?</Label>
                    <Textarea
                      id="referral"
                      value={applicationResponses.referral}
                      onChange={(e) => setApplicationResponses(prev => ({...prev, referral: e.target.value}))}
                      className="border-yellow-200 focus:border-yellow-500"
                      placeholder="I discovered this position through my own research and interest in the company..."
                      rows={3}
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="salary">Salary Expectation</Label>
                      <Input
                        id="salary"
                        value={applicationResponses.salary}
                        onChange={(e) => setApplicationResponses(prev => ({...prev, salary: e.target.value}))}
                        className="border-yellow-200 focus:border-yellow-500"
                        placeholder="65000"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="startDate">Available Start Date</Label>
                      <Input
                        id="startDate"
                        value={applicationResponses.startDate}
                        onChange={(e) => setApplicationResponses(prev => ({...prev, startDate: e.target.value}))}
                        className="border-yellow-200 focus:border-yellow-500"
                        placeholder="Immediately available"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="weekends">Weekend Availability</Label>
                      <Select 
                        value={applicationResponses.weekends} 
                        onValueChange={(value) => setApplicationResponses(prev => ({...prev, weekends: value}))}
                      >
                        <SelectTrigger className="border-yellow-200 focus:border-yellow-500">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Yes">Yes</SelectItem>
                          <SelectItem value="No">No</SelectItem>
                          <SelectItem value="Limited">Limited availability</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="evenings">Evening Availability</Label>
                      <Select 
                        value={applicationResponses.evenings} 
                        onValueChange={(value) => setApplicationResponses(prev => ({...prev, evenings: value}))}
                      >
                        <SelectTrigger className="border-yellow-200 focus:border-yellow-500">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Yes">Yes</SelectItem>
                          <SelectItem value="No">No</SelectItem>
                          <SelectItem value="Limited">Limited availability</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="citizenship">Citizenship Status</Label>
                      <Select 
                        value={applicationResponses.citizenship} 
                        onValueChange={(value) => setApplicationResponses(prev => ({...prev, citizenship: value}))}
                      >
                        <SelectTrigger className="border-yellow-200 focus:border-yellow-500">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="U.S. Citizen/Permanent Resident">U.S. Citizen/Permanent Resident</SelectItem>
                          <SelectItem value="Work Visa">Work Visa</SelectItem>
                          <SelectItem value="Student Visa">Student Visa</SelectItem>
                          <SelectItem value="Other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="references">References</Label>
                    <Textarea
                      id="references"
                      value={applicationResponses.references}
                      onChange={(e) => setApplicationResponses(prev => ({...prev, references: e.target.value}))}
                      className="border-yellow-200 focus:border-yellow-500"
                      placeholder="Available upon request"
                      rows={2}
                    />
                  </div>
                </div>

                {/* EEO Information */}
                <div className="border-t pt-6">
                  <h4 className="font-semibold text-lg mb-4 flex items-center">
                    <Users className="h-5 w-5 mr-2 text-orange-600" />
                    EEO Information (Optional)
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="gender">Gender</Label>
                      <Select 
                        value={eeoInfo.gender} 
                        onValueChange={(value) => setEeoInfo(prev => ({...prev, gender: value}))}
                      >
                        <SelectTrigger className="border-orange-200 focus:border-orange-500">
                          <SelectValue placeholder="Prefer not to answer" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="prefer-not-to-answer">Prefer not to answer</SelectItem>
                          <SelectItem value="Male">Male</SelectItem>
                          <SelectItem value="Female">Female</SelectItem>
                          <SelectItem value="Non-binary">Non-binary</SelectItem>
                          <SelectItem value="Other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="race">Race/Ethnicity</Label>
                      <Select 
                        value={eeoInfo.race} 
                        onValueChange={(value) => setEeoInfo(prev => ({...prev, race: value}))}
                      >
                        <SelectTrigger className="border-orange-200 focus:border-orange-500">
                          <SelectValue placeholder="Prefer not to answer" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="prefer-not-to-answer">Prefer not to answer</SelectItem>
                          <SelectItem value="American Indian or Alaska Native">American Indian or Alaska Native</SelectItem>
                          <SelectItem value="Asian">Asian</SelectItem>
                          <SelectItem value="Black or African American">Black or African American</SelectItem>
                          <SelectItem value="Hispanic or Latino">Hispanic or Latino</SelectItem>
                          <SelectItem value="Native Hawaiian or Other Pacific Islander">Native Hawaiian or Other Pacific Islander</SelectItem>
                          <SelectItem value="White">White</SelectItem>
                          <SelectItem value="Two or More Races">Two or More Races</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={eeoInfo.veteran}
                        onChange={(e) => setEeoInfo(prev => ({...prev, veteran: e.target.checked}))}
                        className="rounded border-orange-300 text-orange-600 focus:ring-orange-500"
                      />
                      <span className="text-sm">Veteran status</span>
                    </label>
                    
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={eeoInfo.disability}
                        onChange={(e) => setEeoInfo(prev => ({...prev, disability: e.target.checked}))}
                        className="rounded border-orange-300 text-orange-600 focus:ring-orange-500"
                      />
                      <span className="text-sm">Disability status</span>
                    </label>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Resume Management Tab */}
          {activeTab === 'resume' && (
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-t-lg">
                <CardTitle className="flex items-center text-2xl">
                  <Upload className="h-6 w-6 mr-3 text-cyan-600" />
                  Resume Management
                </CardTitle>
                <CardDescription>
                  Upload, manage, and parse your resumes
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button 
                    onClick={() => setShowResumeModal(true)}
                    className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:from-cyan-600 hover:to-blue-700"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload New Resume
                  </Button>
                </div>

                {/* Uploaded Resumes */}
                <div className="space-y-4">
                  <h4 className="font-semibold text-lg flex items-center">
                    <FileText className="h-5 w-5 mr-2 text-blue-600" />
                    Your Resumes
                  </h4>
                  
                  {uploadedResumes.length === 0 ? (
                    <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500">No resumes uploaded yet</p>
                      <Button 
                        onClick={() => setShowResumeModal(true)}
                        variant="outline"
                        className="mt-4"
                      >
                        Upload Your First Resume
                      </Button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Array.isArray(uploadedResumes) && uploadedResumes.map((resume) => (
                        <div key={resume.id} className="p-4 border border-blue-200 rounded-lg bg-gradient-to-r from-blue-50 to-cyan-50">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <h5 className="font-medium text-blue-900">{resume.originalName}</h5>
                              <p className="text-sm text-blue-600">
                                Uploaded {new Date(resume.uploadedAt).toLocaleDateString()}
                              </p>
                              {resume.isDefault && (
                                <span className="inline-block mt-1 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                  Default
                                </span>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex flex-wrap gap-2">
                            <Button
                              onClick={() => parseResume(resume.id)}
                              disabled={resumeParsing}
                              size="sm"
                              className="bg-purple-100 text-purple-700 hover:bg-purple-200"
                            >
                              <Brain className="h-3 w-3 mr-1" />
                              {resumeParsing ? 'Parsing...' : 'Auto-Fill Profile'}
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-blue-600 border-blue-300 hover:bg-blue-50"
                            >
                              <Download className="h-3 w-3 mr-1" />
                              Download
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Resume Parsing Info */}
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border border-purple-200">
                  <h4 className="font-semibold text-purple-900 mb-2 flex items-center">
                    <Brain className="h-5 w-5 mr-2" />
                    Smart Resume Parsing
                  </h4>
                  <p className="text-purple-700 text-sm mb-2">
                    Our AI can automatically extract information from your resume to fill in your profile:
                  </p>
                  <ul className="text-purple-600 text-sm space-y-1">
                    <li>• Personal information (name, contact details)</li>
                    <li>• Technical skills and proficiency levels</li>
                    <li>• Education and GPA</li>
                    <li>• Work authorization status</li>
                    <li>• Years of experience</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          )}

          {/* LinkedIn Settings Tab */}
          {activeTab === 'linkedin' && (
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-lg">
                <CardTitle className="flex items-center text-2xl">
                  <Globe className="h-6 w-6 mr-3 text-blue-600" />
                  LinkedIn Bot Settings
                </CardTitle>
                <CardDescription>
                  Configure LinkedIn credentials for automated applications
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex">
                    <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold text-yellow-800">Security Notice</h4>
                      <p className="text-yellow-700 text-sm mt-1">
                        Your LinkedIn credentials are encrypted and stored securely. 
                        They are only used for automated job applications.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="linkedinEmail">LinkedIn Email</Label>
                    <Input
                      id="linkedinEmail"
                      type="email"
                      value={linkedinCreds.email}
                      onChange={(e) => setLinkedinCreds(prev => ({...prev, email: e.target.value}))}
                      className="border-blue-200 focus:border-blue-500"
                      placeholder="your.email@example.com"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="linkedinPassword">LinkedIn Password</Label>
                    <div className="relative">
                      <Input
                        id="linkedinPassword"
                        type={showPassword ? "text" : "password"}
                        value={linkedinCreds.password}
                        onChange={(e) => setLinkedinCreds(prev => ({...prev, password: e.target.value}))}
                        className="border-blue-200 focus:border-blue-500 pr-10"
                        placeholder="Your LinkedIn password"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4 text-gray-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-gray-400" />
                        )}
                      </Button>
                    </div>
                  </div>
                  
                  <Button 
                    onClick={saveLinkedInCredentials}
                    disabled={loading || !linkedinCreds.email || !linkedinCreds.password}
                    className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:from-blue-600 hover:to-indigo-700"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {loading ? 'Saving...' : 'Save LinkedIn Credentials'}
                  </Button>
                </div>

                <div className="border-t pt-6">
                  <h4 className="font-semibold text-lg mb-4 flex items-center">
                    <Settings className="h-5 w-5 mr-2 text-gray-600" />
                    Bot Configuration Tips
                  </h4>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-start">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                      <span>Complete your profile above before starting the bot</span>
                    </div>
                    <div className="flex items-start">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                      <span>Upload and parse your resume for automatic form filling</span>
                    </div>
                    <div className="flex items-start">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                      <span>Set your job preferences and application responses</span>
                    </div>
                    <div className="flex items-start">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                      <span>Enable two-factor authentication on your LinkedIn account</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sticky Save Button */}
        <div className="fixed bottom-6 right-6 z-50">
          <Button 
            onClick={saveProfile}
            disabled={loading}
            size="lg"
            className={`bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700 shadow-2xl transition-all duration-300 ${
              saveSuccess ? 'scale-110' : 'hover:scale-105'
            }`}
          >
            <Save className="h-5 w-5 mr-2" />
            {loading ? 'Saving...' : saveSuccess ? 'Saved!' : 'Save Profile'}
          </Button>
        </div>
      </div>

      {/* Resume Upload Modal */}
      <ResumeUploadModal 
        isOpen={showResumeModal}
        onOpenChange={setShowResumeModal}
        onUploadSuccess={(filename) => {
          console.log('Resume uploaded:', filename)
          loadUploadedResumes()
        }}
      />
    </div>
  )
} 