'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  User, 
  Shield, 
  Settings,
  Save,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '@/components/AuthProvider'

export default function ProfilePage() {
  const { token } = useAuth()
  const [user, setUser] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    website: ''
  })

  const [linkedinCreds, setLinkedinCreds] = useState({
    email: '',
    password: ''
  })

  const [jobPreferences, setJobPreferences] = useState({
    jobTitles: '',
    locations: '',
    remote: true,
    experience: 'mid',
    salaryMin: '',
    skills: ''
  })

  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUser(data.user || {})
        setLinkedinCreds(data.linkedinCreds || {})
        setJobPreferences(data.jobPreferences || {})
      }
    } catch (error) {
      console.error('Error fetching profile:', error)
    }
  }

  const saveProfile = async () => {
    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await fetch('http://localhost:5001/api/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user,
          linkedinCreds,
          jobPreferences
        })
      })

      const data = await response.json()

      if (response.ok) {
        setMessage({ type: 'success', text: 'Profile saved successfully!' })
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to save profile' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="px-4 lg:px-6 h-14 flex items-center border-b">
        <Link className="flex items-center justify-center" href="/">
          <span className="ml-2 text-lg font-semibold">Teemo AI</span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/dashboard">
            Dashboard
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/profile">
            Profile
          </Link>
        </nav>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">Profile Settings</h1>
            <p className="text-muted-foreground">
              Configure your account, LinkedIn credentials, and job preferences
            </p>
          </div>

          {message.text && (
            <div className={`flex items-center gap-2 p-4 rounded-lg ${
              message.type === 'success' 
                ? 'bg-green-50 text-green-700 border border-green-200' 
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {message.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
              {message.text}
            </div>
          )}

          {/* Personal Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Personal Information
              </CardTitle>
              <CardDescription>
                Update your personal details and contact information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    value={user.firstName}
                    onChange={(e) => setUser({...user, firstName: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    value={user.lastName}
                    onChange={(e) => setUser({...user, lastName: e.target.value})}
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={user.email}
                  onChange={(e) => setUser({...user, email: e.target.value})}
                  disabled
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    value={user.phone}
                    onChange={(e) => setUser({...user, phone: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="website">Website</Label>
                  <Input
                    id="website"
                    value={user.website}
                    onChange={(e) => setUser({...user, website: e.target.value})}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* LinkedIn Credentials */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                LinkedIn Credentials
              </CardTitle>
              <CardDescription>
                Your LinkedIn credentials are encrypted and stored securely. These are used by the AI agent to apply to jobs on your behalf.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                  <div className="text-sm text-blue-700">
                    <p className="font-medium">Security Notice:</p>
                    <p>We recommend using a dedicated LinkedIn account for job applications. Your credentials are encrypted using industry-standard security.</p>
                  </div>
                </div>
              </div>

              <div>
                <Label htmlFor="linkedinEmail">LinkedIn Email</Label>
                <Input
                  id="linkedinEmail"
                  type="email"
                  value={linkedinCreds.email}
                  onChange={(e) => setLinkedinCreds({...linkedinCreds, email: e.target.value})}
                  placeholder="your-linkedin-email@example.com"
                />
              </div>

              <div>
                <Label htmlFor="linkedinPassword">LinkedIn Password</Label>
                <div className="relative">
                  <Input
                    id="linkedinPassword"
                    type={showPassword ? "text" : "password"}
                    value={linkedinCreds.password}
                    onChange={(e) => setLinkedinCreds({...linkedinCreds, password: e.target.value})}
                    placeholder="Your LinkedIn password"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Job Preferences */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Job Preferences
              </CardTitle>
              <CardDescription>
                Configure what types of jobs the AI agent should apply for
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="jobTitles">Job Titles</Label>
                <Input
                  id="jobTitles"
                  value={jobPreferences.jobTitles}
                  onChange={(e) => setJobPreferences({...jobPreferences, jobTitles: e.target.value})}
                  placeholder="Software Engineer, Frontend Developer, Full Stack Developer"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Separate multiple job titles with commas
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="locations">Preferred Locations</Label>
                  <Input
                    id="locations"
                    value={jobPreferences.locations}
                    onChange={(e) => setJobPreferences({...jobPreferences, locations: e.target.value})}
                    placeholder="New York, San Francisco, Remote"
                  />
                </div>
                <div>
                  <Label htmlFor="experience">Experience Level</Label>
                  <select
                    id="experience"
                    value={jobPreferences.experience}
                    onChange={(e) => setJobPreferences({...jobPreferences, experience: e.target.value})}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                  >
                    <option value="entry">Entry Level</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior Level</option>
                    <option value="lead">Lead/Principal</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="salaryMin">Minimum Salary</Label>
                  <Input
                    id="salaryMin"
                    type="number"
                    value={jobPreferences.salaryMin}
                    onChange={(e) => setJobPreferences({...jobPreferences, salaryMin: e.target.value})}
                    placeholder="80000"
                  />
                </div>
                <div className="flex items-center space-x-2 pt-6">
                  <input
                    id="remote"
                    type="checkbox"
                    checked={jobPreferences.remote}
                    onChange={(e) => setJobPreferences({...jobPreferences, remote: e.target.checked})}
                  />
                  <Label htmlFor="remote">Include Remote Jobs</Label>
                </div>
              </div>

              <div>
                <Label htmlFor="skills">Skills & Keywords</Label>
                <Input
                  id="skills"
                  value={jobPreferences.skills}
                  onChange={(e) => setJobPreferences({...jobPreferences, skills: e.target.value})}
                  placeholder="React, Python, JavaScript, AWS, Node.js"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Skills to highlight in applications
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button onClick={saveProfile} disabled={loading} size="lg">
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Saving...' : 'Save Profile'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
} 