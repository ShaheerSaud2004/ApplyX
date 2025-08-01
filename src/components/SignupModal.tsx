'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useAuth } from '@/components/AuthProvider'
import { getApiUrl } from '@/lib/utils'
import { CheckCircle2, Mail, Clock, X } from 'lucide-react'
import Link from 'next/link'
import { PrivacyPolicyModal } from './PrivacyPolicyModal'

interface SignupModalProps {
  isOpen: boolean
  onOpenChange: (open: boolean) => void
  onSwitchToLogin?: () => void
}

export function SignupModal({ isOpen, onOpenChange, onSwitchToLogin }: SignupModalProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [acceptTerms, setAcceptTerms] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [emailError, setEmailError] = useState('')
  const [isEmailValid, setIsEmailValid] = useState(false)
  const [passwordRequirements, setPasswordRequirements] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false
  })
  const [isPrivacyModalOpen, setIsPrivacyModalOpen] = useState(false)

  const { login } = useAuth()

  // Email validation function
  const validateEmail = (email: string) => {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    
    if (!email) {
      setEmailError('Email is required')
      setIsEmailValid(false)
      return false
    }
    
    if (!emailPattern.test(email)) {
      setEmailError('Please enter a valid email address')
      setIsEmailValid(false)
      return false
    }
    
    // Additional checks
    if (email.includes('..')) {
      setEmailError('Email cannot contain consecutive dots')
      setIsEmailValid(false)
      return false
    }
    
    if (email.startsWith('.') || email.startsWith('@') || email.endsWith('.')) {
      setEmailError('Invalid email format')
      setIsEmailValid(false)
      return false
    }
    
    const [localPart, domainPart] = email.split('@')
    if (!localPart || !domainPart || !domainPart.includes('.')) {
      setEmailError('Invalid email format')
      setIsEmailValid(false)
      return false
    }
    
    setEmailError('')
    setIsEmailValid(true)
    return true
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value
    setEmail(newEmail)
    validateEmail(newEmail)
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value
    setPassword(newPassword)
    
    // Update password requirements
    setPasswordRequirements({
      length: newPassword.length >= 8,
      uppercase: /[A-Z]/.test(newPassword),
      lowercase: /[a-z]/.test(newPassword),
      number: /\d/.test(newPassword),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(newPassword)
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    // Validation
    if (!validateEmail(email)) {
      setError('Please fix the email validation errors')
      setIsLoading(false)
      return
    }

    // Check password requirements
    const allRequirementsMet = Object.values(passwordRequirements).every(req => req)
    if (!allRequirementsMet) {
      setError('Please ensure your password meets all requirements')
      setIsLoading(false)
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      setIsLoading(false)
      return
    }

    if (!acceptTerms) {
      setError('Please accept the terms and conditions')
      setIsLoading(false)
      return
    }

    try {
      const response = await fetch(getApiUrl('/api/auth/register'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      })

      if (response.ok) {
        const data = await response.json()
        
        // Check if user needs approval
        if (data.status === 'pending') {
          // Show success modal for pending approval
          setError('')
          setShowSuccessModal(true)
          
          // Clear form
          setName('')
          setEmail('')
          setPassword('')
          setConfirmPassword('')
          setAcceptTerms(false)
        } else if (data.token) {
          // Old flow for auto-approved users (if any)
          login(data.token, data.user)
          onOpenChange(false)
          setName('')
          setEmail('')
          setPassword('')
          setConfirmPassword('')
          setError('')
        }
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Registration failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuccessClose = () => {
    setShowSuccessModal(false)
    onOpenChange(false)
  }

  return (
    <>
      <Dialog open={isOpen && !showSuccessModal} onOpenChange={onOpenChange}>
        <DialogContent className="w-[95vw] max-w-md mx-auto relative max-h-[90vh] overflow-y-auto">
          {/* Mobile Close Button */}
          <button
            onClick={() => onOpenChange(false)}
            className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 transition-colors md:hidden"
          >
            <X className="h-5 w-5" />
          </button>
          <DialogHeader className="space-y-3">
            <div className="flex justify-center">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                  </svg>
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-br from-orange-500 to-red-500 rounded-full"></div>
              </div>
            </div>
            <div className="text-center">
              <DialogTitle className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ApplyX
              </DialogTitle>
              <p className="text-xs text-muted-foreground">by Nebula.AI</p>
            </div>
            <DialogTitle className="text-2xl font-bold text-center">Join the Future of Job Applications</DialogTitle>
            <DialogDescription className="text-center">
              Get early access to AI-powered job applications
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                type="text"
                placeholder="Enter your full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={handleEmailChange}
                required
                className={`w-full ${emailError ? 'border-red-500 focus:border-red-500' : isEmailValid ? 'border-green-500 focus:border-green-500' : ''}`}
              />
              {emailError && (
                <p className="text-red-500 text-sm mt-1">{emailError}</p>
              )}
              {isEmailValid && !emailError && (
                <p className="text-green-500 text-sm mt-1">✓ Valid email address</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Create a password"
                value={password}
                onChange={handlePasswordChange}
                required
                className="w-full"
              />
              
              {/* Password Requirements */}
              <div className="mt-2 space-y-1">
                <p className="text-xs font-medium text-gray-600 mb-2">Password Requirements:</p>
                <div className="space-y-1">
                  <div className={`flex items-center text-xs ${passwordRequirements.length ? 'text-green-600' : 'text-gray-500'}`}>
                    <div className={`w-2 h-2 rounded-full mr-2 ${passwordRequirements.length ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    At least 8 characters
                  </div>
                  <div className={`flex items-center text-xs ${passwordRequirements.uppercase ? 'text-green-600' : 'text-gray-500'}`}>
                    <div className={`w-2 h-2 rounded-full mr-2 ${passwordRequirements.uppercase ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    One uppercase letter (A-Z)
                  </div>
                  <div className={`flex items-center text-xs ${passwordRequirements.lowercase ? 'text-green-600' : 'text-gray-500'}`}>
                    <div className={`w-2 h-2 rounded-full mr-2 ${passwordRequirements.lowercase ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    One lowercase letter (a-z)
                  </div>
                  <div className={`flex items-center text-xs ${passwordRequirements.number ? 'text-green-600' : 'text-gray-500'}`}>
                    <div className={`w-2 h-2 rounded-full mr-2 ${passwordRequirements.number ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    One number (0-9)
                  </div>
                  <div className={`flex items-center text-xs ${passwordRequirements.special ? 'text-green-600' : 'text-gray-500'}`}>
                    <div className={`w-2 h-2 rounded-full mr-2 ${passwordRequirements.special ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    One special character (!@#$%^&*)
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="w-full"
              />
            </div>

            <div className="flex items-start space-x-2">
              <Checkbox
                id="terms"
                checked={acceptTerms}
                onCheckedChange={(checked) => setAcceptTerms(checked as boolean)}
                className="mt-1"
              />
              <Label htmlFor="terms" className="text-sm leading-relaxed">
                I agree to the{' '}
                <Link href="/terms" target="_blank" className="text-blue-600 hover:underline">
                  Terms of Service
                </Link>
                {' '}and{' '}
                <button 
                  type="button"
                  onClick={() => setIsPrivacyModalOpen(true)}
                  className="text-blue-600 hover:underline cursor-pointer"
                >
                  Privacy Policy
                </button>
              </Label>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200" 
              disabled={isLoading}
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Button>
          </form>

          <div className="text-center text-sm">
            <span className="text-muted-foreground">Already have an account? </span>
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="text-blue-600 hover:underline font-medium"
            >
              Sign in
            </button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Success Modal for Waitlist */}
      <Dialog open={showSuccessModal} onOpenChange={setShowSuccessModal}>
        <DialogContent className="sm:max-w-md relative">
          {/* Mobile Close Button */}
          <button
            onClick={() => setShowSuccessModal(false)}
            className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 transition-colors md:hidden"
          >
            <X className="h-5 w-5" />
          </button>
          <div className="text-center space-y-6 py-4">
            <div className="flex justify-center">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
                  <CheckCircle2 className="h-8 w-8 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
                  <Clock className="h-3 w-3 text-white" />
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h2 className="text-2xl font-bold text-gray-900">
                🎉 Welcome to the Waitlist!
              </h2>
              <p className="text-gray-600 text-sm leading-relaxed">
                Thank you for signing up! Your account has been created and added to our exclusive waitlist.
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
              <div className="flex items-start space-x-3">
                <Mail className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="text-left">
                  <p className="text-sm font-medium text-blue-900">Check your email!</p>
                  <p className="text-xs text-blue-700">
                    You'll receive an approval notification once our admin reviews your account.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <p className="text-xs text-gray-500">
                <strong>What's next?</strong><br/>
                Our team will review your application and send you login credentials within 24 hours.
              </p>
              
              <Button 
                onClick={handleSuccessClose}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                Got it, thanks!
              </Button>
              
              <button
                onClick={() => {
                  handleSuccessClose()
                  onSwitchToLogin?.()
                }}
                className="text-sm text-blue-600 hover:underline"
              >
                Back to Sign In
              </button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
      
      {/* Privacy Policy Modal */}
      <PrivacyPolicyModal 
        isOpen={isPrivacyModalOpen}
        onClose={() => setIsPrivacyModalOpen(false)}
      />
    </>
  )
} 