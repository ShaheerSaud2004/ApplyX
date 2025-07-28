'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Check, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import { PRICING_PLANS } from '@/config/pricing'
import { SubscriptionPlan } from '@/types'

export default function PricingPage() {
  const handlePlanSelect = async (planId: SubscriptionPlan) => {
    if (planId === SubscriptionPlan.FREE) {
      // Redirect to signup for free plan
      window.location.href = '/auth/signup'
      return
    }

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        // Redirect to signup/login
        window.location.href = '/auth/signup'
        return
      }

      const response = await fetch('/api/stripe/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ plan_id: planId })
      })

      const data = await response.json()
      
      if (data.checkout_url) {
        window.location.href = data.checkout_url
      } else {
        alert('Error creating checkout session. Please try again.')
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Error processing payment. Please try again.')
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
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/">
            Home
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/dashboard">
            Dashboard
          </Link>
        </nav>
      </header>

      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Start free and upgrade as your job search accelerates. No hidden fees, cancel anytime.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {Object.values(PRICING_PLANS).map((plan) => (
            <Card 
              key={plan.id} 
              className={`relative ${
                plan.id === SubscriptionPlan.BASIC 
                  ? 'border-primary shadow-lg scale-105' 
                  : 'border-border'
              }`}
            >
              {plan.id === SubscriptionPlan.BASIC && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </span>
                </div>
              )}

              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                <div className="mt-4">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-muted-foreground">/month</span>
                </div>
                <CardDescription className="mt-2">
                  {plan.dailyApplications} applications per day
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                <ul className="space-y-3">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <Check className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button 
                  className="w-full mt-6" 
                  variant={plan.id === SubscriptionPlan.BASIC ? "default" : "outline"}
                  size="lg"
                  onClick={() => handlePlanSelect(plan.id)}
                >
                  {plan.id === SubscriptionPlan.FREE ? 'Get Started Free' : `Upgrade to ${plan.name}`}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mt-24 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Frequently Asked Questions
          </h2>
          
          <div className="space-y-8">
            <div className="bg-muted/50 rounded-lg p-6">
              <h3 className="font-semibold mb-2">How does the quota system work?</h3>
              <p className="text-muted-foreground">
                Your daily quota resets every 24 hours at midnight. Unused applications don't roll over to the next day, 
                ensuring fair usage across all users.
              </p>
            </div>

            <div className="bg-muted/50 rounded-lg p-6">
              <h3 className="font-semibold mb-2">Can I change my plan anytime?</h3>
              <p className="text-muted-foreground">
                Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately, 
                and you'll be charged or credited accordingly.
              </p>
            </div>

            <div className="bg-muted/50 rounded-lg p-6">
              <h3 className="font-semibold mb-2">What happens if I exceed my daily quota?</h3>
              <p className="text-muted-foreground">
                The agent will automatically stop when you reach your daily limit. You can upgrade your plan 
                or wait until the next day for your quota to reset.
              </p>
            </div>

            <div className="bg-muted/50 rounded-lg p-6">
              <h3 className="font-semibold mb-2">Is my data secure?</h3>
              <p className="text-muted-foreground">
                Absolutely. We use industry-standard encryption and never share your personal information. 
                Your resumes and application data are stored securely and only used for your job applications.
              </p>
            </div>

            <div className="bg-muted/50 rounded-lg p-6">
              <h3 className="font-semibold mb-2">How does the AI tailor my resume?</h3>
              <p className="text-muted-foreground">
                Our AI analyzes each job description and optimizes your resume by highlighting relevant skills, 
                adjusting keywords, and emphasizing experience that matches the role requirements.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center mt-24">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Automate Your Job Search?
          </h2>
          <p className="text-xl text-muted-foreground mb-8">
            Join thousands of professionals who have automated their job applications
          </p>
          <Button size="lg" onClick={() => handlePlanSelect(SubscriptionPlan.FREE)}>
            Start Free Today <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
} 