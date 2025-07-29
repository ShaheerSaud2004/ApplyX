'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from '@/components/ui/dialog'
import { AlertCircle, CheckCircle, Shield, Eye, EyeOff } from 'lucide-react'
import { useAuth } from './AuthProvider'

interface LinkedInCredentialsModalProps {
  isOpen: boolean
  onOpenChange: (open: boolean) => void
  onCredentialsSaved?: () => void
}

export function LinkedInCredentialsModal({ 
  isOpen, 
  onOpenChange, 
  onCredentialsSaved 
}: LinkedInCredentialsModalProps) {
  const { token } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isVerifying, setIsVerifying] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [verificationStatus, setVerificationStatus] = useState<'none' | 'success' | 'failed'>('none')

  const verifyCredentials = async () => {
    if (!email || !password) {
      setError('Both email and password are required for verification')
      return
    }

    setIsVerifying(true)
    setError('')
    setVerificationStatus('none')

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/linkedin/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email,
          password
        })
      })

      const data = await response.json()

      if (response.ok && data.verified) {
        setVerificationStatus('success')
        setSuccess(data.message)
      } else {
        setVerificationStatus('failed')
        setError(data.message || 'Verification failed')
      }
    } catch (err) {
      setVerificationStatus('failed')
      setError('Network error during verification. Please try again.')
    } finally {
      setIsVerifying(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    setSuccess('')

    if (!email || !password) {
      setError('Both email and password are required')
      setIsLoading(false)
      return
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          linkedin_email: email,
          linkedin_password: password
        })
      })

      if (response.ok) {
        setSuccess('LinkedIn credentials saved securely!')
        
        setTimeout(() => {
          setEmail('')
          setPassword('')
          setVerificationStatus('none')
          onCredentialsSaved?.()
          onOpenChange(false)
        }, 1500)
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Failed to save credentials')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    setEmail('')
    setPassword('')
    setError('')
    setSuccess('')
    setVerificationStatus('none')
    onOpenChange(false)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-blue-600" />
            LinkedIn Credentials Required
          </DialogTitle>
          <DialogDescription>
            To start the AI agent, we need your LinkedIn credentials to apply to jobs on your behalf. 
            Your credentials are encrypted and stored securely.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm text-red-600">{error}</span>
            </div>
          )}

          {success && (
            <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-md">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm text-green-600">{success}</span>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="linkedin-email">LinkedIn Email</Label>
            <Input
              id="linkedin-email"
              type="email"
              placeholder="your-email@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="username"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="linkedin-password">LinkedIn Password</Label>
            <div className="relative">
              <Input
                id="linkedin-password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your LinkedIn password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
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

          {/* Verification Section */}
          {email && password && (
            <div className="space-y-2">
              <Button
                type="button"
                variant="outline"
                onClick={verifyCredentials}
                disabled={isVerifying || isLoading}
                className="w-full"
              >
                {isVerifying ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                    Verifying...
                  </>
                ) : (
                  <>
                    <Shield className="h-4 w-4 mr-2" />
                    Verify LinkedIn Credentials
                  </>
                )}
              </Button>

              {verificationStatus === 'success' && (
                <div className="flex items-center gap-2 p-2 bg-green-50 border border-green-200 rounded-md">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-700">✅ LinkedIn credentials verified!</span>
                </div>
              )}

              {verificationStatus === 'failed' && (
                <div className="flex items-center gap-2 p-2 bg-red-50 border border-red-200 rounded-md">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-700">❌ Verification failed</span>
                </div>
              )}
            </div>
          )}

          {/* Security Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <div className="flex items-start gap-3">
              <Shield className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="font-medium text-blue-900 mb-1">Your credentials are secure</p>
                <ul className="text-blue-700 space-y-1">
                  <li>• Encrypted with industry-standard AES-256</li>
                  <li>• Never shared with third parties</li>
                  <li>• Only used for job applications on your behalf</li>
                  <li>• You can delete them anytime</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={handleCancel}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isLoading || !email || !password}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isLoading ? 'Saving...' : 'Save & Continue'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
} 