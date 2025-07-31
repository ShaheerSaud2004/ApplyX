'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowRight, Bot, FileText, Target, TrendingUp, Users, Zap, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '@/components/AuthProvider'
import { AuthModals, useAuthModals } from '@/components/AuthModals'

interface AuthenticatedNavProps {
  onLoginOpen: () => void
  onSignupOpen: () => void
}

function AuthenticatedNav({ onLoginOpen, onSignupOpen }: AuthenticatedNavProps) {
  const { isAuthenticated, user, logout } = useAuth()

  if (isAuthenticated) {
    return (
      <>
        <Link className="text-xs sm:text-sm font-medium hover:underline underline-offset-4 transition-colors hidden sm:block" href="/dashboard">
          Dashboard
        </Link>
        <Link className="text-xs sm:text-sm font-medium hover:underline underline-offset-4 transition-colors hidden sm:block" href="/applications">
          Applications
        </Link>
        <Link className="text-xs sm:text-sm font-medium hover:underline underline-offset-4 transition-colors hidden sm:block" href="/manual-apply">
          Manual Apply Links
        </Link>
        <Link className="text-xs sm:text-sm font-medium hover:underline underline-offset-4 transition-colors hidden sm:block" href="/profile">
          Profile
        </Link>
        {user?.isAdmin && (
          <Link className="text-xs sm:text-sm font-medium hover:underline underline-offset-4 transition-colors text-blue-600 hidden sm:block" href="/admin">
            Admin
          </Link>
        )}
        <div className="flex items-center gap-2 sm:gap-3">
          <span className="text-xs sm:text-sm text-muted-foreground hidden sm:block">
            Welcome, {user?.firstName}
          </span>
          <button
            onClick={logout}
            className="text-xs sm:text-sm font-medium hover:underline underline-offset-4 text-red-600 transition-colors"
          >
            Logout
          </button>
        </div>
      </>
    )
  }

  return (
    <>
      <button
        onClick={onLoginOpen}
        className="text-xs sm:text-sm font-medium hover:underline underline-offset-4 transition-colors"
      >
        Sign In
      </button>
      <Button
        size="sm"
        onClick={onSignupOpen}
        className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white transition-all duration-200 text-xs sm:text-sm px-2 sm:px-3"
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
  const { isAuthenticated } = useAuth()

  if (isAuthenticated) {
    return (
      <div className="flex flex-col sm:flex-row items-center gap-4">
        <Button asChild size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-8">
          <Link href="/dashboard">
            Go to Dashboard <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
        <Button variant="outline" size="lg" asChild className="border-2 border-gray-300 hover:border-blue-500 hover:text-blue-600 transition-all duration-200 px-8">
          <Link href="/profile">Setup Profile</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col sm:flex-row items-center gap-4">
      <Button
        size="lg"
        onClick={onSignupOpen}
        className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-8"
      >
        Start Free Trial <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
      <Button variant="outline" size="lg" asChild className="border-2 border-gray-300 hover:border-blue-500 hover:text-blue-600 transition-all duration-200 px-8">
        <Link href="/pricing">View Pricing</Link>
      </Button>
    </div>
  )
}

// Animated Background Component
function AnimatedBackground() {
  const [particles, setParticles] = useState<Array<{
    left: string;
    top: string;
    animationDelay: string;
    animationDuration: string;
  }>>([]);

  useEffect(() => {
    // Generate particles only on client-side to avoid hydration mismatch
    const newParticles = Array.from({ length: 30 }, () => ({
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 300}%`,
      animationDelay: `${Math.random() * 3}s`,
      animationDuration: `${2 + Math.random() * 3}s`
    }));
    setParticles(newParticles);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* Animated Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/80 via-purple-50/60 to-pink-50/80 animate-gradient-xy"></div>

      {/* Dynamic Moving Gradient Blobs */}
      <div className="absolute top-20 left-10 w-64 h-64 bg-gradient-to-r from-blue-400/15 to-purple-400/15 rounded-full blur-xl animate-blob-1"></div>
      <div className="absolute top-40 right-20 w-80 h-80 bg-gradient-to-r from-purple-400/15 to-pink-400/15 rounded-full blur-xl animate-blob-2"></div>
      <div className="absolute top-[60%] left-1/4 w-72 h-72 bg-gradient-to-r from-pink-400/15 to-blue-400/15 rounded-full blur-xl animate-blob-3"></div>

      {/* Additional moving orbs for full page coverage */}
      <div className="absolute top-[80%] right-1/3 w-56 h-56 bg-gradient-to-r from-indigo-400/15 to-blue-400/15 rounded-full blur-xl animate-blob-4"></div>
      <div className="absolute top-[120%] left-1/2 w-64 h-64 bg-gradient-to-r from-green-400/15 to-blue-400/15 rounded-full blur-xl animate-blob-5"></div>
      <div className="absolute top-[160%] right-10 w-48 h-48 bg-gradient-to-r from-purple-400/15 to-pink-400/15 rounded-full blur-xl animate-blob-6"></div>

      {/* Extra dynamic blobs for more movement */}
      <div className="absolute top-[30%] right-1/2 w-40 h-40 bg-gradient-to-r from-cyan-400/15 to-blue-400/15 rounded-full blur-xl animate-blob-7"></div>
      <div className="absolute top-[100%] left-1/5 w-60 h-60 bg-gradient-to-r from-violet-400/15 to-purple-400/15 rounded-full blur-xl animate-blob-8"></div>

      {/* Geometric Shapes */}
      <div className="absolute top-1/4 right-1/4 w-6 h-6 bg-blue-500/20 rotate-45 animate-spin-slow"></div>
      <div className="absolute top-3/4 left-1/3 w-8 h-8 bg-purple-500/20 rounded-full animate-pulse-slow"></div>
      <div className="absolute top-1/2 right-1/3 w-4 h-4 bg-pink-500/20 animate-bounce-slow"></div>
      <div className="absolute top-[150%] left-1/4 w-5 h-5 bg-indigo-500/20 rounded animate-spin-slow"></div>
      <div className="absolute top-[200%] right-1/2 w-6 h-6 bg-green-500/20 rounded-full animate-pulse-slow"></div>

      {/* Particles - only render after client-side generation */}
      {particles.map((particle, i) => (
        <div
          key={i}
          className="absolute w-1 h-1 bg-blue-500/15 rounded-full animate-twinkle"
          style={{
            left: particle.left,
            top: particle.top,
            animationDelay: particle.animationDelay,
            animationDuration: particle.animationDuration
          }}
        />
      ))}
    </div>
  )
}

// Smooth scroll function
const smoothScrollTo = (elementId: string) => {
  const element = document.getElementById(elementId)
  if (element) {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })
  }
}

export default function HomePage() {
  const {
    isLoginOpen,
    isSignupOpen,
    openLogin,
    openSignup,
    closeLogin,
    closeSignup
  } = useAuthModals()

  return (
    <div className="flex flex-col min-h-screen relative">
      <AnimatedBackground />
      {/* Add Custom CSS for animations and smooth scrolling */}
      <style jsx global>{`
        html {
          scroll-behavior: smooth;
        }

        @keyframes gradient-xy {
          0%, 100% {
            transform: translate(0%, 0%);
          }
          25% {
            transform: translate(-5%, -5%);
          }
          50% {
            transform: translate(5%, -5%);
          }
          75% {
            transform: translate(-5%, 5%);
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0px) translateX(0px);
          }
          33% {
            transform: translateY(-20px) translateX(10px);
          }
          66% {
            transform: translateY(10px) translateX(-10px);
          }
        }

        @keyframes float-delayed {
          0%, 100% {
            transform: translateY(0px) translateX(0px);
          }
          33% {
            transform: translateY(15px) translateX(-15px);
          }
          66% {
            transform: translateY(-10px) translateX(15px);
          }
        }

        @keyframes float-slow {
          0%, 100% {
            transform: translateY(0px) translateX(0px);
          }
          50% {
            transform: translateY(-30px) translateX(20px);
          }
        }

        @keyframes blob-1 {
          0%, 100% {
            transform: translateY(0px) translateX(0px) scale(1) rotate(0deg);
          }
          25% {
            transform: translateY(-40px) translateX(30px) scale(1.1) rotate(90deg);
          }
          50% {
            transform: translateY(-20px) translateX(-25px) scale(0.9) rotate(180deg);
          }
          75% {
            transform: translateY(35px) translateX(15px) scale(1.05) rotate(270deg);
          }
        }

        @keyframes blob-2 {
          0%, 100% {
            transform: translateY(0px) translateX(0px) scale(1) rotate(0deg);
          }
          30% {
            transform: translateY(25px) translateX(-40px) scale(0.8) rotate(120deg);
          }
          60% {
            transform: translateY(-35px) translateX(20px) scale(1.2) rotate(240deg);
          }
        }

        @keyframes blob-3 {
          0%, 100% {
            transform: translateY(0px) translateX(0px) scale(1);
          }
          20% {
            transform: translateY(-50px) translateX(-30px) scale(1.15);
          }
          40% {
            transform: translateY(30px) translateX(40px) scale(0.85);
          }
          60% {
            transform: translateY(-20px) translateX(-50px) scale(1.1);
          }
          80% {
            transform: translateY(45px) translateX(25px) scale(0.9);
          }
        }

        @keyframes blob-4 {
          0%, 100% {
            transform: translateY(0px) translateX(0px) scale(1) rotate(0deg);
          }
          25% {
            transform: translateY(40px) translateX(-35px) scale(0.9) rotate(60deg);
          }
          50% {
            transform: translateY(-30px) translateX(45px) scale(1.1) rotate(180deg);
          }
          75% {
            transform: translateY(20px) translateX(-20px) scale(1.05) rotate(300deg);
          }
        }

        @keyframes blob-5 {
          0%, 100% {
            transform: translateY(0px) translateX(0px) scale(1);
          }
          33% {
            transform: translateY(-60px) translateX(50px) scale(0.8);
          }
          66% {
            transform: translateY(40px) translateX(-60px) scale(1.3);
          }
        }

        @keyframes blob-6 {
          0%, 100% {
            transform: translateY(0px) translateX(0px) scale(1) rotate(0deg);
          }
          40% {
            transform: translateY(55px) translateX(35px) scale(0.7) rotate(144deg);
          }
          80% {
            transform: translateY(-45px) translateX(-40px) scale(1.2) rotate(288deg);
          }
        }

        @keyframes blob-7 {
          0%, 100% {
            transform: translateY(0px) translateX(0px) scale(1);
          }
          25% {
            transform: translateY(-25px) translateX(-45px) scale(1.4);
          }
          50% {
            transform: translateY(35px) translateX(30px) scale(0.6);
          }
          75% {
            transform: translateY(-40px) translateX(50px) scale(1.1);
          }
        }

        @keyframes blob-8 {
          0%, 100% {
            transform: translateY(0px) translateX(0px) scale(1) rotate(0deg);
          }
          30% {
            transform: translateY(50px) translateX(-55px) scale(0.9) rotate(108deg);
          }
          60% {
            transform: translateY(-35px) translateX(40px) scale(1.25) rotate(216deg);
          }
          90% {
            transform: translateY(25px) translateX(-25px) scale(0.8) rotate(324deg);
          }
        }

        @keyframes spin-slow {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        @keyframes pulse-slow {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 0.6;
            transform: scale(1.1);
          }
        }

        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        @keyframes twinkle {
          0%, 100% {
            opacity: 0;
            transform: scale(0.5);
          }
          50% {
            opacity: 1;
            transform: scale(1);
          }
        }

        .animate-gradient-xy {
          animation: gradient-xy 8s ease infinite;
          background-size: 400% 400%;
        }

        .animate-float {
          animation: float 6s ease-in-out infinite;
        }

        .animate-float-delayed {
          animation: float-delayed 8s ease-in-out infinite;
        }

        .animate-float-slow {
          animation: float-slow 10s ease-in-out infinite;
        }

        .animate-blob-1 {
          animation: blob-1 12s ease-in-out infinite;
        }

        .animate-blob-2 {
          animation: blob-2 15s ease-in-out infinite;
        }

        .animate-blob-3 {
          animation: blob-3 18s ease-in-out infinite;
        }

        .animate-blob-4 {
          animation: blob-4 14s ease-in-out infinite;
        }

        .animate-blob-5 {
          animation: blob-5 16s ease-in-out infinite;
        }

        .animate-blob-6 {
          animation: blob-6 13s ease-in-out infinite;
        }

        .animate-blob-7 {
          animation: blob-7 11s ease-in-out infinite;
        }

        .animate-blob-8 {
          animation: blob-8 17s ease-in-out infinite;
        }

        .animate-spin-slow {
          animation: spin-slow 8s linear infinite;
        }

        .animate-pulse-slow {
          animation: pulse-slow 4s ease-in-out infinite;
        }

        .animate-bounce-slow {
          animation: bounce-slow 3s ease-in-out infinite;
        }

        .animate-twinkle {
          animation: twinkle 3s ease-in-out infinite;
        }
      `}</style>

      {/* Header */}
      <header className="px-3 sm:px-4 lg:px-6 h-14 flex items-center border-b relative z-20 bg-white/80 backdrop-blur-sm">
        <Link className="flex items-center justify-center" href="/">
          <div className="flex items-center space-x-1 sm:space-x-2">
            <div className="relative">
              <div className="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="h-3 w-3 sm:h-5 sm:w-5 text-white" />
              </div>
              <div className="absolute -top-0.5 -right-0.5 sm:-top-1 sm:-right-1 w-2 h-2 sm:w-3 sm:h-3 bg-gradient-to-br from-orange-500 to-red-500 rounded-full"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-lg sm:text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ApplyX
              </span>
              <span className="text-xs text-muted-foreground -mt-1 hidden sm:block">by Nebula.AI</span>
            </div>
          </div>
        </Link>
        <nav className="ml-auto flex items-center gap-2 sm:gap-4 lg:gap-6">
          <button
            onClick={() => smoothScrollTo('features')}
            className="text-xs sm:text-sm font-medium hover:underline underline-offset-4 transition-colors cursor-pointer hidden sm:block"
          >
            Features
          </button>
          <button
            onClick={() => smoothScrollTo('pricing')}
            className="text-xs sm:text-sm font-medium hover:underline underline-offset-4 transition-colors cursor-pointer hidden sm:block"
          >
            Pricing
          </button>
          <div className="flex items-center gap-2 sm:gap-4">
            <AuthenticatedNav onLoginOpen={openLogin} onSignupOpen={openSignup} />
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 relative z-10">
        <div className="container px-4 md:px-6 relative z-10">
          <div className="flex flex-col items-center space-y-4 text-center">
            <div className="space-y-6">
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-white/60 backdrop-blur-sm border border-blue-200">
                <Bot className="h-4 w-4 text-blue-600 mr-2" />
                <span className="text-sm font-medium text-blue-900">AI-Powered Job Application Engine</span>
              </div>
              <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
                <span className="bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent">
                  Apply to 100+ jobs
                </span>
                <br />
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  while you sleep
                </span>
              </h1>
              <p className="mx-auto max-w-[600px] text-lg text-gray-600 leading-relaxed">
                ApplyX's AI agent finds perfect job matches, tailors your resume with precision,
                and submits applications 24/7. Land your dream job faster than ever.
              </p>
              <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-500">
                <div className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
                  <span>No manual work</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
                  <span>AI-tailored resumes</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
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
      <section id="features" className="w-full py-12 md:py-24 lg:py-32 relative z-10 scroll-mt-16">
        <div className="container px-4 md:px-6">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
              <span className="bg-gradient-to-r from-gray-900 to-blue-900 bg-clip-text text-transparent">
                Why Choose ApplyX?
              </span>
            </h2>
            <p className="max-w-[700px] mx-auto text-lg text-gray-600 leading-relaxed">
              The complete AI-powered job application platform that works 24/7 to land you interviews
            </p>
          </div>
          <div className="grid gap-8 lg:grid-cols-3 md:grid-cols-2">
            <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:scale-105">
              <CardHeader className="text-center">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-4">
                  <Bot className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl">🚀 Automated job search</CardTitle>
                <CardDescription className="text-gray-600">
                  AI agent automatically finds and applies to relevant jobs while you sleep
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Intelligent job matching</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />24/7 automated applications</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />LinkedIn Easy Apply integration</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:scale-105">
              <CardHeader className="text-center">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4">
                  <FileText className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl">✨ AI-tailored resume + cover letters</CardTitle>
                <CardDescription className="text-gray-600">
                  Personalize your resume and generate unique cover letters for each application
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Keyword optimization</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Custom cover letters</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />ATS-friendly formatting</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:scale-105">
              <CardHeader className="text-center">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-4">
                  <Target className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl">🎯 Easy Apply integration</CardTitle>
                <CardDescription className="text-gray-600">
                  Seamlessly integrates with LinkedIn and other job platforms
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />LinkedIn Easy Apply</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Indeed Quick Apply</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Custom job boards</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:scale-105">
              <CardHeader className="text-center">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mb-4">
                  <TrendingUp className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl">📊 Dashboard + tracking</CardTitle>
                <CardDescription className="text-gray-600">
                  Track all your applications with detailed analytics and insights
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Application tracking</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Success metrics</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Response analytics</li>
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
      <section id="pricing" className="w-full py-12 md:py-24 lg:py-32 relative z-10 scroll-mt-16">
        <div className="container px-4 md:px-6">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
              <span className="bg-gradient-to-r from-gray-900 to-purple-900 bg-clip-text text-transparent">
                Simple, Transparent Pricing
              </span>
            </h2>
            <p className="max-w-[700px] mx-auto text-lg text-gray-600 leading-relaxed">
              Choose the perfect plan for your job search needs
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-3 max-w-5xl mx-auto">
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
          <Link className="text-xs hover:underline underline-offset-4 text-gray-500 hover:text-blue-600" href="#">
            Terms of Service
          </Link>
          <Link className="text-xs hover:underline underline-offset-4 text-gray-500 hover:text-blue-600" href="#">
            Privacy
          </Link>
        </nav>
      </footer>

      {/* Auth Modals */}
      <div className="relative z-50">
        <AuthModals
          isLoginOpen={isLoginOpen}
          isSignupOpen={isSignupOpen}
          onLoginClose={closeLogin}
          onSignupClose={closeSignup}
        />
      </div>
    </div>
  )
} 