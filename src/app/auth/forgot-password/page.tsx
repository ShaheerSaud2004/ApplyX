'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { getApiUrl } from '@/lib/utils'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [emailSent, setEmailSent] = useState(false)
  const [emailError, setEmailError] = useState('')
  const [isEmailValid, setIsEmailValid] = useState(false)

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage({ type: '', text: '' })

    // Validate email
    if (!validateEmail(email)) {
      setMessage({ type: 'error', text: 'Please enter a valid email address' })
      setLoading(false)
      return
    }

    try {
      const response = await fetch(getApiUrl('/api/auth/forgot-password'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (response.ok) {
        setEmailSent(true)
        setMessage({ 
          type: 'success', 
          text: 'Password reset instructions have been sent to your email address.' 
        })
      } else {
        setMessage({ 
          type: 'error', 
          text: data.error || 'Failed to send reset email. Please try again.' 
        })
      }
    } catch (err) {
      setMessage({ 
        type: 'error', 
        text: 'Network error. Please check your connection and try again.' 
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                </svg>
              </div>
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-br from-orange-500 to-red-500 rounded-full"></div>
            </div>
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            ApplyX
          </h2>
          <p className="text-sm text-gray-500">by Nebula.AI</p>
        </div>

        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-bold">
              {emailSent ? 'Check Your Email' : 'Forgot Password?'}
            </CardTitle>
            <CardDescription>
              {emailSent 
                ? 'We sent password reset instructions to your email'
                : 'Enter your email address and we\'ll send you a link to reset your password'
              }
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            {message.text && (
              <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
                message.type === 'success' 
                  ? 'bg-green-50 text-green-700 border border-green-200' 
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}>
                {message.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
                {message.text}
              </div>
            )}

            {!emailSent ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={handleEmailChange}
                    placeholder="Enter your email address"
                    className={`w-full ${emailError ? 'border-red-500 focus:border-red-500' : isEmailValid ? 'border-green-500 focus:border-green-500' : ''}`}
                  />
                  {emailError && (
                    <p className="text-red-500 text-sm mt-1">{emailError}</p>
                  )}
                  {isEmailValid && !emailError && (
                    <p className="text-green-500 text-sm mt-1">✓ Valid email address</p>
                  )}
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700" 
                  disabled={loading}
                >
                  {loading ? 'Sending...' : 'Send Reset Instructions'}
                </Button>
              </form>
            ) : (
              <div className="space-y-4">
                <div className="text-center p-6 bg-green-50 rounded-lg border border-green-200">
                  <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
                  <p className="text-sm text-green-700">
                    If an account with that email exists, you'll receive password reset instructions shortly.
                  </p>
                </div>
                
                <Button 
                  onClick={() => {
                    setEmailSent(false)
                    setEmail('')
                    setMessage({ type: '', text: '' })
                  }}
                  variant="outline" 
                  className="w-full"
                >
                  Send Another Email
                </Button>
              </div>
            )}

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="bg-white px-2 text-muted-foreground">Remember your password?</span>
                </div>
              </div>
              
              <Link href="/auth/login" className="mt-4 flex items-center justify-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium">
                <ArrowLeft className="h-4 w-4" />
                Back to Sign In
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 