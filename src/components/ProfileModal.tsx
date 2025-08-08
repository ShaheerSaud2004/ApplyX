'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
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
  Sparkles,
  X
} from 'lucide-react'
import { useAuth } from '@/components/AuthProvider'
import { getApiUrl } from '@/lib/utils'

interface ProfileModalProps {
  isOpen: boolean
  onClose: () => void
  onCredentialsSaved?: () => void
}

export function ProfileModal({ isOpen, onClose, onCredentialsSaved }: ProfileModalProps) {
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

  // Personal Details
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

  // Skills & Experience
  const [skillsExperience, setSkillsExperience] = useState({
    yearsOfExperience: '3-5',
    skills: [] as string[],
    jobTitles: [] as string[],
    locations: [] as string[],
    newSkill: '',
    newJobTitle: '',
    newLocation: ''
  })

  // Job Preferences
  const [jobPreferences, setJobPreferences] = useState({
    desiredSalary: '',
    salaryType: 'yearly',
    remotePreference: 'hybrid',
    relocationWillingness: true,
    travelWillingness: true,
    contractWillingness: true
  })

  // UI State
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [activeTab, setActiveTab] = useState('personal')

  useEffect(() => {
    if (isOpen) {
      loadUserProfile()
    }
  }, [isOpen])

  const loadUserProfile = async () => {
    if (!token) return
    
    try {
      const response = await fetch(getApiUrl('/api/profile'), {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        
        // Update all profile sections
        if (data.user) {
          setUserProfile(prev => ({
            ...prev,
            firstName: data.user.firstName || '',
            lastName: data.user.lastName || '',
            email: data.user.email || ''
          }))
        }
        
        if (data.linkedin_email) {
          setLinkedinCreds(prev => ({
            ...prev,
            email: data.linkedin_email || ''
          }))
        }
        
        // Load other profile data if available
        if (data.personalDetails) {
          setPersonalDetails(prev => ({ ...prev, ...data.personalDetails }))
        }
        
        if (data.workAuthorization) {
          setWorkAuthorization(prev => ({ ...prev, ...data.workAuthorization }))
        }
        
        if (data.skillsExperience) {
          setSkillsExperience(prev => ({ ...prev, ...data.skillsExperience }))
        }
        
        if (data.jobPreferences) {
          setJobPreferences(prev => ({ ...prev, ...data.jobPreferences }))
        }
      }
    } catch (error) {
      console.error('Error loading profile:', error)
    }
  }

  const saveLinkedInCredentials = async () => {
    setLoading(true)
    setMessage(null)
    
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
        // Call the callback to update dashboard
        if (onCredentialsSaved) {
          onCredentialsSaved()
        }
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

  const saveProfile = async () => {
    setLoading(true)
    setMessage(null)
    
    try {
      const response = await fetch(getApiUrl('/api/profile'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user: userProfile,
          personalDetails,
          workAuthorization,
          skillsExperience,
          jobPreferences
        })
      })

      if (response.ok) {
        setMessage({ type: 'success', text: 'Profile saved successfully!' })
      } else {
        const errorData = await response.json()
        setMessage({ type: 'error', text: errorData.error || 'Failed to save profile' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error saving profile' })
    } finally {
      setLoading(false)
    }
  }

  const addSkill = (skill: string) => {
    if (skill && !skillsExperience.skills.includes(skill)) {
      setSkillsExperience(prev => ({
        ...prev,
        skills: [...prev.skills, skill],
        newSkill: ''
      }))
    }
  }

  const removeSkill = (skill: string) => {
    setSkillsExperience(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill)
    }))
  }

  const addJobTitle = (title: string) => {
    if (title && !skillsExperience.jobTitles.includes(title)) {
      setSkillsExperience(prev => ({
        ...prev,
        jobTitles: [...prev.jobTitles, title],
        newJobTitle: ''
      }))
    }
  }

  const removeJobTitle = (title: string) => {
    setSkillsExperience(prev => ({
      ...prev,
      jobTitles: prev.jobTitles.filter(t => t !== title)
    }))
  }

  const addLocation = (location: string) => {
    if (location && !skillsExperience.locations.includes(location)) {
      setSkillsExperience(prev => ({
        ...prev,
        locations: [...prev.locations, location],
        newLocation: ''
      }))
    }
  }

  const removeLocation = (location: string) => {
    setSkillsExperience(prev => ({
      ...prev,
      locations: prev.locations.filter(l => l !== location)
    }))
  }

  const tabs = [
    { id: 'personal', name: 'Personal Info', icon: User },
    { id: 'contact', name: 'Contact & Location', icon: MapPin },
    { id: 'skills', name: 'Skills & Experience', icon: Brain },
    { id: 'preferences', name: 'Job Preferences', icon: Target },
    { id: 'authorization', name: 'Work Authorization', icon: Shield },
    { id: 'linkedin', name: 'LinkedIn Settings', icon: Globe }
  ]

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-2xl font-bold flex items-center">
                <Sparkles className="h-6 w-6 mr-2 text-purple-600" />
                Complete Your Profile
              </DialogTitle>
              <DialogDescription>
                Set up your comprehensive job application profile with skills tracking and automated responses.
              </DialogDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        {/* Message Display */}
        {message && (
          <div className={`p-4 rounded-lg border ${
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

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{tab.name}</span>
              </button>
            )
          })}
        </div>

        {/* Tab Content */}
        <div className="mt-6">
          {/* Personal Info Tab */}
          {activeTab === 'personal' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    value={userProfile.firstName}
                    onChange={(e) => setUserProfile(prev => ({...prev, firstName: e.target.value}))}
                    placeholder="John"
                  />
                </div>
                <div>
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    value={userProfile.lastName}
                    onChange={(e) => setUserProfile(prev => ({...prev, lastName: e.target.value}))}
                    placeholder="Doe"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={userProfile.email}
                  onChange={(e) => setUserProfile(prev => ({...prev, email: e.target.value}))}
                  placeholder="john.doe@example.com"
                />
              </div>

              <div>
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={userProfile.phone}
                  onChange={(e) => setUserProfile(prev => ({...prev, phone: e.target.value}))}
                  placeholder="+1 (555) 123-4567"
                />
              </div>

              <div>
                <Label htmlFor="website">Website/Portfolio</Label>
                <Input
                  id="website"
                  type="url"
                  value={userProfile.website}
                  onChange={(e) => setUserProfile(prev => ({...prev, website: e.target.value}))}
                  placeholder="https://yourportfolio.com"
                />
              </div>
            </div>
          )}

          {/* Contact & Location Tab */}
          {activeTab === 'contact' && (
            <div className="space-y-6">
              <div>
                <Label htmlFor="streetAddress">Street Address</Label>
                <Input
                  id="streetAddress"
                  value={personalDetails.streetAddress}
                  onChange={(e) => setPersonalDetails(prev => ({...prev, streetAddress: e.target.value}))}
                  placeholder="123 Main St"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={personalDetails.city}
                    onChange={(e) => setPersonalDetails(prev => ({...prev, city: e.target.value}))}
                    placeholder="New York"
                  />
                </div>
                <div>
                  <Label htmlFor="state">State</Label>
                  <Input
                    id="state"
                    value={personalDetails.state}
                    onChange={(e) => setPersonalDetails(prev => ({...prev, state: e.target.value}))}
                    placeholder="NY"
                  />
                </div>
                <div>
                  <Label htmlFor="zipCode">ZIP Code</Label>
                  <Input
                    id="zipCode"
                    value={personalDetails.zipCode}
                    onChange={(e) => setPersonalDetails(prev => ({...prev, zipCode: e.target.value}))}
                    placeholder="10001"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="linkedinUrl">LinkedIn Profile URL</Label>
                <Input
                  id="linkedinUrl"
                  type="url"
                  value={personalDetails.linkedinUrl}
                  onChange={(e) => setPersonalDetails(prev => ({...prev, linkedinUrl: e.target.value}))}
                  placeholder="https://linkedin.com/in/yourprofile"
                />
              </div>
            </div>
          )}

          {/* Skills & Experience Tab */}
          {activeTab === 'skills' && (
            <div className="space-y-6">
              <div>
                <Label htmlFor="yearsOfExperience">Years of Experience</Label>
                <Select
                  value={skillsExperience.yearsOfExperience}
                  onValueChange={(value) => setSkillsExperience(prev => ({...prev, yearsOfExperience: value}))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0-1">0-1 years</SelectItem>
                    <SelectItem value="1-3">1-3 years</SelectItem>
                    <SelectItem value="3-5">3-5 years</SelectItem>
                    <SelectItem value="5-10">5-10 years</SelectItem>
                    <SelectItem value="10+">10+ years</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Skills</Label>
                <div className="flex gap-2 mb-2">
                  <Input
                    value={skillsExperience.newSkill}
                    onChange={(e) => setSkillsExperience(prev => ({...prev, newSkill: e.target.value}))}
                    placeholder="Add a skill (e.g., Python, React)"
                    onKeyPress={(e) => e.key === 'Enter' && addSkill(skillsExperience.newSkill)}
                  />
                  <Button onClick={() => addSkill(skillsExperience.newSkill)} size="sm">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {skillsExperience.skills.map((skill) => (
                    <div key={skill} className="flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                      {skill}
                      <button
                        onClick={() => removeSkill(skill)}
                        className="ml-2 text-blue-600 hover:text-blue-800"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label>Target Job Titles</Label>
                <div className="flex gap-2 mb-2">
                  <Input
                    value={skillsExperience.newJobTitle}
                    onChange={(e) => setSkillsExperience(prev => ({...prev, newJobTitle: e.target.value}))}
                    placeholder="Add job title (e.g., Software Engineer)"
                    onKeyPress={(e) => e.key === 'Enter' && addJobTitle(skillsExperience.newJobTitle)}
                  />
                  <Button onClick={() => addJobTitle(skillsExperience.newJobTitle)} size="sm">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {skillsExperience.jobTitles.map((title) => (
                    <div key={title} className="flex items-center bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                      {title}
                      <button
                        onClick={() => removeJobTitle(title)}
                        className="ml-2 text-green-600 hover:text-green-800"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label>Target Locations</Label>
                <div className="flex gap-2 mb-2">
                  <Input
                    value={skillsExperience.newLocation}
                    onChange={(e) => setSkillsExperience(prev => ({...prev, newLocation: e.target.value}))}
                    placeholder="Add location (e.g., New York, NY)"
                    onKeyPress={(e) => e.key === 'Enter' && addLocation(skillsExperience.newLocation)}
                  />
                  <Button onClick={() => addLocation(skillsExperience.newLocation)} size="sm">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {skillsExperience.locations.map((location) => (
                    <div key={location} className="flex items-center bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                      {location}
                      <button
                        onClick={() => removeLocation(location)}
                        className="ml-2 text-purple-600 hover:text-purple-800"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Job Preferences Tab */}
          {activeTab === 'preferences' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="desiredSalary">Desired Salary</Label>
                  <Input
                    id="desiredSalary"
                    value={jobPreferences.desiredSalary}
                    onChange={(e) => setJobPreferences(prev => ({...prev, desiredSalary: e.target.value}))}
                    placeholder="75000"
                  />
                </div>
                <div>
                  <Label htmlFor="salaryType">Salary Type</Label>
                  <Select
                    value={jobPreferences.salaryType}
                    onValueChange={(value) => setJobPreferences(prev => ({...prev, salaryType: value}))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="yearly">Yearly</SelectItem>
                      <SelectItem value="hourly">Hourly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="remotePreference">Remote Preference</Label>
                <Select
                  value={jobPreferences.remotePreference}
                  onValueChange={(value) => setJobPreferences(prev => ({...prev, remotePreference: value}))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="remote">Remote Only</SelectItem>
                    <SelectItem value="hybrid">Hybrid</SelectItem>
                    <SelectItem value="onsite">On-site</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          {/* Work Authorization Tab */}
          {activeTab === 'authorization' && (
            <div className="space-y-6">
              <div>
                <Label htmlFor="degreeCompleted">Highest Education</Label>
                <Select
                  value={workAuthorization.degreeCompleted}
                  onValueChange={(value) => setWorkAuthorization(prev => ({...prev, degreeCompleted: value}))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="High School">High School</SelectItem>
                    <SelectItem value="Associate's Degree">Associate's Degree</SelectItem>
                    <SelectItem value="Bachelor's Degree">Bachelor's Degree</SelectItem>
                    <SelectItem value="Master's Degree">Master's Degree</SelectItem>
                    <SelectItem value="PhD">PhD</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="usCitizen"
                    checked={workAuthorization.usCitizen}
                    onChange={(e) => setWorkAuthorization(prev => ({...prev, usCitizen: e.target.checked}))}
                    className="rounded"
                  />
                  <Label htmlFor="usCitizen">US Citizen</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="legallyAuthorized"
                    checked={workAuthorization.legallyAuthorized}
                    onChange={(e) => setWorkAuthorization(prev => ({...prev, legallyAuthorized: e.target.checked}))}
                    className="rounded"
                  />
                  <Label htmlFor="legallyAuthorized">Legally authorized to work in the US</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="requireVisa"
                    checked={workAuthorization.requireVisa}
                    onChange={(e) => setWorkAuthorization(prev => ({...prev, requireVisa: e.target.checked}))}
                    className="rounded"
                  />
                  <Label htmlFor="requireVisa">Will require visa sponsorship</Label>
                </div>
              </div>
            </div>
          )}

          {/* LinkedIn Settings Tab */}
          {activeTab === 'linkedin' && (
            <div className="space-y-6">
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
                    <span>Add your skills and target job titles for better matching</span>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                    <span>Set your preferred locations and salary expectations</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between items-center pt-6 border-t">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <div className="flex space-x-2">
            <Button 
              onClick={saveProfile}
              disabled={loading}
              variant="outline"
            >
              <Save className="h-4 w-4 mr-2" />
              Save Profile
            </Button>
            <Button 
              onClick={onClose}
              disabled={loading}
              className="bg-gradient-to-r from-blue-500 to-purple-600"
            >
              Done
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
} 