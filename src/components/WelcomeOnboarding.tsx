'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { CheckCircle, ArrowRight, Bot, Target, Upload } from 'lucide-react'
import { ResumeUploadModal } from './ResumeUploadModal'

interface WelcomeOnboardingProps {
  onComplete?: () => void
  onSkip?: () => void
}

export const WelcomeOnboarding: React.FC<WelcomeOnboardingProps> = ({
  onComplete,
  onSkip
}) => {
  const [currentStep, setCurrentStep] = useState(1)
  const [showResumeUpload, setShowResumeUpload] = useState(false)
  const [formData, setFormData] = useState({
    jobPreferences: '',
    location: '',
    experience: '',
    resumeUploaded: false,
    uploadedResumeName: ''
  })

  const totalSteps = 4
  const progress = (currentStep / totalSteps) * 100

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    } else {
      onComplete?.()
    }
  }

  const handleSkip = () => {
    onSkip?.()
  }

  const updateFormData = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleResumeUploadSuccess = (filename: string) => {
    updateFormData('resumeUploaded', true)
    updateFormData('uploadedResumeName', filename)
    setShowResumeUpload(false)
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <Bot className="w-16 h-16 mx-auto mb-4 text-blue-500" />
              <h2 className="text-2xl font-bold mb-2">Welcome to ApplyX!</h2>
              <p className="text-gray-600">Let's set up your AI-powered job application assistant</p>
            </div>
            <div className="text-center">
              <p className="mb-4">This quick setup will help us customize your job search experience.</p>
              <p className="text-sm text-gray-500">It will only take 2-3 minutes to complete.</p>
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <Target className="w-16 h-16 mx-auto mb-4 text-green-500" />
              <h2 className="text-2xl font-bold mb-2">Job Preferences</h2>
              <p className="text-gray-600">Tell us what kind of job you're looking for</p>
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="jobPreferences">Job Title/Keywords</Label>
                <Input
                  id="jobPreferences"
                  placeholder="e.g., Software Engineer, Marketing Manager"
                  value={formData.jobPreferences}
                  onChange={(e) => updateFormData('jobPreferences', e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="location">Preferred Location</Label>
                <Input
                  id="location"
                  placeholder="e.g., San Francisco, Remote, New York"
                  value={formData.location}
                  onChange={(e) => updateFormData('location', e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="experience">Experience Level</Label>
                <select
                  id="experience"
                  className="w-full p-2 border rounded-md"
                  value={formData.experience}
                  onChange={(e) => updateFormData('experience', e.target.value)}
                >
                  <option value="">Select experience level</option>
                  <option value="entry">Entry Level (0-2 years)</option>
                  <option value="mid">Mid Level (3-5 years)</option>
                  <option value="senior">Senior Level (6+ years)</option>
                  <option value="executive">Executive Level</option>
                </select>
              </div>
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <Upload className="w-16 h-16 mx-auto mb-4 text-purple-500" />
              <h2 className="text-2xl font-bold mb-2">Upload Resume</h2>
              <p className="text-gray-600">Upload your resume for better job matching</p>
            </div>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              {formData.resumeUploaded ? (
                <>
                  <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                  <p className="mb-2 text-green-600 font-medium">Resume uploaded successfully!</p>
                  <p className="text-sm text-gray-500 mb-4">{formData.uploadedResumeName}</p>
                  <div className="flex justify-center gap-2">
                    <Button variant="outline" onClick={() => setShowResumeUpload(true)}>
                      Upload Different Resume
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="mb-2">Upload your resume for better job matching</p>
                  <p className="text-sm text-gray-500 mb-4">Supports PDF, DOC, DOCX (Max 16MB)</p>
                  <Button onClick={() => setShowResumeUpload(true)}>
                    Choose File
                  </Button>
                </>
              )}
            </div>
          </div>
        )

      case 4:
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500" />
              <h2 className="text-2xl font-bold mb-2">Setup Complete!</h2>
              <p className="text-gray-600">Your AI assistant is ready to help you find jobs</p>
            </div>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span>Job Preferences</span>
                <CheckCircle className="w-4 h-4 text-green-500" />
              </div>
              {formData.resumeUploaded && (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span>Resume Uploaded</span>
                  <CheckCircle className="w-4 h-4 text-green-500" />
                </div>
              )}
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span>Ready to start applying!</span>
                <Bot className="w-4 h-4 text-blue-500" />
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <div className="flex justify-between items-center mb-2">
              <CardTitle className="text-lg">Setup Progress</CardTitle>
              <span className="text-sm text-gray-500">{currentStep}/{totalSteps}</span>
            </div>
            <Progress value={progress} className="w-full" />
          </CardHeader>
          <CardContent>
            {renderStep()}
            
            <div className="flex justify-between mt-8">
              <Button 
                variant="ghost" 
                onClick={handleSkip}
              >
                Skip for now
              </Button>
              <Button 
                onClick={handleNext}
                disabled={currentStep === 3 && !formData.resumeUploaded}
              >
                {currentStep === totalSteps ? 'Complete' : 'Next'}
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Resume Upload Modal */}
      <ResumeUploadModal 
        isOpen={showResumeUpload}
        onOpenChange={setShowResumeUpload}
        onUploadSuccess={handleResumeUploadSuccess}
      />
    </>
  )
}

export default WelcomeOnboarding 