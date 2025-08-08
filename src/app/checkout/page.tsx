'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, CheckCircle, CreditCard, Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/components/AuthProvider'
import { getApiUrl } from '@/lib/utils'

const plans = {
  free: {
    name: 'Free',
    price: 0,
    features: ['10 applications per day', 'Basic AI resume tailoring', 'Application tracking']
  },
  basic: {
    name: 'Basic',
    price: 9.99,
    features: ['60 applications per day', 'Advanced AI resume optimization', 'Custom cover letters', 'Priority support']
  },
  pro: {
    name: 'Pro',
    price: 9.99,
    features: ['100+ applications per day', 'Premium AI features', 'Advanced analytics', 'Dedicated support']
  }
}

export default function CheckoutPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user, token } = useAuth()
  const [selectedPlan, setSelectedPlan] = useState('basic')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const plan = searchParams.get('plan')
    if (plan && plans[plan as keyof typeof plans]) {
      setSelectedPlan(plan)
    }
  }, [searchParams])

  const handleCheckout = async () => {
    if (!user || !token) {
      router.push('/auth/login?redirect=/checkout')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(getApiUrl('/api/user/upgrade-plan'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan: selectedPlan
        })
      })

      if (response.ok) {
        // Redirect to dashboard with success message
        router.push('/dashboard?upgrade=success')
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Failed to process checkout')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const selectedPlanData = plans[selectedPlan as keyof typeof plans]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="px-3 sm:px-4 lg:px-6 h-14 flex items-center border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <Link href="/" className="flex items-center space-x-2">
          <Button variant="ghost" size="sm" className="p-0 h-auto">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </Link>
        <div className="ml-auto">
          <h1 className="text-lg font-semibold">Checkout</h1>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-3 sm:px-4 py-6 sm:py-8 max-w-4xl">
        <div className="grid gap-8 md:grid-cols-2">
          {/* Plan Summary */}
          <Card className="border-2 border-blue-500 shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl text-center">Plan Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-bold">{selectedPlanData.name} Plan</h3>
                <div className="text-3xl font-bold text-blue-600 mt-2">
                  ${selectedPlanData.price}
                  {selectedPlanData.price > 0 && <span className="text-lg font-normal text-gray-500">/month</span>}
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="font-semibold">What's included:</h4>
                <ul className="space-y-2">
                  {selectedPlanData.features.map((feature, index) => (
                    <li key={index} className="flex items-center text-sm">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              {selectedPlanData.price > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 text-blue-800">
                    <Shield className="h-4 w-4" />
                    <span className="text-sm font-medium">Secure Payment</span>
                  </div>
                  <p className="text-xs text-blue-600 mt-1">
                    Your payment information is encrypted and secure
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Checkout Form */}
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Complete Your Order</CardTitle>
              <CardDescription>
                {selectedPlanData.price === 0 
                  ? 'Start your free plan immediately' 
                  : 'Enter your payment details to continue'
                }
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {!user ? (
                <div className="text-center space-y-4">
                  <p className="text-gray-600">Please sign in to continue with your purchase</p>
                  <div className="space-y-2">
                    <Button asChild className="w-full">
                      <Link href="/auth/login?redirect=/checkout">Sign In</Link>
                    </Button>
                    <Button asChild variant="outline" className="w-full">
                      <Link href="/auth/signup?redirect=/checkout">Create Account</Link>
                    </Button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 text-green-800">
                      <CheckCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">Signed in as {user.email}</span>
                    </div>
                  </div>

                  {selectedPlanData.price > 0 ? (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="card-number">Card Number</Label>
                        <div className="relative">
                          <CreditCard className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                          <Input
                            id="card-number"
                            placeholder="1234 5678 9012 3456"
                            className="pl-10"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="expiry">Expiry Date</Label>
                          <Input id="expiry" placeholder="MM/YY" />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="cvv">CVV</Label>
                          <Input id="cvv" placeholder="123" />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="name">Cardholder Name</Label>
                        <Input id="name" placeholder="John Doe" />
                      </div>
                    </div>
                  ) : (
                    <div className="text-center space-y-4">
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <p className="text-blue-800 font-medium">Free Plan Selected</p>
                        <p className="text-blue-600 text-sm mt-1">No payment required</p>
                      </div>
                    </div>
                  )}

                  {error && (
                    <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
                      {error}
                    </div>
                  )}

                  <Button 
                    onClick={handleCheckout}
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    {isLoading ? 'Processing...' : selectedPlanData.price === 0 ? 'Start Free Plan' : 'Complete Purchase'}
                  </Button>

                  <p className="text-xs text-gray-500 text-center">
                    By completing your purchase, you agree to our{' '}
                    <Link href="/terms" className="text-blue-600 hover:underline">Terms of Service</Link>
                    {' '}and{' '}
                    <Link href="/privacy" className="text-blue-600 hover:underline">Privacy Policy</Link>
                  </p>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Footer */}
      <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t bg-white/80 backdrop-blur-sm relative z-10 mt-auto">
        <div className="flex items-center space-x-2">
          <p className="text-xs text-gray-500">© 2024 ApplyX</p>
          <span className="text-xs text-gray-300">•</span>
          <p className="text-xs text-gray-500">A product of Nebula.AI</p>
          <span className="text-xs text-gray-300">•</span>
          <p className="text-xs text-gray-500">All rights reserved.</p>
        </div>
        <nav className="sm:ml-auto flex gap-4 sm:gap-6">
          <Link className="text-xs hover:underline underline-offset-4 text-gray-500 hover:text-blue-600" href="/terms">
            Terms of Service
          </Link>
          <Link className="text-xs hover:underline underline-offset-4 text-gray-500 hover:text-blue-600" href="/privacy">
            Privacy Policy
          </Link>
        </nav>
      </footer>
    </div>
  )
} 