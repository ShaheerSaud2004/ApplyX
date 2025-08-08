'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowRight, Bot, FileText, Target, TrendingUp, Users, Zap, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import { useModal } from '@/contexts/ModalContext'
import { useAuth } from '@/components/AuthProvider'

interface AuthenticatedNavProps {
  onLoginOpen: () => void
  onSignupOpen: () => void
}

function AuthenticatedNav({ onLoginOpen, onSignupOpen }: AuthenticatedNavProps) {
  const { user, logout } = useAuth()

  if (user) {
    return (
      <>
        <span className="text-sm text-gray-600 hidden md:block">
          Welcome, {user.firstName ? `${user.firstName} ${user.lastName}` : user.email}
        </span>
        <Button
          size="sm"
          variant="outline"
          onClick={logout}
          className="text-sm px-3 py-2"
        >
          Logout
        </Button>
      </>
    )
  }

  return (
    <>
      <button
        onClick={onLoginOpen}
        className="text-sm font-medium hover:underline underline-offset-4 transition-colors"
      >
        Sign In
      </button>
      <Button
        size="sm"
        onClick={onSignupOpen}
        className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white transition-all duration-200 text-sm px-3 py-2"
      >
        Sign Up
      </Button>
    </>
  )
}

interface CTAButtonsProps {
  onSignupOpen: () => void
}

function CTAButtons({ onSignupOpen }: CTAButtonsProps) {
  return (
    <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto px-4 sm:px-0">
      <Button
        size="lg"
        onClick={onSignupOpen}
        className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-8 py-3 w-full sm:w-auto text-base"
      >
        Start Free Trial <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
      <Button variant="outline" size="lg" asChild className="border-2 border-gray-300 hover:border-blue-500 hover:text-blue-600 transition-all duration-200 px-8 py-3 w-full sm:w-auto text-base">
        <Link href="/pricing">View Pricing</Link>
      </Button>
    </div>
  )
}

// Simple Background Component
function SimpleBackground() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/90 via-purple-50/70 to-pink-50/90"></div>
      <div className="absolute top-20 left-10 w-48 h-48 sm:w-64 sm:h-64 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-xl"></div>
      <div className="absolute top-40 right-10 sm:right-20 w-56 h-56 sm:w-80 sm:h-80 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-full blur-xl"></div>
      <div className="absolute top-[60%] left-1/4 w-48 h-48 sm:w-72 sm:h-72 bg-gradient-to-r from-pink-400/20 to-blue-400/20 rounded-full blur-xl"></div>
    </div>
  )
}

export default function HomePage() {
  const { openLogin, openSignup } = useModal()
  const { user, isLoading } = useAuth()

  // Redirect authenticated users to dashboard
  React.useEffect(() => {
    if (!isLoading && user) {
      window.location.href = '/dashboard'
    }
  }, [user, isLoading])

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  // Show loading or redirect if user is authenticated
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (user) {
    return null // Will redirect to dashboard
  }

  return (
    <div className="flex flex-col min-h-screen relative">
      <SimpleBackground />
      
      {/* Header */}
      <header className="px-4 sm:px-6 lg:px-8 h-16 sm:h-18 flex items-center border-b relative z-20 bg-white/90 backdrop-blur-sm">
        <Link className="flex items-center justify-center" href="/">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <div className="relative">
              <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
              </div>
              <div className="absolute -top-0.5 -right-0.5 sm:-top-1 sm:-right-1 w-2 h-2 sm:w-3 sm:h-3 bg-gradient-to-br from-orange-500 to-red-500 rounded-full"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ApplyX
              </span>
              <span className="text-xs text-muted-foreground -mt-1 hidden sm:block">by Nebula.AI</span>
            </div>
          </div>
        </Link>
        <nav className="ml-auto flex items-center gap-3 sm:gap-4 lg:gap-6">
          <button
            onClick={() => scrollToSection('features')}
            className="text-sm font-medium hover:underline underline-offset-4 transition-colors cursor-pointer hidden md:block"
          >
            Features
          </button>
          <button
            onClick={() => scrollToSection('pricing')}
            className="text-sm font-medium hover:underline underline-offset-4 transition-colors cursor-pointer hidden md:block"
          >
            Pricing
          </button>
          <button
            onClick={() => alert('Privacy Policy coming soon!')}
            className="text-sm font-medium hover:underline underline-offset-4 transition-colors cursor-pointer hidden lg:block"
          >
            Privacy Policy
          </button>
          <div className="flex items-center gap-2 sm:gap-3">
            <AuthenticatedNav onLoginOpen={openLogin} onSignupOpen={openSignup} />
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="w-full py-12 sm:py-16 md:py-24 lg:py-32 xl:py-40 relative z-10">
        <div className="container px-4 md:px-6 relative z-10">
          <div className="flex flex-col items-center space-y-6 sm:space-y-8 text-center">
            <div className="space-y-6 sm:space-y-8">
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-white/70 backdrop-blur-sm border border-blue-200 shadow-sm">
                <Bot className="h-4 w-4 text-blue-600 mr-2" />
                <span className="text-sm font-medium text-blue-900">AI-Powered Job Application Engine</span>
              </div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight px-4 leading-tight">
                <span className="bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent">
                  Apply to 100+ jobs
                </span>
                <br />
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  while you sleep
                </span>
              </h1>
              <p className="mx-auto max-w-[700px] text-lg sm:text-xl text-gray-600 leading-relaxed px-4 sm:px-6">
                ApplyX's AI agent finds perfect job matches, tailors your resume with precision,
                and submits applications 24/7. Land your dream job faster than ever.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-6 text-sm sm:text-base text-gray-500 px-4">
                <div className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  <span>No manual work</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  <span>AI-tailored resumes</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  <span>Real-time tracking</span>
                </div>
              </div>
            </div>
            <div className="pt-4">
              <CTAButtons onSignupOpen={openSignup} />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="w-full py-12 sm:py-16 md:py-24 lg:py-32 relative z-10 scroll-mt-16">
        <div className="container px-4 md:px-6">
          <div className="text-center space-y-6 mb-12 sm:mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold tracking-tight md:text-6xl lg:text-7xl px-4">
              <span className="bg-gradient-to-r from-gray-900 to-blue-900 bg-clip-text text-transparent">
                Why Choose ApplyX?
              </span>
            </h2>
            <p className="max-w-[700px] mx-auto text-lg sm:text-xl text-gray-600 leading-relaxed px-4">
              The complete AI-powered job application platform that works 24/7 to land you interviews
            </p>
          </div>
          <div className="grid gap-6 sm:gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            <Card className="border-0 shadow-xl bg-white/90 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:scale-105 p-6">
              <CardHeader className="text-center pb-4">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-4">
                  <Bot className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl sm:text-2xl">🚀 Automated job search</CardTitle>
                <CardDescription className="text-gray-600 text-base">
                  AI agent automatically finds and applies to relevant jobs while you sleep
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm sm:text-base space-y-3">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />Intelligent job matching</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />24/7 automated applications</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />LinkedIn Easy Apply integration</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-white/90 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:scale-105 p-6">
              <CardHeader className="text-center pb-4">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4">
                  <FileText className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl sm:text-2xl">✨ AI-tailored resume + cover letters</CardTitle>
                <CardDescription className="text-gray-600 text-base">
                  Personalize your resume and generate unique cover letters for each application
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm sm:text-base space-y-3">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />Keyword optimization</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />Custom cover letters</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />ATS-friendly formatting</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-white/90 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:scale-105 p-6">
              <CardHeader className="text-center pb-4">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-4">
                  <Target className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl sm:text-2xl">🎯 Easy Apply integration</CardTitle>
                <CardDescription className="text-gray-600 text-base">
                  Seamlessly integrates with LinkedIn and other job platforms
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm sm:text-base space-y-3">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />LinkedIn Easy Apply</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />Indeed Quick Apply</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />Custom job boards</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-white/90 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:scale-105 p-6">
              <CardHeader className="text-center pb-4">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mb-4">
                  <TrendingUp className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl sm:text-2xl">📊 Dashboard + tracking</CardTitle>
                <CardDescription className="text-gray-600 text-base">
                  Track all your applications with detailed analytics and insights
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm sm:text-base space-y-3">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />Application tracking</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />Success metrics</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />Response analytics</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:scale-105">
              <CardHeader className="text-center">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl flex items-center justify-center mb-4">
                  <Users className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl">💰 Flexible pricing</CardTitle>
                <CardDescription className="text-gray-600">
                  Start free with 10 applications per day, upgrade for more
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Free: 10 applications/day</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Basic: 60 applications/day</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Pro: 100+ applications/day</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:scale-105">
              <CardHeader className="text-center">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-pink-500 to-pink-600 rounded-2xl flex items-center justify-center mb-4">
                  <Zap className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl">⚡ Premium Features</CardTitle>
                <CardDescription className="text-gray-600">
                  Advanced features for power users and job seekers
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Daily email summaries</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Google Sheets export</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Referral bonuses</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="w-full py-8 sm:py-12 md:py-24 lg:py-32 relative z-10 scroll-mt-16">
        <div className="container px-4 md:px-6">
          <div className="text-center space-y-4 mb-8 sm:mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl px-2">
              <span className="bg-gradient-to-r from-gray-900 to-purple-900 bg-clip-text text-transparent">
                Simple, Transparent Pricing
              </span>
            </h2>
            <p className="max-w-[700px] mx-auto text-base sm:text-lg text-gray-600 leading-relaxed px-4">
              Choose the perfect plan for your job search needs
            </p>
          </div>
          <div className="grid gap-6 sm:gap-8 grid-cols-1 md:grid-cols-3 max-w-5xl mx-auto">
            {/* Free Plan */}
            <Card className="border-2 border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl mb-2">Free</CardTitle>
                <div className="text-4xl font-bold mb-2">$0</div>
                <CardDescription>Perfect for getting started</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-3 text-sm">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    10 applications per day
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    Basic AI resume tailoring
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    Application tracking
                  </li>
                </ul>
                <Button className="w-full mt-6" variant="outline" onClick={openSignup}>
                  Get Started Free
                </Button>
              </CardContent>
            </Card>

            {/* Basic Plan */}
            <Card className="border-2 border-blue-500 shadow-xl hover:shadow-2xl transition-all duration-300 relative">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </span>
              </div>
              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl mb-2">Basic</CardTitle>
                <div className="text-4xl font-bold mb-2">$9.99<span className="text-lg font-normal">/month</span></div>
                <CardDescription>Great for active job seekers</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-3 text-sm">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    60 applications per day
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    Advanced AI resume optimization
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    Custom cover letters
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    Priority support
                  </li>
                </ul>
                <Button className="w-full mt-6 bg-blue-500 hover:bg-blue-600" onClick={openSignup}>
                  Start Basic Plan
                </Button>
              </CardContent>
            </Card>

            {/* Pro Plan */}
            <Card className="border-2 border-purple-500 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl mb-2">Pro</CardTitle>
                <div className="text-4xl font-bold mb-2">$19.99<span className="text-lg font-normal">/month</span></div>
                <CardDescription>For serious job hunters</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-3 text-sm">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    100+ applications per day
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    Premium AI features
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    Daily email summaries
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    Export to Google Sheets
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-3" />
                    1-on-1 support
                  </li>
                </ul>
                <Button className="w-full mt-6 bg-purple-500 hover:bg-purple-600" onClick={openSignup}>
                  Start Pro Plan
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 relative z-10">
        <div className="container px-4 md:px-6 relative z-10">
          <div className="flex flex-col items-center space-y-4 text-center">
            <div className="space-y-4">
              <h2 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
                <span className="bg-gradient-to-r from-gray-900 to-purple-900 bg-clip-text text-transparent">
                  Ready to 10x Your
                </span>
                <br />
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Job Search?
                </span>
              </h2>
              <p className="mx-auto max-w-[600px] text-lg text-gray-600 leading-relaxed">
                Join thousands of professionals who have automated their job applications with ApplyX AI
              </p>
            </div>
            <div className="pt-4">
              <CTAButtons onSignupOpen={openSignup} />
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t bg-white/80 backdrop-blur-sm relative z-10">
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
          <button 
            onClick={() => alert('Privacy Policy coming soon!')}
            className="text-xs hover:underline underline-offset-4 text-gray-500 hover:text-blue-600 cursor-pointer"
          >
            Privacy Policy
          </button>
        </nav>
      </footer>
    </div>
  )
} 